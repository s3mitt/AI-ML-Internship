"""
In-memory vector store.

Retrieval uses TF-IDF vectors + cosine similarity (scikit-learn). This is a
deliberately lightweight choice over a neural embedding model (e.g.
sentence-transformers/PyTorch): it needs no GPU, no multi-hundred-MB model
download, and is fast to fit/refit for a learning-project API, while still
being a genuine vector-space retriever rather than plain substring search.
The store is swappable for a neural-embedding or external vector DB backend
later without touching the API layer, since main.py only calls
add_document / search / delete / list_documents on `store`.

Trade-off worth calling out in the testing report: TF-IDF is refit over the
*entire* corpus on every upload, so it captures exact/lexical matches well
but not paraphrases or synonyms the way a neural embedding would.
"""
import threading
from datetime import datetime, timezone
from typing import Optional
from uuid import uuid4

from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity

from app.config import TOP_K
from app.chunking import Chunk


class VectorStore:
    def __init__(self):
        self._lock = threading.Lock()
        # documents[doc_id] = metadata dict (includes "chunk_ids")
        self.documents: dict[str, dict] = {}
        # chunks[chunk_id] = {"text":..., "doc_id":..., "chunk_index":..., "filename":...}
        self.chunks: dict[str, dict] = {}
        self._chunk_ids: list[str] = []
        self._vectorizer: Optional[TfidfVectorizer] = None
        self._matrix = None  # sparse (N, V) TF-IDF matrix, rows aligned to _chunk_ids

    def add_document(self, filename: str, content_type: str, file_size_bytes: int,
                      num_characters: int, chunks: list[Chunk]) -> dict:
        doc_id = str(uuid4())

        with self._lock:
            new_chunk_ids = []
            for c in chunks:
                chunk_id = str(uuid4())
                self.chunks[chunk_id] = {
                    "text": c.text,
                    "doc_id": doc_id,
                    "chunk_index": c.chunk_index,
                    "filename": filename,
                }
                self._chunk_ids.append(chunk_id)
                new_chunk_ids.append(chunk_id)

            self._refit_index_locked()

            metadata = {
                "doc_id": doc_id,
                "filename": filename,
                "content_type": content_type,
                "file_size_bytes": file_size_bytes,
                "num_chunks": len(chunks),
                "num_characters": num_characters,
                "uploaded_at": datetime.now(timezone.utc).isoformat(),
                "chunk_ids": new_chunk_ids,
            }
            self.documents[doc_id] = metadata

        return metadata

    def _refit_index_locked(self):
        """Rebuilds the TF-IDF matrix over all current chunks. Caller holds the lock."""
        if not self._chunk_ids:
            self._vectorizer = None
            self._matrix = None
            return
        texts = [self.chunks[cid]["text"] for cid in self._chunk_ids]
        self._vectorizer = TfidfVectorizer(stop_words="english", max_features=50000)
        self._matrix = self._vectorizer.fit_transform(texts)

    def list_documents(self) -> list[dict]:
        with self._lock:
            return [
                {k: v for k, v in doc.items() if k != "chunk_ids"}
                for doc in self.documents.values()
            ]

    def get_document(self, doc_id: str) -> Optional[dict]:
        with self._lock:
            doc = self.documents.get(doc_id)
            return {k: v for k, v in doc.items() if k != "chunk_ids"} if doc else None

    def delete_document(self, doc_id: str) -> bool:
        with self._lock:
            doc = self.documents.pop(doc_id, None)
            if doc is None:
                return False
            ids_to_remove = set(doc["chunk_ids"])
            self._chunk_ids = [cid for cid in self._chunk_ids if cid not in ids_to_remove]
            for cid in ids_to_remove:
                self.chunks.pop(cid, None)
            self._refit_index_locked()
            return True

    def is_empty(self) -> bool:
        with self._lock:
            return self._matrix is None or len(self._chunk_ids) == 0

    def search(self, query: str, top_k: int = TOP_K, doc_id: Optional[str] = None) -> list[dict]:
        with self._lock:
            if self._matrix is None or len(self._chunk_ids) == 0:
                return []

            query_vec = self._vectorizer.transform([query])
            scores = cosine_similarity(query_vec, self._matrix)[0]

            if doc_id is not None:
                idxs = [i for i, cid in enumerate(self._chunk_ids) if self.chunks[cid]["doc_id"] == doc_id]
                if not idxs:
                    return []
            else:
                idxs = list(range(len(self._chunk_ids)))

            idxs.sort(key=lambda i: -scores[i])
            idxs = idxs[:min(top_k, len(idxs))]

            results = []
            for i in idxs:
                cid = self._chunk_ids[i]
                chunk = self.chunks[cid]
                results.append({
                    "chunk_id": cid,
                    "doc_id": chunk["doc_id"],
                    "filename": chunk["filename"],
                    "chunk_index": chunk["chunk_index"],
                    "text": chunk["text"],
                    "score": float(scores[i]),
                })
            return results


# Single process-wide store (fine for a learning-project API with in-memory state)
store = VectorStore()
