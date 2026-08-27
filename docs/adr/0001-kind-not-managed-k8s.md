# ADR 0001: Use Kind, not managed cloud Kubernetes

## Status
Accepted

## Context
Running a multi-service demo (Online Boutique, 11 services) plus a full
observability stack (Prometheus, OTel Collector, Grafana) requires more
RAM/CPU than a student laptop reliably provides.

## Decision
Use Kind (Kubernetes-in-Docker) on a single cloud VM (AWS EC2, t3.xlarge)
rather than a managed Kubernetes service (EKS/GKE).

## Consequences
- No managed control plane cost (EKS control plane is $73/month flat, 24/7).
- Full control over node topology; matches local dev workflow exactly.
- Tradeoff: no built-in cloud-native features (managed LB, IAM-integrated
  RBAC) — not needed for this project's scope.
- Reproducible from git: `kind create cluster --config cluster/kind-config.yaml`
  recreates the cluster identically on any Docker-capable machine.
