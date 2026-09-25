
"""
API-level tests for the approve/reject endpoints — the actual HTTP
contract, plus the rate limiter wired in main.py.
"""


def test_approve_endpoint_success(client, pending_incident):
    incident, _ = pending_incident

    response = client.post(
        f"/api/v1/incidents/{incident.id}/approve",
        json={"actioned_by": "dashboard:amaya"},
    )

    assert response.status_code == 200
    body = response.json()
    assert body["incident_status"] == "resolved"
    assert body["approval_status"] == "approved"
    assert body["remediation_action"]["status"] == "succeeded"


def test_approve_endpoint_conflict_on_second_call(client, pending_incident):
    incident, _ = pending_incident

    first = client.post(f"/api/v1/incidents/{incident.id}/approve", json={"actioned_by": "dashboard:amaya"})
    second = client.post(f"/api/v1/incidents/{incident.id}/approve", json={"actioned_by": "dashboard:amaya"})

    assert first.status_code == 200
    assert second.status_code == 409


def test_reject_endpoint_requires_reason(client, pending_incident):
    incident, _ = pending_incident

    response = client.post(f"/api/v1/incidents/{incident.id}/reject", json={"actioned_by": "dashboard:amaya"})

    assert response.status_code == 422


def test_approve_endpoint_rate_limited(client, pending_incident):
    incident, _ = pending_incident

    statuses = []
    for _ in range(11):
        response = client.post(
            f"/api/v1/incidents/{incident.id}/approve",
            json={"actioned_by": "dashboard:amaya"},
        )
        statuses.append(response.status_code)

    assert statuses[0] == 200
    assert 429 in statuses, f"Expected a 429 somewhere in {statuses} — rate limit did not trigger"
