import sys, os
sys.path.insert(0, os.path.dirname(__file__))

import uuid as _uuid
from fastapi import FastAPI
from pydantic import BaseModel
from graph import build_graph
from rag.retriever import store_incident

api = FastAPI(title="Warden Agent")


class DiagnoseRequest(BaseModel):
    name: str
    namespace: str = "warden-demo"
    severity: str = "critical"
    description: str = ""
    pod: str = ""
    fingerprint: str = ""


@api.get("/healthz")
def healthz():
    return {"status": "ok"}


@api.post("/diagnose")
def diagnose(req: DiagnoseRequest):
    alert = {
        "name": req.name,
        "namespace": req.namespace,
        "severity": req.severity,
        "description": req.description,
        "pod": req.pod,
    }
    graph = build_graph()
    result = graph.invoke({
        "alert": alert,
        "k8s_context": "",
        "runbook_context": "",
        "incident_history": "",
        "diagnosis": {},
    })

    diag = result["diagnosis"]

    # Persist incident to ChromaDB so future diagnoses can learn from history.
    # Use fingerprint as the stable ID so repeated alerts upsert (idempotent).
    incident_id = req.fingerprint or str(_uuid.uuid4())
    try:
        store_incident(
            incident_id=incident_id,
            description=req.description or req.name,
            action=diag.get("action", "unknown"),
            outcome=diag.get("reason", ""),
        )
    except Exception:
        pass  # Never let memory write block the response

    return {"fingerprint": req.fingerprint, "diagnosis": diag}

