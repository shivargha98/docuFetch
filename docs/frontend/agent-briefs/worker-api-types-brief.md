# Worker Brief: Issue 2 — API Types and Client

## Prerequisite

Issue 1 (Scaffold) must be complete. The Vite project at `/workspace/frontend/` must exist with `src/types/` and `src/api/` directories before you start.

## Your Mission

Create `src/types/api.ts` with TypeScript interfaces matching the FastAPI backend contracts exactly.
Create `src/api/client.ts` with three `fetch`-based functions wrapping the backend endpoints.

Do NOT modify any other file. Do NOT write tests in this task — tests live in `frontend/tests/unit/` and are handled separately.

## What to Build

### File 1: `src/types/api.ts`

```
/workspace/frontend/src/types/api.ts
```

Export these four interfaces (field names must exactly match the FastAPI backend):

```typescript
export interface ChatRequest {
  query: string;
  session_id: string;
}

export interface ChatResponse {
  answer: string;
  sources: string[];
  session_id: string;
}

export interface HealthResponse {
  status: string;
  initial_ingestion_complete: boolean;
}

export interface IngestStatusResponse {
  files_processed: number;
  files_failed: number;
  files_skipped: number;
  last_run: string | null;
}
```

Note on `IngestStatusResponse`: The backend's `GET /ingest/status` returns `files_processed`, `files_failed`, `files_skipped`, and `last_run` (not `doc_count` / `last_run_at`). The hook `useIngestStatus` (Issue 5) will derive `docCount` from `files_processed` and `lastRunAt` from `last_run`. Match the actual backend response shape here.

Add a file description comment at the top of the file.

### File 2: `src/api/client.ts`

```
/workspace/frontend/src/api/client.ts
```

The file must:
- Import from `../types/api`
- Have a description comment at the top
- Hardcode the backend URL as `http://localhost:8000`
- Export three functions, each with a docstring

**`postChat(query: string, sessionId: string): Promise<ChatResponse>`**
- Sends `POST http://localhost:8000/chat`
- Body: `JSON.stringify({ query, session_id: sessionId })`
- Headers: `{ 'Content-Type': 'application/json' }`
- If response.ok is false, throws `new Error('Request failed: ' + response.status)`
- Returns `response.json()` cast as `ChatResponse`

**`getHealth(): Promise<HealthResponse>`**
- Sends `GET http://localhost:8000/health`
- If response.ok is false, throws
- Returns parsed `HealthResponse`

**`getIngestStatus(): Promise<IngestStatusResponse>`**
- Sends `GET http://localhost:8000/ingest/status`
- If response.ok is false, throws
- Returns parsed `IngestStatusResponse`

**Network errors** (fetch rejects): let them propagate naturally — don't catch them inside the client.

No axios. No third-party HTTP library. Native `fetch` only.

## Coding Guidelines (from CLAUDE.md)

- Every function must have a docstring
- Every file must have a description comment at the top
- Simplicity first — minimum code
- No speculative features

## Acceptance Criteria (from issues.md Issue 2)

- [ ] `postChat(query, sessionId)` sends `POST /chat` with `{ query, session_id }` body and returns a parsed `ChatResponse`
- [ ] `getHealth()` sends `GET /health` and returns a parsed `HealthResponse`
- [ ] `getIngestStatus()` sends `GET /ingest/status` and returns a parsed `IngestStatusResponse`
- [ ] A non-2xx HTTP status causes the relevant function to throw an `Error`
- [ ] The project compiles with no TypeScript errors when all hooks import from these files

## Verification

Run `npm run build` from `/workspace/frontend/` after creating both files. It must produce no TypeScript errors.

## What to Write in Your Report

Write your completion report to `/workspace/docs/frontend/agent-reports/worker-api-types-report.md` with:
- Status: DONE or FAILED
- Files created and their key exports
- Result of `npm run build`
- Any deviations from this brief
