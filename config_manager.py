"""
Configuration management functionality
"""
import os
import json
from constants import *


class ConfigManager:
    """Manages application configuration"""
    
    def __init__(self, profile_manager):
        self.profile_manager = profile_manager
        self.config = {}
    
    def load(self):
        """Load configuration from JSON file"""
        config_file = self.profile_manager.get_profile_path(CONFIG_FILE)
        try:
            if os.path.exists(config_file):
                with open(config_file, 'r', encoding='utf-8') as f:
                    self.config = json.load(f)
        except Exception as e:
            print(f"Error loading config: {e}")
            self.config = {}
    
    def save(self):
        """Save configuration to JSON file"""
        config_file = self.profile_manager.get_profile_path(CONFIG_FILE)
        try:
            with open(config_file, 'w', encoding='utf-8') as f:
                json.dump(self.config, f, indent=2, ensure_ascii=False)
        except Exception as e:
            print(f"Error saving config: {e}")
    
    def get(self, key, default=None):
        """Get configuration value"""
        return self.config.get(key, default)
    
    def set(self, key, value):
        """Set configuration value"""
        self.config[key] = value
        self.save()
