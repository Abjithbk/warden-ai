# ADR 0002: Detect incidents with SLO burn-rate alerts, not static thresholds

## Status
Accepted

## Context
Warden needs a detection signal that is meaningful for autonomous remediation.
A static threshold (for example "error rate above 5%") ignores how much error
budget a service actually has, fires on short blips, and stays silent during
slow degradations. False positives are especially costly here because each
alert can trigger an agent diagnosis and a human approval request.

## Decision
Use multi-window, multi-burn-rate alerting from the Google SRE Workbook.

- SLI: ratio of failed to total requests, per service, excluding health checks.
  - frontend: HTTP status 5xx (path /_healthz excluded)
  - checkoutservice: gRPC codes Internal, Unavailable, DeadlineExceeded,
    Unknown, DataLoss (method grpc.health.v1.Health/Check excluded).
    Client-caused codes such as NotFound do not count against the SLO.
- SLO: 99% availability, so the error budget is 0.01.
- Error ratios are precomputed as recording rules
  (warden:sli_error_ratio:rate1m / 5m / 30m) so alert expressions stay short
  and Grafana reads the same series.
- Two alerts, each requiring BOTH a long and a short window to exceed the threshold:

| Alert | Severity | Threshold | Demo windows (long / short) | Production windows |
|---|---|---|---|---|
| WardenErrorBudgetBurnFast | critical | 14.4x budget | 5m / 1m | 1h / 5m |
| WardenErrorBudgetBurnSlow | warning | 6x budget | 30m / 5m | 6h / 30m |

- Alerts route from Alertmanager to the detector receiver, which normalizes
  them into one Incident per alert fingerprint.
- Alertmanager runs with alertmanagerConfigMatcherStrategy: None. Warden alerts
  aggregate by service and carry no namespace label, so the default namespace
  matcher would silently drop them.

## Consequences
- The long window filters short blips. The short window makes the alert clear
  soon after recovery instead of lingering.
- Windows are compressed for the demo so an alert fires in minutes. Production
  values are listed above; the burn-rate multipliers are unchanged.
- Measured (fault injection, paymentservice scaled too 0): Fast fired about
  2 minutes after injection; Fast resolved about 5 minutes after restore,
  Slow about 9 minutes.
- Limitation, SLI dilution: a whole-service SLI hides a broken critical path.
  A total checkout outage moved the frontend error ratio by only about 3%.
  Per-path SLIs (for example /cart/checkout) are future work.
- Limitation: no latency SLO yet. The duration histograms are collected and
  can back one later.
- Limitation: with low traffic (about 0.05 orders/s) ratios are noisy, so
  demo results depend on the load generator.
- The receiver keeps incidents in memory with a single replica until the
  dashboard backend (issue #8) provides persistence.
