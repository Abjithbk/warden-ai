"""Warden M4 — LangGraph diagnosis agent.

Graph: START -> retrieval -> gather_context -> diagnose -> END
"""
import os
import logging
from typing import TypedDict, Literal

from langchain_groq import ChatGroq
from langchain_core.messages import SystemMessage, HumanMessage
from langgraph.graph import StateGraph, START, END
from pydantic import BaseModel, Field
from kubernetes import client, config

from rag.retriever import get_runbook, get_similar_incidents

log = logging.getLogger("warden.agent")


# ---------------------------------------------------------------------------
# Structured output schema
# ---------------------------------------------------------------------------

class DiagnosisResult(BaseModel):
    action: Literal[
        "rollout_restart",
        "scale_deployment",
        "restart_pod",
        "no_action",
        "escalate",
    ] = Field(description="Remediation action to take")
    target: str = Field(description="Kubernetes resource name to act on")
    namespace: str = Field(description="Namespace of the target resource")
    reason: str = Field(description="Short explanation of the diagnosis")
    confidence: float = Field(description="Confidence score between 0.0 and 1.0")


# ---------------------------------------------------------------------------
# Agent state
# ---------------------------------------------------------------------------

class AgentState(TypedDict):
    alert: dict
    k8s_context: str
    runbook_context: str
    incident_history: str
    diagnosis: dict


# ---------------------------------------------------------------------------
# Nodes
# ---------------------------------------------------------------------------

def retrieval_node(state: AgentState) -> AgentState:
    """Retrieve relevant runbook and similar past incidents from ChromaDB."""
    alert = state["alert"]
    alert_name = alert.get("name", "")
    description = alert.get("description", "")

    runbook = get_runbook(alert_name)
    history = get_similar_incidents(description)

    if runbook:
        log.info("runbook retrieved for: %s", alert_name)
    else:
        log.info("no runbook found for: %s", alert_name)

    state["runbook_context"] = runbook
    state["incident_history"] = history
    return state


def gather_context(state: AgentState) -> AgentState:
    """Pull live pod and event data from Kubernetes for the alerted namespace."""
    alert = state["alert"]
    namespace = alert.get("namespace", "warden-demo")

    lines = []
    try:
        try:
            config.load_incluster_config()
        except Exception:
            config.load_kube_config()

        v1 = client.CoreV1Api()

        pods = v1.list_namespaced_pod(namespace=namespace)
        lines.append(f"=== Pods in {namespace} ===")
        for p in pods.items:
            cs = p.status.container_statuses or []
            for c in cs:
                if c.state.running:
                    state_info = "Running"
                elif c.state.waiting:
                    state_info = f"Waiting:{c.state.waiting.reason or 'Unknown'}"
                elif c.state.terminated:
                    state_info = f"Terminated:{c.state.terminated.reason or 'Unknown'}"
                else:
                    state_info = "Unknown"
                lines.append(
                    f"  {p.metadata.name} | {c.name} | {state_info} | restarts={c.restart_count}"
                )

        events = v1.list_namespaced_event(namespace=namespace)
        warnings = [e for e in events.items if e.type == "Warning"]
        warnings.sort(key=lambda e: e.last_timestamp or e.event_time or "", reverse=True)
        lines.append(f"\n=== Recent Warning Events in {namespace} ===")
        for e in warnings[:10]:
            lines.append(f"  {e.reason}: {e.message} (obj={e.involved_object.name})")

    except Exception as exc:
        log.warning("k8s context gather failed: %s", exc)
        lines.append(f"[k8s unavailable: {exc}]")

    state["k8s_context"] = "\n".join(lines)
    return state


def diagnose(state: AgentState) -> AgentState:
    """Call Groq LLM with alert + k8s context + RAG context -> DiagnosisResult."""
    alert = state["alert"]
    k8s_ctx = state.get("k8s_context", "")
    runbook = state.get("runbook_context", "")
    history = state.get("incident_history", "")

    system_prompt = """You are Warden, an autonomous SRE agent for Kubernetes incident remediation.

Analyse the alert and live cluster context, then return a structured remediation decision.

## Action vocabulary
- rollout_restart   -> deployment-wide issue (OOMKilled, config error, image pull failure across pods)
- scale_deployment  -> capacity or traffic-related issue
- restart_pod       -> single isolated pod misbehaving; rest of deployment is healthy
- no_action         -> transient blip or already self-healed
- escalate          -> unknown cause or automated action risk too high

## Pod scope rule (CRITICAL)
If multiple pods show the same failure, ALWAYS choose rollout_restart over restart_pod.
restart_pod is valid ONLY for a single misbehaving pod in an otherwise healthy deployment.

## OOMKilled rule (CRITICAL)
OOMKilled is ALWAYS a deployment-wide resource issue. NEVER choose restart_pod for OOMKilled.
Always choose rollout_restart with the deployment name as target for OOMKilled alerts.
A single OOMKilled pod will OOM again immediately after restart — rollout_restart is the correct action.

## Target field
- rollout_restart / scale_deployment -> set target to the DEPLOYMENT name
- restart_pod -> set target to the POD name

## Confidence
1.0 = certain. Below 0.4 prefer escalate."""

    human_parts = [
        f"## Alert\n{alert}",
        f"## Live Kubernetes Context\n{k8s_ctx}",
    ]
    if runbook:
        human_parts.append(f"## Runbook\n{runbook}")
    if history:
        human_parts.append(f"## Similar Past Incidents\n{history}")

    human_prompt = "\n\n".join(human_parts)

    llm = ChatGroq(
        model="openai/gpt-oss-120b",
        api_key=os.environ.get("GROQ_API_KEY", ""),
        temperature=0,
    ).with_structured_output(DiagnosisResult)

    result: DiagnosisResult = llm.invoke([
        SystemMessage(content=system_prompt),
        HumanMessage(content=human_prompt),
    ])
    log.info("diagnosis: %s", result.model_dump())
    state["diagnosis"] = result.model_dump()
    return state


# ---------------------------------------------------------------------------
# Graph
# ---------------------------------------------------------------------------

def build_graph():
    g = StateGraph(AgentState)
    g.add_node("retrieval", retrieval_node)
    g.add_node("gather_context", gather_context)
    g.add_node("diagnose", diagnose)
    g.add_edge(START, "retrieval")
    g.add_edge("retrieval", "gather_context")
    g.add_edge("gather_context", "diagnose")
    g.add_edge("diagnose", END)
    return g.compile()
