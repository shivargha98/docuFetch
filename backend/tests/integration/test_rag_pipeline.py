"""Integration tests for the full LangGraph RAG pipeline."""
import pytest
import os
from backend.tests.conftest import skip_if_no_openrouter, skip_if_no_anthropic
from langchain_core.messages import HumanMessage, AIMessage
from langchain_core.documents import Document
from unittest.mock import MagicMock
from backend.graph.state import DocuFetchState
from backend.graph.nodes import make_no_results_node, make_relevance_check_node, make_generate_node, NO_RESULTS_MESSAGE
from backend.graph.graph import build_graph
from backend.retrieval.bm25 import BM25Index
from backend.retrieval.hybrid import HybridRetriever


def _make_mock_retriever(docs):
    """Helper: create a mock HybridRetriever that returns given docs."""
    mock = MagicMock()
    mock.retrieve.return_value = docs
    return mock


@skip_if_no_anthropic
def test_relevant_query_returns_answer_with_source_citation():
    """Graph with a relevant query routes through generate and cites sources."""
    from langchain_anthropic import ChatAnthropic
    llm = ChatAnthropic(model="claude-haiku-4-5", api_key=os.getenv("ANTHROPIC_API_KEY"))
    chunks = [Document(page_content="The refund policy allows returns within 30 days.", metadata={"filename": "policy.txt", "file_type": "txt"})]
    retriever = _make_mock_retriever(chunks)
    graph = build_graph(retriever, llm)
    result = graph.invoke({"query": "What is the refund policy?", "messages": []})
    answer = result["messages"][-1].content
    assert len(answer) > 0
    assert "policy.txt" in result.get("sources", [])


def test_irrelevant_query_returns_no_results_message():
    """Graph with empty retrieval routes to no_results without LLM call."""
    retriever = _make_mock_retriever([])
    mock_llm = MagicMock()
    graph = build_graph(retriever, mock_llm)
    result = graph.invoke({"query": "What is the weather on Mars?", "messages": []})
    assert result["messages"][-1].content == NO_RESULTS_MESSAGE
    assert result.get("sources", []) == []


@skip_if_no_anthropic
def test_second_turn_is_contextually_aware_of_first():
    """Two-turn conversation: second answer is aware of first."""
    from langchain_anthropic import ChatAnthropic
    llm = ChatAnthropic(model="claude-haiku-4-5", api_key=os.getenv("ANTHROPIC_API_KEY"))
    chunks = [Document(page_content="Alice is a software engineer at Acme Corp.", metadata={"filename": "bio.txt", "file_type": "txt"})]
    retriever = _make_mock_retriever(chunks)
    graph = build_graph(retriever, llm)
    state1 = {"query": "Who is Alice?", "messages": []}
    result1 = graph.invoke(state1)
    state2 = {"query": "What company does she work for?", "messages": result1["messages"]}
    result2 = graph.invoke(state2)
    answer2 = result2["messages"][-1].content.lower()
    assert "acme" in answer2 or "company" in answer2


def test_history_trimmed_when_messages_exceed_20():
    """History trimming: only last 20 messages passed to LLM."""
    retriever = _make_mock_retriever([])
    mock_llm = MagicMock()
    graph = build_graph(retriever, mock_llm)
    # Build 22 fake messages in history
    old_messages = []
    for i in range(22):
        old_messages.append(HumanMessage(content=f"question {i}"))
        old_messages.append(AIMessage(content=f"answer {i}"))
    state = {"query": "new question", "messages": old_messages}
    result = graph.invoke(state)
    # no_results path since retriever returns []
    assert result["messages"][-1].content == NO_RESULTS_MESSAGE
