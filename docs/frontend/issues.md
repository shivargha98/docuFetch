# Issues

_Generated from: docs/frontend/features.md_

---

## Issue 1: Vite + React + TypeScript + Tailwind Scaffold

**What to build:**
Bootstrap the `frontend/` directory as a Vite React + TypeScript project using `npm`. Install and configure Tailwind CSS. Establish the directory structure (`src/api/`, `src/types/`, `src/hooks/`, `src/components/`, `src/utils/`, `tests/unit/`, `tests/e2e/`) with placeholder files so subsequent issues can be worked independently. The dev server should start and serve a blank page with no errors.

**Acceptance criteria:**
- [ ] `npm run dev` starts the Vite dev server at `http://localhost:5173` with no console errors.
- [ ] `npm run build` produces a production build with no TypeScript or Tailwind compilation errors.
- [ ] Tailwind utility classes applied to a test element in `App.tsx` render correctly in the browser.
- [ ] The directory structure (`src/api/`, `src/types/`, `src/hooks/`, `src/components/`, `src/utils/`, `tests/unit/`, `tests/e2e/`) exists with index or placeholder files in each.

**Blocked by:** None — can start immediately

---

## Issue 2: API Types and Client

**What to build:**
Create `src/types/api.ts` exporting `ChatRequest`, `ChatResponse`, `HealthResponse`, and `IngestStatusResponse` interfaces that match the FastAPI backend contract exactly. Create `src/api/client.ts` implementing `postChat`, `getHealth`, and `getIngestStatus` as thin `fetch` wrappers over `http://localhost:8000`. Non-2xx responses and network errors must throw so callers can catch them.

**Acceptance criteria:**
- [ ] `postChat(query, sessionId)` sends `POST /chat` with `{ query, session_id }` body and returns a parsed `ChatResponse`.
- [ ] `getHealth()` sends `GET /health` and returns a parsed `HealthResponse`.
- [ ] `getIngestStatus()` sends `GET /ingest/status` and returns a parsed `IngestStatusResponse`.
- [ ] A non-2xx HTTP status causes the relevant function to throw an `Error`; a network failure also throws.
- [ ] The project compiles with no TypeScript errors when all hooks import from `types/api.ts` and `api/client.ts`.

**Blocked by:** Issue 1

---

## Issue 3: Source Citation Strip Utility

**What to build:**
Create `src/utils/sources.ts` exporting a pure `stripCitations(text: string): string` function that removes all `[source: filename]` patterns from the input string and collapses any double spaces left behind. This is the only place in the codebase that transforms answer text before display.

**Acceptance criteria:**
- [ ] `stripCitations("Some text [source: report.pdf] here")` returns `"Some text  here"` with no leftover brackets.
- [ ] All `[source: ...]` occurrences are removed when multiple citations appear at arbitrary positions in one string.
- [ ] Filenames with spaces (`[source: my notes.txt]`), hyphens, and dots are matched and removed.
- [ ] A string with no citation patterns is returned unchanged.
- [ ] The original string is not mutated.

**Blocked by:** Issue 1

---

## Issue 4: useHealthGate Hook and Startup Gate UI

**What to build:**
Create `src/hooks/useHealthGate.ts` that polls `GET /health` every 3 seconds via the API client. It exposes a `ready` boolean, starts as `false`, flips to `true` once `initial_ingestion_complete` is `true`, and stops polling. Update `App.tsx` to show a "Preparing your documents…" message with the chat input area hidden when `ready` is `false`. This makes the startup gate demoable end-to-end against the real backend.

**Acceptance criteria:**
- [ ] On load, the app displays "Preparing your documents…" and no chat input is interactive.
- [ ] Once the backend returns `initial_ingestion_complete: true`, the gate message disappears and the chat area becomes visible.
- [ ] The gate does not revert to the preparing state after it has resolved.
- [ ] A failed `/health` poll (backend unreachable or non-2xx) keeps `ready` as `false` without crashing or showing a separate error view.
- [ ] The polling interval is cleared when the component unmounts.

**Blocked by:** Issue 2

---

## Issue 5: useIngestStatus Hook and StatusBar Component

**What to build:**
Create `src/hooks/useIngestStatus.ts` that polls `GET /ingest/status` every 60 seconds and exposes `docCount` and `lastRunAt`. Create `src/components/StatusBar.tsx` that displays these values and a "New chat" button. Wire the `StatusBar` into `App.tsx` so it is always visible (above or below the startup gate). The "New chat" action will be fully wired in Issue 9; here it only needs to accept and call an `onNewChat` prop.

**Acceptance criteria:**
- [ ] `StatusBar` renders the doc count from the most recent `/ingest/status` poll.
- [ ] `StatusBar` renders the last ingestion time as a readable string, or "Never" when `last_run_at` is null.
- [ ] `StatusBar` is visible on the page regardless of whether the startup gate is showing.
- [ ] Clicking "New chat" calls the `onNewChat` prop exactly once.
- [ ] A failed poll leaves the previously-fetched values unchanged; the component does not reset to zero.

