"""
ChromaDB vector store operations for docuFetch.

Provides insert, delete, and query operations against the local ChromaDB
collection. Text chunks store content and metadata; image chunks (added in
Issue 4) store file_path in metadata only.
"""
import chromadb
from langchain_core.documents import Document

COLLECTION_NAME = "docufetch"


class ChromaStore:
    """Manages a ChromaDB collection for docuFetch."""

    def __init__(self, path: str):
        """Open (or create) a PersistentClient at path and get/create the collection."""
        self._client = chromadb.PersistentClient(path=path)
        self._collection = self._client.get_or_create_collection(COLLECTION_NAME)

    def insert_chunks(self, chunks: list[Document], embeddings: list[list[float]]) -> None:
        """
        Insert Document chunks with their embeddings into the collection.
        IDs are generated as filename_chunkindex to be deterministic.
        """
        ids = [f"{chunk.metadata['filename']}_{i}" for i, chunk in enumerate(chunks)]
        self._collection.add(
            ids=ids,
            documents=[c.page_content for c in chunks],
            embeddings=embeddings,
            metadatas=[c.metadata for c in chunks],
        )

    def delete_by_filename(self, filename: str) -> None:
        """Delete all chunks whose metadata filename matches the given filename."""
        self._collection.delete(where={"filename": filename})

    def query(self, embedding: list[float], top_k: int = 3) -> list[Document]:
        """
        Run a vector similarity query. Returns at most top_k Documents
        with their metadata intact.
        """
        count = self._collection.count()
        n_results = min(top_k, count)
        if n_results == 0:
            return []
        results = self._collection.query(
            query_embeddings=[embedding],
            n_results=n_results,
        )
        docs = []
        for doc, meta in zip(results["documents"][0], results["metadatas"][0]):
            docs.append(Document(page_content=doc, metadata=meta))
        return docs

    def get_unique_filenames(self) -> list[str]:
        """Return the list of unique filenames currently stored in the collection."""
        result = self._collection.get(include=["metadatas"])
        filenames = {m["filename"] for m in result["metadatas"]}
        return list(filenames)

    def get_all_text_chunks(self) -> list[Document]:
        """
        Return all stored chunks whose file_type is NOT 'image'.
        Used to build the BM25 index from text content only.
        """
        result = self._collection.get(include=["documents", "metadatas"])
        docs = []
        for doc, meta in zip(result["documents"], result["metadatas"]):
            if meta.get("file_type") != "image":
                docs.append(Document(page_content=doc, metadata=meta))
        return docs
