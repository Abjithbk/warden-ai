# HighLatency Runbook

## Symptoms
p95 or p99 latency exceeds SLO threshold. Burn rate alert firing on latency budget.

## Common Causes
1. Traffic spike — insufficient replicas
2. Downstream service slow — cascading latency
3. CPU throttling due to low limits
4. GC pressure or memory pressure

## Recommended Actions
- If traffic spike: scale_deployment to add replicas
- If downstream dependency: escalate — scaling won't help
- If CPU throttled: escalate for resource limit increase
- If single pod slow: restart_pod

## Do NOT
- Restart pods during a traffic spike — it makes latency worse temporarily
