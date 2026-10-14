import os
import sys
from pathlib import Path
import json

# Add agent to path
sys.path.insert(0, str(Path(__file__).parent))

from graph import build_graph, policy_check, AgentState

def print_separator(title: str):
    print(f"\n{'='*20} {title} {'='*20}")

def test_direct_scenarios():
    print_separator("Testing Policy Decisions Through policy_check")
    scenarios = [
        {
            "name": "Scenario 1: Restart in warden-demo (low risk)",
            "state": {
                "diagnosis": {
                    "action": "rollout_restart",
                    "namespace": "warden-demo",
                    "target": "checkoutservice",
                    "reason": "OOMKilled deployment wide",
                    "confidence": 0.95,
                }
            },
            "expected_status": "auto_executable",
            "expected_allow": True,
        },
        {
            "name": "Scenario 2: Scale-down below min (min=2, desired=1)",
            "state": {
                "diagnosis": {
                    "action": "scale_deployment",
                    "namespace": "warden-demo",
                    "target": "checkoutservice",
                    "current_replicas": 2,
                    "desired_replicas": 1,
                    "reason": "Traffic drop",
                    "confidence": 0.9,
                }
            },
            "expected_status": "denied",
            "expected_allow": False,
        },
        {
            "name": "Scenario 3: Protected namespace (kube-system)",
            "state": {
                "diagnosis": {
                    "action": "restart_pod",
                    "namespace": "kube-system",
                    "target": "coredns",
                    "reason": "Pod unhealthy",
                    "confidence": 0.8,
                }
            },
            "expected_status": "denied",
            "expected_allow": False,
        },
        {
            "name": "Scenario 4: Rollback in warden-demo (always high risk)",
            "state": {
                "diagnosis": {
                    "action": "rollback_deployment",
                    "namespace": "warden-demo",
                    "target": "checkoutservice",
                    "reason": "Bad release v5",
                    "confidence": 0.98,
                }
            },
            "expected_status": "needs_approval",
            "expected_allow": True,
        },
        {
            "name": "Scenario 5: Unknown/unsupported action (deny, no crash)",
            "state": {
                "diagnosis": {
                    "action": "destroy_all",
                    "namespace": "warden-demo",
                    "target": "frontend",
                    "reason": "Test unknown",
                    "confidence": 0.5,
                }
            },
            "expected_status": "denied",
            "expected_allow": False,
        },
    ]

    for sc in scenarios:
        res = policy_check(sc["state"])
        diag = res["diagnosis"]
        print(f"\nTest: {sc['name']}")
        print(f"  Action:        {diag['action']}")
        print(f"  Target:        {diag['namespace']}/{diag['target']}")
        print(f"  Policy Status: {diag['policy_status']}")
        print(f"  Allowed:       {diag['allowed']}")
        print(f"  Risk:          {diag['risk']}")
        print(f"  Reasons:       {diag['policy_reasons']}")

        assert diag["policy_status"] == sc["expected_status"], f"Expected {sc['expected_status']}, got {diag['policy_status']}"
        assert diag["allowed"] == sc["expected_allow"], f"Expected allow={sc['expected_allow']}, got {diag['allowed']}"
        print("  -> PASSED")

if __name__ == "__main__":
    test_direct_scenarios()
    print("\nAll OPA policy scenarios PASSED!")
