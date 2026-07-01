# DocuFetch Frontend — Product Requirements Document

## Problem Statement

The docuFetch backend can answer natural language questions over a user's personal document collection, but it is only accessible via a CLI client. A developer or researcher who wants to query their documents must keep a terminal open, cannot see conversation history at a glance, and has no way to observe the current state of the document index (how many files are ingested, when the last scan ran) without typing `/status`. The CLI is functional but creates unnecessary friction for a tool that will be used repeatedly throughout a work session.

## Solution

DocuFetch gets a single-page web chat UI built in React and TypeScript. It renders a familiar chat interface — message list, auto-growing text input, send button — backed by the existing FastAPI backend. The UI handles three concerns beyond basic chat: it gates the input behind a startup health check so the user cannot query an empty index; it shows live ingestion status (doc count, last run time) in a persistent status bar; and it persists session ID and visible message history across page refreshes so an accidental reload does not erase the conversation. Answers that contain inline source citations are re-rendered with the citations stripped from the body and collected into a distinct sources block after the answer text.

## User Stories

1. As a user, I want a chat interface in my browser so that I can query my documents without keeping a terminal open.
2. As a user, I want the chat input to be blocked with a "Preparing your documents…" message on startup so that I do not accidentally query an empty index before ingestion has finished.
3. As a user, I want the startup gate to resolve automatically once ingestion is complete so that I do not have to manually refresh the page.
4. As a user, I want to type a question and press Enter to send it so that the interaction feels like a standard chat app.
5. As a user, I want to press Shift+Enter to add a newline in the input so that I can write multi-sentence questions without accidentally sending them.
6. As a user, I want the text input to grow vertically as I type so that long questions do not scroll off-screen inside the box.
7. As a user, I want to see a typing indicator while the backend is processing my question so that I know the request is in-flight and not stalled.
8. As a user, I want the input to be disabled while a response is pending so that I cannot send a second query before the first completes.
9. As a user, I want to see the answer rendered as plain readable text so that terse 2–4 sentence responses are easy to scan.
10. As a user, I want inline `[source: filename]` markers stripped from the displayed answer so that citations do not interrupt the prose.
11. As a user, I want source filenames displayed as a distinct block below the answer so that I can see which documents were consulted without hunting through the answer text.
12. As a user, I want the chat to scroll to the latest message automatically so that I never have to scroll down manually after a response arrives.
13. As a user, I want my session ID to persist across page refreshes so that the backend continues my conversation history after an accidental reload.
14. As a user, I want my visible message history to persist across page refreshes so that I can still read the conversation I had before the reload.
15. As a user, I want message history capped at 20 messages so that the displayed context stays in sync with what the backend LLM actually sees.
16. As a user, I want a "New chat" button so that I can deliberately start a fresh conversation and clear the persisted history.
17. As a user, I want to see the current document count in a status bar so that I know how many files are indexed.
18. As a user, I want to see the last ingestion timestamp in the status bar so that I know how recently the index was updated.
19. As a user, I want the status bar to refresh automatically every 60 seconds so that the doc count stays current during a long session without me doing anything.
20. As a user, I want to see an inline error message in the chat when a request fails so that I know something went wrong and can retry.
21. As a user, I want the error message to tell me if the server might not be running so that I know where to look if the backend is down.
22. As a user, I want the input to re-enable after a failed request so that I can retry my question without refreshing the page.
23. As a user, I want the app to run entirely in my browser pointing at `http://localhost:8000` so that no additional infrastructure or deployment is needed.

## Implementation Decisions

### Modules

- **api/client.ts** — thin fetch wrapper for the three backend endpoints (`POST /chat`, `GET /health`, `GET /ingest/status`). Backend URL hardcoded as `http://localhost:8000`. No axios.
- **types/api.ts** — TypeScript interfaces for all request and response shapes (see API Contracts below).
- **hooks/useChat.ts** — owns message state, calls `POST /chat`, syncs session ID and message list to `localStorage`.
- **hooks/useHealthGate.ts** — polls `GET /health` every 3 seconds until `initial_ingestion_complete` is `true`; exposes a boolean `ready` flag.
- **hooks/useIngestStatus.ts** — polls `GET /ingest/status` every 60 seconds; exposes doc count and last run time.
- **components/ChatWindow.tsx** — renders the scrollable message list; auto-scrolls to bottom on new messages.
- **components/MessageBubble.tsx** — renders a single message; user bubbles and assistant bubbles are visually distinct; assistant bubbles display the sources block when sources are present.
- **components/TypingIndicator.tsx** — bouncing-dots placeholder rendered as an assistant bubble while a response is in-flight.
- **components/ChatInput.tsx** — auto-growing textarea; Enter sends, Shift+Enter inserts newline; disabled while loading.
- **components/StatusBar.tsx** — displays doc count and last run time from `useIngestStatus`; contains the "New chat" button.
- **utils/sources.ts** — pure function: strips `[source: filename]` patterns from answer text via regex.
- **App.tsx** — root component; composes all of the above; shows startup gate UI when `useHealthGate` is not yet ready.

### Build Tooling

