"""
Outbound Slack: POST /slack/notify, /slack/test, GET /slack/status, and the
response_url update after a button click. Slack itself is never called —
slack_service._post_json is monkeypatched.
"""

import hashlib
import hmac
import json
import time
from urllib.parse import urlencode

import pytest

from backend.core.config import get_settings
from backend.services import slack_service

SECRET = "test-secret-123"
RESPONSE_URL = "https://hooks.slack.com/actions/T1/B1/xyz"


@pytest.fixture()
def slack_configured(monkeypatch):
    settings = get_settings()
    monkeypatch.setattr(settings, "slack_bot_token", "xoxb-test")
    monkeypatch.setattr(settings, "slack_channel_id", "C123")
    monkeypatch.setattr(settings, "slack_signing_secret", SECRET)


@pytest.fixture()
def slack_calls(monkeypatch):
    """Captures every outbound Slack call; replies like Slack's happy path."""
    calls: list[dict] = []

    def fake_post(url, payload, token=None):
        calls.append({"url": url, "payload": payload, "token": token})
        return {"ok": True, "channel": "C123", "ts": "1700000000.000100"}

    monkeypatch.setattr(slack_service, "_post_json", fake_post)
    return calls


def _signed_click(action_id, incident_id, user=None, response_url=RESPONSE_URL):
    payload = {
        "actions": [{"action_id": action_id, "value": str(incident_id)}],
        "user": user or {"id": "U1"},
        "response_url": response_url,
    }
    body = urlencode({"payload": json.dumps(payload)})
    ts = str(int(time.time()))
    sig = (
        "v0="
        + hmac.new(SECRET.encode(), f"v0:{ts}:{body}".encode(), hashlib.sha256).hexdigest()
    )
    return body, {
        "Content-Type": "application/x-www-form-urlencoded",
        "X-Slack-Request-Timestamp": ts,
        "X-Slack-Signature": sig,
    }


# ---------------------------------------------------------------- status
def test_status_reports_config_without_secrets(client, slack_configured):
    data = client.get("/api/v1/slack/status").json()
    assert data == {
        "can_notify": True,
        "can_receive_actions": True,
        "bot_token_set": True,
        "signing_secret_set": True,
        "channel_id": "C123",
    }
    assert "xoxb" not in json.dumps(data)


def test_status_when_unconfigured(client, monkeypatch):
    settings = get_settings()
    for name in ("slack_bot_token", "slack_channel_id", "slack_signing_secret"):
        monkeypatch.setattr(settings, name, "")
    data = client.get("/api/v1/slack/status").json()
    assert data["can_notify"] is False
    assert data["can_receive_actions"] is False
    assert data["channel_id"] is None


# ------------------------------------------------------------------ test
def test_send_test_message(client, slack_configured, slack_calls):
    response = client.post("/api/v1/slack/test")
    assert response.status_code == 200
    assert response.json()["ok"] is True
    assert slack_calls[0]["url"].endswith("/chat.postMessage")
    assert slack_calls[0]["token"] == "xoxb-test"
    assert slack_calls[0]["payload"]["channel"] == "C123"


def test_send_test_message_unconfigured_returns_503(client, monkeypatch):
    monkeypatch.setattr(get_settings(), "slack_bot_token", "")
    assert client.post("/api/v1/slack/test").status_code == 503


# ---------------------------------------------------------------- notify
def test_notify_posts_buttons_and_stores_ts(
    client, pending_incident, slack_configured, slack_calls, db_session
):
    incident, approval = pending_incident

    response = client.post(f"/api/v1/slack/notify/{incident.id}")

    assert response.status_code == 200
    assert response.json()["already_sent"] is False
    assert response.json()["ts"] == "1700000000.000100"

    blocks = slack_calls[0]["payload"]["blocks"]
    actions = next(b for b in blocks if b["type"] == "actions")
    assert [e["action_id"] for e in actions["elements"]] == [
        "approve_incident",
        "reject_incident",
    ]
    assert all(e["value"] == str(incident.id) for e in actions["elements"])

    db_session.refresh(approval)
    assert approval.slack_message_ts == "1700000000.000100"
    assert approval.slack_channel == "C123"


