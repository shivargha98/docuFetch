---
name: project-docufetch-backend
description: Institutional patterns and key decisions from the docuFetch backend PM loop — covers PRD structure, feature groupings, issue slicing, and test strategy.
metadata:
  type: project
---

docuFetch backend PM loop completed 2026-06-30. All artifacts generated from scratch using grill_doc_roadmap.md as the sole source of truth.

**Why:** grill_doc_roadmap.md was the only existing artifact; PRD, features, issues, and tests were all synthesized from the 15 architectural decisions documented in that grill session.

**How to apply:** In future loops, grill_doc_roadmap.md is the canonical planning source. Always read it before generating any artifact. Its decision log is authoritative — never override it.

## Module groupings used (match these in future work)
- ingestion/ — scanner, loaders, chunkers
- embeddings/ — OpenRouter embedding client, ChromaDB store
- retrieval/ — BM25 index, hybrid EnsembleRetriever + RRF
- graph/ — DocuFetchState, LangGraph nodes, graph assembly
- api/ — FastAPI server, lifespan, scheduler, routes
- cli.py — standalone httpx client

## Issue slicing pattern
9 issues in dependency order: scaffold (1) → TXT/PDF ingest + endpoints (2) → Markdown (3), Image (4), Scheduler (5), Hybrid retrieval (6) → LangGraph pipeline (7) → POST /chat (8) → CLI (9).
Key decision: LangGraph pipeline is one issue (7), not per-node — nodes share state and testing them in isolation is not meaningful at this scale.

## Test strategy
- 54 tests: 21 unit, 19 integration, 14 API
- No mocking of ChromaDB or LangGraph in integration tests — real instances only
- CLI httpx calls ARE mocked in unit tests (connection error, session_id reuse, /quit)
- Integration and API tests require real ANTHROPIC_API_KEY and OPENROUTER_API_KEY
- conftest.py fixtures are stubs — developer must implement before running

## File naming convention (docs/backend/)
- grill_doc_roadmap.md — Q&A planning session output
- prd.md — product requirements document
- features.md — features grouped by module with acceptance criteria
- issues.md — vertical slice issues in dependency order
- tests.md — test plan (Given/When/Then format)
- context.md — PM loop context and decisions (NOT pm-loop-context.md)
- tasks.md — PM loop task checklist and progress log

Stub files live in backend/tests/ (not docs/backend/tests/).

[[project-docufetch-stack]]
