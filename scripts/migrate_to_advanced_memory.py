#!/usr/bin/env python3
"""
Migration Script: Old State File → Advanced Memory Architecture
Migrates data from thesidia_hybrid_adaptive_state.json to new three-layer memory system
"""

import json
import sys
from pathlib import Path
from datetime import datetime

# Add project root to path
project_root = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(project_root))
sys.path.insert(0, str(project_root / 'src'))

from src.memory.memory_manager import MemoryManager


def migrate_state_file(state_file_path: str = "data/thesidia_hybrid_adaptive_state.json"):
    """
    Migrate old state file to new memory architecture
    
    Args:
        state_file_path: Path to old state file
    """
    print("="*60)
    print("MIGRATION: Old State File → Advanced Memory Architecture")
    print("="*60)
    print()
    
    # Check if state file exists
    state_file = Path(state_file_path)
    if not state_file.exists():
        # Try alternative paths
        alt_paths = [
            "../data/thesidia_hybrid_adaptive_state.json",
            "thesidia_hybrid_adaptive_state.json"
        ]
        for alt_path in alt_paths:
            if Path(alt_path).exists():
                state_file = Path(alt_path)
                break
        else:
            print(f"❌ State file not found: {state_file_path}")
            print("   Migration skipped (no existing state to migrate)")
            return
    
    # Backup old state file
    backup_path = state_file.with_suffix('.json.BAK_migration_' + datetime.now().strftime('%Y%m%d_%H%M%S'))
    import shutil
    shutil.copy2(state_file, backup_path)
    print(f"✅ Backed up state file to: {backup_path.name}")
    print()
    
    # Load old state
    print("📖 Loading old state file...")
    try:
        with open(state_file, 'r', encoding='utf-8') as f:
            old_state = json.load(f)
    except Exception as e:
        print(f"❌ Error loading state file: {e}")
        return
    
    print(f"   - Interactions: {len(old_state.get('interactions', []))}")
    print(f"   - Personality: {'Yes' if 'personality' in old_state else 'No'}")
    print(f"   - Capabilities: {'Yes' if 'capabilities' in old_state else 'No'}")
    print(f"   - Learning: {'Yes' if 'learning' in old_state else 'No'}")
    print()
    
    # Initialize memory manager
    print("🔧 Initializing new memory system...")
    memory_manager = MemoryManager(base_dir=project_root)
    print("   ✅ Memory manager initialized")
    print()
    
    # Migrate data
    print("📦 Migrating data...")
    
    # Migrate interactions to ephemeral (last 2 only)
    interactions = old_state.get('interactions', [])
    if interactions:
        print(f"   - Migrating {min(2, len(interactions))} interactions to ephemeral memory...")
        for interaction in interactions[-2:]:
            user_input = interaction.get('input', '')
            assistant_output = interaction.get('output', '')
            metadata = {
                'timestamp': interaction.get('timestamp'),
                'type': interaction.get('type', 'conversation')
            }
            memory_manager.store_interaction(user_input, assistant_output, metadata)
        print("   ✅ Ephemeral memory migrated")
    
    # Migrate structured data
    print("   - Migrating structured data...")
    
    if 'personality' in old_state:
        memory_manager.structured.set('system_state.personality', old_state['personality'])
        print("     ✅ Personality migrated")
    
    if 'capabilities' in old_state:
        memory_manager.structured.set('system_state.capabilities', old_state['capabilities'])
        print("     ✅ Capabilities migrated")
    
    if 'learning' in old_state:
        memory_manager.structured.set('system_state.learning', old_state['learning'])
        print("     ✅ Learning migrated")
    
    if 'gnostic_map' in old_state:
        memory_manager.structured.set('system_state.gnostic_map', old_state['gnostic_map'])
        print("     ✅ Gnostic map migrated")
    
    if 'emergence' in old_state:
        memory_manager.structured.set('system_state.emergence', old_state['emergence'])
        print("     ✅ Emergence migrated")
    
    if 'consciousness' in old_state:
        memory_manager.structured.set('system_state.consciousness', old_state['consciousness'])
        print("     ✅ Consciousness migrated")
    
    print()
    
    # Migrate interactions to vector memory (if they pass gatekeeper)
    print("   - Migrating interactions to vector memory (with gatekeeper validation)...")
    vector_count = 0
    for interaction in interactions:
        user_input = interaction.get('input', '')
        assistant_output = interaction.get('output', '')
        metadata = {
            'timestamp': interaction.get('timestamp'),
            'type': interaction.get('type', 'conversation')
        }
        
        # Check if should store (gatekeeper will validate)
        combined = f"{user_input} {assistant_output}"
        should_store, reason = memory_manager.gatekeeper.should_store(combined, metadata)
        
        if should_store:
            memory_manager.vector.store(assistant_output, {
                **metadata,
                'user_input': user_input
            })
            vector_count += 1
    
    print(f"     ✅ {vector_count} interactions stored in vector memory")
    print()
    
    # Display stats
    print("="*60)
    print("MIGRATION COMPLETE")
    print("="*60)
    print()
    
    stats = memory_manager.get_stats()
    print("Memory Statistics:")
    print(f"  - Ephemeral: {stats['ephemeral']['total_interactions']} interactions")
    print(f"  - Structured: {len(stats['structured']['sections'])} sections")
    print(f"  - Vector: {stats['vector']['total_entries']} entries")
    print()
    
    print("New Memory Files:")
    print(f"  - {stats['ephemeral']['memory_file']}")
    print(f"  - {stats['structured']['memory_file']}")
    print(f"  - {stats['vector']['vectors_dir']}/memory_index.json")
    print()
    
    print("✅ Migration successful!")
    print()
    print("Next Steps:")
    print("  1. Test the new memory system")
    print("  2. Integrate MemoryManager into ThesidiaHybridAdaptive")
    print("  3. Verify old state file is no longer needed")
    print()


if __name__ == "__main__":
    migrate_state_file()

