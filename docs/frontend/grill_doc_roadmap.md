# DocuFetch Frontend — Grill Session Roadmap

All architectural decisions for the frontend, resolved in order of dependency. Reference material: `docs/backend/prd.md`, `docs/backend/grill_doc_roadmap.md`, and direct inspection of `backend/api/routes.py` and `backend/graph/nodes.py`.

---

## The App in One Paragraph

The frontend is a single-page React + TypeScript chat UI (Vite, Tailwind CSS) that talks directly to the existing FastAPI backend at `http://localhost:8000`. It shows one chat screen with a persistent status bar (doc count, last ingestion time, polled every 60s). On load it blocks the chat input behind a `/health` poll until `initial_ingestion_complete` is true, then lets the user converse with the RAG pipeline via `POST /chat`. Session ID and visible message history persist in `localStorage` so refreshes don't lose context; a "New chat" button lets the user deliberately reset both. Answers are rendered as plain text with inline `[source: filename]` citations stripped out and re-rendered as a distinct sources block after the answer. No component library — plain Tailwind utility classes throughout.

---

## Decision Log

### Q1 — Scope of the frontend v1
**Decision: Chat + status bar (Option B)**

A chat screen (message list + input) plus a small persistent status bar showing doc count and last ingestion time, read from `GET /ingest/status`. No manual "re-ingest now" button — that stays a CLI/debug operation, not user-facing UI.

---

### Q2 — Build tooling
**Decision: Vite + React (Option A)**

No SSR/routing needs for a single-page local tool. Vite gives fast HMR and minimal config.

---

### Q3 — TypeScript or JavaScript
**Decision: TypeScript (Option A)**

Typed request/response shapes for `/chat`, `/health`, `/ingest/status` catch backend contract drift at compile time.

---

### Q4 — Component styling approach
**Decision: Plain Tailwind, no component library (Option A)**

The UI is message list, message bubble, textarea, send button, status bar — no modals/menus/dropdowns that would justify shadcn/ui or Headless UI.

---

### Q5 — API client
**Decision: Native `fetch` (Option A)**

Three simple JSON endpoints, no auth/interceptors — wrapped in a small `src/api/client.ts` helper. No axios.

---

### Q6 — Session ID persistence
**Decision: `localStorage` (Option B)**

A page refresh is incidental, not an intent to reset — session ID survives refresh and tab close/reopen. If the backend has since restarted and forgotten that session_id, `sessions.get(id, [])` on the backend already defaults to empty history with no special-casing needed.

---

### Q7 — Message history display persistence
**Decision: Persist message list in `localStorage` (Option A)**

