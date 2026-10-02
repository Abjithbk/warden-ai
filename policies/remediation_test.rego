package warden.remediation

import rego.v1

test_deny_protected_namespace if {
	not allow with input as {
		"action": "restart",
		"namespace": "kube-system",
		"target": "coredns",
	}
		with data.protected_namespaces as ["kube-system", "monitoring"]
}

test_allow_restart_in_normal_namespace if {
	allow with input as {
		"action": "restart",
		"namespace": "warden-demo",
		"target": "checkoutservice",
	}
		with data.protected_namespaces as ["kube-system", "monitoring"]
}

test_deny_scale_below_min if {
	not allow with input as {
		"action": "scale",
		"namespace": "warden-demo",
		"target": "checkoutservice",
		"current_replicas": 2,
		"desired_replicas": 1,
	}
		with data.protected_namespaces as ["kube-system", "monitoring"]
		with data.min_replicas as {"checkoutservice": 2}
		with data.default_min_replicas as 1
}

test_allow_scale_at_min if {
	allow with input as {
		"action": "scale",
		"namespace": "warden-demo",
		"target": "checkoutservice",
		"current_replicas": 2,
		"desired_replicas": 2,
	}
		with data.protected_namespaces as ["kube-system", "monitoring"]
		with data.min_replicas as {"checkoutservice": 2}
		with data.default_min_replicas as 1
}

test_rollback_is_always_high_risk if {
	result := decision with input as {
		"action": "rollback",
		"namespace": "warden-demo",
		"target": "checkoutservice",
	}
		with data.protected_namespaces as ["kube-system", "monitoring"]

	result.risk == "high"
}
