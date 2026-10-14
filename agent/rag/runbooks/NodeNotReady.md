# NodeNotReady Runbook

## Symptoms
Kubernetes node reports NotReady status. Pods on the node may be evicted or pending.

## Common Causes
1. kubelet failure on the node
2. Node resource exhaustion — disk, memory, or PID pressure
3. Network partition between node and control plane

## Recommended Actions
- escalate immediately — node-level issues require human intervention
- Do not attempt automated pod restarts on a NotReady node

## Do NOT
- Attempt rollout_restart on pods scheduled to a NotReady node
- Ignore — pods will be rescheduled but root cause remains
