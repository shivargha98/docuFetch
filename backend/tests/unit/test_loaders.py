"""Unit tests for the per-file-type document loaders."""
import pytest
from pathlib import Path
from backend.ingestion.loaders import load_txt, load_pdf, load_md, load_image, load_file, UnsupportedFileTypeError


def test_pdf_loader_returns_non_empty_string(sample_pdf_file):
    text = load_pdf(sample_pdf_file)
    assert isinstance(text, str)
    assert len(text) > 0
    assert "test" in text.lower() or "pdf" in text.lower() or "docufetch" in text.lower()


def test_txt_loader_returns_raw_text(sample_txt_file):
    expected = sample_txt_file.read_text(encoding="utf-8")
    result = load_txt(sample_txt_file)
    assert result == expected


def test_markdown_loader_preserves_heading_markers(sample_md_file):
    text = load_md(sample_md_file)
    assert isinstance(text, str)
    assert len(text) > 0
    assert "#" in text


def test_image_loader_returns_bytes(sample_image_file):
    result = load_image(sample_image_file)
    assert isinstance(result, bytes)
    assert len(result) > 0


def test_unsupported_extension_raises_named_error(tmp_watch_folder):
    bad_file = tmp_watch_folder / "document.docx"
    bad_file.write_bytes(b"fake docx content")
    with pytest.raises(UnsupportedFileTypeError) as exc_info:
        load_file(bad_file)
    assert ".docx" in str(exc_info.value)
