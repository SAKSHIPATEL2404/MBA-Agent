# backend/app/retriever.py

from sentence_transformers import SentenceTransformer, util
import torch

class Retriever:
    def __init__(self, model_name="all-MiniLM-L6-v2"):
        self.model = SentenceTransformer(model_name)

        self.user_documents = {}

        self.user_embeddings = {}

    def add_doc(self, user_id, text):
        """Stores message + embedding for each user"""
        emb = self.model.encode(text, convert_to_tensor=True)
        if user_id not in self.user_documents:
            self.user_documents[user_id] = []
            self.user_embeddings[user_id] = []

        self.user_documents[user_id].append(text)
        self.user_embeddings[user_id].append(emb)

    def retrieve(self, user_id, query, top_k=3):
        """Return top-k relevant previous messages"""

        if user_id not in self.user_embeddings or len(self.user_embeddings[user_id]) == 0:
            return []

        query_emb = self.model.encode(query, convert_to_tensor=True)

        docs = self.user_documents[user_id]
        embeddings = self.user_embeddings[user_id]

        doc_embeddings = torch.stack(embeddings)

        scores = util.cos_sim(query_emb, doc_embeddings)[0]

        k = min(top_k, scores.size(0))

        top_results = scores.topk(k)
        indices = top_results.indices.tolist()

        retrieved_docs = [docs[i] for i in indices]
        return retrieved_docs

    def search(self, user_id, query, top_k=3):
        """Wrapper for retrieve() used by orchestrator"""
        return self.retrieve(user_id, query, top_k)

