"""
BM25 keyword index for docuFetch.

Builds an in-memory BM25 index from text chunks stored in ChromaDB.
Image chunks are excluded — they have no text content to keyword-match.
The index can be rebuilt from scratch without restarting the server.
"""
from langchain_core.documents import Document
from rank_bm25 import BM25Okapi


class BM25Index:
    """In-memory BM25 index over text chunks."""

    def __init__(self, documents: list[Document]):
        """
        Build the BM25 index from a list of Documents.
        Tokenises each document's page_content by whitespace splitting.
        Image chunks (file_type='image') are excluded even if passed in.
        """
        self._docs = [d for d in documents if d.metadata.get("file_type") != "image"]
        tokenised = [d.page_content.lower().split() for d in self._docs]
        self._index = BM25Okapi(tokenised) if tokenised else None

    def query(self, query_text: str, top_k: int = 5) -> list[Document]:
        """
        Return up to top_k Documents ranked by BM25 score for query_text.
        Returns an empty list if the index is empty.
        """
        if self._index is None or not self._docs:
            return []
        tokens = query_text.lower().split()
        scores = self._index.get_scores(tokens)
        ranked = sorted(range(len(scores)), key=lambda i: scores[i], reverse=True)
        return [self._docs[i] for i in ranked[:top_k]]
