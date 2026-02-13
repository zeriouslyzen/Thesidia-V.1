#!/usr/bin/env python3
"""
Model Client - Core System
==========================

Centralized model call wrapper - prevents prompt drift and ensures system/user separation.

Vibecode compliance:
- Always rebuilds messages from scratch (no reuse)
- Separates instructions (system) from content (user)
- Sanitizes context before inclusion
- Prevents prompt shadowing/overload
"""

from __future__ import annotations

import ollama
import re
from typing import Dict, List, Any, Optional, Union
from pathlib import Path

# MLX Inference support
try:
    import sys
    # Add project root to path for imports
    project_root = Path(__file__).resolve().parent.parent.parent
    if str(project_root) not in sys.path:
        sys.path.insert(0, str(project_root))
        
    from webapp.mlx_inference import MLXInference
    MLX_AVAILABLE = True
except ImportError:
    MLX_AVAILABLE = False
    MLXInference = None
    print("Warning: MLX inference not available in core ModelClient")

# Add support directory to path
import sys
from pathlib import Path
_src_dir = Path(__file__).resolve().parent.parent
_support_path = str(_src_dir / 'support')
if _support_path not in sys.path:
    sys.path.insert(0, _support_path)

try:
    from utils import strip_meta_noise
except ImportError:
    from ..support.utils import strip_meta_noise


