# PM Loop Context

**Scope:** frontend
**Feature:** DocuFetch web chat UI — React + TypeScript + Tailwind CSS SPA
**Date:** 2026-07-01

## Important Decisions (from grill_doc_roadmap.md)

- Build tooling: Vite + React + TypeScript
- Styling: Plain Tailwind CSS — no component library
- API client: Native fetch, wrapped in src/api/client.ts — no axios
- Session ID: Persisted in localStorage (survives refresh)
- Message history: Persisted in localStorage, capped at 20 messages
- Answer rendering: Plain text, whitespace-pre-wrap — no react-markdown
- Source citations: Regex-strip [source: filename] from answer text, render sources array as distinct block after the answer
- Loading state: Bouncing-dots typing indicator + disabled input during /chat call
- Startup gate: Poll GET /health every 3s until initial_ingestion_complete; block input until then
- Error handling: Inline error message in chat stream on network/500 failure
- CORS: CORSMiddleware already added to backend for http://localhost:5173
- Status bar: Poll GET /ingest/status every 60s; "New chat" button in status bar
- Backend URL: Hardcoded http://localhost:8000 in src/api/client.ts
- Package manager: npm
- Testing: Vitest + React Testing Library (component/unit), Playwright (e2e against real backend)
- Test files: plan in docs/frontend/tests.md, stubs in frontend/tests/

## Key Outputs by Stage

### PRD
[Will be populated after Step 2]

### Features
[Will be populated after Step 3]

### Issues
[Will be populated after Step 4]

### Test Suite
[Will be populated after Step 5]

## Open Questions / Risks

- Backend must be running for Playwright e2e tests — test setup should document this prerequisite
- localStorage cap at 20 messages must stay in sync with backend session history trim logic
- [source: filename] regex pattern must be robust enough to handle filenames with spaces or special characters