The backend has no `GET` history endpoint, so the frontend must store the visible message list itself, capped at 20 messages (matching the backend's cap) to keep it in sync with what the LLM actually sees as context.

---

### Q8 — Answer rendering
**Decision: Plain text, no Markdown (Option A)**

PRD answers are terse 2–4 sentence prose, not structured content. Line breaks preserved via `whitespace-pre-wrap`. No `react-markdown` dependency.

---

### Q9 — Displaying sources
**Decision: Strip inline citations, render sources block after the answer (Option B)**

Confirmed via `backend/graph/nodes.py`: the LLM's answer text already contains inline `[source: filename]` citations that can appear mid-sentence (not guaranteed to land at the end), and the API separately returns a deduplicated `sources: string[]` array. Per explicit user requirement — sources must always appear after the full answer, not scattered inline — the frontend regex-strips `[source: filename]` patterns from the displayed answer text, then renders the `sources` array as a distinct block underneath once the full answer has rendered.

---

### Q10 — Loading/typing indicator
**Decision: Typing indicator + disabled input (Option A)**

`/chat` is a single blocking call (no streaming — LangGraph invokes synchronously, potentially 2 LLM calls). A bouncing-dots placeholder bubble shows while waiting; the input box is disabled until the response arrives.

---

### Q11 — Startup gating on `/health`
**Decision: Block chat until ingestion complete (Option A)**

Poll `GET /health` every ~3 seconds while `initial_ingestion_complete` is false, showing a "Preparing your documents…" state and a disabled input. Stop polling once true. This directly prevents querying against a partially-empty index — the exact false-negative failure mode hit during backend debugging.

---

### Q12 — Backend unreachable / request failure handling
**Decision: Inline error message in the chat stream (Option A)**

Network failures or 500s during a `/chat` call replace the typing indicator with a distinct inline error message (e.g. "⚠ Something went wrong — is the server running?"), and re-enable the input for retry. If `/health` itself is unreachable during the Q11 startup gate, it's treated identically to "still preparing" — no separate error state, since polling will naturally recover once the server comes up.

---

### Q13 — Dev-server/backend connectivity
**Decision: `CORSMiddleware` on the backend (Option A)**

Vite's dev server (default port `5173`) and FastAPI (`8000`) are cross-origin. Rather than a Vite dev-only proxy, `CORSMiddleware` is added to the FastAPI app (allowing `http://localhost:5173`) — a small, one-time backend change. The frontend always calls the absolute backend URL, identically in dev and any future build, with no proxy config to keep in sync separately.

**Backend change:** `CORSMiddleware` added to `backend/api/server.py` (`allow_origins=["http://localhost:5173"]`) — done.

---

### Q14 — Frontend testing framework
**Decision: Vitest + React Testing Library + Playwright (Option B)**

- **Vitest + RTL** for component/unit tests, mocking only the network boundary (`fetch`) — consistent with the backend's "don't mock internals" philosophy applied to the frontend's own external boundary.
- **Playwright** for a small number of true end-to-end tests run against the real running backend.
- Test suite lives under `docs/frontend/tests/` (plan) and `frontend/tests/` (actual test code), mirroring the backend's `docs/backend/tests.md` + `docs/backend/tests/` split.

---

### Q15 — Message input UX
**Decision: Auto-growing textarea, Enter to send, Shift+Enter for newline (Option A)**

Standard chat-app convention; allows multi-sentence questions without the input scrolling off-screen.

---

### Q16 — "New conversation" control
**Decision: "New chat" button in the status bar (Option A)**

Generates a fresh UUID session ID and clears the persisted message list (and its `localStorage` entries). The only way to deliberately reset context now that session ID and history persist indefinitely.

---

### Q17 — Backend URL configuration
**Decision: Hardcoded constant (Option A)**

`http://localhost:8000` hardcoded in `src/api/client.ts`. No `.env`/Vite env var — this is a personal, single-machine tool where the backend URL will never vary across environments.

---

### Q18 — Package manager
**Decision: npm (Option A)**

Ships with Node, no extra install step; no monorepo/workspace need to justify pnpm or yarn.

---

### Q19 — Status bar refresh behavior
**Decision: Poll `/ingest/status` every 60 seconds (Option A)**

Matches the backend's own ingestion scheduler interval, keeping doc count / last run time live during a session without over-polling.

---

## Architecture Summary

### Phases

**P1 — Scaffold**
- `npm create vite@latest` (React + TypeScript template) in `frontend/`
- Tailwind CSS setup
- Add `CORSMiddleware` to `backend/api/server.py` (allow `http://localhost:5173`)

**P2 — Core chat**
- `ChatWindow`, `MessageBubble`, `ChatInput` components
- `useChat` hook: message state, `POST /chat` integration, `localStorage` sync for session_id + message list (capped at 20)
- Answer text rendering with `[source: filename]` regex-stripped, sources block rendered after

**P3 — Gating & status**
- `useHealthGate` hook: polls `GET /health` every 3s until `initial_ingestion_complete`, blocks input until then
- `StatusBar` component: polls `GET /ingest/status` every 60s (doc count, last run time), includes "New chat" button

**P4 — Polish**
- Typing indicator (bouncing dots) while awaiting `/chat` response
- Inline error message + retry on request failure
- Auto-scroll to bottom on new messages

**P5 — Testing**
- Vitest + RTL component tests (network boundary mocked)
- Playwright end-to-end tests against the running backend
- Test plan documented in `docs/frontend/tests.md`, suite in `frontend/tests/`

### Key Types (frontend)
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

### File Structure (Frontend)
```
docuFetch/
├── frontend/
│   ├── src/
│   │   ├── api/
│   │   │   └── client.ts          # fetch wrapper for /chat, /health, /ingest/status
│   │   ├── components/
│   │   │   ├── ChatWindow.tsx
│   │   │   ├── MessageBubble.tsx
│   │   │   ├── TypingIndicator.tsx
│   │   │   ├── ChatInput.tsx
│   │   │   └── StatusBar.tsx
│   │   ├── hooks/
│   │   │   ├── useChat.ts         # message state, send logic, localStorage sync
│   │   │   ├── useHealthGate.ts   # polls /health until ingestion complete
│   │   │   └── useIngestStatus.ts # polls /ingest/status every 60s
│   │   ├── types/
│   │   │   └── api.ts             # ChatRequest, ChatResponse, HealthResponse, IngestStatusResponse
│   │   ├── utils/
│   │   │   └── sources.ts         # strip [source: ...] regex
│   │   ├── App.tsx
│   │   └── main.tsx
│   ├── tests/
│   │   ├── unit/                  # Vitest + RTL component tests
│   │   └── e2e/                   # Playwright tests against running backend
│   ├── index.html
│   ├── package.json
│   ├── tailwind.config.ts
│   ├── vite.config.ts
│   └── tsconfig.json
```

### Required Backend Change
- ~~Add `CORSMiddleware` to `backend/api/server.py` allowing origin `http://localhost:5173`~~ — done, needed before frontend dev work can call the API at all (Q13).
