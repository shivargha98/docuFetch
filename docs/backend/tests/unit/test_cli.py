"""
Unit tests for the CLI client (cli.py).

Covers: session_id reuse across queries, human-readable error on server
unreachable, and clean /quit exit. All HTTP calls are mocked with httpx — no
running server required.
"""

import pytest
from unittest.mock import patch, MagicMock


def test_cli_reuses_same_session_id_across_queries():
    """
    Given a CLI session started with a mocked httpx client,
    when two queries are submitted sequentially,
    both HTTP requests to /chat should contain the same session_id value,
    and the session_id should be a valid UUID4 format.

    Source: Feature: Interactive CLI Client — criterion 5 | Issue 9 — criterion 2
    """
    raise NotImplementedError


def test_cli_prints_readable_error_when_server_unreachable(capsys):
    """
    Given that httpx raises a ConnectError for all requests,
    when the user submits a query,
    the CLI should print a message containing the server URL and a readable
    description of the problem — no raw exception traceback — and should not
    crash.

    Source: Feature: Interactive CLI Client — criterion 6 | Issue 9 — criterion 6
    """
    raise NotImplementedError


def test_quit_exits_cleanly():
    """
    Given a running CLI prompt loop,
    when the user types /quit,
    the process should exit with code 0 and no error message should be printed.

    Source: Feature: Interactive CLI Client — criterion 4 | Issue 9 — criterion 5
    """
    raise NotImplementedError
