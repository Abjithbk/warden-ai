import json
from pathlib import Path

import pytest
from fastapi.testclient import TestClient

import main

DATA = Path(__file__).parent


@pytest.fixture(autouse=True)
def clean_store():
    main.incidents.clear()
    yield
    main.incidents.clear()


@pytest.fixture
def client() -> TestClient:
    return TestClient(main.app)


def load(name: str) -> dict:
    return json.loads((DATA / name).read_text())


def make_payload(fingerprint: str, status: str = "firing") -> dict:
    return {
        "version": "4",
        "status": status,
        "alerts": [
            {
                "status": status,
                "labels": {"alertname": "WardenErrorBudgetBurnFast", "service": "frontend"},
                "annotations": {},
                "startsAt": "2026-09-19T05:00:00Z",
                "fingerprint": fingerprint,
            }
        ],
    }


def test_healthz(client):
    response = client.get("/healthz")
    assert response.status_code == 200
    assert response.json() == {"status": "ok"}


def test_firing_creates_incident(client):
    response = client.post("/webhook/alertmanager", json=load("sample_firing.json"))
    assert response.status_code == 200
    assert response.json() == {"received": 1}

    incidents = client.get("/incidents").json()
    assert len(incidents) == 1
    incident = incidents[0]
    assert incident["fingerprint"] == "abc123def456"
    assert incident["service"] == "checkoutservice"
    assert incident["severity"] == "critical"
    assert incident["burn"] == "fast"
    assert incident["status"] == "firing"
    assert incident["resolved_at"] is None


def test_resolved_updates_same_incident(client):
    client.post("/webhook/alertmanager", json=load("sample_firing.json"))
    client.post("/webhook/alertmanager", json=load("sample_resolved.json"))

    incidents = client.get("/incidents").json()
    assert len(incidents) == 1
    assert incidents[0]["status"] == "resolved"
    assert incidents[0]["resolved_at"] == "2026-09-19T05:29:00Z"


def test_resolved_with_zero_end_time_has_no_resolved_at(client):
    payload = make_payload("zero1", status="resolved")
    payload["alerts"][0]["endsAt"] = "0001-01-01T00:00:00Z"
    client.post("/webhook/alertmanager", json=payload)

    incident = client.get("/incidents").json()[0]
    assert incident["status"] == "resolved"
    assert incident["resolved_at"] is None


def test_missing_labels_default_to_unknown(client):
    payload = {
        "alerts": [
            {"status": "firing", "startsAt": "2026-09-19T05:00:00Z", "fingerprint": "bare1"}
        ]
    }
    client.post("/webhook/alertmanager", json=payload)

    incident = client.get("/incidents").json()[0]
    assert incident["alertname"] == "unknown"
    assert incident["service"] == "unknown"
    assert incident["severity"] == "unknown"


def test_status_filter(client):
    client.post("/webhook/alertmanager", json=make_payload("a1", "firing"))
    client.post("/webhook/alertmanager", json=make_payload("b2", "resolved"))

    firing = client.get("/incidents", params={"status": "firing"}).json()
    resolved = client.get("/incidents", params={"status": "resolved"}).json()
    assert [i["fingerprint"] for i in firing] == ["a1"]
    assert [i["fingerprint"] for i in resolved] == ["b2"]


def test_invalid_status_rejected(client):
    payload = make_payload("bad1")
    payload["alerts"][0]["status"] = "bogus"
    response = client.post("/webhook/alertmanager", json=payload)
    assert response.status_code == 422


def test_store_is_capped_and_evicts_oldest(client, monkeypatch):
    monkeypatch.setattr(main, "MAX_INCIDENTS", 2)
    for fingerprint in ("one", "two", "three"):
        client.post("/webhook/alertmanager", json=make_payload(fingerprint))

    fingerprints = [i["fingerprint"] for i in client.get("/incidents").json()]
    assert fingerprints == ["three", "two"]
