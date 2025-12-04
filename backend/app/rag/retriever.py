# backend/app/rag/retriever.py
# Simple chroma-based retriever. For local dev, you can use Chroma or stub results.
import os

try:
    from chromadb import Client
    from chromadb.config import Settings
    CHROMA_AVAILABLE = True
except Exception:
    CHROMA_AVAILABLE = False

# backend/app/rag/retriever.py
# Chroma disabled for now — fallback retriever

class Retriever:
    def __init__(self):
        pass

    def add_docs(self, docs: list):
        return

    def retrieve(self, query: str, k: int = 4):
        return []
