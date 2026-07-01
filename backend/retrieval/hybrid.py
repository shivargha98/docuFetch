"""
Hybrid retriever for docuFetch.

Runs BM25 keyword search and ChromaDB vector similarity search in parallel,
then fuses the two ranked result lists using Reciprocal Rank Fusion (RRF).
Returns the top-K fused chunks.
"""
from langchain_core.documents import Document

from backend.retrieval.bm25 import BM25Index
from backend.embeddings.store import ChromaStore
from backend.embeddings.embedder import EmbeddingClient


def _rrf_fuse(list_a: list[Document], list_b: list[Document], final_k: int = 3) -> list[Document]:
    """
    Fuse two ranked Document lists using Reciprocal Rank Fusion.

    Score formula: sum of 1/(rank+60) across all lists where the document appears.
    Deduplication key: (filename, first 100 chars of page_content).
    Returns at most final_k Documents sorted by descending fused score.
    """
    scores: dict[str, float] = {}
    doc_map: dict[str, Document] = {}

    for rank, doc in enumerate(list_a, start=1):
        key = doc.metadata.get("filename", "") + doc.page_content[:100]
        scores[key] = scores.get(key, 0.0) + 1.0 / (rank + 60)
        doc_map[key] = doc

    for rank, doc in enumerate(list_b, start=1):
        key = doc.metadata.get("filename", "") + doc.page_content[:100]
        scores[key] = scores.get(key, 0.0) + 1.0 / (rank + 60)
        doc_map[key] = doc

    sorted_keys = sorted(scores, key=lambda k: scores[k], reverse=True)
    return [doc_map[k] for k in sorted_keys[:final_k]]


class HybridRetriever:
    """Combines BM25 and vector similarity retrieval via RRF fusion."""

    def __init__(self, bm25_index: BM25Index, chroma_store: ChromaStore, embedder: EmbeddingClient):
        """
        Initialise the hybrid retriever with both retrieval backends and the embedder.
        bm25_index can be rebuilt and replaced via rebuild_bm25().
        """
        self._bm25 = bm25_index
        self._store = chroma_store
        self._embedder = embedder

    def rebuild_bm25(self, documents: list[Document]) -> None:
        """
        Replace the BM25 index with a freshly built one from documents.
        Call this after each ingestion run to keep the index current.
        """
        self._bm25 = BM25Index(documents)

    def retrieve(self, query: str, n_per_retriever: int = 5, final_k: int = 3) -> list[Document]:
        """
        Run BM25 and vector search, fuse results with RRF, return top final_k chunks.

        BM25 searches text chunks only (images excluded at index build time).
        Vector search includes all chunks (text and image).
        """
        bm25_results = self._bm25.query(query, top_k=n_per_retriever)
        query_embedding = self._embedder.embed_texts([query])[0]
        vector_results = self._store.query(query_embedding, top_k=n_per_retriever)
        return _rrf_fuse(bm25_results, vector_results, final_k=final_k)
