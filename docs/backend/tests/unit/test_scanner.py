"""
Unit tests for the file scanner (change detection) module.

Covers: SHA256-based classification of files as new, modified, deleted, or
unchanged, and persistence of hash_store.json after a scan run.

All tests use real file I/O via tmp_path — no external services required.
"""

import pytest


def test_new_file_classified_as_new(tmp_watch_folder, hash_store_path):
    """
    Given an empty hash_store.json and one TXT file in the watch folder,
    when the scanner runs,
    the file should appear in the 'new' list and not in 'modified' or 'deleted'.

    Source: Feature: File Change Detection — criterion 1 | Issue 5 — criterion 1
    """
    raise NotImplementedError


def test_modified_file_classified_as_modified(tmp_watch_folder, hash_store_path):
    """
    Given a hash_store.json containing a file's old hash, and that file now
    has different content (and therefore a different SHA256) on disk,
    when the scanner runs,
    the file should appear in the 'modified' list only.

    Source: Feature: File Change Detection — criterion 2 | Issue 5 — criterion 2
    """
    raise NotImplementedError


def test_deleted_file_classified_as_deleted(tmp_watch_folder, hash_store_path):
    """
    Given a hash_store.json with a file entry, but that file no longer exists
    on disk,
    when the scanner runs,
    the file should appear in the 'deleted' list only.

    Source: Feature: File Change Detection — criterion 3 | Issue 5 — criterion 3
    """
    raise NotImplementedError


def test_unchanged_file_produces_no_action(tmp_watch_folder, hash_store_path):
    """
    Given a hash_store.json containing a file's current hash, and the file on
    disk has not changed,
    when the scanner runs,
    the file should not appear in new, modified, or deleted lists.

    Source: Feature: File Change Detection — criterion 5
    """
    raise NotImplementedError


def test_hash_store_updated_after_scan(tmp_watch_folder, hash_store_path):
    """
    Given a folder with one new file and one file whose entry exists in the
    store but was deleted from disk,
    when the scanner runs and the hash store is persisted,
    the new file's hash should appear in hash_store.json and the deleted
    file's entry should be absent.

    Source: Feature: File Change Detection — criterion 4
    """
    raise NotImplementedError
