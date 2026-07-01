# DocuFetch Frontend — Agent Context

**Last updated:** 2026-07-01

## What Was Built / Decided

### PRD (docs/frontend/prd.md)
- 23 user stories covering: startup gate, chat send/receive, source citation rendering, localStorage persistence, status bar, error handling, "New chat" reset.
- Modules identified: api/client.ts, types/api.ts, hooks (useChat, useHealthGate, useIngestStatus), components (ChatWindow, MessageBubble, TypingIndicator, ChatInput, StatusBar), utils/sources.ts, App.tsx.
- Key API contracts typed in TypeScript: ChatRequest, ChatResponse, HealthResponse, IngestStatusResponse.
- CORS already configured on backend for http://localhost:5173.

### Features (docs/frontend/features.md)
- 12 features across 5 module groups: API (2), Utils (1), Hooks (3), Components (5), App (1).
- All 23 user stories are covered — no orphaned stories.
- Feature list: Backend API Client, API Type Contracts, Source Citation Strip, useChat, useHealthGate, useIngestStatus, ChatWindow, MessageBubble, TypingIndicator, ChatInput, StatusBar, App Root and Startup Gate.

### Key Decisions Recorded
- Session ID + message list persisted in localStorage, cap at 20 matching backend trim.
- [source: filename] regex-stripped from answer; sources array rendered as block below answer.
- Startup gate: poll /health every 3s; block input until initial_ingestion_complete = true.
- Error handling: inline error bubble in chat stream; input re-enabled for retry.
- Status bar: polls /ingest/status every 60s; contains "New chat" button.
- Testing: Vitest + RTL for unit/component; Playwright for e2e against real backend.

## Open Risks
- Message history cap (20) must stay in sync with backend routes.py trim logic.
- [source: ...] regex must handle filenames with spaces, hyphens, dots.
- Playwright e2e tests require backend running — must be documented as a prerequisite.
