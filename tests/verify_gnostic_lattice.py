
import sys
import os
import json
import time
from pathlib import Path

# Add project root to path
project_root = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(project_root))

from src.synthesis.gnostic_lattice import GnosticLattice
from src.synthesis.metrics_tracker import MetricsTracker

def test_gnostic_lattice_logic():
    print("--- Testing GnosticLattice Logic ---")
    data_dir = project_root / 'data'
    data_dir.mkdir(exist_ok=True)
    lattice_file = data_dir / 'test_lattice.json'
    
    # Clean up
    if lattice_file.exists():
        lattice_file.unlink()
        
    lattice = GnosticLattice(storage_file=str(lattice_file))
    
    # 1. Update with Entities
    entities = ["Asherah", "Central Banking", "Elohim"]
    relations = [
        ("Asherah", "Elohim", "suppressed_by"),
        ("Elohim", "Central Banking", "evolved_into")
    ]
    
    lattice.update(entities, relations, context_id="test_q1")
    print("✅ Lattice updated with initial entities")
    
    # 2. Reinforce Connection
    lattice.update(["Asherah"], [("Asherah", "Elohim", "suppressed_by")], context_id="test_q2")
    print("✅ Lattice reinforced")
    
    # 3. Check Weights
    graph_data = lattice.get_full_graph_data()
    
    asherah_node = next((n for n in graph_data['nodes'] if n['id'] == 'Asherah'), None)
    if asherah_node and asherah_node['weight'] == 2:
        print(f"✅ Node weight correct: {asherah_node['weight']}")
    else:
        print(f"❌ Node weight incorrect: {asherah_node}")
        
    edge = next((e for e in graph_data['links'] if e['source'] == 'Asherah' and e['target'] == 'Elohim'), None)
    if edge and edge['weight'] == 2:
        print(f"✅ Edge weight correct: {edge['weight']}")
    else:
        print(f"❌ Edge weight incorrect: {edge}")
        
    # 4. Burn Check
    burning = lattice.get_burning_nodes(limit=1)
    if burning and burning[0]['id'] in ["Asherah", "Elohim"]:
        print(f"✅ Burning node identified: {burning[0]['id']}")
    else:
        print(f"❌ Burning node check failed: {burning}")

def test_metrics_integration():
    print("\n--- Testing MetricsTracker Integration ---")
    data_dir = project_root / 'data'
    data_dir.mkdir(exist_ok=True)
    metrics_file = data_dir / 'test_metrics_lattice.json'
    lattice_file = data_dir / 'gnostic_lattice.json' # MetricsTracker looks here relative to metrics file
    
    if metrics_file.exists(): metrics_file.unlink()
    if lattice_file.exists(): lattice_file.unlink()
    
    mt = MetricsTracker(storage_file=str(metrics_file))
    
    # Simulate Output
    output = """
//exposure
Analysis of the suppressed feminine.

**Key Entities:** Sophia, Demiurge, Control Grid

The pattern suggests:
Sophia -> Demiurge
    """
    
    mt.submit_task("test_mt_1", "test query", output)
    print("✅ Submitted task to MetricsTracker")
    
    time.sleep(1) # Wait for thread
    
    # Check if lattice file created
    if lattice_file.exists():
        with open(lattice_file, 'r') as f:
            data = json.load(f)
            nodes = [n['id'] for n in data['nodes']]
            if "Sophia" in nodes and "Demiurge" in nodes:
                print("✅ Lattice updated via MetricsTracker (Entities found)")
            else:
                print(f"❌ Lattice missing entities: {nodes}")
                
            links = data['links']
            if any(l['source'] == 'Sophia' and l['target'] == 'Demiurge' for l in links):
                 print("✅ Lattice updated via MetricsTracker (Relations found)")
            else:
                 print(f"❌ Lattice missing relations: {links}")
    else:
        print("❌ Lattice file not created by MetricsTracker")

if __name__ == "__main__":
    test_gnostic_lattice_logic()
    test_metrics_integration()
