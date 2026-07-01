"""
Entry point shim for uvicorn.

Imports the FastAPI app from the backend package so the server can be started
with: uvicorn server:app --port 8000 --reload
"""
from backend.api.server import app  # noqa: F401
