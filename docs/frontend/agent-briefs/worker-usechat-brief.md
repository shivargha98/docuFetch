# Worker Brief: Issue 8 — useChat Hook

## Prerequisites

- Issue 1 (Scaffold) complete — Vite project at `/workspace/frontend/`
- Issue 2 (API Types + Client) complete — `src/api/client.ts` exports `postChat`; `src/types/api.ts` exports `ChatResponse`
- Issue 3 (Citation Strip Utility) complete — only needed for the Message type context; `stripCitations` is used in `MessageBubble` not in this hook directly

Verify before starting:
- `/workspace/frontend/src/api/client.ts` (must export `postChat`)
- `/workspace/frontend/src/types/api.ts` (must export `ChatResponse`)

Also: Issue 6 may have created `src/types/message.ts` with the `Message` type. If that file exists, import from it. If not, define the `Message` type inline in the hook.

## Your Mission

Create `src/hooks/useChat.ts` — the hook that owns all chat state: message list, loading state, session ID, localStorage persistence, error handling. Also write its integration tests.

## What to Build

### File 1: `src/hooks/useChat.ts`

```
/workspace/frontend/src/hooks/useChat.ts
```

**LocalStorage keys:**
```typescript
const SESSION_KEY = 'docufetch_session_id'
const MESSAGES_KEY = 'docufetch_messages'
const MESSAGE_CAP = 20
```

**Message type** (import from `src/types/message.ts` if it exists, otherwise define locally):
```typescript
interface Message {
  id: string;
  role: 'user' | 'assistant' | 'error';
  text: string;
  sources?: string[];
}
```

**Return type:**
```typescript
interface UseChatReturn {
  messages: Message[];
  isLoading: boolean;
  sendMessage: (query: string) => Promise<void>;
  resetChat: () => void;
}
```

**Initialization:**
```typescript
// Session ID: read from localStorage or generate new UUID4
const initSessionId = (): string => {
  const existing = localStorage.getItem(SESSION_KEY)
  if (existing) return existing
  const newId = crypto.randomUUID() // built-in browser API, no uuid package needed for this
  localStorage.setItem(SESSION_KEY, newId)
  return newId
}

// Messages: rehydrate from localStorage, cap at 20
const initMessages = (): Message[] => {
  try {
    const stored = localStorage.getItem(MESSAGES_KEY)
    if (!stored) return []
    const parsed = JSON.parse(stored) as Message[]
    return parsed.slice(-MESSAGE_CAP)
  } catch {
    return []
  }
}
```

**`sendMessage(query: string)`:**
1. Set `isLoading = true`
2. Generate a unique ID for the user message: `crypto.randomUUID()`
3. Append user message: `{ id, role: 'user', text: query }`
4. Persist updated message list to localStorage (capped at 20)
5. Call `postChat(query, sessionId)`
6. On success: append assistant message `{ id: crypto.randomUUID(), role: 'assistant', text: response.answer, sources: response.sources }`
7. On failure (catch): append error message `{ id: crypto.randomUUID(), role: 'error', text: 'Request failed. Is the server running?' }`
8. Set `isLoading = false` in finally block
9. Persist final message list to localStorage after update

**Helper: persist to localStorage**
```typescript
const persistMessages = (msgs: Message[]) => {
  const capped = msgs.slice(-MESSAGE_CAP)
  localStorage.setItem(MESSAGES_KEY, JSON.stringify(capped))
}
```

**`resetChat()`:**
1. Generate a new session ID with `crypto.randomUUID()`
2. Update `sessionId` state
3. Store new session ID in localStorage
4. Set `messages = []`
5. Persist empty array to localStorage

**State:**
```typescript
const [sessionId, setSessionId] = useState<string>(() => initSessionId())
const [messages, setMessages] = useState<Message[]>(() => initMessages())
const [isLoading, setIsLoading] = useState(false)
```

Add a file description comment at the top. Add docstrings to the hook and all helper functions.

### File 2: `tests/unit/useChat.test.ts`

```
/workspace/frontend/tests/unit/useChat.test.ts
```

