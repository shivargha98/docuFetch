# Worker Brief: Issue 9 — App Root Composition (Full Integration)

## Prerequisites (ALL must be complete before starting)

- Issue 1: Scaffold — `/workspace/frontend/` Vite project exists
- Issue 2: API Types + Client — `src/api/client.ts`, `src/types/api.ts` exist
- Issue 3: Citation Strip — `src/utils/sources.ts` exists
- Issue 4: useHealthGate — `src/hooks/useHealthGate.ts` exists
- Issue 5: useIngestStatus + StatusBar — `src/hooks/useIngestStatus.ts`, `src/components/StatusBar.tsx` exist
- Issue 6: Components — `src/components/MessageBubble.tsx`, `src/components/TypingIndicator.tsx`, `src/components/ChatWindow.tsx` exist
- Issue 7: ChatInput — `src/components/ChatInput.tsx` exists
- Issue 8: useChat — `src/hooks/useChat.ts` exists

Verify all files above exist before making any changes.

## Your Mission

Wire all hooks and components into `src/App.tsx` to produce the complete single-page layout. Also write the integration tests for App and set up the E2E test stubs.

## What to Build

### File 1: `src/App.tsx` (OVERWRITE the existing placeholder)

```
/workspace/frontend/src/App.tsx
```

**Layout:**
```
┌─────────────────────────────────┐
│  StatusBar (always visible)     │
├─────────────────────────────────┤
│  [STARTUP GATE if not ready]    │
│   OR                            │
│  ChatWindow (scrollable)        │
│  ChatInput (pinned to bottom)   │
└─────────────────────────────────┘
```

**Hooks used:**
- `useHealthGate()` → `{ ready }`
- `useChat()` → `{ messages, isLoading, sendMessage, resetChat }`
- `useIngestStatus()` → `{ docCount, lastRunAt }`

**Startup gate:** When `ready` is `false`, show:
```tsx
<div className="flex-1 flex items-center justify-center text-gray-500">
  <div className="text-center">
    <div className="text-lg font-medium mb-2">Preparing your documents…</div>
    <div className="text-sm">Please wait while the index is being built.</div>
  </div>
</div>
```

When `ready` is `true`, show `ChatWindow` + `ChatInput`.

**Full App structure:**
```tsx
function App() {
  const { ready } = useHealthGate()
  const { messages, isLoading, sendMessage, resetChat } = useChat()
  const { docCount, lastRunAt } = useIngestStatus()

  return (
    <div className="flex flex-col h-screen bg-gray-50">
      <StatusBar docCount={docCount} lastRunAt={lastRunAt} onNewChat={resetChat} />
      {!ready ? (
        <StartupGate />
      ) : (
        <>
          <ChatWindow messages={messages} isLoading={isLoading} />
          <ChatInput onSend={sendMessage} isLoading={isLoading} />
        </>
      )}
    </div>
  )
}
```

You can inline `StartupGate` as a local function component or just inline the JSX — keep it simple.

Add a file description comment at the top. Add a docstring to the App component.

### File 2: `tests/unit/App.test.tsx`

```
/workspace/frontend/tests/unit/App.test.tsx
```

Write RTL integration tests for the 6 App test cases from tests.md. Mock `fetch` globally.

**Setup:**
```typescript
beforeEach(() => {
  vi.useFakeTimers()
  localStorage.clear()
})
afterEach(() => {
  vi.useRealTimers()
  vi.restoreAllMocks()
})
```

You will need to mock `fetch` for both `/health` and `/ingest/status` simultaneously. Use `vi.fn()` with `mockImplementation` based on the URL:

```typescript
vi.stubGlobal('fetch', vi.fn(async (url: string) => {
  if (url.includes('/health')) {
    return { ok: true, json: async () => ({ status: 'ok', initial_ingestion_complete: false }) }
  }
  if (url.includes('/ingest/status')) {
    return { ok: true, json: async () => ({ files_processed: 5, files_failed: 0, files_skipped: 0, last_run: null }) }
  }
  throw new Error('unexpected fetch: ' + url)
}))
```

**Test 1: startup gate is visible and chat input is not interactive on initial render**
- Mock `/health` returning `initial_ingestion_complete: false`
- Render `<App />`
- Assert "Preparing" text is visible
- Assert no enabled chat textarea is present (either absent or disabled)

**Test 2: startup gate clears and chat input activates when health poll returns ready**
- First `/health` call returns `false`; after calling `vi.advanceTimersByTimeAsync(3000)`, mock returns `true`
- Render `<App />`
- Advance timers
- Assert gate message is gone
- Assert enabled chat textarea is present

**Test 3: StatusBar is visible during the startup gate**
- Mock `/health` with `initial_ingestion_complete: false`
- Render `<App />`
- Assert StatusBar content (doc count or "New chat" button) is present

**Test 4: sending a message shows typing indicator then appends the response**
- Render App in ready state (health returns `true`)
- Mock `/chat` to resolve after a delay with `{ answer: 'The sky is blue.', sources: ['weather.pdf'], session_id: 'abc' }`
- User types a question and presses Enter
- Assert typing indicator visible while pending
- After resolution: assert answer text visible, sources block visible, typing indicator gone

