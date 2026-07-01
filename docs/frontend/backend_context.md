# Frontend Build — Decisions and Context Log

_Started: 2026-07-01_

## Architectural Decisions

### Tailwind Version
Using Tailwind CSS v3 (not v4). Config approach: `tailwind.config.js` + `@tailwind directives` in a CSS file imported into `main.tsx`.

### Polling Intervals
- Health gate (`useHealthGate`): 3 seconds — short-lived, only until ingestion is complete
- Ingest status (`useIngestStatus`): 60 seconds — lifetime of session (PRD note on page 32 and issues.md both say 60s; features.md description says "60 seconds")

### Backend URL
Hardcoded as `http://localhost:8000`. No env var, no proxy — matches PRD Implementation Decisions.

### No Axios
`api/client.ts` uses native `fetch` only. PRD explicitly says "No axios."

### Message Cap
20 entries in localStorage — matches backend `history[-20:]` trim in routes.py.

### Session Persistence
UUID4 generated on first load, stored in localStorage key. Message list stored as JSON array, also in localStorage. "New chat" clears both and generates a new UUID4.

### Source Citation Rendering
Two sources of citation data: `answer` text (may contain inline `[source: filename]`) and `sources` array. Strip inline markers from `answer` before display. Render `sources` array as a distinct block below the answer. `sources` array is authoritative.

### Test Stack
- Unit + integration: Vitest + React Testing Library (`@testing-library/react`)
- E2E: Playwright
- Test files live in `frontend/tests/unit/` and `frontend/tests/e2e/`

### Dev Server Port
5173 (Vite default). Backend CORS is pinned to `http://localhost:5173`. Do not change this port.

### App.tsx Lifecycle
Issue 4 adds a minimal gate to App.tsx (health gate rendering only). Issue 9 replaces/extends it with full composition. Worker for Issue 9 must overwrite App.tsx in full.

## Worker Outcomes Log

### Issue 1 — Scaffold (DONE)
- Vitest needed `--passWithNoTests` flag (added to vitest config) since v4.x exits code 1 with no test files.
- All dirs created with placeholder index.ts files.

### Issue 2 — API Types + Client (DONE)
- `src/types/index.ts` and `src/api/index.ts` placeholder stubs still export `{}` (left untouched). Hook workers must import from `src/types/api.ts` and `src/api/client.ts` directly, not from index files.
- Build: zero TypeScript errors, 16 modules.

### Issue 3 — Source Citation Strip (DONE)
- `src/utils/sources.ts` and `tests/unit/sources.test.ts` created. All 6 tests pass.

### Issue 4 — useHealthGate (DONE)
- Used `useRef` to hold interval ID for reliable cleanup in both the async callback and the `useEffect` cleanup.
- Test deviation: Test 4 used `vi.advanceTimersByTimeAsync(9000)` instead of `vi.runAllTimersAsync()` to avoid Vitest infinite-loop guard on error-polling hooks.
- All 5 tests pass.

### Issue 7 — ChatInput (DONE)
- `src/components/ChatInput.tsx` and `tests/unit/ChatInput.test.tsx` created. All 4 tests pass.

### Issue 8 — useChat (DONE)
- CRITICAL: `src/types/message.ts` did NOT exist when Issue 8 ran (Issue 6 not yet complete). useChat defines `Message` type inline.
- After Issue 6 completes and creates `src/types/message.ts`, the App composition worker (Issue 9) must ensure the Message type is consistent — either useChat is updated to import from `src/types/message.ts` or it keeps inline definition (both must match exactly).
- `crypto.randomUUID()` used instead of the `uuid` package for session ID generation (browser native API).
- All 8 tests pass.

### Issue 5 — useIngestStatus + StatusBar (pending)
### Issue 6 — MessageBubble + TypingIndicator + ChatWindow (pending)

## Deviations from Plan

- `scrollIntoView is not a function` errors were present in test output from multiple workers — this is a jsdom limitation. The ChatWindow scroll test must stub `Element.prototype.scrollIntoView` in the test setup or per-test. Issue 6 worker's components brief included this instruction; verify it was followed in the report.
- Message type defined inline in `useChat.ts` rather than imported from `src/types/message.ts` (which didn't exist yet). Issue 9 must reconcile this.
