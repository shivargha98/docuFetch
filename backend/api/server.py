"""
FastAPI application for docuFetch.

Defines the app instance, startup state, and the /health endpoint. All other
routes are registered via backend.api.routes and will be added by subsequent
workers. Environment variables are loaded from a .env file at import time.
"""
import asyncio
import os
from contextlib import asynccontextmanager

from dotenv import load_dotenv
from fastapi import FastAPI

from langchain_anthropic import ChatAnthropic

from backend.api.routes import router
from backend.embeddings.store import ChromaStore
from backend.embeddings.embedder import EmbeddingClient
from backend.ingestion.pipeline import run_ingestion
from backend.retrieval.bm25 import BM25Index
from backend.retrieval.hybrid import HybridRetriever
from backend.graph.graph import build_graph

load_dotenv()


async def _ingestion_scheduler(app: FastAPI) -> None:
    """
    Background asyncio task that runs ingestion at startup then every 60 seconds.
    Runs run_ingestion in a thread executor to avoid blocking the event loop.
    """
    watch_folder = os.getenv("WATCH_FOLDER", "")
    hash_store_path = os.getenv("HASH_STORE_PATH", "./hash_store.json")

    result = await asyncio.to_thread(
        run_ingestion, watch_folder, app.state.chroma_store, app.state.embedder, hash_store_path
    )
    app.state.ingestion_status = result
    # Rebuild BM25 index with newly ingested documents
    new_text_chunks = app.state.chroma_store.get_all_text_chunks()
    app.state.hybrid_retriever.rebuild_bm25(new_text_chunks)
    app.state.initial_ingestion_complete = True

    while True:
        await asyncio.sleep(60)
        result = await asyncio.to_thread(
            run_ingestion, watch_folder, app.state.chroma_store, app.state.embedder, hash_store_path
        )
        app.state.ingestion_status = result
        # Rebuild BM25 index with newly ingested documents
        new_text_chunks = app.state.chroma_store.get_all_text_chunks()
        app.state.hybrid_retriever.rebuild_bm25(new_text_chunks)


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Initialize shared resources at startup and launch the ingestion scheduler."""
    app.state.chroma_store = ChromaStore(path=os.getenv("CHROMA_DB_PATH", "./chroma_db"))
    app.state.embedder = EmbeddingClient(api_key=os.getenv("OPENROUTER_API_KEY", ""))
    app.state.initial_ingestion_complete = False
    app.state.sessions = {}

    # Initialize HybridRetriever and LangGraph graph
    text_chunks = app.state.chroma_store.get_all_text_chunks()
    bm25_index = BM25Index(text_chunks)
    app.state.hybrid_retriever = HybridRetriever(bm25_index, app.state.chroma_store, app.state.embedder)

    llm = ChatAnthropic(model="claude-haiku-4-5", api_key=os.getenv("ANTHROPIC_API_KEY", ""))
    app.state.graph = build_graph(app.state.hybrid_retriever, llm)

    task = asyncio.create_task(_ingestion_scheduler(app))
    yield
    task.cancel()
    try:
        await task
    except asyncio.CancelledError:
        pass


app = FastAPI(title="docuFetch", lifespan=lifespan)

app.include_router(router)


@app.get("/health")
def health():
    """Returns server status and whether initial ingestion has completed."""
    return {
        "status": "ok",
        "initial_ingestion_complete": app.state.initial_ingestion_complete,
    }
