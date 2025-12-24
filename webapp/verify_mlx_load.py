from mlx_lm import load
import os

model_path = "mlx-community/Qwen2.5-1.5B-Instruct-4bit"

print(f"Attempting to load {model_path}...")
try:
    model, tokenizer = load(model_path)
    print("Success! Model loaded.")
except Exception as e:
    print(f"Error loading model: {e}")
