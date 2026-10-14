"""Warden detector receiver.

Accepts Alertmanager webhook payloads and normalizes each alert into an
Incident. Incidents are held in memory for now; persistence arrives with the
dashboard backend (M8) and the agent consumes them from M4 onward.
"""
import json
import logging
import os
from collections import OrderedDict
from datetime import datetime, timezone
from threading import RLock, Thread
from typing import Literal

import httpx
from dotenv import load_dotenv
from fastapi import FastAPI
from pydantic import BaseModel, Field

load_dotenv()

logging.basicConfig(level=logging.INFO, format="%(message)s")
log = logging.getLogger("warden.detector")

MAX_INCIDENTS = 200
ZERO_TIME = "0001-01-01T00:00:00Z"
AGENT_URL = os.environ.get("AGENT_URL", "http://localhost:8001")


class AMAlert(BaseModel):
    status: Literal["firing", "resolved"]
    labels: dict[str, str] = Field(default_factory=dict)
    annotations: dict[str, str] = Field(default_factory=dict)
    startsAt: str
    endsAt: str = ZERO_TIME
    generatorURL: str = ""
    fingerprint: str


class AMWebhook(BaseModel):
    version: str = "4"
    status: str = "firing"
    alerts: list[AMAlert] = Field(default_factory=list)


class Incident(BaseModel):
    fingerprint: str
    alertname: str
    service: str
    severity: str
    burn: str
    slo: str
    status: Literal["firing", "resolved"]
    summary: str
    description: str
    started_at: str
    resolved_at: str | None = None
    updated_at: str


app = FastAPI(title="Warden Detector Receiver")
incidents: "OrderedDict[str, Incident]" = OrderedDict()
incidents_lock = RLock()


def normalize(alert: AMAlert) -> Incident:
    labels, ann = alert.labels, alert.annotations
    resolved_at = None
    if alert.status == "resolved" and alert.endsAt != ZERO_TIME:
        resolved_at = alert.endsAt
    return Incident(
        fingerprint=alert.fingerprint,
        alertname=labels.get("alertname", "unknown"),
        service=labels.get("service", "unknown"),
        severity=labels.get("severity", "unknown"),
        burn=labels.get("burn", "unknown"),
        slo=labels.get("slo", "unknown"),
        status=alert.status,
        summary=ann.get("summary", ""),
        description=ann.get("description", ""),
        started_at=alert.startsAt,
        resolved_at=resolved_at,
        updated_at=datetime.now(timezone.utc).isoformat(),
    )


def call_agent(incident: Incident) -> None:
    """POST incident to agent /diagnose in a background thread."""
    payload = {
        "name": incident.alertname,
        "namespace": "warden-demo",
        "severity": incident.severity,
        "description": incident.description,
        "pod": "",
        "fingerprint": incident.fingerprint,
    }
    try:
        resp = httpx.post(f"{AGENT_URL}/diagnose", json=payload, timeout=60)
        resp.raise_for_status()
        log.info(json.dumps({"event": "agent_diagnosis", "fingerprint": incident.fingerprint, "result": resp.json()}))
    except Exception as exc:
        log.error(json.dumps({"event": "agent_error", "fingerprint": incident.fingerprint, "error": str(exc)}))


@app.get("/healthz")
def healthz() -> dict:
    return {"status": "ok"}


@app.post("/webhook/alertmanager")
def alertmanager_webhook(payload: AMWebhook) -> dict:
    for alert in payload.alerts:
        incident = normalize(alert)
        with incidents_lock:
            existing = incidents.get(incident.fingerprint)
            if existing is None or incident.started_at >= existing.started_at:
                incidents[incident.fingerprint] = incident
                incidents.move_to_end(incident.fingerprint)
                while len(incidents) > MAX_INCIDENTS:
                    incidents.popitem(last=False)
        log.info(json.dumps({"event": "incident", **incident.model_dump()}))
        if incident.status == "firing":
            Thread(target=call_agent, args=(incident,), daemon=True).start()
    return {"received": len(payload.alerts)}


@app.get("/incidents")
def list_incidents(status: Literal["firing", "resolved"] | None = None) -> list[Incident]:
    with incidents_lock:
        items = list(incidents.values())
    if status:
        items = [i for i in items if i.status == status]
    return list(reversed(items))
