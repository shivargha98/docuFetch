# DocuFetch - Project Brain

## Project - What We Are Building

**docuFetch** is a personal RAG application, it ingests folders, creates embeddings of the files inside the folder and stores them in a local vector store (ChromaDB). A simple web chat UI lets the user ask questions; the system retrieves the top-3 relevant chunks, generates a 2–4 sentence answer via OpenRouter API, and cites the source filename. If no relevant document is found, it says so explicitly.

**NOTE** : We first create the backend, test it out, then we go on to create the frontend

## Tech Stack

- **Backend:** Python, FastAPI
- **Frontend:** React, Tailwind CSS
- **Vector store:** ChromaDB (local)
- **LLM:** Claude (Anthropic)

## File Structure

```
docuFetch/
├── .claude/  <- You are here
├── backend/
│   ├── ingestion/      # folder scanning, chunking, embedding generation
│   ├── ...           # other backend modules (api, retrieval, etc.)
├── frontend/   # React + Tailwind web chat UI
├── requirements.txt
├── docs/
    ├── backend/
        ├── grill_doc_roadmap.md    <- Summary of the plan Q and A.
        ├── prd.md                  <- Product requirements document
        ├── features.md             <- PRD converted to full list of features
        ├── issues.md               <- features converted to issues
        ├── tasks.md                <- written by the agent, tracker for what tasks lie ahead
        ├── tests.md                <- Entire test plan for the backend
        ├── tests/                  <- Entire test suite for the backend
        ├── context.md              <- Memory context for the agents, stores all the important decisions.
        ├── backend_context.md      <-  Memory context for the agents, for backend work
        ├── backend_TASKS.md        <- written by the backend orchestrator agent, on to track the feature/issue builds
        ├── orchestrator_plan       <- written by the orchestrator planner on how we build the backend
        ├── agent-briefs/           <- agent briefs for the worker agents
        ├── agent-reports/          <- agent reports from the worker agents
    ├── frontend/
        ├── grill_doc_roadmap.md    <- Summary of the plan Q and A.
        ├── prd.md                  <- Product requirements document
        ├── features.md             <- PRD converted to full list of features
        ├── issues.md               <- features converted to issues
        ├── tasks.md                <- written by the agent, tracker for what tasks lie ahead
        ├── tests.md                <- Entire test plan for the backend
        ├── tests/                  <- Entire test suite for the backend
        ├── context.md              <- Memory context for the agents, stores all the important decisions.
        ├── backend_context.md      <-  Memory context for the agents, for backend work
        ├── backend_TASKS.md        <- written by the backend orchestrator agent, on to track the feature/issue builds
        ├── orchestrator_plan       <- written by the orchestrator planner on how we build the backend
        ├── agent-briefs/           <- agent briefs for the worker agents
        ├── agent-reports/          <- agent reports from the worker agents
├── README.md
```

## Coding Guidelines

- For every function there must be a docstring explaining what the function actually does
- For every code file created, there must be a description at the top, the description should e about what the code in the file does.
- **Think Before Coding** -> Don't assume. Don't hide confusion. Surface tradeoffs, use a scratchpad to see different possible solutions.
- **Simplicity First** -> Minimum code that solves the problem. Nothing speculative.

    - No features beyond what was asked.
    - No abstractions for single-use code.
    - No "flexibility" or "configurability" that wasn't requested.
    - No error handling for impossible scenarios.
    - If you write 200 lines and it could be 50, rewrite it.
- **Surgical Changes** -> Touch only what you must. Clean up only your own mess. When editing existing code:

    - Don't "improve" adjacent code, comments, or formatting.
    - Don't refactor things that aren't broken.
    - Match existing style, even if you'd do it differently.
    - If you notice unrelated dead code, mention it - don't delete it.

    **When your changes create orphans:**

    - Remove imports/variables/functions that YOUR changes made unused.
    - Don't remove pre-existing dead code unless asked.

**The test:** Every changed line should trace directly to the user's request.
- **Goal-Driven Execution** -> Define success criteria. Loop until verified.

## Python Environment

The `.gitignore` is configured for Python with support for common tooling:

- **Virtual environments:** `.venv`, `venv/`, `env/` (standard `venv` or `uv`)
- **Package managers:** pip, pipenv, poetry, pdm, uv, pixi
- **Linting/typing:** ruff (`.ruff_cache/`), mypy, pytype, pyre
- **Testing:** pytest (`.pytest_cache/`), tox, coverage

Once the project is set up, typical commands will likely follow these patterns:

```bash
# Install dependencies
pip install -r requirements.txt
# or: uv sync / poetry install

# Run tests
pytest

# Run a single test
pytest tests/path/to/test_file.py::test_name

# Lint
ruff check .
ruff format .
```

## Running the Application

Start the backend + frontend with:

```bash
uvicorn server:app --port 8000 --reload --reload-dir backend
```

**Important:** the ingestion scheduler writes to `chroma_db/` and `hash_store.json` in the project root on every run. Plain `--reload` (which watches the whole project root by default) treats those writes as code changes and respawns the worker process — old workers can linger and hold concurrent connections to the same ChromaDB SQLite file, corrupting it (HNSW index files and the SQLite metadata table go out of sync, leading to `doc_count: 0` / "no relevant information" answers despite ingested data). `--reload-dir backend` fixes this by only watching `backend/` (where the actual application code lives), so root-level data files are never treated as reload triggers.

Do **not** use `--reload-exclude "chroma_db/*"` as a fix — on Windows, Click (uvicorn's CLI framework) auto-expands wildcard arguments against the real filesystem before uvicorn parses them, which crashes with `Error: Got unexpected extra argument (chroma_db\chroma.sqlite3)` regardless of shell or quoting. `--reload-dir` avoids the wildcard entirely.

Editing `server.py` itself (the root-level entrypoint shim) won't trigger a reload since it's outside `backend/` — restart manually after touching that file.

If corruption happens again: kill all stray python processes for this project, delete `chroma_db/` and `hash_store.json`, and restart with the command above.

**Update this file as and when the structure gets modified.**
