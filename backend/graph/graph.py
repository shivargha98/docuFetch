"""
LangGraph graph assembly for the docuFetch RAG pipeline.

Wires the four nodes into a compiled graph:
  retrieve → relevance_check → (generate | no_results)

The conditional edge routes to generate when is_relevant=True,
and to no_results when is_relevant=False.
"""
from langgraph.graph import StateGraph, END
from langchain_anthropic import ChatAnthropic

from backend.graph.state import DocuFetchState
from backend.graph.nodes import (
    make_retrieve_node,
    make_relevance_check_node,
    make_generate_node,
    make_no_results_node,
)
from backend.retrieval.hybrid import HybridRetriever


def build_graph(hybrid_retriever: HybridRetriever, llm: ChatAnthropic):
    """
    Build and compile the docuFetch LangGraph pipeline.

    Returns a compiled graph that accepts DocuFetchState and returns
    an updated DocuFetchState with answer in messages[-1] and sources.
    """
    workflow = StateGraph(DocuFetchState)

    workflow.add_node("retrieve", make_retrieve_node(hybrid_retriever))
    workflow.add_node("relevance_check", make_relevance_check_node(llm))
    workflow.add_node("generate", make_generate_node(llm))
    workflow.add_node("no_results", make_no_results_node())

    workflow.set_entry_point("retrieve")
    workflow.add_edge("retrieve", "relevance_check")
    workflow.add_conditional_edges(
        "relevance_check",
        lambda state: "generate" if state.get("is_relevant") else "no_results",
        {"generate": "generate", "no_results": "no_results"},
    )
    workflow.add_edge("generate", END)
    workflow.add_edge("no_results", END)

    return workflow.compile()
