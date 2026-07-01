"""
LangGraph node implementations for the docuFetch RAG pipeline.

Each node is a factory function that captures its dependencies (LLM, retriever)
and returns a callable that takes/returns DocuFetchState dicts.

Nodes:
  retrieve          — hybrid retrieval, populates retrieved_chunks
  relevance_check   — Claude Haiku yes/no relevance judgment
  generate          — Claude Haiku 2-4 sentence answer with source citations
  no_results        — returns standard "no relevant information" message
"""
from langchain_core.documents import Document
from langchain_core.messages import HumanMessage, AIMessage

from backend.graph.state import DocuFetchState
from backend.retrieval.hybrid import HybridRetriever

NO_RESULTS_MESSAGE = "I couldn't find relevant information in your documents."


def make_retrieve_node(hybrid_retriever: HybridRetriever):
    """Factory: returns the retrieve node function bound to hybrid_retriever."""
    def retrieve(state: DocuFetchState) -> dict:
        """Run hybrid retrieval for the current query, populate retrieved_chunks."""
        query = state.get("query", "")
        chunks = hybrid_retriever.retrieve(query) if query else []
        return {"retrieved_chunks": chunks}
    return retrieve


def make_relevance_check_node(llm):
    """Factory: returns the relevance_check node function bound to llm."""
    def relevance_check(state: DocuFetchState) -> dict:
        """
        Judge whether retrieved chunks are relevant to the query.
        Sets is_relevant=False immediately if retrieved_chunks is empty
        (no LLM call made). Otherwise asks Claude Haiku yes/no.
        """
        chunks = state.get("retrieved_chunks", [])
        if not chunks:
            return {"is_relevant": False}

        chunks_text = "\n\n".join(
            f"[source: {c.metadata.get('filename', 'unknown')}]\n{c.page_content}"
            for c in chunks
        )
        prompt = (
            f"Query: {state.get('query', '')}\n\n"
            f"Retrieved document chunks:\n{chunks_text}\n\n"
            "Are these chunks relevant to answering the query? "
            "Answer with only 'yes' or 'no'."
        )
        response = llm.invoke([HumanMessage(content=prompt)])
        is_relevant = "yes" in response.content.strip().lower()
        return {"is_relevant": is_relevant}
    return relevance_check


def make_generate_node(llm):
    """Factory: returns the generate node function bound to llm."""
    def generate(state: DocuFetchState) -> dict:
        """
        Generate a 2-4 sentence answer grounded in retrieved_chunks.
        Cites source filenames inline as [source: filename].
        Appends the new HumanMessage and AIMessage to messages history.
        History is trimmed to at most 20 messages before the LLM call.
        """
        chunks = state.get("retrieved_chunks", [])
        query = state.get("query", "")
        messages = state.get("messages", [])

        # Trim history to last 20 messages before LLM call
        history = messages[-20:] if len(messages) > 20 else messages

        chunks_text = "\n\n".join(
            f"[source: {c.metadata.get('filename', 'unknown')}]\n{c.page_content}"
            for c in chunks
        )
        sources = list({
            c.metadata["filename"]
            for c in chunks
            if c.metadata.get("filename")
        })

        prompt = (
            f"Using only the provided documents, answer the following question in "
            f"exactly 2-4 sentences. Cite each source as [source: filename].\n\n"
            f"Documents:\n{chunks_text}\n\n"
            f"Question: {query}"
        )
        call_messages = history + [HumanMessage(content=prompt)]
        response = llm.invoke(call_messages)

        updated_messages = messages + [HumanMessage(content=query), response]
        return {"sources": sources, "messages": updated_messages}
    return generate


def make_no_results_node():
    """Factory: returns the no_results node function (no external dependencies)."""
    def no_results(state: DocuFetchState) -> dict:
        """
        Return the standard no-results message and append it to messages history.
        sources is set to an empty list.
        """
        query = state.get("query", "")
        messages = state.get("messages", [])
        ai_msg = AIMessage(content=NO_RESULTS_MESSAGE)
        updated_messages = messages + [HumanMessage(content=query), ai_msg]
        return {"sources": [], "messages": updated_messages}
    return no_results
