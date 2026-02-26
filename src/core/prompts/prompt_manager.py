import yaml
import os
from typing import Dict, Any, Optional

class PromptManager:
    """Singleton for managing agent system prompts with live reload support."""
    _instance = None
    _prompts: Dict[str, Any] = {}
    
    def __new__(cls):
        if cls._instance is None:
            cls._instance = super(PromptManager, cls).__new__(cls)
            # Both manager and yaml are now in src/core/prompts/
            cls._instance.current_dir = os.path.dirname(os.path.abspath(__file__))
            cls._instance._yaml_path = os.path.join(cls._instance.current_dir, "prompts.yaml")
            cls._instance._load_prompts()
        return cls._instance
    
    def set_config_path(self, path: str):
        """Changes the target YAML file path and reloads prompts."""
        self._yaml_path = path
        self._load_prompts()
        print(f"🔄 PromptManager: Config path set to {path}")

    def _load_prompts(self):
        """Loads prompts from current YAML file."""
        if not os.path.exists(self._yaml_path):
            print(f"⚠️ Warning: {self._yaml_path} not found. Starting with empty prompts.")
            self._prompts = {}
            return

        try:
            with open(self._yaml_path, "r", encoding="utf-8") as f:
                self._prompts = yaml.safe_load(f) or {}
        except Exception as e:
            print(f"⚠️ Error loading {self._yaml_path}: {e}")
            self._prompts = {}

    def get_prompt(self, target: str, field: str = "system") -> str:
        """Retrieves a specific prompt for an agent node."""
        # Auto-reload logic could be added here if needed, 
        # but for now we'll manually reload or assume singleton persistence.
        node_data = self._prompts.get(target, {})
        return node_data.get(field, "")

    def update_prompt(self, target: str, prompt_text: str, field: str = "system"):
        """Updates a prompt in memory and persists it to YAML."""
        if target not in self._prompts:
            self._prompts[target] = {}
        
        self._prompts[target][field] = prompt_text
        self._save_prompts()

    def _save_prompts(self):
        """Saves current in-memory prompts to current YAML file."""
        try:
            with open(self._yaml_path, "w", encoding="utf-8") as f:
                yaml.dump(self._prompts, f, allow_unicode=True, sort_keys=False)
        except Exception as e:
            print(f"⚠️ Error saving {self._yaml_path}: {e}")

    def reload(self):
        """Force reloads prompts from disk."""
        self._load_prompts()

# Global Instance
prompt_manager = PromptManager()