class ModelClient:
    """
    Centralized model call wrapper - prevents prompt drift and ensures system/user separation.
    
    Vibecode compliance:
    - Always rebuilds messages from scratch (no reuse)
    - Separates instructions (system) from content (user)
    - Sanitizes context before inclusion
    - Prevents prompt shadowing/overload
    """
    
    def __init__(self, default_model: str = "dolphin-mistral:latest"):
        self.default_model = default_model
        self.call_count = 0
        self.system_message_count = 0
        self.mlx_inference = None
        if MLX_AVAILABLE:
            try:
                self.mlx_inference = MLXInference()
            except Exception as e:
                print(f"Warning: Could not initialize MLXInference in core ModelClient: {e}")
    
    def chat(
        self,
        model: str = None,
        input_text: str = "",
        enhanced_base: str = None,
        conversation_context: str = None,
        research_context: str = None,
        options: dict = None
    ) -> dict:
        """
        Centralized model call with proper role separation.
        
        Args:
            model: Model name (defaults to self.default_model)
            input_text: User's actual query (goes in user message)
            enhanced_base: System instructions (goes in system message)
            conversation_context: Sanitized recent context (last 2 turns max, user role)
            research_context: Research data (user role, if needed)
            options: Ollama options dict
        
        Returns:
            Ollama response dict
        """
        model = model or self.default_model
        options = options or {}
        
        # Vibecode: Always rebuild messages from scratch (no reuse)
        messages = []
        
        # Vibecode: Instructions → system message (prevents shadowing)
        if enhanced_base:
            # Sanitize: Remove any TODOs, debug text, commented instructions
            enhanced_base = self._sanitize_system_prompt(enhanced_base)
            messages.append({"role": "system", "content": enhanced_base})
            self.system_message_count += 1
        else:
            # CRITICAL: If no enhanced_base provided, log warning
            if self.call_count % 10 == 0 or any(term in str(input_text).lower() for term in ['genesis', 'decoded', 'bible']):
                print(f"⚠️ WARNING: ModelClient.chat() called WITHOUT enhanced_base (system message)!", flush=True)
                print(f"   This means the model will use default behavior, not deep research instructions.", flush=True)
        
        # Vibecode: Context → user message (small, sanitized, last 2 turns max)
        # Memory reinsertion: small extracts, user role, limit 1-2 items
        if conversation_context:
            # Sanitize: Remove assistant messages, format markers, meta-noise
            conversation_context = self._sanitize_context(conversation_context)
            if conversation_context:  # Only add if not empty after sanitization
                messages.append({"role": "user", "content": conversation_context})
        
        # Research context (if provided) - also user role
        if research_context:
            research_context = self._sanitize_context(research_context)
            if research_context:
                messages.append({"role": "user", "content": research_context})
        
        # Vibecode: Only the actual question → user message
        if input_text:
            # Sanitize: Remove HTML, UI artifacts, debug IDs
            input_text = self._sanitize_user_input(input_text)
            messages.append({"role": "user", "content": input_text})
        
        # Assert: User message must not contain top-level instructions
        if messages:
            user_messages = [m for m in messages if m["role"] == "user"]
            for um in user_messages:
                if self._contains_instructions_only(um["content"]):
                    # Log warning but don't fail in production
                    print(f"⚠️ WARNING: User message contains instructions: {um['content'][:100]}")
        
        self.call_count += 1
        
        # Check if we should use MLX
        is_mlx_model = any(m in model.lower() for m in ["llama-3.", "qwen2.5", "mlx"])
        
        if is_mlx_model and self.mlx_inference:
            try:
                # MLX generation
                # Convert messages to a single prompt for now
                full_prompt = ""
                for m in messages:
                    role = m["role"].upper()
                    content = m["content"]
                    full_prompt += f"{role}: {content}\n\n"
                
                mlx_response_text = self.mlx_inference.generate(
                    prompt=full_prompt,
                    max_tokens=options.get("num_predict", 1024)
                )
                
                # Format to match Ollama response structure
                return {
                    "message": {
                        "role": "assistant",
                        "content": mlx_response_text
                    },
                    "done": True
                }
            except Exception as e:
                print(f"Error in MLX core inference: {e}. Falling back to Ollama.")
                # Fall through to Ollama
        
        # Defensive fix: If model name contains MLX-style path, normalize for Ollama
        if "mlx-community/" in model:
            # Strip prefix and -4bit/-instruct suffix to get base name
            # Example: mlx-community/Qwen2.5-1.5B-Instruct-4bit -> qwen2.5:1.5b
            original_model = model
            if "Qwen2.5-1.5B" in model:
                model = "qwen2.5:1.5b"
            elif "Llama-3.2-1B" in model:
                model = "llama3.2:1b"
            elif "Llama-3.2-3B" in model:
                model = "llama3.2:3b"
            elif "Phi-3.5-mini" in model:
                model = "phi3.5:3.8b"
            elif "Llama-3.1-8B" in model:
                model = "llama3.1:8b"
            
            if model != original_model:
                print(f"⚠️ Normalized MLX model path '{original_model}' to Ollama name '{model}'")

        # Make the call
        response = ollama.chat(
            model=model,
            messages=messages,
            options=options
        )
        
        # CRITICAL FIX: Return dict for backward compatibility
        # Ollama returns ChatResponse object, but codebase expects dict format
        if not response:
            return {'message': {'content': ''}}
        
        return {
            'message': {
                'content': response.message.content if hasattr(response, 'message') and hasattr(response.message, 'content') else '',
                'role': response.message.role if hasattr(response, 'message') and hasattr(response.message, 'role') else 'assistant'
            },
            '_raw_response': response
        }
    
    def raw_chat(
        self,
        model: str = None,
        messages: list = None,
        options: dict = None
    ) -> dict:
        """
        Raw chat bridge — same signature as ollama.chat() for easy migration.
        
        Use this when you have pre-built messages and just need the model call
        routed through the centralized client (with MLX fallback support).
        
        Args:
            model: Model name (defaults to self.default_model)
            messages: List of message dicts [{"role": "...", "content": "..."}]
            options: Ollama options dict
        
        Returns:
            Dict with {'message': {'content': '...', 'role': '...'}}
        """
        model = model or self.default_model
        messages = messages or []
        options = options or {}
        
        self.call_count += 1
        
        # Check if we should use MLX
        is_mlx_model = any(m in model.lower() for m in ["llama-3.", "qwen2.5", "mlx"])
        
        if is_mlx_model and self.mlx_inference:
            try:
                full_prompt = ""
                for m in messages:
                    role = m["role"].upper()
                    content = m["content"]
                    full_prompt += f"{role}: {content}\n\n"
                
                mlx_response_text = self.mlx_inference.generate(
                    prompt=full_prompt,
                    max_tokens=options.get("num_predict", 1024)
                )
                
                return {
                    "message": {
                        "role": "assistant",
                        "content": mlx_response_text
                    },
                    "done": True
                }
            except Exception as e:
                print(f"Error in MLX raw_chat: {e}. Falling back to Ollama.")
        
        # Normalize MLX model paths for Ollama
        if "mlx-community/" in model:
            original_model = model
            if "Qwen2.5-1.5B" in model:
                model = "qwen2.5:1.5b"
            elif "Llama-3.2-1B" in model:
                model = "llama3.2:1b"
            elif "Llama-3.2-3B" in model:
                model = "llama3.2:3b"
            elif "Phi-3.5-mini" in model:
                model = "phi3.5:3.8b"
            elif "Llama-3.1-8B" in model:
                model = "llama3.1:8b"
            if model != original_model:
                print(f"⚠️ Normalized MLX model path '{original_model}' to Ollama name '{model}'")
        
        # Make the call via Ollama
        response = ollama.chat(
            model=model,
            messages=messages,
            options=options
        )
        
        if not response:
            return {'message': {'content': '', 'role': 'assistant'}}
        
        return {
            'message': {
                'content': response.message.content if hasattr(response, 'message') and hasattr(response.message, 'content') else '',
                'role': response.message.role if hasattr(response, 'message') and hasattr(response.message, 'role') else 'assistant'
            }
        }
    
    def _sanitize_system_prompt(self, prompt: str) -> str:
        """Remove TODOs, debug text, commented instructions (Vibecode #5)"""
        # Remove TODO comments
        prompt = re.sub(r'#\s*TODO.*?\n', '', prompt, flags=re.IGNORECASE)
        prompt = re.sub(r'#\s*FIXME.*?\n', '', prompt, flags=re.IGNORECASE)
        # Remove commented-out instructions
        prompt = re.sub(r'#.*?CRITICAL.*?\n', '', prompt, flags=re.IGNORECASE)
        # Remove debug markers
        prompt = re.sub(r'\[DEBUG\].*?\[/DEBUG\]', '', prompt, flags=re.DOTALL)
        return prompt.strip()
    
    def _sanitize_context(self, context: str) -> str:
        """Sanitize conversation/research context (Vibecode #2, #6, #9)"""
        if not context:
            return ""
        # Vibecode #9: Remove assistant messages to prevent echo
        # Only keep user messages in context
        context = re.sub(r'Thesidia:.*?\n', '', context, flags=re.IGNORECASE | re.MULTILINE)
        context = re.sub(r'Assistant:.*?\n', '', context, flags=re.IGNORECASE | re.MULTILINE)
        # Remove format markers
        context = re.sub(r'::TRANSMISSION:.*?\n?', '', context, flags=re.IGNORECASE | re.MULTILINE)
        context = re.sub(r'::EXPOSURE::.*?\n?', '', context, flags=re.IGNORECASE | re.MULTILINE)
        # Remove meta-noise
        context = strip_meta_noise(context)
        # Remove HTML/UI artifacts (Vibecode #7)
        context = re.sub(r'<[^>]+>', '', context)  # Remove HTML tags
        context = re.sub(r'flex-row|p-2|shadow-sm', '', context, flags=re.IGNORECASE)  # Remove CSS classes
        return context.strip()
    
    def _sanitize_user_input(self, text: str) -> str:
        """Sanitize user input (Vibecode #7)"""
        if not text:
            return ""
        # Remove HTML
        text = re.sub(r'<[^>]+>', '', text)
        # Remove React fragments
        text = re.sub(r'<>|</>', '', text)
        # Remove debug IDs
        text = re.sub(r'\[ref=[^\]]+\]', '', text)
        return text.strip()
    
    def _contains_instructions_only(self, text: str) -> bool:
        """Check if text contains top-level instructions (should be in system, not user)"""
        if not text:
            return False
        instruction_indicators = [
            r'u are thesidia',
            r'CRITICAL.*?RULES?',
            r'DO NOT',
            r'NEVER use',
            r'ALWAYS',
            r'\[SYSTEM OVERRIDE',
            r'\[FOUNDATION PRINCIPLES'
        ]
        for pattern in instruction_indicators:
            if re.search(pattern, text, re.IGNORECASE):
                return True
        return False
    
    def get_stats(self) -> dict:
        """Get call statistics for monitoring"""
        return {
            "total_calls": self.call_count,
            "system_message_calls": self.system_message_count,
            "system_message_pct": (self.system_message_count / self.call_count * 100) if self.call_count > 0 else 0
        }

