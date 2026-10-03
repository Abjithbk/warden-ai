"""
Unit tests for security/slack.py — signature verification in isolation.
No HTTP layer here, so these can't be flaky due to the 5-minute replay
window the way an end-to-end curl test can be.
"""

import hashlib
import hmac
import time

from backend.security.slack import is_valid_slack_signature

SECRET = "test-secret-123"


def _sign(secret: str, timestamp: str, body: str) -> str:
    base = f"v0:{timestamp}:{body}"
    return "v0=" + hmac.new(secret.encode(), base.encode(), hashlib.sha256).hexdigest()


def test_valid_signature_accepted():
    ts = str(int(time.time()))
    body = "payload=test"
    sig = _sign(SECRET, ts, body)

    assert is_valid_slack_signature(
        signing_secret=SECRET,
        request_body=body.encode(),
        timestamp_header=ts,
        signature_header=sig,
    )


def test_tampered_body_rejected():
    ts = str(int(time.time()))
    sig = _sign(SECRET, ts, "payload=original")

    assert not is_valid_slack_signature(
        signing_secret=SECRET,
        request_body=b"payload=tampered",
        timestamp_header=ts,
        signature_header=sig,
    )


def test_wrong_secret_rejected():
    ts = str(int(time.time()))
    body = "payload=test"
    sig = _sign("wrong-secret", ts, body)

    assert not is_valid_slack_signature(
        signing_secret=SECRET,
        request_body=body.encode(),
        timestamp_header=ts,
        signature_header=sig,
    )


def test_stale_timestamp_rejected():
    old_ts = str(int(time.time()) - 400)  # older than MAX_REQUEST_AGE_SECONDS (300)
    body = "payload=test"
    sig = _sign(SECRET, old_ts, body)

    assert not is_valid_slack_signature(
        signing_secret=SECRET,
        request_body=body.encode(),
        timestamp_header=old_ts,
        signature_header=sig,
    )


def test_missing_signing_secret_fails_closed():
    ts = str(int(time.time()))
    body = "payload=test"
    sig = _sign(SECRET, ts, body)

    assert not is_valid_slack_signature(
        signing_secret="",
        request_body=body.encode(),
        timestamp_header=ts,
        signature_header=sig,
    )
