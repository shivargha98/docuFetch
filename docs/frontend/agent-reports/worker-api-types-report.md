### Status
COMPLETE

### What I Built

- `/workspace/frontend/src/types/api.ts` — 21 lines. Exports four interfaces: `ChatRequest`, `ChatResponse`, `HealthResponse`, `IngestStatusResponse`. Field names match the FastAPI backend contracts exactly.
- `/workspace/frontend/src/api/client.ts` — 44 lines. Exports three fetch-based functions: `postChat`, `getHealth`, `getIngestStatus`. Imports from `../types/api`. Hardcodes `http://localhost:8000`. Each function throws `new Error('Request failed: ' + response.status)` on non-2xx; network errors propagate naturally.

### Test Results

`npm run build` from `/workspace/frontend/` — PASS (tsc + vite build, 16 modules, no TypeScript errors).

No unit tests were written in this task (brief explicitly excluded them).

### What the Orchestrator Should Know

- `IngestStatusResponse` uses `last_run: string | null` (not `last_run_at`) matching the actual backend field name. The `useIngestStatus` hook (Issue 5) is expected to alias this to `lastRunAt`.
- The existing `src/types/index.ts` and `src/api/index.ts` placeholder stubs were left untouched — they still export `{}`. If downstream hooks import from those index files rather than directly from `api.ts`/`client.ts`, the orchestrator should decide whether to add re-exports in the index files.

### What the Next Worker Needs

Hook workers (Issues 3–5) should import types from `src/types/api.ts` and functions from `src/api/client.ts`. Exports are:
- Types: `ChatRequest`, `ChatResponse`, `HealthResponse`, `IngestStatusResponse`
- Functions: `postChat(query: string, sessionId: string): Promise<ChatResponse>`, `getHealth(): Promise<HealthResponse>`, `getIngestStatus(): Promise<IngestStatusResponse>`

### Blockers

None.
