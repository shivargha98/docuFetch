"""
Shared pytest fixtures for the docuFetch backend test suite.

Provides: temporary watch folder, ChromaDB store (temp-dir-backed), sample
files for each supported type (TXT, PDF, Markdown, JPEG), and the FastAPI
TestClient with a clean app state.
"""
import json
import os
import pytest
from pathlib import Path
from fastapi.testclient import TestClient
from PIL import Image
import fpdf
from dotenv import load_dotenv

# Load .env before any fixture checks os.getenv() for API keys.
# Without this, real keys from .env are not available when the fixture decides
# whether to use dummy values, causing chat/embedding tests to fail with 401.
load_dotenv()


@pytest.fixture
def tmp_watch_folder(tmp_path):
    """Creates an empty temporary directory that acts as the watched folder."""
    folder = tmp_path / "watch"
    folder.mkdir()
    return folder


@pytest.fixture
def hash_store_path(tmp_path):
    """Returns a path for hash_store.json inside a temp directory. File does not exist yet."""
    return tmp_path / "hash_store.json"


@pytest.fixture
def chromadb_store(tmp_path):
    """
    Creates a real ChromaStore backed by a temp directory.
    Returns a ChromaStore instance. Isolated per test.
    """
    from backend.embeddings.store import ChromaStore
    return ChromaStore(path=str(tmp_path / "chroma"))


@pytest.fixture
def sample_txt_file(tmp_watch_folder):
    """
    Writes a plain-text file with known content to the watch folder.
    Content is long enough to produce multiple chunks (>512 chars).
    Returns the Path to the file.
    """
    content = (
        "The quick brown fox jumps over the lazy dog. " * 20 +
        "This document discusses the policy for refund requests. " * 10 +
        "All refund requests must be submitted within 30 days of purchase. " * 5
    )
    path = tmp_watch_folder / "notes.txt"
    path.write_text(content, encoding="utf-8")
    return path


@pytest.fixture
def sample_pdf_file(tmp_watch_folder):
    """
    Writes a minimal PDF file with known text content to the watch folder.
    Uses fpdf2 to create a real (non-mocked) PDF. Returns the Path to the file.
    """
    pdf = fpdf.FPDF()
    pdf.add_page()
    pdf.set_font("Helvetica", size=12)
    pdf.cell(200, 10, txt="This is a test PDF document for docuFetch.", ln=True)
    pdf.cell(200, 10, txt="It contains sample text for testing PDF ingestion.", ln=True)
    path = tmp_watch_folder / "test.pdf"
    pdf.output(str(path))
    return path


@pytest.fixture
def sample_md_file(tmp_watch_folder):
    """
    Writes a Markdown file with three distinct ## sections to the watch folder.
    Returns the Path to the file.
    """
    content = (
        "# Main Title\n\n"
        "## Section One\n\nContent about section one. This is the first section of the document.\n\n"
        "## Section Two\n\nContent about section two. This is the second section with different information.\n\n"
        "## Section Three\n\nContent about section three. This is the third and final section.\n"
    )
    path = tmp_watch_folder / "notes.md"
    path.write_text(content, encoding="utf-8")
    return path


@pytest.fixture
def sample_image_file(tmp_watch_folder):
    """
    Writes a minimal valid JPEG image (10x10 pixels) to the watch folder.
    Returns the Path to the file.
    """
    path = tmp_watch_folder / "photo.jpg"
    img = Image.new("RGB", (10, 10), color=(128, 64, 32))
    img.save(str(path), "JPEG")
    return path


@pytest.fixture
def test_client(tmp_path, monkeypatch):
    """
    Returns a FastAPI TestClient wrapping the docuFetch app.
    Sets required env vars to safe test values.
    Must be used as context manager to trigger lifespan.
    """
    watch_folder = tmp_path / "watch"
    watch_folder.mkdir()
    chroma_path = tmp_path / "chroma"
    hash_store = tmp_path / "hash_store.json"

    monkeypatch.setenv("WATCH_FOLDER", str(watch_folder))
    monkeypatch.setenv("CHROMA_DB_PATH", str(chroma_path))
    monkeypatch.setenv("HASH_STORE_PATH", str(hash_store))
    # Use actual keys from environment if available; fall back to dummy values
    # (tests that need real API calls will skip if keys are dummies)
    if not os.getenv("OPENROUTER_API_KEY"):
        monkeypatch.setenv("OPENROUTER_API_KEY", "dummy-key-for-tests")
    if not os.getenv("ANTHROPIC_API_KEY"):
        monkeypatch.setenv("ANTHROPIC_API_KEY", "dummy-key-for-tests")

    from backend.api.server import app
    return TestClient(app)


import os as _os
skip_if_no_openrouter = pytest.mark.skipif(
    not _os.getenv("OPENROUTER_API_KEY") or _os.getenv("OPENROUTER_API_KEY") == "dummy-key-for-tests",
    reason="OPENROUTER_API_KEY not set"
)
skip_if_no_anthropic = pytest.mark.skipif(
    not _os.getenv("ANTHROPIC_API_KEY") or _os.getenv("ANTHROPIC_API_KEY") == "dummy-key-for-tests",
    reason="ANTHROPIC_API_KEY not set"
)
