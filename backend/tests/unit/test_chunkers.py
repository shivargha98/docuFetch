"""Unit tests for the structure-aware chunking module."""
import pytest
from pathlib import Path
from PIL import Image
from langchain_core.documents import Document
from backend.ingestion.chunkers import chunk_text, chunk_md, chunk_image, chunk_file


def test_markdown_chunks_split_at_header_boundaries():
    md_text = "## Section One\n\nFirst section content here.\n\n## Section Two\n\nSecond section content here.\n\n## Section Three\n\nThird section content here.\n"
    chunks = chunk_md(md_text, "test.md")
    assert len(chunks) == 3
    for chunk in chunks:
        assert chunk.metadata["file_type"] == "markdown"


def test_text_chunks_do_not_exceed_512_characters():
    long_text = "word " * 500  # well over 512 chars
    chunks = chunk_text(long_text, "test.txt", "txt")
    assert all(len(c.page_content) <= 512 for c in chunks)


def test_consecutive_text_chunks_have_64_char_overlap():
    long_text = "abcdefghij" * 100  # 1000 chars, will produce multiple chunks
    chunks = chunk_text(long_text, "test.txt", "txt")
    assert len(chunks) >= 2
    # Last 64 chars of chunk N == first 64 chars of chunk N+1
    for i in range(len(chunks) - 1):
        assert chunks[i].page_content[-64:] == chunks[i + 1].page_content[:64]


def test_image_produces_exactly_one_chunk(sample_image_file):
    chunks = chunk_image(sample_image_file, "photo.jpg")
    assert len(chunks) == 1


def test_text_chunks_carry_filename_and_file_type_metadata(sample_txt_file):
    text = sample_txt_file.read_text()
    chunks = chunk_file(text, "notes.txt", "txt")
    for chunk in chunks:
        assert chunk.metadata["filename"] == "notes.txt"
        assert chunk.metadata["file_type"] == "txt"


def test_image_chunk_carries_file_path_and_no_content(sample_image_file):
    chunks = chunk_image(sample_image_file, "photo.jpg")
    assert len(chunks) == 1
    chunk = chunks[0]
    assert chunk.page_content == ""
    assert "file_path" in chunk.metadata
    assert "photo.jpg" in chunk.metadata["file_path"]
