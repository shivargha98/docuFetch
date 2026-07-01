"""
SHA256-based file change detection for docuFetch.

Scans the watch folder, computes SHA256 hashes for all files, and compares
against a persisted hash_store.json to classify files as new, modified, or
deleted. Updates hash_store.json after each scan.
"""
import hashlib
import json
from pathlib import Path


def _compute_sha256(path: Path) -> str:
    """Compute the SHA256 hash of a file's contents."""
    data = path.read_bytes()
    return hashlib.sha256(data).hexdigest()


def scan_folder(watch_folder: str, hash_store_path: str) -> dict:
    """
    Walk watch_folder and classify files relative to hash_store.json.

    Returns:
        {
            "new": [Path, ...],       # files not in hash store
            "modified": [Path, ...],  # files whose hash changed
            "deleted": [str, ...],    # filenames in store but absent from disk
        }

    Side effect: writes updated hashes to hash_store_path.
    """
    store_file = Path(hash_store_path)
    if store_file.exists():
        old_store = json.loads(store_file.read_text())
    else:
        old_store = {}

    new_files = []
    modified_files = []
    new_store = {}
    store_file_resolved = store_file.resolve()

    for path in Path(watch_folder).rglob("*"):
        if not path.is_file():
            continue
        if path.resolve() == store_file_resolved:
            continue
        filename = path.name
        current_hash = _compute_sha256(path)
        new_store[filename] = current_hash

        if filename not in old_store:
            new_files.append(path)
        elif old_store[filename] != current_hash:
            modified_files.append(path)

    deleted = [filename for filename in old_store if filename not in new_store]

    store_file.write_text(json.dumps(new_store, indent=2))

    return {
        "new": new_files,
        "modified": modified_files,
        "deleted": deleted,
    }
