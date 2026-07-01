"""
Per-file-type document loaders for docuFetch.

Each loader reads a single file and returns its content in a form the
chunkers can consume. Unsupported extensions raise UnsupportedFileTypeError.
Image loading (JPEG, JPG, PNG) is added in Issue 4.
"""
from pathlib import Path

import pdfplumber
from PIL import Image


class UnsupportedFileTypeError(Exception):
    """Raised when a file with an unsupported extension is passed to a loader."""
    pass


def load_txt(path: Path) -> str:
    """Load a plain-text file and return its content as a string."""
    return path.read_text(encoding="utf-8")


def load_pdf(path: Path) -> str:
    """Load a PDF file using pdfplumber and return all extracted text as a single string."""
    with pdfplumber.open(path) as pdf:
        pages = [page.extract_text() or "" for page in pdf.pages]
    return "\n".join(pages)


def load_md(path: Path) -> str:
    """Load a Markdown file and return its raw text content with heading markers preserved."""
    return path.read_text(encoding="utf-8")


def load_image(path: Path) -> bytes:
    """
    Open and validate an image file using Pillow, then return its raw bytes.
    Raises UnsupportedFileTypeError if Pillow cannot open the file.
    """
    try:
        with Image.open(path) as img:
            img.verify()  # validates the image without fully loading it
    except Exception as exc:
        raise UnsupportedFileTypeError(f"Cannot load image at {path}: {exc}") from exc
    return path.read_bytes()


def load_file(path: Path) -> str | bytes:
    """
    Dispatch to the appropriate loader based on file suffix.

    Supports .txt, .pdf, .md, .jpg, .jpeg, and .png.
    Returns str for text-based files and bytes for images.
    Raises UnsupportedFileTypeError for all other extensions.
    """
    suffix = path.suffix.lower()
    if suffix == ".txt":
        return load_txt(path)
    elif suffix == ".pdf":
        return load_pdf(path)
    elif suffix == ".md":
        return load_md(path)
    elif suffix in (".jpg", ".jpeg", ".png"):
        return load_image(path)
    else:
        raise UnsupportedFileTypeError(f"Unsupported file type: {path.suffix}")
