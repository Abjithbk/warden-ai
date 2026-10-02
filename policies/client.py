import requests

OPA_URL = "http://localhost:8181/v1/data/warden/remediation/decision"

def check_policy(action: str, namespace: str, target: str, **extra) -> dict:
    """
    Sends a proposed remediation action to OPA and returns its decision.
    Returns: {"allow": bool, "risk": "low"|"high", "reasons": [str]}
    """
    payload = {
        "input": {
            "action": action,
            "namespace": namespace,
            "target": target,
            **extra,
        }
    }
    resp = requests.post(OPA_URL, json=payload, timeout=5)
    resp.raise_for_status()
    return resp.json()["result"]
