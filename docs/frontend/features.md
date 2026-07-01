# Features

_Generated from: docs/frontend/prd.md_

## API

### Feature: Backend API Client

A thin `fetch`-based module (`src/api/client.ts`) that wraps all three backend endpoints — `POST /chat`, `GET /health`, and `GET /ingest/status` — with the backend URL hardcoded as `http://localhost:8000`. It is the only place in the frontend that constructs HTTP requests; all hooks call through it.

**Acceptance criteria:**
- [ ] `postChat(query, sessionId)` sends a `POST` to `/chat` with the correct JSON body and returns a parsed `ChatResponse`.
- [ ] `getHealth()` sends a `GET` to `/health` and returns a parsed `HealthResponse`.
- [ ] `getIngestStatus()` sends a `GET` to `/ingest/status` and returns a parsed `IngestStatusResponse`.
- [ ] A non-2xx response or network error causes the relevant function to throw an error that the caller can catch.
- [ ] No axios or third-party HTTP library is imported — native `fetch` only.

---

### Feature: API Type Contracts

A `src/types/api.ts` module that exports TypeScript interfaces for every request and response shape exchanged with the backend. These types are the compile-time contract between the frontend and the FastAPI routes.

**Acceptance criteria:**
- [ ] `ChatRequest`, `ChatResponse`, `HealthResponse`, and `IngestStatusResponse` are all exported from `types/api.ts`.
- [ ] Field names and optionality match the backend contract: `sources` is `string[]`, `last_run_at` is `string | null`, `initial_ingestion_complete` is `boolean`.
- [ ] The project compiles with no TypeScript errors when `api/client.ts` and all hooks import from `types/api.ts`.

---

## Utils

### Feature: Source Citation Strip

A pure function in `src/utils/sources.ts` that accepts an answer string and returns it with all `[source: filename]` patterns removed, collapsing any resulting extra whitespace. This is the sole transformation applied to answer text before display.

**Acceptance criteria:**
- [ ] A string with a single `[source: report.pdf]` pattern returns the string with that pattern removed and no leading/trailing whitespace artifact.
- [ ] A string with multiple citations scattered at arbitrary positions (mid-sentence, end) returns the string with all of them removed.
- [ ] Filenames containing spaces, hyphens, and dots are matched and stripped correctly.
- [ ] A string with no `[source: ...]` pattern is returned unchanged.
- [ ] The function has no side effects and does not mutate its input.

---

## Hooks

### Feature: useChat — Message State and Send

A `src/hooks/useChat.ts` hook that owns the message list, sends queries to `POST /chat` via the API client, appends responses to the list, syncs session ID and message list to `localStorage`, and exposes an error state when requests fail. The message list is capped at 20 entries to stay in sync with the backend session trim.

**Acceptance criteria:**
- [ ] Calling `sendMessage(query)` appends a user message to the list, then appends the assistant response once the request resolves.
- [ ] A typing/loading state is `true` from the moment `sendMessage` is called until the response (or error) arrives.
- [ ] On `fetch` failure or non-2xx response, `error` is set to a non-null string and the message list receives an error bubble entry instead of an assistant message.
- [ ] Session ID is read from `localStorage` on initialisation; a new UUID4 is generated and persisted if none exists.
- [ ] The message list is persisted to `localStorage` after every update and rehydrated from it on mount, capped at 20 entries.
- [ ] `resetChat()` clears the message list and generates a fresh session ID, updating `localStorage` for both.

---

### Feature: useHealthGate — Startup Ingestion Gate

A `src/hooks/useHealthGate.ts` hook that polls `GET /health` every 3 seconds. It exposes a `ready` boolean that starts as `false` and becomes `true` exactly once — when a poll response returns `initial_ingestion_complete: true`. Polling stops after that. If the backend is unreachable, the hook stays in the not-ready state without a separate error.

**Acceptance criteria:**
- [ ] `ready` is `false` on mount and while `initial_ingestion_complete` is `false`.
- [ ] `ready` becomes `true` on the first poll that returns `initial_ingestion_complete: true` and does not revert.
- [ ] Polling stops after `ready` becomes `true` — no further `GET /health` calls are made.
- [ ] A failed `GET /health` call (network error or non-2xx) is treated as "still preparing": `ready` stays `false` and the next poll fires at the normal interval.
- [ ] The polling interval clears on component unmount to prevent memory leaks.

---

### Feature: useIngestStatus — Live Ingestion Polling

A `src/hooks/useIngestStatus.ts` hook that polls `GET /ingest/status` every 60 seconds and exposes `docCount` and `lastRunAt`. The poll interval matches the backend's own ingestion scheduler.

