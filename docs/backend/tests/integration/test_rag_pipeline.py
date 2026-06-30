"""
Integration tests for the full LangGraph RAG pipeline.

Covers: end-to-end query returning an answer with source citation, no-results
path for irrelevant queries, multi-turn conversation context, and history
trimming at 20 messages.

Requires ANTHROPIC_API_KEY (for Claude Haiku) and OPENROUTER_API_KEY (for
embeddings). Uses real ChromaDB (temp dir) and a compiled LangGraph graph.
"""

import pytest


def test_relevant_query_returns_answer_with_source_citation(chromadb_collection, sample_txt_file):
    """
    Given a TXT document with specific content ingested, and the LangGraph
    graph compiled,
    when the graph is invoked with a query that directly asks about that content,
    the returned answer should be between 2 and 4 sentences, sources should
    contain the filename, and the answer text should include a [source: filename]
    citation.

    Source: Feature: LangGraph Graph Assembly — criterion 1 | PRD User Story 8, 9
    """
    raise NotImplementedError


def test_irrelevant_query_returns_no_results_message(chromadb_collection, sample_txt_file):
    """
    Given a document about one topic ingested and the LangGraph graph compiled,
    when the graph is invoked with a query about a completely unrelated topic,
    the returned answer should equal exactly
    "I couldn't find relevant information in your documents."
    and sources should be an empty list.

    Source: Feature: LangGraph Graph Assembly — criterion 2 | PRD User Story 10
    """
    raise NotImplementedError


def test_second_turn_is_contextually_aware_of_first(chromadb_collection, sample_txt_file):
    """
    Given an ingested document and a compiled graph with one prior exchange
    in the session state,
    when the graph is invoked with a follow-up question that only makes sense
    given the prior turn,
    the answer should reflect awareness of the prior question and messages
    should contain entries from both turns.

    Source: Feature: LangGraph Graph Assembly — criterion 3 | PRD User Story 13
    """
    raise NotImplementedError


def test_history_trimmed_when_messages_exceed_20(chromadb_collection):
    """
    Given a DocuFetchState with a messages list of 22 entries,
    when the graph is invoked (triggering the history trim step),
    the LLM should be called with at most 20 messages and the oldest messages
    (entries 1 and 2) should be absent from the trimmed list.

    Source: Feature: LangGraph Graph Assembly — criterion 4 | PRD User Story 13
    """
    raise NotImplementedError
