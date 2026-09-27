"""LangGraph pipeline: evidence gathering -> diagnosis -> validation/retry.
Nodes wrap the functions built in M4.2 (schemas.py, prompts.py) and
M4.3 (tools.py). This graph is diagnosis-only; M5-M7 will extend it
with policy, approval, and execution nodes.
"""

from typing import TypedDict
from dotenv import load_dotenv
load_dotenv()
import os
from langchain_groq import ChatGroq
from langgraph.graph import StateGraph, END

from prompts import SYSTEM
from schemas import Action, Diagnosis
from tools import gather_evidence

MAX_RETRIES = 1


class AgentState(TypedDict):
    namespace: str
    target: str
    promql: str
    evidence: str
    diagnosis: Diagnosis | None
    attempts: int
    error: str | None


def evidence_node(state: AgentState) -> AgentState:
    evidence = gather_evidence(state["namespace"], state["target"], state["promql"])
    return {**state, "evidence": evidence}


def diagnose_node(state: AgentState) -> AgentState:
    llm = ChatGroq(model="openai/gpt-oss-120b", temperature=0, api_key=os.environ["GROQ_API_KEY"])
    structured = llm.with_structured_output(Diagnosis)
    try:
        diagnosis = structured.invoke([("system", SYSTEM), ("human", state["evidence"])])
        return {**state, "diagnosis": diagnosis, "error": None}
    except Exception as exc:
        return {
            **state,
            "diagnosis": None,
            "error": f"{type(exc).__name__}: {exc}",
            "attempts": state["attempts"] + 1,
        }


def fallback_node(state: AgentState) -> AgentState:
    fallback = Diagnosis(
        root_cause=f"Diagnosis failed after {state['attempts']} attempt(s): {state['error']}",
        confidence=0.0,
        evidence=[],
        proposed_action=Action.no_action,
        namespace=state["namespace"],
        target=state["target"],
    )
    return {**state, "diagnosis": fallback}


def should_retry(state: AgentState) -> str:
    if state["diagnosis"] is not None:
        return "done"
    if state["attempts"] <= MAX_RETRIES:
        return "retry"
    return "fallback"


def build_graph():
    graph = StateGraph(AgentState)
    graph.add_node("evidence", evidence_node)
    graph.add_node("diagnose", diagnose_node)
    graph.add_node("fallback", fallback_node)

    graph.set_entry_point("evidence")
    graph.add_edge("evidence", "diagnose")
    graph.add_conditional_edges(
        "diagnose",
        should_retry,
        {"retry": "diagnose", "fallback": "fallback", "done": END},
    )
    graph.add_edge("fallback", END)

    return graph.compile()

if __name__ == "__main__":
    import sys

    target = sys.argv[1] if len(sys.argv) > 1 else "frontend"
    promql = f'up{{namespace="warden-demo",job="{target}"}}'

    app = build_graph()
    result = app.invoke(
        {
            "namespace": "warden-demo",
            "target": target,
            "promql": promql,
            "evidence": "",
            "diagnosis": None,
            "attempts": 0,
            "error": None,
        }
    )
    print(result["diagnosis"].model_dump_json(indent=2))
