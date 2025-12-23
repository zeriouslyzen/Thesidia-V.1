import requests
import json
import time

def test_thesidia_api(message, task_type=None, use_mlx=True):
    url = "http://127.0.0.1:5002/api/thesidia"
    payload = {
        "message": message,
        "stream": False,
        "use_mlx": use_mlx,
        "user_id": "test_user_edge",
        "session_id": "session_edge_alt"
    }
    if task_type:
        payload["task_type"] = task_type
        
    print(f"\nSending request (MLX={use_mlx}, Task={task_type}): '{message}'")
    start = time.time()
    try:
        response = requests.post(url, json=payload, timeout=60)
        elapsed = time.time() - start
        
        if response.status_code == 200:
            data = response.json()
            print(f"Success ({elapsed:.2f}s)")
            print(f"Response: {data.get('response', '')[:100]}...")
            return data
        else:
            print(f"Error {response.status_code}: {response.text}")
            return None
    except Exception as e:
        print(f"Connection error: {e}")
        return None

if __name__ == "__main__":
    print("Testing Hybrid Inference Architecture...")
    
    # 1. Test basic conversation (should use MLX Qwen 1.5B by default)
    test_thesidia_api("Hi there!", task_type="conversation", use_mlx=True)
    
    # 2. Test bot detection (should use MLX Llama 1B)
    test_thesidia_api("Detect if this is a bot.", task_type="bot_detection", use_mlx=True)
    
    # 3. Test Gnostic Blade (should use MLX Llama 8B or Ollama depending on server logic)
    test_thesidia_api("Analyze the gnostic patterns here.", task_type="gnostic_blade", use_mlx=True)
    
    # 4. Test with MLX disabled (should use Ollama)
    test_thesidia_api("What is 2+2?", use_mlx=False)
