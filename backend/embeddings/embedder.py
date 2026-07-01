"""
OpenRouter embedding client for docuFetch.

Sends text strings to the nvidia/llama-nemotron-embed-vl-1b-v2:free model
via the OpenRouter API (OpenAI-compatible) and returns embedding vectors.
Image embedding (raw bytes via base64 data URI) is added in Issue 4.
"""
import base64
import os

import openai

_MIME_TYPES = {".jpg": "image/jpeg", ".jpeg": "image/jpeg", ".png": "image/png"}


class EmbeddingClient:
    """Wraps the OpenRouter embedding API."""

    def __init__(self, api_key: str):
        """Initialise the OpenAI-compatible client pointed at OpenRouter."""
        self._client = openai.OpenAI(
            api_key=api_key,
            base_url="https://openrouter.ai/api/v1",
        )
        self._model = os.getenv("OPENROUTER_EMBED_MODEL", "nvidia/llama-nemotron-embed-vl-1b-v2:free")

    def embed_texts(self, texts: list[str]) -> list[list[float]]:
        """
        Embed a list of text strings. Returns one vector per input string.
        Raises openai.OpenAIError on API failure.
        """
        response = self._client.embeddings.create(
            model=self._model,
            input=texts,
            encoding_format="float",
        )
        return [item.embedding for item in response.data]

    def embed_image(self, image_bytes: bytes, suffix: str = ".jpg") -> list[float]:
        """
        Embed raw image bytes using the OpenRouter VL model.
        Returns one embedding vector of the same dimensionality as text embeddings (2048).
        suffix is the file extension used to determine the MIME type.
        """
        mime_type = _MIME_TYPES.get(suffix.lower(), "image/jpeg")
        b64 = base64.b64encode(image_bytes).decode("utf-8")
        response = self._client.embeddings.create(
            model=self._model,
            input=f"data:{mime_type};base64,{b64}",
            encoding_format="float",
        )
        return response.data[0].embedding
