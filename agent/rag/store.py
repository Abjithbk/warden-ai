import chromadb
from chromadb.utils.embedding_functions import ONNXMiniLM_L6_V2
from pathlib import Path

CHROMA_PATH = Path(__file__).parent.parent / "data" / "chroma"
_EF = ONNXMiniLM_L6_V2()

# Singleton client — avoids opening a new PersistentClient on every request
# which can cause SQLite file-lock contention under concurrent load.
_client: chromadb.PersistentClient | None = None


def get_client() -> chromadb.PersistentClient:
    global _client
    if _client is None:
        CHROMA_PATH.mkdir(parents=True, exist_ok=True)
        _client = chromadb.PersistentClient(path=str(CHROMA_PATH))
    return _client


def get_runbook_collection(client=None):
    client = client or get_client()
    return client.get_or_create_collection("runbooks", embedding_function=_EF)


def get_incident_collection(client=None):
    client = client or get_client()
    return client.get_or_create_collection("incidents", embedding_function=_EF)
