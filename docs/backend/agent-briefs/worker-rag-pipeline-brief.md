# Worker Brief — Issue 7: LangGraph RAG Pipeline (Retrieve → Relevance Check → Generate / No-Results)

**Working directory:** `/workspace`
**Issue:** Issue 7 (from docs/backend/issues.md)
**Your report goes to:** `docs/backend/agent-reports/worker-rag-pipeline-report.md`

---

## Context

Issues 2–6 built ingestion, storage, and retrieval. You are building the LangGraph-based RAG pipeline that sits on top of all of it — and wiring the `HybridRetriever` into the server so routes can use it.

Files you own:
- `backend/graph/state.py` (new)
- `backend/graph/nodes.py` (new)
- `backend/graph/graph.py` (new)
- `backend/api/server.py` (modify — add HybridRetriever + LangGraph graph init + BM25 rebuild after ingestion)

Do NOT touch `loaders.py`, `chunkers.py`, `embedder.py`, `store.py`, `bm25.py`, `hybrid.py`, `routes.py`, or `pipeline.py` — another worker is modifying some of those concurrently.

---

## pip Environment

```bash
pip install -r /workspace/requirements.txt --user --break-system-packages
```
Use `python3 -m pytest`. PATH includes `/home/claude/.local/bin`.

---

## Existing Interfaces You Build On

**`backend/retrieval/hybrid.py`** — `HybridRetriever`:
```python
class HybridRetriever:
    def __init__(self, bm25_index: BM25Index, chroma_store: ChromaStore, embedder: EmbeddingClient): ...
    def retrieve(self, query: str, n_per_retriever: int = 5, final_k: int = 3) -> list[Document]: ...
    def rebuild_bm25(self, documents: list[Document]) -> None: ...
```

**`backend/retrieval/bm25.py`** — `BM25Index`:
```python
class BM25Index:
    def __init__(self, documents: list[Document]): ...
    def query(self, query_text: str, top_k: int = 5) -> list[Document]: ...
```

**`backend/embeddings/store.py`** — `ChromaStore.get_all_text_chunks() -> list[Document]`

**`backend/api/server.py`** — current lifespan initializes `chroma_store`, `embedder`, `initial_ingestion_complete`, `sessions`. The `_ingestion_scheduler` function calls `run_ingestion` and updates `app.state.ingestion_status`. You are adding to this lifespan.

---

## Files to Create / Modify

### 1. `backend/graph/state.py` (NEW)

```python
"""
LangGraph state schema for docuFetch.

DocuFetchState is the shared TypedDict that flows through every node in the
RAG pipeline, carrying conversation history, the current query, retrieved
chunks, relevance verdict, and source filenames.
"""
from typing import TypedDict


class DocuFetchState(TypedDict, total=False):
    """
    Shared state for the docuFetch LangGraph pipeline.

    All fields are optional (total=False) so nodes can return partial updates.
    """
    messages: list        # HumanMessage + AIMessage conversation history (capped at 20)
    query: str            # Current user query string
    retrieved_chunks: list  # top-K Document objects from hybrid retrieval
    is_relevant: bool     # Result of the relevance check node
    sources: list         # List of unique source filenames from the answer
```

### 2. `backend/graph/nodes.py` (NEW)

Four node factory functions. All are closed over their dependencies (llm, retriever) using factory functions so the graph can be instantiated with real dependencies at server startup and with mocked dependencies in tests.

