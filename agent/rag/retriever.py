from .store import get_runbook_collection, get_incident_collection


def get_runbook(alert_name: str, n_results: int = 1) -> str:
    try:
        col = get_runbook_collection()
        # Guard: ChromaDB raises InvalidArgumentError if n_results < 1
        effective_n = max(1, n_results)
        results = col.query(query_texts=[alert_name], n_results=effective_n)
        docs = results.get("documents", [[]])[0]
        return "\n\n".join(docs) if docs else ""
    except Exception:
        return ""


def get_similar_incidents(description: str, n_results: int = 3) -> str:
    col = get_incident_collection()
    try:
        count = col.count()
        if count == 0:
            return ""
        # Guard: cannot request more results than documents in collection
        effective_n = min(n_results, count)
        results = col.query(query_texts=[description], n_results=effective_n)
        docs = results.get("documents", [[]])[0]
        return "\n\n".join(docs) if docs else ""
    except Exception:
        return ""


def store_incident(incident_id: str, description: str, action: str, outcome: str):
    col = get_incident_collection()
    col.upsert(
        ids=[incident_id],
        documents=[f"Incident: {description}\nAction taken: {action}\nOutcome: {outcome}"],
        metadatas=[{"action": action}],
    )
