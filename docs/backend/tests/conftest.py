"""
Shared pytest fixtures for the docuFetch backend test suite.

Provides: temporary watch folder, ChromaDB client (temp-dir-backed), sample
files for each supported type (TXT, PDF, Markdown, JPEG), and the FastAPI
TestClient with a clean app state.
"""

import pytest


@pytest.fixture
def tmp_watch_folder(tmp_path):
    """
    Creates an empty temporary directory that acts as the watched folder.
    Each test gets its own isolated folder; torn down automatically after the test.
    """
    folder = tmp_path / "watch"
    folder.mkdir()
    return folder


@pytest.fixture
def hash_store_path(tmp_path):
    """
    Returns a path for hash_store.json inside a temp directory.
    The file does not exist yet — tests that need a pre-populated store
    should write it themselves.
    """
    return tmp_path / "hash_store.json"


@pytest.fixture
def chromadb_collection(tmp_path):
    """
    Creates a real ChromaDB client backed by a temp directory and returns
    a fresh collection named 'test_collection'. Isolated per test.
    Fill in with: import chromadb; client = chromadb.PersistentClient(path=str(tmp_path / "chroma"))
    """
    raise NotImplementedError


@pytest.fixture
def sample_txt_file(tmp_watch_folder):
    """
    Writes a plain-text file with known content to the watch folder.
    Returns the Path to the file.
    Content should be long enough to produce multiple chunks (>512 chars).
    """
    raise NotImplementedError


@pytest.fixture
def sample_pdf_file(tmp_watch_folder):
    """
    Writes a minimal PDF file with known text content to the watch folder.
    Returns the Path to the file.
    Use a library like fpdf2 or reportlab to create a real (non-mocked) PDF.
    """
    raise NotImplementedError


@pytest.fixture
def sample_md_file(tmp_watch_folder):
    """
    Writes a Markdown file with three distinct ## sections to the watch folder.
    Returns the Path to the file.
    Each section should have unique content so chunk boundaries can be verified.
    """
    raise NotImplementedError


@pytest.fixture
def sample_image_file(tmp_watch_folder):
    """
    Writes a minimal valid JPEG image to the watch folder.
    Returns the Path to the file.
    Use Pillow to create a 10x10 pixel image to keep test fixtures tiny.
    """
    raise NotImplementedError


@pytest.fixture
def test_client():
    """
    Returns a FastAPI TestClient wrapping the docuFetch app.
    The app should be imported from backend.api.server.
    Each test gets a fresh app.state (sessions, ingestion_status, etc.).
    """
    raise NotImplementedError
