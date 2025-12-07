#!/usr/bin/env python3
"""
Representation Probe
====================
Accesses hidden states and attention patterns to surface latent concepts.
Falls back gracefully when direct model access is unavailable.
"""

from __future__ import annotations

from typing import Dict, Any, List, Optional

from ..core.model_loader import DirectModelLoader


class RepresentationProbe:
    """Probe model internals; safe no-op when unavailable."""

    def __init__(self, model_name: str = "gpt2"):
        self.loader = DirectModelLoader(model_name=model_name)

    def probe_activations(self, text: str, layer: Optional[int] = None) -> Dict[str, Any]:
        """Return hidden states/attentions or empty when unavailable."""
        if not self.loader.is_available():
            return {"available": False, "hidden_states": [], "attentions": []}
        try:
            import torch  # type: ignore

            tokenizer = self.loader.get_tokenizer()
            model = self.loader.get_model()
            inputs = tokenizer(text, return_tensors="pt")
            with torch.no_grad():
                outputs = model(**inputs, output_hidden_states=True, output_attentions=True)
            hs = outputs.hidden_states
            atts = outputs.attentions
            if layer is not None and 0 <= layer < len(hs):
                hs = [hs[layer]]
            if layer is not None and 0 <= layer < len(atts):
                atts = [atts[layer]]
            return {
                "available": True,
                "hidden_states": [h.cpu().tolist()[:1] for h in hs],  # truncate for safety
                "attentions": [a.cpu().tolist()[:1] for a in atts],
            }
        except Exception as e:
            return {"available": False, "error": str(e), "hidden_states": [], "attentions": []}

    def detect_contradictions_in_activations(self, text1: str, text2: str) -> float:
        """Rudimentary difference metric between two activations."""
        if not self.loader.is_available():
            return 0.0
        try:
            import torch  # type: ignore

            tokenizer = self.loader.get_tokenizer()
            model = self.loader.get_model()
            t1 = tokenizer(text1, return_tensors="pt")
            t2 = tokenizer(text2, return_tensors="pt")
            with torch.no_grad():
                h1 = model(**t1, output_hidden_states=True).hidden_states[-1]
                h2 = model(**t2, output_hidden_states=True).hidden_states[-1]
            diff = torch.mean(torch.abs(h1 - h2)).item()
            return float(diff)
        except Exception:
            return 0.0