**Acceptance criteria:**
- [ ] `docCount` and `lastRunAt` are populated from the first successful poll response.
- [ ] Values update automatically after each subsequent 60-second poll without user interaction.
- [ ] A failed poll leaves the previously-fetched values unchanged (no reset to zero or null).
- [ ] The polling interval clears on component unmount.

---

## Components

### Feature: ChatWindow

A `src/components/ChatWindow.tsx` component that renders the scrollable list of messages. It receives the message list and a loading flag, renders a `MessageBubble` per message and a `TypingIndicator` while loading, and scrolls to the bottom automatically whenever a new message is appended.

**Acceptance criteria:**
- [ ] Each item in the message list renders as a `MessageBubble`.
- [ ] When `isLoading` is `true`, a `TypingIndicator` appears after the last message bubble.
- [ ] The scroll position moves to the bottom whenever the message list length increases or `isLoading` changes to `true`.
- [ ] An empty message list renders without errors — no crash on zero items.

---

### Feature: MessageBubble

A `src/components/MessageBubble.tsx` component that renders a single chat message. User messages and assistant messages are visually distinct (different alignment or colour). Assistant messages apply the citation strip to the answer text and render the sources block below the answer when `sources` is non-empty. Error messages render in a distinct error style.

**Acceptance criteria:**
- [ ] A message with `role: "user"` renders with user-side styling; a message with `role: "assistant"` renders with assistant-side styling.
- [ ] The displayed answer text has all `[source: ...]` patterns removed before rendering.
- [ ] When `sources` is a non-empty array, a labelled sources block appears below the answer text listing each filename.
- [ ] When `sources` is empty or absent, no sources block is rendered.
- [ ] A message with `role: "error"` renders in a visually distinct error style.

---

### Feature: TypingIndicator

A `src/components/TypingIndicator.tsx` component that renders a bouncing-dots animation styled as an assistant message bubble. It is shown by `ChatWindow` while a `POST /chat` request is in-flight.

**Acceptance criteria:**
- [ ] The component renders as an assistant-side bubble (matching `MessageBubble` assistant styling).
- [ ] Three animated dots are present in the rendered output.
- [ ] The component accepts no required props — it is entirely self-contained.

---

### Feature: ChatInput

A `src/components/ChatInput.tsx` component that renders an auto-growing textarea. Pressing Enter (without Shift) submits the current value and clears the input. Pressing Shift+Enter inserts a newline. The textarea is disabled and visually muted while `isLoading` is `true`.

**Acceptance criteria:**
- [ ] Pressing Enter with text in the input calls `onSend` with the trimmed value and clears the field.
- [ ] Pressing Shift+Enter inserts a newline into the input without triggering `onSend`.
- [ ] When `isLoading` is `true`, the textarea and send button are both disabled.
- [ ] The textarea grows in height as content exceeds one line and does not show a scrollbar while content fits.
- [ ] Submitting with an empty or whitespace-only string does not call `onSend`.

---

### Feature: StatusBar

A `src/components/StatusBar.tsx` component that displays the current document count and last ingestion time sourced from `useIngestStatus`, and contains the "New chat" button. Clicking "New chat" calls the reset handler passed as a prop.

**Acceptance criteria:**
- [ ] The rendered bar displays the `docCount` value.
- [ ] The rendered bar displays the `lastRunAt` value (formatted as a readable string, or "Never" if null).
- [ ] Clicking "New chat" calls the `onNewChat` prop handler exactly once.
- [ ] The component renders without errors when `docCount` is `0` and `lastRunAt` is `null`.

---

## App

### Feature: App Root and Startup Gate

`src/App.tsx` composes all hooks and components into the single-page layout. While `useHealthGate` reports `ready: false`, it renders a startup gate view ("Preparing your documents…") with the chat input disabled. Once ready, the full chat layout is shown. The "New chat" action wired from `StatusBar` delegates to `useChat`'s `resetChat`.

**Acceptance criteria:**
- [ ] On initial load, the startup gate message is visible and the chat input is not interactive.
- [ ] Once `useHealthGate` returns `ready: true`, the startup gate message disappears and the chat input becomes active.
- [ ] Sending a message via `ChatInput` calls `useChat`'s `sendMessage` and the response appears in `ChatWindow`.
- [ ] Clicking "New chat" in `StatusBar` clears the visible message list and resets the session (delegating to `resetChat`).
- [ ] `StatusBar` is always visible — it is not hidden behind the startup gate.
