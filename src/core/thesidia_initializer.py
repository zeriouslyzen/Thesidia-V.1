import sys
import os
import importlib
from pathlib import Path
from datetime import datetime

# Lazy import placeholders
ThesidiaHybridAdaptive = None
KnowledgeBase = None
UserMemoryManager = None
UserInterestTracker = None
AstronomicalPatternEngine = None

def _lazy_import_modules():
    """Lazy import modules to avoid errors in restricted environments."""
    global ThesidiaHybridAdaptive, KnowledgeBase, UserMemoryManager, UserInterestTracker, AstronomicalPatternEngine
    
    if ThesidiaHybridAdaptive is None:
        try:
            # Absolute imports from src directory (assumed to be in path)
            from thesidia_hybrid_adaptive import ThesidiaHybridAdaptive
            from knowledge_base import KnowledgeBase
            from memory.user_memory_manager import UserMemoryManager
            from user_interest_tracker import UserInterestTracker
            from astronomical_patterns import AstronomicalPatternEngine
            return True
        except Exception as e:
            print(f"Warning: Could not import Thesidia modules: {e}")
            import traceback
            traceback.print_exc()
            return False
    return True

class ThesidiaInitializer:
    """
    Centralized initializer for Thesidia components.
    Ensures consistent setup across web server and standalone API.
    """
    
    def __init__(self, project_root):
        self.project_root = Path(project_root)
        self.thesidia = None
        self.knowledge_base = None
        self.user_memory_manager = None
        self.interest_tracker = None
        self.astronomical_engine = None
        self.thesidia_ready = False
        self.ollama_status = False

    def check_ollama(self):
        """Check if Ollama is running."""
        try:
            import ollama
            ollama.list()
            return True
        except Exception:
            return False

    def init(self, force_fresh=False):
        """Initialize all Thesidia components."""
        if not _lazy_import_modules():
            return False
            
        self.ollama_status = self.check_ollama()
        if not self.ollama_status:
            print("Warning: Ollama not available. Thesidia personality will be limited.")
            # We continue anyway because some features might work without it
        
        # Initialize Managers
        if self.knowledge_base is None:
            self.knowledge_base = KnowledgeBase(base_dir=self.project_root)
        if self.user_memory_manager is None:
            self.user_memory_manager = UserMemoryManager(base_dir=self.project_root)
        if self.interest_tracker is None:
            self.interest_tracker = UserInterestTracker(base_dir=self.project_root)
        if self.astronomical_engine is None:
            self.astronomical_engine = AstronomicalPatternEngine(data_dir=self.project_root / 'data')

        try:
            global ThesidiaHybridAdaptive
            if force_fresh:
                # Reload to ensure latest code
                if 'thesidia_hybrid_adaptive' in sys.modules:
                    importlib.reload(sys.modules['thesidia_hybrid_adaptive'])
                from thesidia_hybrid_adaptive import ThesidiaHybridAdaptive
            
            # Create fresh instance
            self.thesidia = ThesidiaHybridAdaptive(model="dolphin-mistral:latest")
            
            if self.user_memory_manager:
                self.thesidia.user_memory_manager = self.user_memory_manager
            
            self.thesidia.load_state()
            self.thesidia_ready = True
            return True
        except Exception as e:
            print(f"Error during Thesidia initialization: {e}")
            import traceback
            traceback.print_exc()
            self.thesidia_ready = False
            return False

    def get_status(self):
        """Get the current system status."""
        features = {}
        if self.thesidia:
            try:
                features = {
                    'deep_research': getattr(self.thesidia, 'deep_research_engine', None) is not None,
                    'web_search': getattr(self.thesidia, 'web_search', None) is not None,
                    'model_routing': hasattr(self.thesidia, 'capabilities') and getattr(self.thesidia.capabilities, 'model_router', None) is not None,
                }
            except Exception:
                features = {}
                
        return {
            'ollama_status': self.ollama_status,
            'thesidia_ready': self.thesidia_ready,
            'model': self.thesidia.model if self.thesidia else None,
            'features': features,
            'timestamp': datetime.now().isoformat()
        }
