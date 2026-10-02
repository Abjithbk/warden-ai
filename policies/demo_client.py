from client import check_policy

# Simulated agent outputs — mimics what M4 is expected to emit
mock_plans = [
    {"action": "restart", "namespace": "warden-demo", "target": "checkoutservice"},
    {"action": "scale", "namespace": "warden-demo", "target": "checkoutservice",
     "current_replicas": 2, "desired_replicas": 1},
    {"action": "restart", "namespace": "kube-system", "target": "coredns"},
    {"action": "rollback", "namespace": "warden-demo", "target": "frontend"},
]

for plan in mock_plans:
    result = check_policy(**plan)
    print(f"{plan['action']:10} {plan['target']:15} -> {result}")
