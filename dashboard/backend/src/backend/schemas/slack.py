"""Response schemas for the Slack settings / notify endpoints."""

from pydantic import BaseModel


class SlackStatusOut(BaseModel):
    # True when Warden can post messages (bot token + channel set).
    can_notify: bool
    # True when Warden can accept button clicks (signing secret set).
    can_receive_actions: bool
    bot_token_set: bool
    signing_secret_set: bool
    channel_id: str | None


class SlackTestOut(BaseModel):
    ok: bool
    channel: str
    ts: str


class SlackNotifyOut(BaseModel):
    incident_id: int
    approval_request_id: int
    channel: str
    ts: str
    already_sent: bool