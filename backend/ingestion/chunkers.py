"""
Structure-aware document chunkers for docuFetch.

Each chunker takes loaded content and returns a list of LangChain Document
objects with page_content and metadata fields. Image chunking is added in
Issue 4.
"""
from pathlib import Path

from langchain_core.documents import Document
from langchain_text_splitters import MarkdownHeaderTextSplitter, RecursiveCharacterTextSplitter


def chunk_text(text: str, filename: str, file_type: str) -> list[Document]:
    """
    Split text into chunks of at most 512 chars with 64-char overlap.
    Each chunk carries filename and file_type in its metadata.
    Used for both TXT and PDF files.
    """
    splitter = RecursiveCharacterTextSplitter(chunk_size=512, chunk_overlap=64)
    raw_chunks = splitter.split_text(text)
    return [
        Document(page_content=chunk, metadata={"filename": filename, "file_type": file_type})
        for chunk in raw_chunks
    ]


def chunk_md(text: str, filename: str) -> list[Document]:
    """
    Split Markdown text at #, ##, and ### header boundaries.
    Each chunk corresponds to exactly one section. Every chunk carries
    filename and file_type='markdown' in its metadata.
    """
    headers_to_split_on = [("#", "h1"), ("##", "h2"), ("###", "h3")]
    splitter = MarkdownHeaderTextSplitter(headers_to_split_on=headers_to_split_on)
    docs = splitter.split_text(text)
    for doc in docs:
        doc.metadata["filename"] = filename
        doc.metadata["file_type"] = "markdown"
    return docs


def chunk_image(path: Path, filename: str) -> list[Document]:
    """
    Return a single Document chunk for an image file.
    Content is empty; metadata contains filename, file_type, and file_path.
    """
    return [Document(
        page_content="",
        metadata={
            "filename": filename,
            "file_type": "image",
            "file_path": str(path.resolve()),
        }
    )]


def chunk_file(content: str | bytes, filename: str, file_type: str, path: Path = None) -> list[Document]:
    """
    Dispatch to the appropriate chunker based on file_type.

    Supports 'txt', 'pdf', 'markdown', and 'image'.
    For images, path must be provided to store file_path in metadata.
    Raises ValueError for unknown types.
    """
    if file_type in ("txt", "pdf"):
        return chunk_text(content, filename, file_type)
    elif file_type == "markdown":
        return chunk_md(content, filename)
    elif file_type == "image":
        return chunk_image(path, filename)
    raise ValueError(f"No chunker for file type: {file_type}")
