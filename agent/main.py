import sys, os
sys.path.insert(0, os.path.dirname(__file__))

from fastapi import FastAPI
from pydantic import BaseModel
from graph import build_graph

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
    return {"fingerprint": req.fingerprint, "diagnosis": result["diagnosis"]}