Write Vitest + `renderHook` + `act` tests for the 8 integration test cases from tests.md.

Mock `fetch` via `vi.stubGlobal('fetch', vi.fn(...))`. Use `localStorage` directly (jsdom provides it).

**Setup / teardown:**
```typescript
beforeEach(() => {
  localStorage.clear()
  vi.restoreAllMocks()
})
```

**Test 1: sendMessage appends a user message immediately and an assistant message after resolution**
- Mock `fetch` to resolve with `{ answer: '42', sources: [], session_id: 'abc' }`
- Call `sendMessage('What is the answer?')`
- Assert user message with text 'What is the answer?' appears in the list
- After resolution, assert assistant message with text '42' appears

**Test 2: isLoading is true during the request and false after resolution**
- Mock `fetch` with a controlled promise
- After `sendMessage`, assert `isLoading === true`
- After promise resolves, assert `isLoading === false`

**Test 3: API failure appends an error entry and resets isLoading to false**
- Mock `fetch` to reject with `new Error('network')`
- Call `sendMessage('question')`
- Assert error-role message is appended
- Assert `isLoading === false`

**Test 4: session ID is read from localStorage if one already exists**
- Set `localStorage.setItem('docufetch_session_id', 'existing-uuid')`
- Mount hook
- Mock `fetch` and call `sendMessage`
- Assert the request body contains `session_id: 'existing-uuid'`
  - To check: capture the call args: `const body = JSON.parse(vi.mocked(fetch).mock.calls[0][1].body)`
  - Assert `body.session_id === 'existing-uuid'`

**Test 5: a new UUID4 is generated and saved to localStorage if no session ID exists**
- `localStorage` is empty
- Mount hook
- Assert `localStorage.getItem('docufetch_session_id')` is non-null after mount
- Assert it matches UUID4 pattern: `/^[0-9a-f]{8}-[0-9a-f]{4}-4[0-9a-f]{3}-[89ab][0-9a-f]{3}-[0-9a-f]{12}$/i`

**Test 6: message list is rehydrated from localStorage on mount**
- Seed: `localStorage.setItem('docufetch_messages', JSON.stringify([{ id: '1', role: 'user', text: 'hi' }, { id: '2', role: 'assistant', text: 'hello', sources: [] }]))`
- Mount hook
- Assert `result.current.messages` has 2 entries

**Test 7: message list is capped at 20 entries**
- Seed localStorage with 21 messages (generate 21 items with `role: 'user'`)
- Mount hook
- Assert `result.current.messages.length <= 20`

**Test 8: resetChat generates a fresh session ID and clears message list in localStorage**
- Seed with session ID and 2 messages
- Mount hook
- Call `resetChat()`
- Assert `result.current.messages` is empty
- Assert `localStorage.getItem('docufetch_session_id')` differs from original
- Assert `localStorage.getItem('docufetch_messages')` is `'[]'`

Imports:
```typescript
import { renderHook, act } from '@testing-library/react'
import { vi, describe, it, expect, beforeEach } from 'vitest'
import useChat from '../../src/hooks/useChat'
```

## Coding Guidelines (from CLAUDE.md)

- Every function must have a docstring
- Every file must have a description comment at the top
- Simplicity first

## Acceptance Criteria (from issues.md Issue 8)

- [ ] `sendMessage` adds user message immediately, then assistant after API responds
- [ ] `isLoading` is true during request, false after
- [ ] On API failure, error-role message appended, input re-enabled
- [ ] Session ID persists in localStorage; reloading reuses same ID
- [ ] Message list persists in localStorage, capped at 20
- [ ] `resetChat()` results in new session ID and empty message list in localStorage

## Verification

Run `npm run test` from `/workspace/frontend/` — all useChat tests must pass.

## What to Write in Your Report

Write your completion report to `/workspace/docs/frontend/agent-reports/worker-usechat-report.md` with:
- Status: DONE or FAILED
- Files created
- Test results
- Any deviations from this brief (especially if `src/types/message.ts` was or wasn't found)
