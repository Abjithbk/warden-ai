#!/bin/sh
set -e
echo "Ingesting runbooks into ChromaDB..."
python -m rag.ingest
echo "Starting agent..."
exec uvicorn main:api --host 0.0.0.0 --port 8001
