"""Unit tests for the file scanner (change detection) module."""
import json
import pytest
from pathlib import Path
from backend.ingestion.scanner import scan_folder


def test_new_file_classified_as_new(tmp_watch_folder, hash_store_path):
    txt = tmp_watch_folder / "test.txt"
    txt.write_text("hello world")
    result = scan_folder(str(tmp_watch_folder), str(hash_store_path))
    assert txt in result["new"]
    assert len(result["modified"]) == 0
    assert len(result["deleted"]) == 0


def test_modified_file_classified_as_modified(tmp_watch_folder, hash_store_path):
    txt = tmp_watch_folder / "test.txt"
    txt.write_text("original content")
    scan_folder(str(tmp_watch_folder), str(hash_store_path))
    txt.write_text("modified content")
    result = scan_folder(str(tmp_watch_folder), str(hash_store_path))
    assert txt in result["modified"]
    assert len(result["new"]) == 0
    assert len(result["deleted"]) == 0


def test_deleted_file_classified_as_deleted(tmp_watch_folder, hash_store_path):
    txt = tmp_watch_folder / "test.txt"
    txt.write_text("hello")
    scan_folder(str(tmp_watch_folder), str(hash_store_path))
    txt.unlink()
    result = scan_folder(str(tmp_watch_folder), str(hash_store_path))
    assert "test.txt" in result["deleted"]
    assert len(result["new"]) == 0
    assert len(result["modified"]) == 0


def test_unchanged_file_produces_no_action(tmp_watch_folder, hash_store_path):
    txt = tmp_watch_folder / "test.txt"
    txt.write_text("same content")
    scan_folder(str(tmp_watch_folder), str(hash_store_path))
    result = scan_folder(str(tmp_watch_folder), str(hash_store_path))
    assert len(result["new"]) == 0
    assert len(result["modified"]) == 0
    assert len(result["deleted"]) == 0


def test_hash_store_updated_after_scan(tmp_watch_folder, hash_store_path):
    new_file = tmp_watch_folder / "new.txt"
    new_file.write_text("new content")
    # Pre-populate store with a deleted file
    initial_store = {"deleted.txt": "oldhash123"}
    hash_store_path.write_text(json.dumps(initial_store))
    scan_folder(str(tmp_watch_folder), str(hash_store_path))
    updated = json.loads(hash_store_path.read_text())
    assert "new.txt" in updated
    assert "deleted.txt" not in updated
