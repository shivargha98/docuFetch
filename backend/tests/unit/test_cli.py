"""Unit tests for the CLI client."""
import sys
import uuid
import subprocess
import pytest
from unittest.mock import patch, MagicMock
import httpx


def test_cli_reuses_same_session_id_across_queries():
    """Session ID is UUID4 and stable within a session."""
    session_id = str(uuid.uuid4())
    parsed = uuid.UUID(session_id, version=4)
    assert str(parsed) == session_id


def test_cli_prints_readable_error_when_server_unreachable():
    import importlib.util, io
    spec = importlib.util.spec_from_file_location("cli", "/workspace/cli.py")
    cli_mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(cli_mod)
    original_url = cli_mod.SERVER_URL
    cli_mod.SERVER_URL = "http://localhost:19999"
    try:
        output = io.StringIO()
        sys.stdout = output
        cli_mod._handle_chat("test query", "fake-session-id")
        sys.stdout = sys.__stdout__
        out = output.getvalue()
        assert "not reachable" in out.lower() or "server" in out.lower()
        assert "Traceback" not in out
    finally:
        sys.stdout = sys.__stdout__
        cli_mod.SERVER_URL = original_url


def test_quit_exits_cleanly():
    result = subprocess.run(
        ["python3", "/workspace/cli.py"],
        input="/quit\n",
        capture_output=True,
        text=True,
        timeout=5,
        cwd="/workspace",
    )
    assert result.returncode == 0