```python
"""
LangGraph node implementations for the docuFetch RAG pipeline.

Each node is a factory function that captures its dependencies (LLM, retriever)
and returns a callable that takes/returns DocuFetchState dicts.

Nodes:
  retrieve          — hybrid retrieval, populates retrieved_chunks
  relevance_check   — Claude Haiku yes/no relevance judgment
  generate          — Claude Haiku 2-4 sentence answer with source citations
  no_results        — returns standard "no relevant information" message
"""
from langchain_core.documents import Document
from langchain_core.messages import HumanMessage, AIMessage

from backend.graph.state import DocuFetchState
from backend.retrieval.hybrid import HybridRetriever

NO_RESULTS_MESSAGE = "I couldn't find relevant information in your documents."


def make_retrieve_node(hybrid_retriever: HybridRetriever):
    """Factory: returns the retrieve node function bound to hybrid_retriever."""
    def retrieve(state: DocuFetchState) -> dict:
        """Run hybrid retrieval for the current query, populate retrieved_chunks."""
        query = state.get("query", "")
        chunks = hybrid_retriever.retrieve(query) if query else []
        return {"retrieved_chunks": chunks}
    return retrieve


def make_relevance_check_node(llm):
    """Factory: returns the relevance_check node function bound to llm."""
    def relevance_check(state: DocuFetchState) -> dict:
        """
        Judge whether retrieved chunks are relevant to the query.
        Sets is_relevant=False immediately if retrieved_chunks is empty
        (no LLM call made). Otherwise asks Claude Haiku yes/no.
        """
        chunks = state.get("retrieved_chunks", [])
        if not chunks:
            return {"is_relevant": False}
        
        chunks_text = "\n\n".join(
            f"[source: {c.metadata.get('filename', 'unknown')}]\n{c.page_content}"
            for c in chunks
        )
        prompt = (
            f"Query: {state.get('query', '')}\n\n"
            f"Retrieved document chunks:\n{chunks_text}\n\n"
            "Are these chunks relevant to answering the query? "
            "Answer with only 'yes' or 'no'."
        )
        response = llm.invoke([HumanMessage(content=prompt)])
        is_relevant = "yes" in response.content.strip().lower()
        return {"is_relevant": is_relevant}
    return relevance_check


def make_generate_node(llm):
    """Factory: returns the generate node function bound to llm."""
    def generate(state: DocuFetchState) -> dict:
        """
        Generate a 2-4 sentence answer grounded in retrieved_chunks.
        Cites source filenames inline as [source: filename].
        Appends the new HumanMessage and AIMessage to messages history.
        History is trimmed to at most 20 messages before the LLM call.
        """
        chunks = state.get("retrieved_chunks", [])
        query = state.get("query", "")
        messages = state.get("messages", [])
        
        # Trim history to last 20 messages before LLM call
        history = messages[-20:] if len(messages) > 20 else messages
        
        chunks_text = "\n\n".join(
            f"[source: {c.metadata.get('filename', 'unknown')}]\n{c.page_content}"
            for c in chunks
        )
        sources = list({
            c.metadata["filename"]
            for c in chunks
            if c.metadata.get("filename")
        })
        
        prompt = (
            f"Using only the provided documents, answer the following question in "
            f"exactly 2-4 sentences. Cite each source as [source: filename].\n\n"
            f"Documents:\n{chunks_text}\n\n"
            f"Question: {query}"
        )
        call_messages = history + [HumanMessage(content=prompt)]
        response = llm.invoke(call_messages)
        
        updated_messages = messages + [HumanMessage(content=query), response]
        return {"sources": sources, "messages": updated_messages}
    return generate


def make_no_results_node():
    """Factory: returns the no_results node function (no external dependencies)."""
    def no_results(state: DocuFetchState) -> dict:
        """
        Return the standard no-results message and append it to messages history.
        sources is set to an empty list.
        """
        query = state.get("query", "")
        messages = state.get("messages", [])
        ai_msg = AIMessage(content=NO_RESULTS_MESSAGE)
        updated_messages = messages + [HumanMessage(content=query), ai_msg]
        return {"sources": [], "messages": updated_messages}
    return no_results
```

### 3. `backend/graph/graph.py` (NEW)

```python
"""
LangGraph graph assembly for the docuFetch RAG pipeline.

Wires the four nodes into a compiled graph:
  retrieve → relevance_check → (generate | no_results)

The conditional edge routes to generate when is_relevant=True,
and to no_results when is_relevant=False.
"""
from langgraph.graph import StateGraph, END
from langchain_anthropic import ChatAnthropic

from backend.graph.state import DocuFetchState
from backend.graph.nodes import (
    make_retrieve_node,
    make_relevance_check_node,
    make_generate_node,
    make_no_results_node,
)
from backend.retrieval.hybrid import HybridRetriever


def build_graph(hybrid_retriever: HybridRetriever, llm: ChatAnthropic):
    """
    Build and compile the docuFetch LangGraph pipeline.

    Returns a compiled graph that accepts DocuFetchState and returns
    an updated DocuFetchState with answer in messages[-1] and sources.
    """
    workflow = StateGraph(DocuFetchState)
    
    workflow.add_node("retrieve", make_retrieve_node(hybrid_retriever))
    workflow.add_node("relevance_check", make_relevance_check_node(llm))
    workflow.add_node("generate", make_generate_node(llm))
    workflow.add_node("no_results", make_no_results_node())
    
    workflow.set_entry_point("retrieve")
    workflow.add_edge("retrieve", "relevance_check")
    workflow.add_conditional_edges(
        "relevance_check",
        lambda state: "generate" if state.get("is_relevant") else "no_results",
        {"generate": "generate", "no_results": "no_results"},
    )
    workflow.add_edge("generate", END)
    workflow.add_edge("no_results", END)
    
    return workflow.compile()
```

### 4. `backend/api/server.py` (MODIFY — add HybridRetriever + graph init + BM25 rebuild)

Make three targeted additions to the existing server.py. Do not remove or restructure any existing code.

**Addition A — imports (add near the top with existing imports):**
```python
from langchain_anthropic import ChatAnthropic
from backend.retrieval.bm25 import BM25Index
from backend.retrieval.hybrid import HybridRetriever
from backend.graph.graph import build_graph
```

**Addition B — in the `lifespan` function, after the existing state init block (before creating the scheduler task):**
```python
# Initialize HybridRetriever and LangGraph graph
text_chunks = app.state.chroma_store.get_all_text_chunks()
bm25_index = BM25Index(text_chunks)
app.state.hybrid_retriever = HybridRetriever(bm25_index, app.state.chroma_store, app.state.embedder)

llm = ChatAnthropic(model="claude-3-5-haiku-20241022", api_key=os.getenv("ANTHROPIC_API_KEY", ""))
app.state.graph = build_graph(app.state.hybrid_retriever, llm)
```

