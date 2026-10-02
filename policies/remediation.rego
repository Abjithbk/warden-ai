package warden.remediation

import rego.v1

# Default decision: deny unless explicitly allowed
default allow := false

# Default risk: high unless explicitly marked low
default risk := "high"

# --- Deny rules -------------------------------------------------

# Deny any action targeting a protected namespace
deny contains msg if {
	input.namespace in data.protected_namespaces
	msg := sprintf("namespace '%s' is protected", [input.namespace])
}

# Deny scale-down actions that would drop below the configured minimum
deny contains msg if {
	input.action == "scale"
	target_min := object.get(data.min_replicas, input.target, data.default_min_replicas)
	input.desired_replicas < target_min
	msg := sprintf("desired_replicas %d below min_replicas %d for '%s'", [input.desired_replicas, target_min, input.target])
}

# --- Allow logic --------------------------------------------------

allow if {
	count(deny) == 0
}

# --- Risk classification -----------------------------------------

# Restarts are considered low risk when allowed
risk := "low" if {
	allow
	input.action == "restart"
}

# Scale actions that stay at/above minimum, and don't scale down drastically, are low risk
risk := "low" if {
	allow
	input.action == "scale"
	input.desired_replicas >= input.current_replicas
}

# Rollbacks are treated as high risk regardless (always require approval)
risk := "high" if {
	input.action == "rollback"
}

# --- Final decision object exposed to the caller -------------------

decision := {
	"allow": allow,
	"risk": risk,
	"reasons": deny,
}
