# Worker Brief: Issue 4 — useHealthGate Hook

## Prerequisites

- Issue 1 (Scaffold) complete — Vite project exists at `/workspace/frontend/`
- Issue 2 (API Types + Client) complete — `src/types/api.ts` and `src/api/client.ts` exist

Verify these files exist before starting:
- `/workspace/frontend/src/api/client.ts` (must export `getHealth`)
- `/workspace/frontend/src/types/api.ts` (must export `HealthResponse`)

## Your Mission

Create `src/hooks/useHealthGate.ts` — a polling hook that watches `GET /health` every 3 seconds and exposes a `ready` boolean. Also write its integration tests.

Do NOT modify `App.tsx` in this task — App composition is handled by Issue 9.

## What to Build

### File 1: `src/hooks/useHealthGate.ts`

```
/workspace/frontend/src/hooks/useHealthGate.ts
```

**Return type:**
```typescript
interface UseHealthGateReturn {
  ready: boolean;
}
```

**Behaviour:**
- `ready` starts as `false` on mount
- Polls `getHealth()` from `src/api/client.ts` every 3000ms using `setInterval`
- When a poll response has `initial_ingestion_complete: true`, set `ready` to `true` and **clear the interval** (no more polls after ready)
- If a poll throws (network error, non-2xx): catch the error silently, keep `ready` as `false`, let the next scheduled poll fire normally
- On component unmount: clear the interval to prevent memory leaks

**Pattern to follow:**
```typescript
useEffect(() => {
  // fire one poll immediately on mount, then every 3s
  const poll = async () => {
    try {
      const result = await getHealth()
      if (result.initial_ingestion_complete) {
        setReady(true)
        clearInterval(intervalId)
      }
    } catch {
      // stay not-ready, next poll will retry
    }
  }
  
  poll() // immediate first poll
  const intervalId = setInterval(poll, 3000)
  
  return () => clearInterval(intervalId)
}, [])
```

Note: The `clearInterval` inside the async callback and in the cleanup both target the same `intervalId`. This is correct — if the interval fires again before the async poll resolves, it will run but the `setReady(true)` path won't be hit again (React state setter is idempotent for the same value). To be safe, track a ref to stop polling cleanly:

```typescript
const intervalRef = useRef<ReturnType<typeof setInterval> | null>(null)
```

Add a file description comment at the top. Add a docstring to the hook function.

### File 2: `tests/unit/useHealthGate.test.ts`

```
/workspace/frontend/tests/unit/useHealthGate.test.ts
```

Write Vitest + RTL `renderHook` tests covering the 5 integration test cases from tests.md.

Mock `fetch` globally in each test using `vi.stubGlobal('fetch', vi.fn())`.
Use `vi.useFakeTimers()` + `vi.advanceTimersByTimeAsync(3000)` to control the polling interval.

**Test 1: ready is false on initial render**
```typescript
vi.stubGlobal('fetch', vi.fn(() => new Promise(() => {}))) // never resolves
const { result } = renderHook(() => useHealthGate())
expect(result.current.ready).toBe(false)
```

**Test 2: ready becomes true after poll returns initial_ingestion_complete: true**
```typescript
vi.useFakeTimers()
vi.stubGlobal('fetch', vi.fn().mockResolvedValue({
  ok: true,
  json: () => Promise.resolve({ status: 'ok', initial_ingestion_complete: true })
}))
const { result } = renderHook(() => useHealthGate())
await vi.runAllTimersAsync()
expect(result.current.ready).toBe(true)
```

**Test 3: no further fetch calls are made after ready becomes true**
- Mock fetch to return `initial_ingestion_complete: true`
- Mount hook, advance timers past the ready point
- Advance another full interval
- Assert `fetch` was called exactly once (or at most once after ready — the initial immediate poll)

**Test 4: a failed health poll keeps ready false without showing an error state**
```typescript
vi.stubGlobal('fetch', vi.fn().mockRejectedValue(new Error('network error')))
const { result } = renderHook(() => useHealthGate())
await vi.runAllTimersAsync()
expect(result.current.ready).toBe(false)
// no error property escapes
```

**Test 5: polling interval is cleared on unmount**
- Mount hook, unmount it
- Advance timers past the poll interval
- Assert `fetch` was not called after unmount (or only called during mount, not after)

Test imports:
```typescript
import { renderHook, waitFor, act } from '@testing-library/react'
import { vi, describe, it, expect, afterEach, beforeEach } from 'vitest'
import useHealthGate from '../../src/hooks/useHealthGate'
```

Remember to call `vi.useRealTimers()` and `vi.restoreAllMocks()` in `afterEach`.

## Coding Guidelines (from CLAUDE.md)

- Every function must have a docstring
- Every file must have a description comment at the top
- Simplicity first

## Acceptance Criteria (from issues.md Issue 4)

- [ ] `ready` is `false` on mount and while `initial_ingestion_complete` is `false`
- [ ] `ready` becomes `true` once `initial_ingestion_complete: true` and does not revert
- [ ] Polling stops after `ready` becomes `true`
- [ ] A failed poll keeps `ready` as `false` without crashing
- [ ] The polling interval clears on component unmount

## Verification

Run `npm run test` from `/workspace/frontend/` — all useHealthGate tests must pass.

## What to Write in Your Report

Write your completion report to `/workspace/docs/frontend/agent-reports/worker-healthgate-report.md` with:
- Status: DONE or FAILED
- Files created
- Test results
- Any deviations from this brief
