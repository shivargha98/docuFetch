# Frontend Orchestrator Plan

_Written: 2026-07-01_

## Build Target

docuFetch frontend — React + TypeScript + Tailwind CSS (Vite), at `/workspace/frontend/`.
Backend already running at `http://localhost:8000` — do not touch backend files.

## Issue Inventory (from issues.md)

| # | Issue | Blocked by |
|---|-------|-----------|
| 1 | Vite + React + TypeScript + Tailwind Scaffold | None |
| 2 | API Types and Client | 1 |
| 3 | Source Citation Strip Utility | 1 |
| 4 | useHealthGate Hook + Startup Gate UI | 2 |
| 5 | useIngestStatus Hook + StatusBar Component | 2 |
| 6 | MessageBubble, TypingIndicator, ChatWindow Components | 1, 3 |
| 7 | ChatInput Component | 1 |
| 8 | useChat Hook | 2, 3 |
| 9 | App Root Composition — Full Integration | 4, 5, 6, 7, 8 |

## Build Order

### Round 1 — Serial (foundation)
- Issue 1: Scaffold

Rationale: Every subsequent issue depends on the Vite project structure existing. Must be serial.

### Round 2 — Parallel (leaf issues with no shared-file conflict)
- Issue 2: API Types and Client → `src/types/api.ts`, `src/api/client.ts`
- Issue 3: Source Citation Strip → `src/utils/sources.ts`
- Issue 7: ChatInput Component → `src/components/ChatInput.tsx`

Rationale: All three touch distinct, non-overlapping files. Each only depends on Issue 1 being done. Safe to parallelize.

### Round 3 — Parallel (mid-layer, no shared-file conflict)
- Issue 4: useHealthGate → `src/hooks/useHealthGate.ts`
- Issue 5: useIngestStatus + StatusBar → `src/hooks/useIngestStatus.ts`, `src/components/StatusBar.tsx`
- Issue 6: MessageBubble + TypingIndicator + ChatWindow → `src/components/MessageBubble.tsx`, `src/components/TypingIndicator.tsx`, `src/components/ChatWindow.tsx`
- Issue 8: useChat → `src/hooks/useChat.ts`

Rationale: All four touch distinct file sets. All their dependencies (Issues 2, 3) complete in Round 2.
Risk note: Issue 6 imports from `src/utils/sources.ts` (Issue 3 output). Verify that file exists before launching.

### Round 4 — Serial (composition)
- Issue 9: App Root Composition → `src/App.tsx`

Rationale: Wires all hooks + components; must see all Round 3 outputs. Serial.

### Round 5 — Integration
- Spawn integration worker to run the full test suite (unit + integration + E2E stubs).

## Shared-File Risk Map

- `src/App.tsx` is touched by Issues 4 (partial) and 9 (full). Issues 4 and 9 are in different rounds — no conflict.
- `src/main.tsx` is scaffold-only (Issue 1), not modified after.
- No two Round 2 issues touch the same file.
- No two Round 3 issues touch the same file.

## Key Constraints

- Tailwind CSS v3 (not v4): `tailwind.config.js` + `@tailwind` directives in CSS.
- No axios — native `fetch` only in `api/client.ts`.
- Polling intervals: health gate = 3s, ingest status = 60s (PRD notes say 60s, issues.md says 60s — use 60s).
- Message cap: 20 entries in localStorage.
- Backend URL hardcoded: `http://localhost:8000`.
- Dev server port: 5173 (Vite default, matches backend CORS config).

## Status

- [ ] Round 1 — not started
- [ ] Round 2 — not started
- [ ] Round 3 — not started
- [ ] Round 4 — not started
- [ ] Round 5 (Integration) — not started
