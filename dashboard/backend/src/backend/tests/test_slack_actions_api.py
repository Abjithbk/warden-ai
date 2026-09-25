
"""
API-level tests for POST /api/v1/slack/actions.
"""

import hashlib
import hmac
import time

SECRET = "test-secret-123"


def _sign(secret: str, timestamp: str, body: str) -> str:
    base = f"v0:{timestamp}:{body}"
    return "v0=" + hmac.new(secret.encode(), base.encode(), hashlib.sha256).hexdigest()


def test_slack_approve_with_invalid_signature_returns_401(client, monkeypatch):
    from backend.core.config import get_settings

    monkeypatch.setattr(get_settings(), "slack_signing_secret", SECRET)

    ts = str(int(time.time()))
    body = 'payload={"actions":[{"action_id":"approve_incident","value":"1"}],"user":{"id":"U1"}}'

    response = client.post(
        "/api/v1/slack/actions",
        headers={
            "Content-Type": "application/x-www-form-urlencoded",
            "X-Slack-Request-Timestamp": ts,
            "X-Slack-Signature": "v0=wrongsignature",
        },
        content=body,
    )

    assert response.status_code == 401


def test_slack_approve_with_valid_signature_succeeds(client, pending_incident, monkeypatch):
    from backend.core.config import get_settings

    monkeypatch.setattr(get_settings(), "slack_signing_secret", SECRET)

    incident, _ = pending_incident

    ts = str(int(time.time()))
    body = f'payload={{"actions":[{{"action_id":"approve_incident","value":"{incident.id}"}}],"user":{{"id":"U1"}}}}'
    sig = _sign(SECRET, ts, body)

    response = client.post(
        "/api/v1/slack/actions",
        headers={
            "Content-Type": "application/x-www-form-urlencoded",
            "X-Slack-Request-Timestamp": ts,
            "X-Slack-Signature": sig,
        },
        content=body,
    )

    assert response.status_code == 200
    assert f"Incident #{incident.id} approved" in response.json()["text"]