**Addition C — in `_ingestion_scheduler`, after each `run_ingestion` call (both the startup run and the loop run), add a BM25 rebuild:**
```python
# Rebuild BM25 index with newly ingested documents
new_text_chunks = app.state.chroma_store.get_all_text_chunks()
app.state.hybrid_retriever.rebuild_bm25(new_text_chunks)
```

The updated `_ingestion_scheduler` should look like:
```python
async def _ingestion_scheduler(app: FastAPI) -> None:
    """..."""
    watch_folder = os.getenv("WATCH_FOLDER", "")
    hash_store_path = os.getenv("HASH_STORE_PATH", "./hash_store.json")

    # First run at startup
    result = await asyncio.to_thread(
        run_ingestion, watch_folder, app.state.chroma_store, app.state.embedder, hash_store_path
    )
    app.state.ingestion_status = result
    new_text_chunks = app.state.chroma_store.get_all_text_chunks()
    app.state.hybrid_retriever.rebuild_bm25(new_text_chunks)
    app.state.initial_ingestion_complete = True

    while True:
        await asyncio.sleep(60)
        result = await asyncio.to_thread(
            run_ingestion, watch_folder, app.state.chroma_store, app.state.embedder, hash_store_path
        )
        app.state.ingestion_status = result
        new_text_chunks = app.state.chroma_store.get_all_text_chunks()
        app.state.hybrid_retriever.rebuild_bm25(new_text_chunks)
```

---

## Acceptance Criteria (verify all before reporting done)

- [ ] `DocuFetchState` can be instantiated with only `query` and no other fields without error
- [ ] `no_results` node returns `"I couldn't find relevant information in your documents."` in the last AIMessage
- [ ] `no_results` node sets `sources` to empty list
- [ ] `relevance_check` node sets `is_relevant=False` without making an LLM call when `retrieved_chunks=[]`
- [ ] The graph can be imported and compiled (`build_graph(...)`) without error
- [ ] Invoking the graph with a relevant query (mock or real) routes through `generate`
- [ ] Invoking the graph with empty chunks routes through `no_results`

---

## How to Verify

**Unit tests — no API keys needed for most:**

```python
# Test 1: DocuFetchState partial instantiation
from backend.graph.state import DocuFetchState
state = DocuFetchState(query="test query")
assert state["query"] == "test query"
# Should not raise KeyError for missing fields
print("Test 1 passed: partial instantiation")

# Test 2: no_results node
from backend.graph.nodes import make_no_results_node
no_results = make_no_results_node()
result = no_results({"query": "anything", "messages": [], "is_relevant": False, "retrieved_chunks": []})
assert result["sources"] == []
from langchain_core.messages import AIMessage
last_msg = result["messages"][-1]
assert isinstance(last_msg, AIMessage)
assert "couldn't find" in last_msg.content
print("Test 2 passed: no_results node")

# Test 3: relevance_check with empty chunks (no LLM call)
from unittest.mock import MagicMock
from backend.graph.nodes import make_relevance_check_node
mock_llm = MagicMock()
relevance_check = make_relevance_check_node(mock_llm)
result = relevance_check({"query": "test", "retrieved_chunks": []})
assert result["is_relevant"] == False
mock_llm.invoke.assert_not_called()
print("Test 3 passed: relevance_check skips LLM when chunks empty")

# Test 4: build_graph compiles without error (uses mock deps)
from unittest.mock import MagicMock
from backend.graph.graph import build_graph
mock_retriever = MagicMock()
mock_llm = MagicMock()
graph = build_graph(mock_retriever, mock_llm)
assert graph is not None
print("Test 4 passed: graph compiles")

# Test 5: graph routes to no_results when chunks empty
from langchain_core.documents import Document
mock_retriever.retrieve.return_value = []
state = {"query": "completely unrelated topic", "messages": []}
result = graph.invoke(state)
last_msg = result["messages"][-1]
assert "couldn't find" in last_msg.content
assert result["sources"] == []
print("Test 5 passed: graph routes to no_results with empty chunks")

print("All graph tests passed")
```

Run: `cd /workspace && python3 scratch_graph.py`

---

## Coding Standards

- Every file must have a module-level docstring
- Every function must have a docstring
- Factory functions: clear docstring explaining the node's purpose
- The `NO_RESULTS_MESSAGE` constant must be the exact string: `"I couldn't find relevant information in your documents."`

---

## What to Write in Your Report

Write `docs/backend/agent-reports/worker-rag-pipeline-report.md` with:
1. Status: DONE or FAILED
2. Files created/modified (line counts)
3. Verification output (paste scratch test results)
4. Interface summary for Issue 8 (POST /chat):
   - How to invoke the compiled graph: `graph.invoke({"query": ..., "messages": [...]})`
   - What the returned state contains: `result["messages"][-1].content` for answer, `result["sources"]` for filenames, `result["messages"]` for updated history
   - Where the graph lives at runtime: `request.app.state.graph`
5. Any deviations and why
