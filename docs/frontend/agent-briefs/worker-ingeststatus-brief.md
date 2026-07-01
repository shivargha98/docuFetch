# Worker Brief: Issue 5 — useIngestStatus Hook + StatusBar Component

## Prerequisites

- Issue 1 (Scaffold) complete — Vite project exists at `/workspace/frontend/`
- Issue 2 (API Types + Client) complete — `src/types/api.ts` and `src/api/client.ts` exist

Verify these files exist before starting:
- `/workspace/frontend/src/api/client.ts` (must export `getIngestStatus`)
- `/workspace/frontend/src/types/api.ts` (must export `IngestStatusResponse`)

## Your Mission

Create `src/hooks/useIngestStatus.ts` and `src/components/StatusBar.tsx`. Also write their unit/integration tests.

## What to Build

### File 1: `src/hooks/useIngestStatus.ts`

```
/workspace/frontend/src/hooks/useIngestStatus.ts
```

**Return type:**
```typescript
interface UseIngestStatusReturn {
  docCount: number;
  lastRunAt: string | null;
}
```

**Behaviour:**
- Polls `getIngestStatus()` from `src/api/client.ts` every **60000ms** (60 seconds)
- On first successful poll, sets `docCount` and `lastRunAt` from the response
- `docCount` maps to `response.files_processed` from the `IngestStatusResponse`
- `lastRunAt` maps to `response.last_run` from the `IngestStatusResponse`
- On a failed poll (catch block): leave the previously-fetched values unchanged — do NOT reset to 0/null
- On unmount: clear the interval

**Initial state:** `docCount: 0`, `lastRunAt: null`

**Pattern:** Same as useHealthGate but with 60000ms interval and no "stop polling when done" logic.

Fire one poll immediately on mount, then every 60 seconds.

Add a file description comment at the top. Add a docstring to the hook function.

### File 2: `src/components/StatusBar.tsx`

```
/workspace/frontend/src/components/StatusBar.tsx
```

**Props interface:**
```typescript
interface StatusBarProps {
  docCount: number;
  lastRunAt: string | null;
  onNewChat: () => void;
}
```

**Behaviour:**
- Displays `docCount` as a number
- Displays `lastRunAt` as a human-readable string — if null, display `"Never"`; if non-null, format with `new Date(lastRunAt).toLocaleString()` or similar
- Contains a "New chat" button that calls `onNewChat` exactly once when clicked
- Renders without errors when `docCount` is 0 and `lastRunAt` is null

**Styling (Tailwind):**
- Container: `flex items-center justify-between px-4 py-2 bg-white border-b border-gray-200 text-sm text-gray-600`
- Status info span: show "Docs: {docCount} | Last indexed: {formattedTime}"
- New chat button: `px-3 py-1 bg-gray-100 hover:bg-gray-200 rounded text-gray-700 text-sm`

Add a file description comment at the top. Add docstrings.

### File 3: `tests/unit/useIngestStatus.test.ts`

```
/workspace/frontend/tests/unit/useIngestStatus.test.ts
```

Write Vitest + `renderHook` tests for the 4 integration test cases from tests.md:

**Test 1: docCount and lastRunAt are populated from the first poll**
- Mock `fetch` to return `{ files_processed: 7, files_failed: 0, files_skipped: 0, last_run: "2026-07-01T10:00:00Z" }`
- Mount hook with fake timers
- Advance timers, assert `docCount === 7` and `lastRunAt === "2026-07-01T10:00:00Z"`

**Test 2: values update after a subsequent poll**
- First poll returns `files_processed: 7`; second poll returns `files_processed: 12`
- Advance 60s, assert `docCount === 12`

**Test 3: a failed poll leaves previous values unchanged**
- First poll returns `files_processed: 5`; second poll rejects
- Advance 60s, assert `docCount` remains `5`

**Test 4: polling interval is cleared on unmount**
- Mount then unmount hook
- Advance past 60s
- Assert no additional `fetch` call fires after unmount

### File 4: `tests/unit/StatusBar.test.tsx`

```
/workspace/frontend/tests/unit/StatusBar.test.tsx
```

Write RTL unit tests for the 5 StatusBar test cases from tests.md:

**Test 1: displays the current document count**
- Render `<StatusBar docCount={42} lastRunAt={null} onNewChat={vi.fn()} />`
- Assert `42` is visible

**Test 2: displays the last ingestion time as a readable string**
- Render with `lastRunAt="2026-07-01T10:00:00Z"`
- Assert some human-readable representation is visible (not the raw ISO string or "Never")

**Test 3: displays "Never" when lastRunAt is null**
- Render with `lastRunAt={null}`
- Assert text "Never" is present

**Test 4: clicking New chat calls the onNewChat handler exactly once**
- Render with `onNewChat` spy
- Click "New chat" button
- Assert spy called exactly once

**Test 5: renders without error when docCount is 0 and lastRunAt is null**
- Render with `docCount={0}` and `lastRunAt={null}`
- Assert no runtime error and `0` is visible

## Coding Guidelines (from CLAUDE.md)

- Every function must have a docstring
- Every file must have a description comment at the top
- Simplicity first

## Acceptance Criteria (from issues.md Issue 5)

- [ ] `StatusBar` renders the doc count from the most recent `/ingest/status` poll
- [ ] `StatusBar` renders "Never" when `last_run_at` is null
- [ ] `StatusBar` is visible on the page regardless of startup gate
- [ ] Clicking "New chat" calls `onNewChat` exactly once
- [ ] A failed poll leaves previously-fetched values unchanged

## Verification

Run `npm run test` from `/workspace/frontend/` — all useIngestStatus and StatusBar tests must pass.

## What to Write in Your Report

Write your completion report to `/workspace/docs/frontend/agent-reports/worker-ingeststatus-report.md` with:
- Status: DONE or FAILED
- Files created
- Test results
- Any deviations from this brief
