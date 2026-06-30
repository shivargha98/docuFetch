"""
Unit tests for the per-file-type document loaders.

Covers: PDF (pdfplumber), TXT (file read), Markdown (file read), image
(Pillow bytes), and rejection of unsupported file extensions.

All tests use real files via tmp_path fixtures — no mocking required.
"""

import pytest


def test_pdf_loader_returns_non_empty_string(sample_pdf_file):
    """
    Given a valid PDF file with known text content,
    when the PDF loader is called,
    the return value should be a non-empty string containing text from the PDF.

    Source: Feature: Per-File-Type Document Loaders — criterion 1
    """
    raise NotImplementedError


def test_txt_loader_returns_raw_text(sample_txt_file):
    """
    Given a TXT file with known content,
    when the TXT loader is called,
    the returned string should exactly match the file's contents.

    Source: Feature: Per-File-Type Document Loaders — criterion 3
    """
    raise NotImplementedError


def test_markdown_loader_preserves_heading_markers(sample_md_file):
    """
    Given a Markdown file containing #, ##, and ### headers,
    when the Markdown loader is called,
    the returned string should contain the '#' heading markers intact.

    Source: Feature: Per-File-Type Document Loaders — criterion 2
    """
    raise NotImplementedError


def test_image_loader_returns_bytes(sample_image_file):
    """
    Given a valid JPEG file,
    when the image loader is called,
    the return value should be a non-empty bytes object.
    The same assertion should hold for JPG and PNG files.

    Source: Feature: Per-File-Type Document Loaders — criterion 4
    """
    raise NotImplementedError


def test_unsupported_extension_raises_named_error(tmp_watch_folder):
    """
    Given a file with an unsupported extension (e.g. .docx),
    when any loader is invoked for this file,
    a specific named exception (not a generic Exception) should be raised,
    and the exception message should identify the unsupported extension.

    Source: Feature: Per-File-Type Document Loaders — criterion 5
    """
    raise NotImplementedError
