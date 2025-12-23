"""
MLX Inference Module for Thesidia
================================
High-performance edge inference using Apple MLX framework.
Provides 2-3x faster inference than Ollama on Apple Silicon.
"""

import time
from typing import Optional, Dict, Any, Generator
import os

# MLX imports
try:
    from mlx_lm import load, generate, stream_generate
    MLX_AVAILABLE = True
except ImportError:
    MLX_AVAILABLE = False
    print("Warning: MLX not available. Install with: pip install mlx mlx-lm")


class MLXInference:
    """MLX-based inference engine for edge AI."""
    
    # Available MLX models (HuggingFace paths)
    MODELS = {
        "llama3.2:1b": "mlx-community/Llama-3.2-1B-Instruct-4bit",
        "qwen2.5:1.5b": "mlx-community/Qwen2.5-1.5B-Instruct-4bit",
        "llama3.2:3b": "mlx-community/Llama-3.2-3B-Instruct-4bit",
        "phi3.5:3.8b": "mlx-community/Phi-3.5-mini-instruct-4bit",
    }
    
    def __init__(self):
        self.loaded_models: Dict[str, Any] = {}
        self.current_model: Optional[str] = None
        
    def is_available(self) -> bool:
        """Check if MLX is available."""
        return MLX_AVAILABLE
    
    def list_models(self) -> list:
        """List available MLX models."""
        return list(self.MODELS.keys())
    
    def load_model(self, model_name: str) -> bool:
        """Load a model into memory."""
        if not MLX_AVAILABLE:
            return False
            
        if model_name in self.loaded_models:
            self.current_model = model_name
            return True
        
        if model_name not in self.MODELS:
            print(f"Unknown model: {model_name}. Available: {list(self.MODELS.keys())}")
            return False
        
        try:
            print(f"Loading MLX model: {model_name}...")
            start = time.time()
            model, tokenizer = load(self.MODELS[model_name])
            self.loaded_models[model_name] = (model, tokenizer)
            self.current_model = model_name
            print(f"Model loaded in {time.time() - start:.2f}s")
            return True
        except Exception as e:
            print(f"Failed to load model: {e}")
            return False
    
    def unload_model(self, model_name: str) -> bool:
        """Unload a model to free memory."""
        if model_name in self.loaded_models:
            del self.loaded_models[model_name]
            if self.current_model == model_name:
                self.current_model = None
            return True
        return False
    
    def generate(
        self,
        prompt: str,
        model_name: Optional[str] = None,
        max_tokens: int = 500,
        temperature: float = 0.7,
        system_prompt: Optional[str] = None
    ) -> str:
        """Generate a response using MLX."""
        if not MLX_AVAILABLE:
            raise RuntimeError("MLX not available")
        
        # Use specified model or default
        model_name = model_name or self.current_model or "llama3.2:1b"
        
        # Load model if needed
        if model_name not in self.loaded_models:
            if not self.load_model(model_name):
                raise RuntimeError(f"Failed to load model: {model_name}")
        
        model, tokenizer = self.loaded_models[model_name]
        
        # Format prompt with system message if provided
        if system_prompt:
            full_prompt = f"{system_prompt}\n\nUser: {prompt}\n\nAssistant:"
        else:
            full_prompt = prompt
        
        # Generate response
        start = time.time()
        response = generate(
            model, 
            tokenizer, 
            prompt=full_prompt, 
            max_tokens=max_tokens
        )
        elapsed = time.time() - start
        
        return response


