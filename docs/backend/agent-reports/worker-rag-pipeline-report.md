### Status
COMPLETE

### What I Built

**Files created:**
- `/workspace/backend/graph/state.py` — 22 lines. `DocuFetchState` TypedDict with `total=False` so all fields are optional.
- `/workspace/backend/graph/nodes.py` — 100 lines. Four factory functions: `make_retrieve_node`, `make_relevance_check_node`, `make_generate_node`, `make_no_results_node`. Defines `NO_RESULTS_MESSAGE` constant.
- `/workspace/backend/graph/graph.py` — 47 lines. `build_graph(hybrid_retriever, llm)` assembles and compiles the StateGraph with conditional edge routing.

**Files modified:**
- `/workspace/backend/api/server.py` — 93 lines (was 74). Three additions:
  - Addition A: imported `ChatAnthropic`, `BM25Index`, `HybridRetriever`, `build_graph` near top
  - Addition B: in `lifespan`, initializes `app.state.hybrid_retriever` and `app.state.graph` before scheduler task
  - Addition C: in `_ingestion_scheduler`, calls `rebuild_bm25` after each `run_ingestion` call (both startup and loop)

### Test Results

All 5 verification tests run with `python3 scratch_graph.py`:

- Test 1 — `DocuFetchState` partial instantiation with `query` only: **PASS**
- Test 2 — `no_results` node returns correct AIMessage and empty sources list: **PASS**
- Test 3 — `relevance_check` sets `is_relevant=False` without LLM call when chunks empty: **PASS**
- Test 4 — `build_graph` compiles without error using mock deps: **PASS**
- Test 5 — graph routes to `no_results` path when retriever returns empty list: **PASS**

```
Test 1 passed: partial instantiation
Test 2 passed: no_results node
Test 3 passed: relevance_check skips LLM when chunks empty
Test 4 passed: graph compiles
Test 5 passed: graph routes to no_results with empty chunks
All graph tests passed
```

### What the Orchestrator Should Know

- The `backend/graph/__init__.py` already existed (empty) so no additional `__init__` file was needed.
- `ChatAnthropic` is typed as the `llm` parameter in `build_graph` but the function accepts any object with an `.invoke()` method — tests use `MagicMock` without issue.
- The `generate` node stores `HumanMessage(content=query)` (plain query, not the full prompt) in `messages` history, which keeps conversation history compact and readable.

### What the Next Worker Needs

**Issue 8 (POST /chat route) integration guide:**

- **How to invoke the graph:**
  ```python
  result = request.app.state.graph.invoke({"query": query_str, "messages": session_messages})
  ```
- **What the returned state contains:**
  - `result["messages"][-1].content` — the LLM answer string (or the no-results message)
  - `result["sources"]` — list of unique source filenames cited (empty list if no results)
  - `result["messages"]` — full updated conversation history to save back to the session
- **Where the graph lives at runtime:** `request.app.state.graph`
- **Where the retriever lives at runtime:** `request.app.state.hybrid_retriever`
- **Sessions dict:** `request.app.state.sessions` — a dict keyed by session ID, store `result["messages"]` there and pass it back on the next turn.

### Blockers

None.
