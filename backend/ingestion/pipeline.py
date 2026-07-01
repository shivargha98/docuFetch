"""
Ingestion pipeline orchestrator for docuFetch.

Walks the watch folder, identifies supported files (.txt, .pdf at this stage),
deletes their existing ChromaDB chunks, reloads, rechunks, re-embeds, and
reinserts. Returns a result dict with doc_count and error.
"""
import os
from datetime import datetime, timezone

from backend.ingestion.loaders import load_file, load_image, UnsupportedFileTypeError
from backend.ingestion.chunkers import chunk_file, chunk_image
from backend.ingestion.scanner import scan_folder
from backend.embeddings.embedder import EmbeddingClient
from backend.embeddings.store import ChromaStore

SUPPORTED_EXTENSIONS = {".txt", ".pdf", ".md", ".jpg", ".jpeg", ".png"}

EXTENSION_TO_FILE_TYPE = {
    ".txt": "txt",
    ".pdf": "pdf",
    ".md": "markdown",
    ".jpg": "image",
    ".jpeg": "image",
    ".png": "image",
}


def run_ingestion(watch_folder: str, store: ChromaStore, embedder: EmbeddingClient, hash_store_path: str) -> dict:
    """
    Walk watch_folder, ingest only changed/new files into store using embedder.

    Uses hash-based change detection to avoid reprocessing unchanged files.
    Handles deletions by removing chunks from the store.

    Returns {"doc_count": int, "last_run_at": str (ISO8601), "last_error": None or str}.
    """
    last_error = None

    try:
        changes = scan_folder(watch_folder, hash_store_path)

        for filename in changes["deleted"]:
            store.delete_by_filename(filename)

        for path in changes["new"] + changes["modified"]:
            if path.suffix.lower() not in SUPPORTED_EXTENSIONS:
                continue
            filename = path.name
            file_type = EXTENSION_TO_FILE_TYPE.get(path.suffix.lower(), path.suffix.lower().lstrip("."))
            store.delete_by_filename(filename)

            if file_type == "image":
                image_bytes = load_image(path)
                chunks = chunk_image(path, filename)
                embedding = embedder.embed_image(image_bytes, suffix=path.suffix)
                store.insert_chunks(chunks, [embedding])
            else:
                text = load_file(path)
                chunks = chunk_file(text, filename, file_type)
                embeddings = embedder.embed_texts([c.page_content for c in chunks])
                store.insert_chunks(chunks, embeddings)

    except Exception as exc:
        last_error = str(exc)

    return {
        "doc_count": len(store.get_unique_filenames()),
        "last_run_at": datetime.now(timezone.utc).isoformat(),
        "last_error": last_error,
    }
