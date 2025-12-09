"""
History management functionality
"""
import os
import json
from datetime import datetime
from constants import *


class HistoryManager:
    """Manages browsing history"""
    
    def __init__(self, profile_manager):
        self.profile_manager = profile_manager
        self.history = []
        self.enabled = False
    
    def load(self):
        """Load browsing history from JSON file"""
        history_file = self.profile_manager.get_profile_path(HISTORY_FILE)
        try:
            if os.path.exists(history_file):
                with open(history_file, 'r', encoding='utf-8') as f:
                    self.history = json.load(f)
        except Exception as e:
            print(f"Error loading history: {e}")
            self.history = []
    
    def save(self):
        """Save browsing history to JSON file"""
        history_file = self.profile_manager.get_profile_path(HISTORY_FILE)
        try:
            with open(history_file, 'w', encoding='utf-8') as f:
                json.dump(self.history, f, indent=2, ensure_ascii=False)
        except Exception as e:
            print(f"Error saving history: {e}")
    
    def add(self, url, title):
        """Add a URL to browsing history (keeps last 20 entries)"""
        if not self.enabled:
            return
            
        if not url or url == "about:blank":
            return
        
        entry = {
            "url": url,
            "title": title if title else url,
            "timestamp": datetime.now().isoformat()
        }
        
        # Avoid duplicate consecutive entries
        if self.history and self.history[-1].get("url") == url:
            return
        
        self.history.append(entry)
        
        # Keep only last entries
        if len(self.history) > MAX_HISTORY_ENTRIES:
            self.history = self.history[-MAX_HISTORY_ENTRIES:]
        
        self.save()
    
    def clear(self):
        """Clear all browsing history"""
        self.history = []
        self.save()
    
    def get_all(self):
        """Get all history entries"""
        return self.history