def test_notify_twice_does_not_double_post(
    client, pending_incident, slack_configured, slack_calls
):
    incident, _ = pending_incident
    client.post(f"/api/v1/slack/notify/{incident.id}")
    second = client.post(f"/api/v1/slack/notify/{incident.id}")

    assert second.json()["already_sent"] is True
    assert len(slack_calls) == 1


def test_notify_force_reposts(client, pending_incident, slack_configured, slack_calls):
    incident, _ = pending_incident
    client.post(f"/api/v1/slack/notify/{incident.id}")
    client.post(f"/api/v1/slack/notify/{incident.id}?force=true")
    assert len(slack_calls) == 2


def test_notify_unconfigured_returns_503(client, pending_incident, monkeypatch):
    monkeypatch.setattr(get_settings(), "slack_bot_token", "")
    incident, _ = pending_incident
    assert client.post(f"/api/v1/slack/notify/{incident.id}").status_code == 503


def test_notify_slack_error_returns_502(
    client, pending_incident, slack_configured, monkeypatch
):
    monkeypatch.setattr(
        slack_service,
        "_post_json",
        lambda url, payload, token=None: {"ok": False, "error": "channel_not_found"},
    )
    incident, _ = pending_incident
    response = client.post(f"/api/v1/slack/notify/{incident.id}")
    assert response.status_code == 502
    assert "channel_not_found" in response.json()["detail"]


def test_notify_unknown_incident_returns_404(client, slack_configured):
    assert client.post("/api/v1/slack/notify/9999").status_code == 404


def test_notify_already_actioned_returns_409(
    client, pending_incident, slack_configured, slack_calls
):
    incident, _ = pending_incident
    client.post(f"/api/v1/incidents/{incident.id}/approve", json={})
    assert client.post(f"/api/v1/slack/notify/{incident.id}").status_code == 409
    assert slack_calls == []


# --------------------------------------------------- click -> response_url
def test_click_approve_replaces_original_message(
    client, pending_incident, slack_configured, slack_calls
):
    incident, _ = pending_incident
    body, headers = _signed_click(
        "approve_incident", incident.id, user={"id": "U1", "username": "amaya"}
    )

    response = client.post("/api/v1/slack/actions", headers=headers, content=body)

    assert response.status_code == 200
    assert "approved" in response.json()["text"]
    assert "slack:amaya" in response.json()["text"]

    update = slack_calls[-1]
    assert update["url"] == RESPONSE_URL
    assert update["payload"]["replace_original"] is True
    # buttons are gone from the replacement message
    assert all(b["type"] != "actions" for b in update["payload"]["blocks"])


def test_click_after_already_actioned_sends_ephemeral_not_error(
    client, pending_incident, slack_configured, slack_calls
):
    incident, _ = pending_incident
    client.post(f"/api/v1/incidents/{incident.id}/approve", json={})

    body, headers = _signed_click("approve_incident", incident.id)
    response = client.post("/api/v1/slack/actions", headers=headers, content=body)

    assert response.status_code == 200  # no error icon for the Slack user
    assert slack_calls[-1]["payload"]["response_type"] == "ephemeral"
    assert slack_calls[-1]["payload"]["replace_original"] is False


def test_click_with_non_slack_response_url_is_not_called(
    client, pending_incident, slack_configured, slack_calls
):
    incident, _ = pending_incident
    body, headers = _signed_click(
        "reject_incident", incident.id, response_url="https://evil.example.com/x"
    )

    response = client.post("/api/v1/slack/actions", headers=headers, content=body)

    assert response.status_code == 200
    assert slack_calls == []