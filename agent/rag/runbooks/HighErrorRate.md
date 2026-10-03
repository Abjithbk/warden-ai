# HighErrorRate Runbook

## Symptoms
HTTP 5xx error rate exceeds threshold. Burn rate alert firing on error budget.

## Common Causes
1. Upstream dependency failure
2. Database connection exhaustion
3. Bad deployment — new code introduced regression
4. Resource exhaustion — CPU throttling causing timeouts

## Recommended Actions
- If recent deployment: rollout_restart to trigger rollback evaluation
- If dependency failure: escalate — automated restart will not help
- If single pod returning errors: restart_pod
- If all pods affected: rollout_restart

## Do NOT
- Scale up blindly without checking if the cause is a bad deployment
