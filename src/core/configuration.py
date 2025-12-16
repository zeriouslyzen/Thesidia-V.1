#!/usr/bin/env python3
"""
Configuration Management - Feature flags and runtime configuration
Provides configuration validation and runtime updates
"""

from typing import Dict, Any, Optional, List, Set
from pathlib import Path
import json
from datetime import datetime
import threading


class Configuration:
    """
    Centralized configuration management with feature flags.
    
    Provides:
    - Feature flag management
    - Configuration validation
    - Runtime configuration updates
    - Configuration persistence
    """
    
    def __init__(self, config_file: Optional[Path] = None):
        """
        Initialize configuration manager.
        
        Args:
            config_file: Optional path to configuration file
        """
        self.config_file = config_file
        self._config: Dict[str, Any] = {}
        self._feature_flags: Dict[str, bool] = {}
        self._lock = threading.Lock()
        
        # Default feature flags
        self._default_feature_flags = {
            "hierarchical_memory": False,
            "multimodal_memory": False,
            "psych_inspired_memory": False,
            "neural_symbolic_hybrid": False,
            "multi_agent_system": False,
            "deepseek_integration": False,
            "kimi_integration": False,
            "uncensored_agi": False,
            "intel_acceleration": False,
            "autonomous_tool_calling": False,
            "long_context": False,
            "atomspace": False,
            "embodied_memory": False
        }
        
        # Initialize with defaults
        self._feature_flags = self._default_feature_flags.copy()
        
        # Load from file if provided
        if config_file and config_file.exists():
            self.load_from_file(config_file)
    
    def enable_feature(self, feature_name: str) -> bool:
        """
        Enable a feature flag.
        
        Args:
            feature_name: Name of feature to enable
            
        Returns:
            True if enabled, False if feature doesn't exist
        """
        with self._lock:
            if feature_name in self._feature_flags:
                self._feature_flags[feature_name] = True
                return True
            return False
    
    def disable_feature(self, feature_name: str) -> bool:
        """
        Disable a feature flag.
        
        Args:
            feature_name: Name of feature to disable
            
        Returns:
            True if disabled, False if feature doesn't exist
        """
        with self._lock:
            if feature_name in self._feature_flags:
                self._feature_flags[feature_name] = False
                return True
            return False
    
    def is_feature_enabled(self, feature_name: str) -> bool:
        """
        Check if a feature is enabled.
        
        Args:
            feature_name: Name of feature to check
            
        Returns:
            True if enabled, False otherwise
        """
        with self._lock:
            return self._feature_flags.get(feature_name, False)
    
    def get_enabled_features(self) -> List[str]:
        """
        Get list of enabled feature flags.
        
        Returns:
            List of enabled feature names
        """
        with self._lock:
            return [name for name, enabled in self._feature_flags.items() if enabled]
    
    def set_config(self, key: str, value: Any):
        """
        Set a configuration value.
        
        Args:
            key: Configuration key
            value: Configuration value
        """
        with self._lock:
            self._config[key] = value
    
    def get_config(self, key: str, default: Any = None) -> Any:
        """
        Get a configuration value.
        
        Args:
            key: Configuration key
            default: Default value if key not found
            
        Returns:
            Configuration value or default
        """
        with self._lock:
            return self._config.get(key, default)
    
    def load_from_file(self, config_file: Path):
        """
        Load configuration from JSON file.
        
        Args:
            config_file: Path to configuration file
        """
        try:
            with open(config_file, 'r') as f:
                data = json.load(f)
                
            with self._lock:
                # Load feature flags
                if "feature_flags" in data:
                    for flag, value in data["feature_flags"].items():
                        if flag in self._feature_flags:
                            self._feature_flags[flag] = value
                
                # Load config
                if "config" in data:
                    self._config.update(data["config"])
        except Exception as e:
            print(f"Error loading configuration from {config_file}: {e}")
    
    def save_to_file(self, config_file: Optional[Path] = None):
        """
        Save configuration to JSON file.
        
        Args:
            config_file: Optional path (uses self.config_file if not provided)
        """
        target_file = config_file or self.config_file
        if not target_file:
            return
        
        try:
            data = {
                "feature_flags": self._feature_flags.copy(),
                "config": self._config.copy(),
                "saved_at": datetime.now().isoformat()
            }
            
            target_file.parent.mkdir(parents=True, exist_ok=True)
            with open(target_file, 'w') as f:
                json.dump(data, f, indent=2)
        except Exception as e:
            print(f"Error saving configuration to {target_file}: {e}")
    
    def validate_config(self) -> List[str]:
        """
        Validate configuration and return any errors.
        
        Returns:
            List of validation error messages
        """
        errors = []
        
        # Validate feature flags
        for flag_name in self._feature_flags:
            if not isinstance(self._feature_flags[flag_name], bool):
                errors.append(f"Feature flag '{flag_name}' must be boolean")
        
        # Add custom validation logic here
        
        return errors
    
    def get_all_config(self) -> Dict[str, Any]:
        """
        Get all configuration as dictionary.
        
        Returns:
            Dictionary with all configuration
        """
        with self._lock:
            return {
                "feature_flags": self._feature_flags.copy(),
                "config": self._config.copy()
            }
    
    def reset_to_defaults(self):
        """Reset configuration to defaults."""
        with self._lock:
            self._feature_flags = self._default_feature_flags.copy()
            self._config = {}


# Global configuration instance
_global_config: Optional[Configuration] = None


def get_configuration() -> Configuration:
    """
    Get the global configuration instance.
    
    Returns:
        Global Configuration instance
    """
    global _global_config
    if _global_config is None:
        config_file = Path("data") / "config" / "thesidia_config.json"
        _global_config = Configuration(config_file=config_file)
    return _global_config


def set_configuration(config: Configuration):
    """
    Set the global configuration instance.
    
    Args:
        config: Configuration instance to use globally
    """
    global _global_config
    _global_config = config

