# Cluster Setup

Local 3-node Kind cluster for Warden AI development.

## Prerequisites
- Docker
- kind v0.33.0-alpha+
- kubectl

## Create the cluster

```bash
kind create cluster --name warden --config kind-config.yaml
kubectl cluster-info --context kind-warden
```

## Topology
- 1 control-plane node
- 2 worker nodes
- Port 30080 (NodePort) mapped to host port 8080

## Storage
Uses Kind's default `local-path-provisioner` (hostPath-backed, node-local).
This is ephemeral and tied to the node container's filesystem — acceptable
for a dev/demo cluster, not representative of production-grade storage
(which would use a CSI driver backed by cloud block storage).

## MetalLB (LoadBalancer support)
```bash
kubectl apply -f metallb-config.yaml
```
