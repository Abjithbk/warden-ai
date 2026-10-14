from pathlib import Path
from .store import get_client, get_runbook_collection


def ingest_runbooks():
    client = get_client()
    col = get_runbook_collection(client)
    runbook_dir = Path(__file__).parent / "runbooks"

    for f in runbook_dir.glob("*.md"):
        text = f.read_text()
        alert_name = f.stem
        col.upsert(
            ids=[alert_name],
            documents=[text],
            metadatas=[{"alert": alert_name}],
        )
        print(f"ingested: {alert_name}")


if __name__ == "__main__":
    ingest_runbooks()
    print("done")
