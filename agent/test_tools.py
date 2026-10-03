from tools import query_prometheus, get_k8s_context, query_tempo

print("=== Prometheus ===")
print(query_prometheus('up{namespace="warden-demo"}'))

print("\n=== K8s context ===")
print(get_k8s_context("warden-demo", "frontend"))

print("\n=== Tempo ===")
print(query_tempo("frontend"))
