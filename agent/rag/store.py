import chromadb
from chromadb.utils.embedding_functions import SentenceTransformerEmbeddingFunction
from pathlib import Path

CHROMA_PATH = Path(__file__).parent.parent / "data" / "chroma"
_EF = SentenceTransformerEmbeddingFunction(model_name="all-MiniLM-L6-v2")


def get_client() -> chromadb.PersistentClient:
    CHROMA_PATH.mkdir(parents=True, exist_ok=True)
    return chromadb.PersistentClient(path=str(CHROMA_PATH))


def get_runbook_collection(client=None):
    client = client or get_client()
    return client.get_or_create_collection("runbooks", embedding_function=_EF)


def get_incident_collection(client=None):
    client = client or get_client()
    return client.get_or_create_collection("incidents", embedding_function=_EF)
