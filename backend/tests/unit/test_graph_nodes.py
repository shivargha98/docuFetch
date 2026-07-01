"""Unit tests for LangGraph nodes and DocuFetchState schema."""
import pytest
from unittest.mock import MagicMock
from langchain_core.messages import AIMessage
from backend.graph.state import DocuFetchState
from backend.graph.nodes import make_no_results_node, make_relevance_check_node, NO_RESULTS_MESSAGE


def test_docufetch_state_partial_instantiation():
    state = DocuFetchState(query="test query")
    assert state["query"] == "test query"
    # Should not raise KeyError
    _ = state.get("messages", [])
    _ = state.get("retrieved_chunks", [])


def test_no_results_node_returns_exact_message():
    no_results = make_no_results_node()
    result = no_results({"query": "anything", "messages": [], "is_relevant": False, "retrieved_chunks": []})
    last_msg = result["messages"][-1]
    assert isinstance(last_msg, AIMessage)
    assert last_msg.content == NO_RESULTS_MESSAGE


def test_no_results_node_sets_sources_to_empty_list():
    no_results = make_no_results_node()
    result = no_results({"query": "anything", "messages": [], "is_relevant": False})
    assert result["sources"] == []


def test_relevance_check_skips_llm_when_chunks_empty():
    mock_llm = MagicMock()
    relevance_check = make_relevance_check_node(mock_llm)
    result = relevance_check({"query": "test", "retrieved_chunks": []})
    assert result["is_relevant"] == False
    mock_llm.invoke.assert_not_called()
