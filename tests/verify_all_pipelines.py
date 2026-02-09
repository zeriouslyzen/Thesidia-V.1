
import sys
import os
import json
import time
import shutil
from pathlib import Path
from datetime import datetime

# Add project root to path
project_root = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(project_root))

# Import Components
from src.synthesis.conversation_manager import ConversationManager
from src.synthesis.metrics_tracker import MetricsTracker
from src.synthesis.gnostic_lattice import GnosticLattice
from src.support.semantic_router import _get_embedding_model

def setup_test_env():
    """Setup isolated test environment for data."""
    data_dir = project_root / 'data' / 'test_env'
    if data_dir.exists():
        shutil.rmtree(data_dir)
    data_dir.mkdir(parents=True, exist_ok=True)
    return data_dir

def section(title):
    print(f"\n{'='*60}")
    print(f"🧪 {title}")
    print(f"{'='*60}")

def verify_forensic_pipeline():
    """Verify the entire forensic pipeline from thread to lattice."""
    
    data_dir = setup_test_env()
    metrics_file = data_dir / 'forensic_metrics.json'
    lattice_file = data_dir / 'gnostic_lattice.json'
    history_file = data_dir / 'conversation_history.json'
    
    # Initialize Components
    cm = ConversationManager(storage_file=str(history_file))
    mt = MetricsTracker(storage_file=str(metrics_file))
    
    # ---------------------------------------------------------
    # TEST 1: Threading & Context Injection
    # ---------------------------------------------------------
    section("TEST 1: Threading & Context")
    
    # Query 1 (Parent)
    q1_id = "q1_root"
    q1_out = """
//exposure
The architecture of **The Central Bank** relies on debt mechanisms.
**Key Entities:** The Central Bank, Usury
    """
    cm.store_query(q1_id, "Analyze banking", q1_out)
    
    # Query 2 (Child/Thread)
    thread_query = "Trace the origins of Usury"
    context = cm.build_context_prompt(thread_query, q1_id)
    
    if "The Central Bank" in context and "Usury" in context:
        print("✅ Context Injection: PASSED")
        print("\n--- [FULL CONTEXT PROMPT] ---")
        print(context)
        print("-----------------------------\n")
    else:
        print(f"❌ Context Injection: FAILED\n{context}")

    # ... (Test 2 remains same) ...


    # TEST 2: Semantic Entity Resolution (The Brain)
    # ---------------------------------------------------------
    section("TEST 2: Semantic Entity Resolution")
    
    # Check if model is available
    model = _get_embedding_model()
    if not model:
        print("⚠️  Semantic Model not available (skipping semantic test)")
    else:
        print("🧠 Semantic Model Loaded")
        
        # Step 1: Establish baseline node "Central Banking"
        mt.submit_task("t1", "q1", 
            "**Key Entities:** Central Banking, The Fed")
        time.sleep(5) # Wait for background thread (allow model load)
        
        # Step 2: Introduce synonymous term "The Central Bank System"
        mt.submit_task("t2", "q2", 
            "**Key Entities:** The Central Bank System, Fiat Currency")
        time.sleep(5)
        
        # Verify Lattice
        lattice = GnosticLattice(storage_file=str(lattice_file))
        graph = lattice.get_full_graph_data()
        nodes = [n['id'] for n in graph['nodes']]
        
        print(f"Nodes in Lattice: {nodes}")
        
        if "Central Banking" in nodes and "The Central Bank System" not in nodes:
             print("✅ Semantic Merge: PASSED ('The Central Bank System' -> 'Central Banking')")
             # Calculate similarity manually to show user
             e1 = model.encode(["Central Banking"])[0]
             e2 = model.encode(["The Central Bank System"])[0]
             import numpy as np
             sim = np.dot(e1, e2) / (np.linalg.norm(e1) * np.linalg.norm(e2))
             print(f"\n--- [SEMANTIC MATCH DETAILS] ---")
             print(f"Term 1: 'Central Banking'")
             print(f"Term 2: 'The Central Bank System'")
             print(f"Similarity Score: {sim:.4f} (Threshold: 0.85)")
             print(f"Result: MERGED")
             print("--------------------------------\n")
        elif "Central Banking" in nodes and "The Central Bank System" in nodes:
             print("⚠️  Semantic Merge: FAILED (Nodes are separate)")
             e1 = model.encode(["Central Banking"])[0]
             e2 = model.encode(["The Central Bank System"])[0]
             import numpy as np
             sim = np.dot(e1, e2) / (np.linalg.norm(e1) * np.linalg.norm(e2))
             print(f"    Similarity check: {sim:.4f}")
        else:
             print("❌ Semantic Merge: FAILED (Unexpected state)")

    # ---------------------------------------------------------
    # TEST 3: Background Metrics
    # ---------------------------------------------------------
    section("TEST 3: Background Metrics")
    
    if metrics_file.exists():
        with open(metrics_file, 'r') as f:
            metrics_data = json.load(f)
            if "t1" in metrics_data and metrics_data["t1"]["pattern_count"] > 0:
                print("✅ Metrics Calculation: PASSED")
                print("\n--- [FULL METRICS OUTPUT] ---")
                print(json.dumps(metrics_data["t1"], indent=2))
                print("-----------------------------\n")
            else:
                print("❌ Metrics Calculation: FAILED (Data missing or empty)")
    else:
        print("❌ Metrics Calculation: FAILED (File not found)")

    print("\n🏁 Unified Verification Complete")

if __name__ == "__main__":
    verify_forensic_pipeline()
