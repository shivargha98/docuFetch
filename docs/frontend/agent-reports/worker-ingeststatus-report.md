### Status
COMPLETE

### What I Built

**New files created:**

- `/workspace/frontend/src/hooks/useIngestStatus.ts` (37 lines)
  Custom React hook that polls `getIngestStatus()` immediately on mount then every 60 seconds, exposing `docCount` (from `files_processed`) and `lastRunAt` (from `last_run`). Failed polls leave prior values unchanged; interval is cleared on unmount.

- `/workspace/frontend/src/components/StatusBar.tsx` (36 lines)
  Functional component rendering doc count and last-run time in a styled flex bar. Shows "Never" when `lastRunAt` is null; formats non-null values via `toLocaleString()`. Contains a "New chat" button that calls `onNewChat` on click.

- `/workspace/frontend/tests/unit/useIngestStatus.test.ts` (109 lines)
  Four Vitest + `renderHook` tests covering: initial poll population, subsequent poll updates, failed-poll value preservation, and unmount interval cleanup.

- `/workspace/frontend/tests/unit/StatusBar.test.tsx` (48 lines)
  Five RTL tests covering: doc count display, formatted last-run string, "Never" fallback, "New chat" button callback, and zero-state rendering.

**Files modified (minor):**

- `/workspace/frontend/src/hooks/index.ts` — updated placeholder to export `useIngestStatus`
- `/workspace/frontend/src/components/index.ts` — updated placeholder to export `StatusBar`

### Test Results

All 45 tests pass (9 test files):

- `useIngestStatus > docCount and lastRunAt are populated from the first poll` — PASS
- `useIngestStatus > values update after a subsequent poll` — PASS
- `useIngestStatus > a failed poll leaves previous values unchanged` — PASS
- `useIngestStatus > polling interval is cleared on unmount` — PASS
- `StatusBar > displays the current document count` — PASS
- `StatusBar > displays the last ingestion time as a human-readable string` — PASS
- `StatusBar > displays "Never" when lastRunAt is null` — PASS
- `StatusBar > clicking New chat calls the onNewChat handler exactly once` — PASS
- `StatusBar > renders without error when docCount is 0 and lastRunAt is null` — PASS

All pre-existing tests continued to pass (no regressions).

### What the Orchestrator Should Know

- The initial version of the hook tests used `vi.runAllTimersAsync()` which caused vitest to abort with "Aborting after running 10000 timers, assuming an infinite loop!" because `setInterval` creates an unbounded chain. Switched to `vi.advanceTimersByTime()` + `await Promise.resolve()` inside `act()` to flush microtasks without running the timer chain infinitely — same approach as the existing `useHealthGate` tests in this project.
- Both index files (`src/hooks/index.ts` and `src/components/index.ts`) were placeholder stubs containing `export {}`. Updated them to re-export the new hook and component respectively. This is a minimal change not explicitly mentioned in the brief but required for consistent module resolution.

### What the Next Worker Needs

Integration worker: `useIngestStatus` is exported from `src/hooks/useIngestStatus.ts` and re-exported from `src/hooks/index.ts`. It returns `{ docCount: number, lastRunAt: string | null }`. `StatusBar` is exported as default from `src/components/StatusBar.tsx` and re-exported from `src/components/index.ts`. It accepts props `{ docCount, lastRunAt, onNewChat }`.

### Blockers

None.
