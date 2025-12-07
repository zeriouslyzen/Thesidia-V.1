#!/usr/bin/env python3
"""
Embedding Utilities
-------------------
Generates embeddings using Ollama when available, with a graceful fallback to
sentence-transformers if installed. If neither is available, returns None so
callers can degrade gracefully.
"""

from __future__ import annotations

from typing import Optional, List


class EmbeddingGenerator:
    """Generate embeddings with graceful fallbacks."""

    def __init__(self, model: str = "clean-mistral:latest"):
        self.model = model
        self._ollama = self._try_import_ollama()
        self._st_model = self._try_load_sentence_transformer()

    def _try_import_ollama(self):
        try:
            import ollama  # type: ignore

            return ollama
        except Exception:
            return None

    def _try_load_sentence_transformer(self):
        try:
            from sentence_transformers import SentenceTransformer  # type: ignore

            return SentenceTransformer("all-MiniLM-L6-v2")
        except Exception:
            return None

    def get_embedding(self, text: str) -> Optional[List[float]]:
        """Return embedding vector or None if unavailable."""
        if not text:
            return None

        # Prefer Ollama embeddings if available
        if self._ollama:
            try:
                resp = self._ollama.embeddings(model=self.model, prompt=text)
                emb = resp.get("embedding") if isinstance(resp, dict) else getattr(resp, "embedding", None)
                if emb:
                    return list(emb)
            except Exception:
                pass

        # Fallback to sentence-transformers if installed
        if self._st_model:
            try:
                return self._st_model.encode(text).tolist()
            except Exception:
                pass

        # Graceful failure
        return None


