import re
import json
import os
import threading
from datetime import datetime
from pathlib import Path

# Try to import Gnostic Lattice
try:
    from .gnostic_lattice import GnosticLattice
except ImportError:
    GnosticLattice = None

class MetricsTracker:
    """
    Background metrics tracking for forensic queries.
    Calculates complexity, pattern density, and updates the Gnostic Lattice.
    """
    
    def __init__(self, storage_file="data/forensic_metrics.json"):
        self.storage_file = storage_file
        # Ensure directory exists
        Path(self.storage_file).parent.mkdir(parents=True, exist_ok=True)
        
        # Initialize Lattice
        self.lattice = None
        if GnosticLattice:
            lattice_path = Path(self.storage_file).parent / "gnostic_lattice.json"
            self.lattice = GnosticLattice(storage_file=str(lattice_path))
        
    def submit_task(self, query_id, query, output):
        """
        Submit a metrics calculation task to be run in the background.
        """
        thread = threading.Thread(
            target=self._calculate_and_store,
            args=(query_id, query, output)
        )
        thread.daemon = True
        thread.start()
        
    def _calculate_and_store(self, query_id, query, output):
        """
        Worker function to calculate metrics, update lattice, and store.
        """
        try:
            metrics = self._calculate_metrics(output)
            self._store_metrics(query_id, metrics)
            
            # Update Gnostic Lattice (Knowledge Graph)
            if self.lattice:
                self._update_lattice(query_id, output)
                
        except Exception as e:
            print(f"Error tracking metrics for {query_id}: {e}")

    def _calculate_metrics(self, output):
        """
        Calculate intelligence metrics from output text.
        """
        # 1. Forensic Quality Index (FQI) - heuristics based on structure
        fqi = 0.0
        if "//exposure" in output.lower(): fqi += 2.0
        if "//burial sites" in output.lower(): fqi += 2.0
        if "//thread options" in output.lower(): fqi += 1.0
        if "**Epistemological Grounding:**" in output: fqi += 2.0
        if "::EXPOSURE::" in output: fqi += 1.5 # Legacy support
        
        # 2. Pattern Density (PRS)
        # Count bold entities or patterns
        patterns = re.findall(r'\*\*(.*?)\*\*', output)
        pattern_count = len(patterns)
        prs = min(10.0, pattern_count * 0.5)
        
        # 3. Cognitive Depth Value (CDV) - length / complexity
        length = len(output)
        cdv = min(10.0, length / 500.0)
        
        return {
            "fqi": min(10.0, fqi),
            "prs": round(prs, 2),
            "cdv": round(cdv, 2),
            "pattern_count": pattern_count,
            "calculated_at": datetime.now().isoformat()
        }

    def _update_lattice(self, query_id, output):
        """
        Extract entities/relations and update the Gnostic Lattice.
        Uses semantic similarity to merge concepts.
        """
        entities = set()
        relations = []
        
        # 1. Extract specifically marked sections
        # ... (same as before) ...
        entity_section = re.search(r'(?:Key [Ee]ntities:|\*\*Key [Ee]ntities:\*\*)\s*(.*)', output)
        if entity_section:
            raw_entities = entity_section.group(1).split(',')
            for e in raw_entities:
                e = e.strip().strip('*').strip()
                if e and len(e) < 50:
                    entities.add(e)
        
        bold_terms = re.findall(r'\*\*(.*?)\*\*', output)
        for term in bold_terms:
            if len(term) > 3 and len(term) < 40 and not term.isupper():
                entities.add(term)
        
        lines = output.split('\n')
        for line in lines:
            if '->' in line or '→' in line:
                parts = re.split(r'->|→', line)
                if len(parts) == 2:
                    src = parts[0].strip().strip('*')
                    tgt = parts[1].strip().strip('*')
                    if len(src) < 40 and len(tgt) < 40:
                        relations.append((src, tgt, "implies"))
                        entities.add(src)
                        entities.add(tgt)

        # SEMANTIC RESOLUTION
        # Instead of sending raw strings, we check similarity against existing lattice nodes
        # If similarity > 0.85, map to existing node.
        
        resolved_entities = []
        resolved_relations = []
        entity_map = {} # raw -> resolved
        
        try:
            from ..support.semantic_router import _get_embedding_model
            model = _get_embedding_model()
            
            if model and self.lattice:
                existing_nodes = list(self.lattice.graph.nodes())
                if existing_nodes:
                    existing_embeddings = model.encode(existing_nodes)
                    import numpy as np
                else:
                    existing_embeddings = None

                for entity in entities:
                    resolved_name = entity
                    if existing_embeddings is not None and len(existing_nodes) > 0:
                        embedding = model.encode([entity])[0]
                        similarities = np.dot(existing_embeddings, embedding) / (
                            np.linalg.norm(existing_embeddings, axis=1) * np.linalg.norm(embedding)
                        )
                        max_idx = np.argmax(similarities)
                        max_sim = similarities[max_idx]
                        
                        if max_sim > 0.85: # High confidence threshold
                            resolved_name = existing_nodes[max_idx]
                            # print(f"🧠 Semantic Merge: '{entity}' -> '{resolved_name}' ({max_sim:.2f})")
                    
                    entity_map[entity] = resolved_name
                    resolved_entities.append(resolved_name)
                    
            else:
                # Fallback if model not loaded
                resolved_entities = list(entities)
                entity_map = {e: e for e in entities}
                
        except Exception as e:
            print(f"Semantic resolution failed: {e}")
            resolved_entities = list(entities)
            entity_map = {e: e for e in entities}

        # Resolve relations
        for src, tgt, rel in relations:
            r_src = entity_map.get(src, src)
            r_tgt = entity_map.get(tgt, tgt)
            # Avoid self-loops from merging
            if r_src != r_tgt:
                resolved_relations.append((r_src, r_tgt, rel))

        # Update lattice with resolved data
        if resolved_entities or resolved_relations:
            self.lattice.update(resolved_entities, resolved_relations, context_id=query_id)

    def _store_metrics(self, query_id, metrics):
        """
        Store metrics in JSON file.
        """
        # Simple file-based append for MVP
        try:
            data = {}
            if os.path.exists(self.storage_file):
                with open(self.storage_file, 'r') as f:
                    try:
                        data = json.load(f)
                    except:
                        data = {}
            
            data[query_id] = metrics
            
            with open(self.storage_file, 'w') as f:
                json.dump(data, f, indent=2)
        except Exception as e:
            print(f"Error writing metrics file: {e}")
