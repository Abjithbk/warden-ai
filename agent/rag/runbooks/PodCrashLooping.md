# PodCrashLooping Runbook

## Symptoms
Pod restarts more than 5 times in 10 minutes. Status shows OOMKilled or CrashLoopBackOff.

## Common Causes
1. Memory limit too low — OOMKilled
2. Application startup failure — bad env var, missing secret, misconfigured liveness probe
3. Image pull failure or corrupted image

## Recommended Actions
- OOMKilled: ALWAYS rollout_restart the deployment. A single pod restart will OOM again immediately.
- CrashLoopBackOff on multiple pods: rollout_restart the deployment
- CrashLoopBackOff on single isolated pod, rest healthy: restart_pod
- Unknown cause with high risk: escalate

## Do NOT
- Use restart_pod for OOMKilled — the pod will crash again immediately
- Delete and recreate the deployment unless rollback is required
- Ignore if more than 3 services are affected simultaneously
