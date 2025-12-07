#!/usr/bin/env python3
"""
Direct Model Loader
-------------------
Loads models via transformers for features that require direct access to logits
or activations. Designed to fail gracefully if dependencies are unavailable.
"""

from __future__ import annotations

from typing import Optional


class DirectModelLoader:
    """Load models directly (transformers) when available."""

    def __init__(self, model_name: str = "gpt2"):
        self.model_name = model_name
        self.tokenizer = None
        self.model = None
        self.available = False
        self._init_model()

    def _init_model(self):
        try:
            from transformers import AutoModelForCausalLM, AutoTokenizer  # type: ignore
            import torch  # noqa: F401

            self.tokenizer = AutoTokenizer.from_pretrained(self.model_name)
            self.model = AutoModelForCausalLM.from_pretrained(self.model_name)
            self.available = True
        except Exception as e:
            # Dependencies or model not available; stay unavailable
            print(f"DirectModelLoader unavailable: {e}")
            self.available = False

    def is_available(self) -> bool:
        return self.available and self.model is not None and self.tokenizer is not None

    def get_model(self):
        return self.model

    def get_tokenizer(self):
        return self.tokenizer


