"""
Integration tests for BM25 index construction and hybrid retrieval with RRF fusion.

Covers: BM25 exclusion of image chunks, BM25 index rebuild after ingestion,
hybrid retrieval returning at most 3 fused chunks, and RRF ranking advantage
for documents strong in both retrievers.

Uses real ChromaDB (temp dir) and requires OPENROUTER_API_KEY for embeddings.
"""

import pytest


def test_bm25_index_excludes_image_chunks(tmp_watch_folder, chromadb_collection, sample_txt_file, sample_image_file):
    """
    Given a ChromaDB collection with both text and image chunks ingested,
    when the BM25 index is built from ChromaDB text chunks,
    a BM25 query for any term should never return an image chunk and the
    BM25 index document count should equal the number of text chunks only.

    Source: Feature: BM25 Index — criterion 3 |
            Feature: Hybrid Retriever with RRF Fusion — criterion 4
    """
    raise NotImplementedError


def test_bm25_index_rebuild_includes_new_documents(tmp_watch_folder, chromadb_collection):
    """
    Given a BM25 index built from an initial set of documents,
    when a new document is ingested and the index is rebuilt,
    a BM25 keyword query matching the new document's content should return
    that document.

    Source: Feature: BM25 Index — criterion 4
    """
    raise NotImplementedError


def test_hybrid_retrieval_returns_at_most_three_chunks(chromadb_collection):
    """
    Given a ChromaDB collection with 10+ ingested text chunks,
    when the hybrid retriever is called with a query,
    at most 3 chunks should be returned and all returned chunks should have
    a filename in their metadata.

    Source: Feature: Hybrid Retriever with RRF Fusion — criterion 2
    """
    raise NotImplementedError


def test_dual_relevant_document_ranks_first_after_rrf(tmp_watch_folder, chromadb_collection):
    """
    Given two documents ingested: one whose content matches both the query
    keyword and its semantic meaning, and one that only semantically relates,
    when the hybrid retriever is called with that keyword query,
    the document with both keyword and semantic relevance should be ranked
    first in the fused output.

    Source: Feature: Hybrid Retriever with RRF Fusion — criterion 3
    """
    raise NotImplementedError
