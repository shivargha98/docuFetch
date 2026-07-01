### Status
COMPLETE

### What I Built

**Modified (1 file):**
- `/workspace/frontend/src/hooks/useChat.ts` — removed the inline `Message` interface definition and replaced it with `import type { Message } from '../types/message'`. The field shapes matched exactly (id, role, text, sources?), so no other changes were needed. (-5 lines, net no functional change)

**Overwritten (1 file):**
- `/workspace/frontend/src/App.tsx` — full implementation: imports and wires `useHealthGate`, `useChat`, `useIngestStatus`, `StatusBar`, `ChatWindow`, `ChatInput`. Includes a local `StartupGate` function component. File-level description comment and docstrings on both functions. (55 lines)

**Created (2 files):**
- `/workspace/frontend/tests/unit/App.test.tsx` — 6 RTL integration tests for App. Uses `fireEvent` (not `userEvent`) for input interactions to avoid fake-timer deadlocks, and `act` + `Promise.resolve()` ticks instead of `waitFor` or `vi.runAllTimersAsync()`. Stubs `Element.prototype.scrollIntoView` in `beforeEach`. (270 lines)
- `/workspace/frontend/tests/e2e/app.spec.ts` — 3 Playwright E2E stubs (startup gate, chat question/answer, new-chat reset). Excluded from Vitest via `vite.config.ts` update. (35 lines)

**Modified (1 file):**
- `/workspace/frontend/vite.config.ts` — added `exclude: ['**/node_modules/**', '**/tests/e2e/**']` to the Vitest `test` config so Playwright spec files are not picked up by Vitest. (+1 line)

### Test Results

All 51 unit/integration tests pass across 10 test files:

- App > Test 1: startup gate is visible and chat input is not interactive on initial render — PASS
- App > Test 2: startup gate clears and chat input activates when health poll returns ready — PASS
- App > Test 3: StatusBar is visible during the startup gate — PASS
- App > Test 4: sending a message shows typing indicator then appends the response — PASS
- App > Test 5: chat API failure shows inline error bubble and re-enables the input — PASS
- App > Test 6: New chat clears the visible message list — PASS
- All 45 pre-existing tests from other workers continue to pass without regression.

### What the Orchestrator Should Know

1. **Pre-existing build failure**: `npm run build` fails before and after my changes. Rolldown (Vite 8's bundler) reports `ChatResponse`, `HealthResponse`, and `IngestStatusResponse` as missing exports from `src/types/api.ts`, even though they are clearly exported there. `tsc --noEmit` passes cleanly — this is a Rolldown bundler bug with TypeScript interface re-exports. The failure pre-dates this worker's work (confirmed by stashing all changes and reproducing the same error). The orchestrator should address this separately, likely by using `vite-plugin-dts` or switching to `export type` in the bundler config, or downgrading the Vite/Rolldown version.

2. **`userEvent` unusable with fake timers**: The brief suggested `userEvent.setup({ advanceTimers: vi.advanceTimersByTime })` but in practice `userEvent` hangs when fake timers are active (its internal `setTimeout`-based delays never fire). All input interactions in the App tests use `fireEvent` instead, which works reliably.

3. **`waitFor` avoided with fake timers**: `waitFor` uses `setInterval` internally and hangs under fake timers. All async checks use `await act(async () => { ...; await Promise.resolve(); await Promise.resolve() })` followed by direct DOM assertions.

4. **`useChat.ts` Message type**: The inline `Message` interface was identical to `src/types/message.ts` — no field-shape mismatches, just a straightforward import replacement.

### What the Next Worker Needs

No downstream worker depends on this worker's output — this is the final integration issue (Issue 9). The full frontend is now wired.

### Blockers

None.
