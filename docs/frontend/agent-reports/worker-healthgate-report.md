### Status
COMPLETE

### What I Built

**Files created:**

1. `/workspace/frontend/src/hooks/useHealthGate.ts` — 51 lines
   - Default-exported `useHealthGate` hook
   - Polls `getHealth()` from `src/api/client.ts` every 3000 ms via `setInterval`
   - Uses `useRef` to track the interval so both the "ready" branch and the cleanup can clear it safely
   - Sets `ready` to `true` once `initial_ingestion_complete` is `true`, then clears the interval
   - Silently swallows errors so polling continues on the next tick
   - Clears interval on unmount via the `useEffect` cleanup

2. `/workspace/frontend/tests/unit/useHealthGate.test.ts` — 75 lines
   - 5 Vitest + RTL `renderHook` tests
   - Uses `vi.useFakeTimers()` / `vi.advanceTimersByTimeAsync` / `vi.runAllTimersAsync`
   - `vi.restoreAllMocks()` + `vi.useRealTimers()` in `afterEach`

### Test Results

All 5 useHealthGate tests pass:

- PASS — ready is false on initial render
- PASS — ready becomes true after poll returns initial_ingestion_complete: true
- PASS — no further fetch calls are made after ready becomes true
- PASS — a failed health poll keeps ready false without showing an error state
- PASS — polling interval is cleared on unmount

### What the Orchestrator Should Know

- The brief's "Test 4" example used `vi.runAllTimersAsync()` on a hook polling indefinitely (network errors keep the interval alive). This causes Vitest to abort with "assuming an infinite loop" after 10 000 timer ticks. I replaced it with `vi.advanceTimersByTimeAsync(9000)` (3 full intervals), which exercises the same behaviour correctly and is the right approach for any always-polling hook.
- `ChatWindow.test.tsx` (4 failures) and `useIngestStatus.test.ts` (4 failures) were already failing before this work. These are not regressions from this brief.

### What the Next Worker Needs

Integration worker (Issue 9 — App composition): `useHealthGate` is the default export from `src/hooks/useHealthGate.ts`. It returns `{ ready: boolean }`. Import with:
```typescript
import useHealthGate from './hooks/useHealthGate'
```
When `ready` is `false`, show a loading/waiting screen; when `true`, render the main chat UI.

### Blockers
None.
