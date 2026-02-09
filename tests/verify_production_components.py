
import sys
import os
import json
import time
from pathlib import Path

# Add project root to path
project_root = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(project_root))

from src.synthesis.conversation_manager import ConversationManager
from src.synthesis.metrics_tracker import MetricsTracker

def test_conversation_manager():
    print("--- Testing ConversationManager ---")
    data_dir = project_root / 'data'
    data_dir.mkdir(exist_ok=True)
    history_file = data_dir / 'test_forensic_history.json'
    
    # cleanup
    if history_file.exists():
        history_file.unlink()
        
    cm = ConversationManager(storage_file=str(history_file))
    
    # 1. Store a Query
    query_id = "test_q1"
    query = "Analyze the suppression of Gnostic texts"
    output = """
//exposure

The suppression of Gnostic texts reveals a systematic erasure of direct-access spiritual methodologies.

**Key Entities:** Nag Hammadi, Irenaeus, Orthodoxy
    """
    
    cm.store_query(query_id, query, output)
    print(f"✅ Stored query {query_id}")
    
    # 2. Retrieve history (reload)
    cm2 = ConversationManager(storage_file=str(history_file))
    saved = cm2.get_query(query_id)
    if saved and saved['query'] == query:
        print("✅ Retrieved query successfully")
    else:
        print("❌ Failed to retrieve query")
        
    # 3. Build Context Prompt
    child_query = "Trace the timeline of Irenaeus"
    context_prompt = cm.build_context_prompt(child_query, query_id)
    
    print("\nGenerated Context Prompt:")
    print(context_prompt)
    
    if "CONTEXT FROM PREVIOUS ANALYSIS" in context_prompt and "Irenaeus" in context_prompt:
        print("✅ Context injection working")
    else:
        print("❌ Context injection failed")

def test_metrics_tracker():
    print("\n--- Testing MetricsTracker ---")
    data_dir = project_root / 'data'
    data_dir.mkdir(exist_ok=True)
    metrics_file = data_dir / 'test_forensic_metrics.json'
    
    # cleanup
    if metrics_file.exists():
        metrics_file.unlink()
        
    mt = MetricsTracker(storage_file=str(metrics_file))
    
    # 1. Submit a task
    output = """
//exposure
Test content for metrics.

//thread options
- Option 1

**Epistemological Grounding:** █████ 5/7 layers aligned (HIGH)
    """
    
    mt.submit_task("test_q1", "test query", output)
    print("✅ Submitted metrics task (background)")
    
    # Wait for thread
    time.sleep(1)
    
    # 2. Check file
    if metrics_file.exists():
        with open(metrics_file, 'r') as f:
            data = json.load(f)
            if "test_q1" in data:
                print("✅ Metrics file created and populated")
                print("Metrics:", json.dumps(data["test_q1"], indent=2))
                
                # Check specifics
                m = data["test_q1"]
                if m['fqi'] > 0 and m['prs'] > 0:
                     print("✅ FQI and PRS calculated")
                else:
                     print("❌ Metrics calculation seem suspicious (zeros)")
            else:
                print("❌ Query ID not found in metrics file")
    else:
        print("❌ Metrics file not created")

if __name__ == "__main__":
    test_conversation_manager()
    test_metrics_tracker()
