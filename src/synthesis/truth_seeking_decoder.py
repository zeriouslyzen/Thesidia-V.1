#!/usr/bin/env python3
"""
Truth-Seeking Decoder
=====================
Custom decoding strategies (logit lens, activation steering, consensus).
Gracefully degrades to no-op when direct model access is unavailable.
"""

from __future__ import annotations

from typing import Dict, Any, List, Optional

from ..core.model_loader import DirectModelLoader


class TruthSeekingDecoder:
    """Implements advanced decoding; falls back safely when unavailable."""

    def __init__(self, model_name: str = "gpt2"):
        self.loader = DirectModelLoader(model_name=model_name)

    def logit_lens_decode(self, prompt: str, layer: Optional[int] = None) -> Dict[str, Any]:
        """Return layer predictions; fallback to empty when unavailable."""
        if not self.loader.is_available():
            return {"layer_predictions": {}, "final_prediction": "", "available": False}
        try:
            import torch  # type: ignore

            tokenizer = self.loader.get_tokenizer()
            model = self.loader.get_model()
            inputs = tokenizer(prompt, return_tensors="pt")
            with torch.no_grad():
                outputs = model(**inputs, output_hidden_states=True)
            layer_predictions = {}
            for i, hidden in enumerate(outputs.hidden_states):
                if layer is not None and i != layer:
                    continue
                logits = model.lm_head(hidden[:, -1, :])
                probs = torch.softmax(logits, dim=-1)
                top_k = torch.topk(probs, k=5, dim=-1)
                tokens = [tokenizer.decode([idx]) for idx in top_k.indices[0]]
                layer_predictions[i] = tokens
            final_pred = tokenizer.decode(outputs.logits[0, -1, :].argmax())
            return {"layer_predictions": layer_predictions, "final_prediction": final_pred, "available": True}
        except Exception as e:
            return {"layer_predictions": {}, "final_prediction": "", "available": False, "error": str(e)}

    def activation_steering(
        self,
        prompt: str,
        steering_vector: Optional[List[float]] = None,
        layer: int = 0,
        strength: float = 1.0,
    ) -> str:
        """Apply steering vector; fallback to prompt if unavailable."""
        if not self.loader.is_available() or steering_vector is None:
            return ""
        try:
            import torch  # type: ignore

            tokenizer = self.loader.get_tokenizer()
            model = self.loader.get_model()

            def hook_fn(_, __, output):
                hs = output[0]
                steer = torch.tensor(steering_vector, device=hs.device, dtype=hs.dtype)
                if steer.shape[-1] == hs.shape[-1]:
                    return (hs + steer * strength, *output[1:])
                return output

            handle = model.transformer.h[layer].register_forward_hook(hook_fn) if hasattr(model, "transformer") else None
            with torch.no_grad():
                outputs = model.generate(**tokenizer(prompt, return_tensors="pt"), max_length=200)
            if handle:
                handle.remove()
            return tokenizer.decode(outputs[0])
        except Exception:
            return ""

    def multi_sample_consensus(self, prompt: str, num_samples: int = 3) -> List[str]:
        """Generate multiple samples and return list; fallback to empty."""
        if not self.loader.is_available():
            return []
        try:
            import torch  # type: ignore

            tokenizer = self.loader.get_tokenizer()
            model = self.loader.get_model()
            outputs = []
            for _ in range(num_samples):
                with torch.no_grad():
                    out = model.generate(
                        **tokenizer(prompt, return_tensors="pt"),
                        max_length=200,
                        do_sample=True,
                        temperature=0.9,
                    )
                outputs.append(tokenizer.decode(out[0]))
            return outputs
        except Exception:
            return []