Vite with the React + TypeScript template. `npm` as the package manager. Tailwind CSS for all styling — no component library.

### API Contracts

Key TypeScript types (from prototype):

```typescript
interface ChatRequest {
  query: string;
  session_id: string;
}

interface ChatResponse {
  answer: string;
  sources: string[];
  session_id: string;
}

interface HealthResponse {
  status: string;
  initial_ingestion_complete: boolean;
}

interface IngestStatusResponse {
  doc_count: number;
  last_run_at: string | null;
  last_error: string | null;
}
```

### Session and History Persistence

- Session ID: UUID4 generated on first load, stored in `localStorage`, reused on refresh.
- Message list: stored in `localStorage` as a JSON array, capped at 20 entries. On page load, the stored list is rehydrated into component state before the first render.
- "New chat" clears both the session ID entry and the message list entry from `localStorage` and generates a new UUID4.

### Source Citation Rendering

The backend's `/chat` response contains two sources of citation data that must be reconciled:
- `answer`: plain text that may contain inline `[source: filename]` patterns at arbitrary positions.
- `sources`: a deduplicated `string[]` of filenames.

The frontend regex-strips all `[source: ...]` patterns from `answer` before display, then renders the `sources` array as a labelled block beneath the answer text. The `sources` array is authoritative for the sources block — it is not derived from parsing the answer text.

### Startup Gate Behavior

On mount, `useHealthGate` begins polling `GET /health` every 3 seconds. While `initial_ingestion_complete` is `false` (or the backend is unreachable), the chat input is replaced with a "Preparing your documents…" message and a visual loading indicator. Once `true`, the gate lifts and chat becomes available. If `/health` is unreachable, the hook treats it identically to "still preparing" — no separate error state; polling resumes naturally when the server comes up.

### Error Handling

Network failures or non-2xx responses from `POST /chat` replace the typing indicator bubble with a distinct inline error message. The error message prompts the user to check whether the server is running. Input is re-enabled immediately for retry. No toast or modal — the error lives in the chat stream as an assistant-styled error bubble.

### CORS

`CORSMiddleware` is already configured on the backend at `http://localhost:5173` (the Vite dev server default). No proxy config in `vite.config.ts`.

## Testing Decisions

Good frontend tests call a component or hook with specific inputs and assert on rendered output or returned state — they do not assert on which internal functions were called. The network boundary (`fetch`) is the correct mock seam: mock `fetch` in unit and component tests, call the real backend in e2e tests.

**Modules to test:**

- `utils/sources.ts` — unit tests for the regex strip function covering standard citations, mid-sentence placement, multiple citations, filenames with spaces.
- `hooks/useChat.ts` — hook tests using `renderHook` from RTL; mock `fetch`; verify message list growth, localStorage sync, error state on fetch failure.
- `hooks/useHealthGate.ts` — hook tests; mock `fetch`; verify gate stays closed while `initial_ingestion_complete` is false, opens once true.
- `hooks/useIngestStatus.ts` — hook tests; mock `fetch`; verify doc count and last run time update on poll.
- `components/MessageBubble.tsx` — RTL tests for user vs assistant styling, sources block presence/absence, error bubble rendering.
- `components/ChatInput.tsx` — RTL tests for disabled state, Enter-to-send, Shift+Enter newline.
- `components/StatusBar.tsx` — RTL tests for doc count display, "New chat" click clearing state.
- `App.tsx` (integration) — RTL tests composing all components; mock fetch for health gate flow (blocked → ready) and a full send/receive cycle.
- `e2e/` — Playwright tests against the real running backend: startup gate lifts after ingestion, a question receives an answer, sources block appears, "New chat" clears history.

**Test file location:** plan in `docs/frontend/tests.md`; stub files in `frontend/tests/unit/` and `frontend/tests/e2e/`.

## Out of Scope

- Manual re-ingest button in the UI (remains a CLI operation).
- Authentication or multi-user support.
- Persistent session history across server restarts (backend drops history on restart; this is acceptable).
- Markdown rendering in answers (plain text with `whitespace-pre-wrap` only).
- Page-number or section-header citations (filename only, matching backend output).
- File upload or folder selection UI (ingestion path is configured in the backend `.env`).
- Streaming responses (backend uses a synchronous LangGraph invocation; no SSE or WebSocket).
- Dark mode toggle (Tailwind dark mode not in scope for v1).
- Responsive/mobile layout (desktop browser only for this personal tool).
- Document preview or full-text display.
- Distributed or cloud deployment.

## Further Notes

- The visible message history cap of 20 entries must stay in sync with the backend's own trim of `history[-20:]` in `routes.py`. If the backend cap changes, the frontend cap should change to match.
- The `[source: filename]` regex should be written to handle filenames containing spaces, hyphens, and dots, since those are common in the document collections this tool targets.
- Vite's default port is `5173`; the backend CORS config is pinned to that origin. If the port is changed, the backend `allow_origins` list must be updated to match.
- The `GET /health` polling interval (3s) and `GET /ingest/status` polling interval (60s) are intentionally different: health polling is short-lived (only active until ingestion completes) while status polling runs for the lifetime of the session.
