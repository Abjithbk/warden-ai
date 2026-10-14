import os
import requests


class PolicyUnavailableError(Exception):
    """Raised when OPA responds successfully but returns no decision result."""
    pass


DEFAULT_OPA_URL = "http://localhost:8181/v1/data/warden/remediation/decision"
OPA_URL = os.environ.get("OPA_URL", DEFAULT_OPA_URL)


def check_policy(action: str, namespace: str, target: str, **extra) -> dict:
    """
    Sends a proposed remediation action to OPA and returns its decision.
    Returns: {"allow": bool, "risk": "low"|"high", "reasons": [str]}

    Raises:
        requests.RequestException: on HTTP/connection failures (OPA unreachable, timeout, etc.)
        PolicyUnavailableError: if OPA responds but the response has no 'result' key
            (e.g. the policy path doesn't exist or evaluation produced no value)
    """
    url = os.environ.get("OPA_URL", OPA_URL)
    payload = {
        "input": {
            "action": action,
            "namespace": namespace,
            "target": target,
            **extra,
        }
    }
    resp = requests.post(url, json=payload, timeout=5)
    resp.raise_for_status()

    body = resp.json()
    if "result" not in body:
        raise PolicyUnavailableError(
            f"OPA returned no 'result' for decision path warden/remediation/decision; "
            f"response body: {body}"
        )
    return body["result"]
