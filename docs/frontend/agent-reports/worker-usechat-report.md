### Status
COMPLETE

### What I Built

**`/workspace/frontend/src/hooks/useChat.ts`** — 130 lines
- Defines the `Message` and `UseChatReturn` interfaces inline (no `src/types/message.ts` was found)
- Implements `initSessionId`, `initMessages`, and `persistMessages` helpers, each with docstrings
- Exports `useChat` default hook managing `sessionId`, `messages`, and `isLoading` state
- `sendMessage` appends the user message immediately (with localStorage persist), calls `postChat`, then appends assistant or error message in a finally block that resets `isLoading`
- `resetChat` generates a new `crypto.randomUUID()`, updates both state and localStorage

**`/workspace/frontend/tests/unit/useChat.test.ts`** — 122 lines
- 8 Vitest test cases using `renderHook` + `act` from `@testing-library/react`
- Mocks `fetch` via `vi.stubGlobal`; uses jsdom's `localStorage` directly
- `beforeEach` clears localStorage and restores all mocks

### Test Results

| Test | Result |
|---|---|
| Test 1: sendMessage appends user then assistant message | PASS |
| Test 2: isLoading true during request, false after | PASS |
| Test 3: API failure appends error entry, resets isLoading | PASS |
| Test 4: session ID read from localStorage when present | PASS |
| Test 5: new UUID4 generated and saved when no session ID exists | PASS |
| Test 6: message list rehydrated from localStorage on mount | PASS |
| Test 7: message list capped at 20 entries | PASS |
| Test 8: resetChat clears messages and rotates session ID | PASS |

4 pre-existing tests in `ChatWindow.test.tsx` fail with `scrollIntoView is not a function` — these are unrelated to this feature and were failing before my changes.

### What the Orchestrator Should Know

- `src/types/message.ts` does not exist; the `Message` interface is defined locally in `useChat.ts`. If a future worker (e.g. MessageBubble) expects to import `Message` from a shared types file, that file still needs to be created.
- The 4 `ChatWindow.test.tsx` failures are a jsdom limitation (`scrollIntoView` is not implemented). The ChatWindow component should mock or guard `scrollIntoView` in its tests, or mock it in the test setup. This is out of scope for this brief.

### What the Next Worker Needs

The hook exports:
```typescript
export default function useChat(): UseChatReturn
// where UseChatReturn = { messages: Message[], isLoading: boolean, sendMessage: (query: string) => Promise<void>, resetChat: () => void }
```
from `/workspace/frontend/src/hooks/useChat.ts`.

The `Message` type (`id`, `role: 'user'|'assistant'|'error'`, `text`, `sources?`) is defined locally in that file — any component consuming it should either import the hook and infer the type, or the orchestrator should extract `Message` to `src/types/message.ts` for sharing.

### Blockers

None.
