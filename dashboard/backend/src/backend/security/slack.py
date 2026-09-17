
"""
Slack request signature verification (HMAC-SHA256), per Slack's spec:
https://api.slack.com/authentication/verifying-requests-from-slack

Every request from Slack carries X-Slack-Request-Timestamp and
X-Slack-Signature. We recompute the signature ourselves from the raw body
and compare with hmac.compare_digest (constant-time, avoids timing attacks)
— never trust the payload before this check passes.
"""

import hashlib
import hmac
import time

SLACK_SIGNATURE_VERSION = "v0"
MAX_REQUEST_AGE_SECONDS = 60 * 5  # reject anything older than 5 minutes (replay protection)


def is_valid_slack_signature(
    *,
    signing_secret: str,
    request_body: bytes,
    timestamp_header: str | None,
    signature_header: str | None,
) -> bool:
    if not signing_secret:
        # Misconfiguration, not a Slack-side problem — fail closed either way.
        return False
    if not timestamp_header or not signature_header:
        return False

    try:
        timestamp = int(timestamp_header)
    except ValueError:
        return False

    if abs(time.time() - timestamp) > MAX_REQUEST_AGE_SECONDS:
        return False

    base_string = f"{SLACK_SIGNATURE_VERSION}:{timestamp}:{request_body.decode('utf-8')}"
    computed = (
        SLACK_SIGNATURE_VERSION
        + "="
        + hmac.new(signing_secret.encode("utf-8"), base_string.encode("utf-8"), hashlib.sha256).hexdigest()
    )

    return hmac.compare_digest(computed, signature_header)