**Test 5: chat API failure shows inline error bubble and re-enables the input**
- Render App in ready state
- Mock `/chat` to reject
- User sends a message
- Assert error-role bubble visible
- Assert textarea is re-enabled (not disabled)

**Test 6: New chat clears the visible message list**
- Render App in ready state with two messages visible
- Click "New chat"
- Assert message bubbles are gone
- Assert textarea is still active

### File 3: `tests/e2e/app.spec.ts`

```
/workspace/frontend/tests/e2e/app.spec.ts
```

Write Playwright E2E test stubs for the 3 E2E test cases from tests.md. These are stubs — they contain the test structure but may not pass without a running backend. Keep them runnable in structure.

```typescript
import { test, expect } from '@playwright/test'

test.describe('docuFetch E2E', () => {
  test('startup gate appears on load and resolves after backend ingestion completes', async ({ page }) => {
    await page.goto('/')
    await expect(page.getByText(/preparing your documents/i)).toBeVisible()
    await expect(page.locator('textarea')).toBeEnabled({ timeout: 60000 })
  })

  test('user sends a question and receives an answer with a sources block', async ({ page }) => {
    await page.goto('/')
    await expect(page.locator('textarea')).toBeEnabled({ timeout: 60000 })
    await page.locator('textarea').fill('What documents are indexed?')
    await page.keyboard.press('Enter')
    await expect(page.getByText(/Sources:/)).toBeVisible({ timeout: 30000 })
  })

  test('New chat clears history and next message starts a fresh session', async ({ page }) => {
    await page.goto('/')
    await expect(page.locator('textarea')).toBeEnabled({ timeout: 60000 })
    await page.locator('textarea').fill('Tell me something')
    await page.keyboard.press('Enter')
    await expect(page.getByRole('button', { name: /new chat/i })).toBeVisible()
    await page.getByRole('button', { name: /new chat/i }).click()
    // Previous messages should be gone
    await expect(page.getByText('Tell me something')).not.toBeVisible()
  })
})
```

## Coding Guidelines (from CLAUDE.md)

- Every function must have a docstring
- Every file must have a description comment at the top
- Simplicity first — no speculative features

## Critical Gotchas (discovered during Round 3 — read before writing any tests)

### 1. Message type reconciliation
`src/types/message.ts` now exists (created by Issue 6) and exports `Message` and `MessageRole`.
`src/hooks/useChat.ts` currently defines `Message` inline. You MUST update `useChat.ts` to import `Message` from `../../types/message` instead of defining it locally. Check that the field shapes match — if there is any mismatch, the shared `src/types/message.ts` definition is authoritative.

### 2. `scrollIntoView` stub in App tests
jsdom does not implement `scrollIntoView`. Any test that renders `ChatWindow` (which uses `scrollIntoView`) will throw unless you stub it. Add this in `beforeEach` or at the top of any describe block that renders `<App />`:
```typescript
beforeEach(() => {
  Element.prototype.scrollIntoView = vi.fn()
})
```

### 3. Fake timers + `setInterval` — do NOT use `vi.runAllTimersAsync()`
`vi.runAllTimersAsync()` triggers Vitest's infinite-loop guard when `setInterval` is active (as in `useHealthGate` and `useIngestStatus`). Use this pattern instead to advance time and flush microtasks:
```typescript
await act(async () => {
  vi.advanceTimersByTime(3000)
  await Promise.resolve()
})
```
Or for the health gate ready transition in App tests:
```typescript
await act(async () => {
  vi.advanceTimersByTime(3000)
})
await waitFor(() => expect(screen.queryByText(/preparing/i)).not.toBeInTheDocument())
```

### 4. Multi-endpoint fetch mock
When App renders, it fires both `GET /health` and `GET /ingest/status` polling. Your fetch mock must handle both URLs. Pattern:
```typescript
vi.stubGlobal('fetch', vi.fn(async (url: string) => {
  if ((url as string).includes('/health')) {
    return { ok: true, json: async () => ({ status: 'ok', initial_ingestion_complete: false }) }
  }
  if ((url as string).includes('/ingest/status')) {
    return { ok: true, json: async () => ({ files_processed: 0, files_failed: 0, files_skipped: 0, last_run: null }) }
  }
  throw new Error('unexpected fetch: ' + url)
}))
```
To switch the health mock to `ready: true` after the first call, use `mockResolvedValueOnce` for the first call then `mockResolvedValue` for subsequent ones.

## Acceptance Criteria (from issues.md Issue 9)

- [ ] On load with ingestion incomplete: "Preparing your documents…" visible, chat input not interactive
- [ ] Once ingestion completes: chat input active, gate message gone
- [ ] Typing + Enter sends to backend; answer and sources appear in chat window
- [ ] While response pending: typing indicator visible, input disabled
- [ ] On failed request: inline error bubble, input re-enables
- [ ] Clicking "New chat": visible message history cleared, next message is a fresh session
- [ ] Status bar with doc count and last ingestion time visible at all times

## Verification

Run `npm run test` from `/workspace/frontend/` — all App unit/integration tests must pass.
(E2E tests require running backend — confirm they compile cleanly with `npm run build`)

## What to Write in Your Report

Write your completion report to `/workspace/docs/frontend/agent-reports/worker-app-composition-report.md` with:
- Status: DONE or FAILED
- Files created/modified
- Test results (unit/integration)
- Build output
- Any deviations from this brief