class InferenceRouter:
    """
    Routes inference requests to the optimal backend.
    
    Supports:
    - MLX (fast, edge-native)
    - Ollama (more models, larger context)
    """
    
    # Task-to-model mapping
    TASK_ROUTES = {
        # Fast tasks -> Small MLX models
        "bot_detection": ("mlx", "llama3.2:1b"),
        "sentiment": ("mlx", "llama3.2:1b"),
        "classification": ("mlx", "llama3.2:1b"),
        "summarization_short": ("mlx", "llama3.2:1b"),
        
        # Medium tasks -> Larger MLX models
        "authenticity": ("mlx", "qwen2.5:1.5b"),
        "summarization": ("mlx", "qwen2.5:1.5b"),
        "conversation": ("mlx", "qwen2.5:1.5b"),
        
        # Complex tasks -> Ollama (larger models)
        "gnostic_blade": ("ollama", "llama3.1:8b"),
        "deep_research": ("ollama", "llama3.1:8b"),
        "code_generation": ("ollama", "deepseek-coder:6.7b"),
        
        # Custom agents -> Ollama
        "oracle_agent": ("ollama", "oracle-agent:latest"),
        "archaeologist_agent": ("ollama", "archaeologist-agent:latest"),
        "scrutineer_agent": ("ollama", "scrutineer-agent:latest"),
        "surveyor_agent": ("ollama", "surveyor-agent:latest"),
        "dissident_agent": ("ollama", "dissident-agent:latest"),
    }
    
    def __init__(self, ollama_url: str = "http://localhost:11434"):
        self.mlx = MLXInference()
        self.ollama_url = ollama_url
        
    def route(self, task_type: str, complexity: str = "medium") -> tuple:
        """
        Get the optimal backend and model for a task.
        
        Returns: (backend, model_name)
        """
        if task_type in self.TASK_ROUTES:
            return self.TASK_ROUTES[task_type]
        
        # Default to MLX with Qwen for unknown tasks
        return ("mlx", "qwen2.5:1.5b")
    
    async def infer(
        self,
        prompt: str,
        task_type: str = "conversation",
        max_tokens: int = 500,
        system_prompt: Optional[str] = None,
        **kwargs
    ) -> str:
        """
        Route and execute inference request.
        """
        backend, model = self.route(task_type)
        
        if backend == "mlx" and self.mlx.is_available():
            return self.mlx.generate(
                prompt=prompt,
                model_name=model,
                max_tokens=max_tokens,
                system_prompt=system_prompt
            )
        else:
            # Fallback to Ollama
            return await self._ollama_generate(
                prompt=prompt,
                model=model,
                max_tokens=max_tokens,
                system_prompt=system_prompt
            )
    
    async def _ollama_generate(
        self,
        prompt: str,
        model: str,
        max_tokens: int = 500,
        system_prompt: Optional[str] = None
    ) -> str:
        """Generate using Ollama API."""
        import aiohttp
        
        payload = {
            "model": model,
            "prompt": prompt,
            "stream": False,
            "options": {
                "num_predict": max_tokens
            }
        }
        
        if system_prompt:
            payload["system"] = system_prompt
        
        async with aiohttp.ClientSession() as session:
            async with session.post(
                f"{self.ollama_url}/api/generate",
                json=payload
            ) as resp:
                if resp.status == 200:
                    data = await resp.json()
                    return data.get("response", "")
                else:
                    raise RuntimeError(f"Ollama error: {resp.status}")


# Singleton instances
_mlx_inference = None
_inference_router = None


def get_mlx_inference() -> MLXInference:
    """Get singleton MLX inference instance."""
    global _mlx_inference
    if _mlx_inference is None:
        _mlx_inference = MLXInference()
    return _mlx_inference


def get_inference_router() -> InferenceRouter:
    """Get singleton inference router instance."""
    global _inference_router
    if _inference_router is None:
        _inference_router = InferenceRouter()
    return _inference_router


# Quick test
if __name__ == "__main__":
    print("Testing MLX Inference...")
    
    mlx = get_mlx_inference()
    
    if mlx.is_available():
        print(f"Available models: {mlx.list_models()}")
        
        # Test generation
        response = mlx.generate(
            prompt="In one sentence, what is edge AI?",
            model_name="llama3.2:1b",
            max_tokens=100
        )
        print(f"\nResponse: {response}")
    else:
        print("MLX not available")
