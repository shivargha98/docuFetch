"""
LangGraph state schema for docuFetch.

DocuFetchState is the shared TypedDict that flows through every node in the
RAG pipeline, carrying conversation history, the current query, retrieved
chunks, relevance verdict, and source filenames.
"""
from typing import TypedDict


class DocuFetchState(TypedDict, total=False):
    """
    Shared state for the docuFetch LangGraph pipeline.

    All fields are optional (total=False) so nodes can return partial updates.
    """
    messages: list        # HumanMessage + AIMessage conversation history (capped at 20)
    query: str            # Current user query string
    retrieved_chunks: list  # top-K Document objects from hybrid retrieval
    is_relevant: bool     # Result of the relevance check node
    sources: list         # List of unique source filenames from the answer