**Blocked by:** Issue 2

---

## Issue 6: MessageBubble, TypingIndicator, and ChatWindow Components

**What to build:**
Create `src/components/MessageBubble.tsx`, `src/components/TypingIndicator.tsx`, and `src/components/ChatWindow.tsx`. `MessageBubble` applies `stripCitations` to assistant answer text, renders a sources block when `sources` is non-empty, distinguishes user/assistant/error roles visually, and mirrors `TypingIndicator`'s assistant-side bubble style for the error variant. `TypingIndicator` renders three animated dots as an assistant bubble. `ChatWindow` renders the message list and a `TypingIndicator` when `isLoading` is true, and scrolls to the bottom on list updates.

**Acceptance criteria:**
- [ ] A user message renders right-aligned (or equivalent user-side styling); an assistant message renders left-aligned (or equivalent assistant-side styling).
- [ ] An assistant message with `[source: notes.pdf]` in its text displays the text without the citation marker and shows "notes.pdf" in a sources block below the answer.
- [ ] An assistant message with an empty `sources` array shows no sources block.
- [ ] An error-role message renders in a distinct error style.
- [ ] `ChatWindow` with `isLoading={true}` renders a `TypingIndicator` after the last message bubble.
- [ ] `ChatWindow` scrolls to the bottom when a new message is appended.

**Blocked by:** Issue 1, Issue 3

---

## Issue 7: ChatInput Component

**What to build:**
Create `src/components/ChatInput.tsx` — an auto-growing textarea and send button. Enter (without Shift) calls `onSend` with the trimmed value and clears the field. Shift+Enter inserts a newline. When `isLoading` is `true`, both the textarea and the send button are disabled and visually muted. Submitting an empty or whitespace-only string is a no-op.

**Acceptance criteria:**
- [ ] Pressing Enter with "Hello" in the field calls `onSend("Hello")` and clears the input.
- [ ] Pressing Shift+Enter inserts a newline character and does not call `onSend`.
- [ ] When `isLoading` is `true`, the textarea and send button are both disabled (not interactable).
- [ ] The textarea height increases to accommodate content beyond one line without showing a scrollbar.
- [ ] Pressing Enter with only whitespace in the field does not call `onSend`.

**Blocked by:** Issue 1

---

## Issue 8: useChat Hook — Send, Receive, Persistence, and Error Handling

**What to build:**
Create `src/hooks/useChat.ts`. It initialises session ID from `localStorage` (generating a new UUID4 if absent) and rehydrates the message list from `localStorage` (capped at 20). `sendMessage(query)` appends a user message, sets `isLoading`, calls `postChat`, appends the assistant response on success, or sets an error entry in the message list on failure. `resetChat()` generates a fresh session ID, clears the message list, and updates `localStorage` for both.

**Acceptance criteria:**
- [ ] Calling `sendMessage("What is X?")` adds a user message immediately, then adds the assistant's answer once the API responds.
- [ ] `isLoading` is `true` from the start of `sendMessage` until the response (or error) arrives, then `false`.
- [ ] On API failure, an error message entry is appended to the message list and the input is re-enabled.
- [ ] Session ID persists in `localStorage`; reloading the page reuses the same ID without generating a new one.
- [ ] The message list persists in `localStorage` across reloads, capped at 20 entries.
- [ ] `resetChat()` results in a new session ID and an empty message list, both updated in `localStorage`.

**Blocked by:** Issue 2, Issue 3

---

## Issue 9: App Root Composition — Full Integration

**What to build:**
Wire all hooks and components into `App.tsx` to produce the complete single-page layout. `useHealthGate` controls the startup gate. `useChat` drives the message list and send flow. `useIngestStatus` feeds `StatusBar`. `StatusBar`'s "New chat" button calls `useChat`'s `resetChat`. `ChatWindow`, `ChatInput`, and `StatusBar` are composed into a layout where the status bar is always visible, the startup gate occupies the main area while not ready, and the chat (window + input) occupies the main area once ready.

**Acceptance criteria:**
- [ ] On load with the backend running but ingestion incomplete, the user sees "Preparing your documents…" and cannot type a message.
- [ ] Once ingestion completes, the chat input becomes active and the preparing message is gone.
- [ ] Typing a question and pressing Enter sends it to the backend; the answer and sources appear in the chat window.
- [ ] While the response is pending, the typing indicator appears and the input is disabled.
- [ ] On a failed request, an inline error message appears in the chat and the input re-enables for retry.
- [ ] Clicking "New chat" clears the visible message history and the next message starts a fresh backend session.
- [ ] The status bar showing doc count and last ingestion time is visible at all times.

**Blocked by:** Issue 4, Issue 5, Issue 6, Issue 7, Issue 8
