"""
API / contract tests for all FastAPI endpoints.

Covers: GET /health, POST /ingest, GET /ingest/status, and POST /chat.
Uses FastAPI's TestClient — no real server process needed.

Tests assert on HTTP status codes, response shapes (keys and types), and
observable session behaviour. They do not assert on internal implementation
details such as which internal functions are called.
"""

import pytest


# ---------------------------------------------------------------------------
# GET /health
# ---------------------------------------------------------------------------

def test_health_returns_200_with_expected_schema(test_client):
    """
    Given the FastAPI app is running,
    when GET /health is called,
    HTTP status should be 200, the body should contain 'status': 'ok', and
    the key 'initial_ingestion_complete' should be present with a boolean value.

    Source: Feature: GET /health Endpoint — criterion 1
    """
    raise NotImplementedError


def test_health_initial_ingestion_complete_false_before_startup(test_client):
    """
    Given the FastAPI app started with the scheduler not yet completed,
    when GET /health is called immediately,
    'initial_ingestion_complete' should be false.

    Source: Feature: GET /health Endpoint — criterion 2
    """
    raise NotImplementedError


def test_health_initial_ingestion_complete_true_after_startup(test_client):
    """
    Given the FastAPI app started and the startup ingestion run has completed,
    when GET /health is called,
    'initial_ingestion_complete' should be true.

    Source: Feature: GET /health Endpoint — criterion 3
    """
    raise NotImplementedError


# ---------------------------------------------------------------------------
# POST /ingest
# ---------------------------------------------------------------------------

def test_ingest_returns_200_with_confirmation(test_client):
    """
    Given the FastAPI app is running,
    when POST /ingest is called,
    HTTP status should be 200 and the response body should contain a
    non-empty confirmation message string.

    Source: Feature: POST /ingest Endpoint — criterion 1 | Issue 2 — criterion 1
    """
    raise NotImplementedError


def test_ingest_makes_new_files_queryable(test_client, tmp_watch_folder):
    """
    Given a new TXT file placed in WATCH_FOLDER after server startup,
    when POST /ingest is called and then POST /chat is called with a query
    matching the new file's content,
    the /chat response 'sources' list should include the new file's filename.

    Source: Feature: POST /ingest Endpoint — criterion 3 | Issue 2 — criterion 4
    """
    raise NotImplementedError


# ---------------------------------------------------------------------------
# GET /ingest/status
# ---------------------------------------------------------------------------

def test_ingest_status_returns_expected_schema(test_client):
    """
    Given the FastAPI app is running,
    when GET /ingest/status is called,
    HTTP status should be 200 and the body should contain doc_count (int),
    last_run_at (string or null), and last_error (string or null).

    Source: Feature: GET /ingest/status Endpoint — criterion 1
    """
    raise NotImplementedError


def test_ingest_status_doc_count_reflects_ingested_documents(test_client, tmp_watch_folder):
    """
    Given two documents have been ingested,
    when GET /ingest/status is called,
    doc_count should equal 2.

    Source: Feature: GET /ingest/status Endpoint — criterion 2
    """
    raise NotImplementedError


def test_ingest_status_last_run_at_null_before_any_run(test_client):
    """
    Given the FastAPI app started with no ingestion run triggered,
    when GET /ingest/status is called,
    last_run_at should be null.

    Source: Feature: GET /ingest/status Endpoint — criterion 3
    """
    raise NotImplementedError


def test_ingest_status_last_error_null_after_successful_run(test_client, tmp_watch_folder):
    """
    Given an ingestion run completed without errors,
    when GET /ingest/status is called,
    last_error should be null.

    Source: Feature: GET /ingest/status Endpoint — criterion 4
    """
    raise NotImplementedError


# ---------------------------------------------------------------------------
# POST /chat
# ---------------------------------------------------------------------------

def test_chat_returns_expected_response_schema(test_client):
    """
    Given at least one document is ingested and a valid UUID session_id is prepared,
    when POST /chat is called with {"query": "...", "session_id": "<uuid>"},
    HTTP status should be 200 and the body should contain 'answer' (non-empty
    string), 'sources' (list), and 'session_id' (the same UUID sent).

    Source: Feature: POST /chat Endpoint — criterion 1 | Issue 8 — criterion 1
    """
    raise NotImplementedError


def test_chat_sources_contains_filenames_not_paths(test_client, tmp_watch_folder):
    """
    Given a document named 'policy.pdf' is ingested and its content matches
    the query,
    when POST /chat is called,
    'sources' should contain 'policy.pdf' (filename only, not a full path)
    and no entry in 'sources' should contain a directory separator.

    Source: Feature: POST /chat Endpoint — criterion 1 | PRD: Source citation format
    """
    raise NotImplementedError


def test_chat_same_session_id_shares_conversation_context(test_client, tmp_watch_folder):
    """
    Given a document is ingested and a UUID session_id is chosen,
    when a first POST /chat asks about the document and a second POST /chat
    with the same session_id asks a follow-up using a pronoun,
    the second response should be coherent given the first answer.

    Source: Feature: POST /chat Endpoint — criterion 2 | Issue 8 — criterion 2
    """
    raise NotImplementedError


def test_chat_different_session_ids_have_independent_contexts(test_client):
    """
    Given two distinct UUID session_ids,
    when Session A asks a question and Session B asks an unrelated question,
    Session B's response should contain no reference to Session A's conversation
    and app.state.sessions should contain two separate history entries.

    Source: Feature: POST /chat Endpoint — criterion 3 | Issue 8 — criterion 3
    """
    raise NotImplementedError


def test_chat_returns_no_results_message_for_irrelevant_query(test_client, tmp_watch_folder):
    """
    Given a document about topic A is ingested,
    when POST /chat is called with a query about an unrelated topic B,
    'answer' should equal "I couldn't find relevant information in your documents."
    and 'sources' should be an empty list.

    Source: PRD User Story 10 | Feature: No-Results Node
    """
    raise NotImplementedError
