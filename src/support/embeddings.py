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
                import ollama  # type: ignore
                response = ollama.embeddings(model=self.model, prompt=text)
                emb = response.get('embedding', response.embedding if hasattr(response, 'embedding') else [])
                if emb:
                    return list(emb)
            except Exception as e:
                print(f"⚠️ Local embedding error: {e}")
                # Return a zero vector of a common embedding size (e.g., 384 for all-MiniLM-L6-v2)
                # or None if a specific size isn't guaranteed or desired for fallback.
                # For now, returning None to indicate failure, consistent with original logic.
                pass


        # Fallback to sentence-transformers if installed
        if self._st_model:
            try:
                return self._st_model.encode(text).tolist()
            except Exception:
                pass

        # Graceful failure
        return None


