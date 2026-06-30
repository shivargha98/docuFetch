"""
Unit tests for individual LangGraph nodes and the DocuFetchState schema.

Covers: state schema instantiation, no_results node return values, and
relevance_check node short-circuit behaviour when retrieved_chunks is empty.

LLM clients are mocked in this module — no Anthropic API calls made.
"""

import pytest
from unittest.mock import MagicMock


def test_docufetch_state_partial_instantiation():
    """
    Given no precondition,
    when DocuFetchState is instantiated with only the 'query' field provided,
    the instantiation should succeed and unspecified fields should be absent
    or defaulted without raising a KeyError.

    Source: Feature: LangGraph State Schema — criterion 2
    """
    raise NotImplementedError


def test_no_results_node_returns_exact_message():
    """
    Given a DocuFetchState with is_relevant=False and retrieved_chunks=[],
    when the no_results node is invoked,
    the returned state's answer (or last AIMessage) should equal exactly:
    "I couldn't find relevant information in your documents."

    Source: Feature: No-Results Node — criterion 1
    """
    raise NotImplementedError


def test_no_results_node_sets_sources_to_empty_list():
    """
    Given a DocuFetchState with is_relevant=False,
    when the no_results node is invoked,
    state['sources'] should be an empty list.

    Source: Feature: No-Results Node — criterion 2
    """
    raise NotImplementedError


def test_relevance_check_skips_llm_when_chunks_empty():
    """
    Given a DocuFetchState with retrieved_chunks=[],
    when the relevance_check node is invoked with a mocked LLM client,
    is_relevant should be set to False and the mocked LLM client should
    never be called.

    Source: Feature: Relevance Check Node — criterion 3
    """
    raise NotImplementedError
