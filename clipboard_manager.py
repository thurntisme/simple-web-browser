"""
Clipboard manager for tracking and managing clipboard history.
Stores all clipboard content as a list with timestamps.
"""

import json
import os
from datetime import datetime
from PyQt5.QtCore import QObject, QTimer, pyqtSignal
from PyQt5.QtWidgets import QApplication
from constants import STORAGE_DIR


class ClipboardManager(QObject):
    """Manages clipboard history and provides clipboard utilities"""
    
    # Signal emitted when clipboard content changes
    clipboard_changed = pyqtSignal(str)
    
    def __init__(self, profile_manager):
        super().__init__()
        self.profile_manager = profile_manager
        self.clipboard_history = []
        self.max_history_items = 100  # Maximum items to store
        self.last_clipboard_content = ""
        
        # Setup clipboard monitoring
        self.clipboard = QApplication.clipboard()
        self.clipboard.dataChanged.connect(self.on_clipboard_changed)
        
        # Timer to periodically check clipboard (backup method)
        self.timer = QTimer()
        self.timer.timeout.connect(self.check_clipboard)
        self.timer.start(1000)  # Check every second
        
        self.load()
    
    def get_clipboard_file_path(self):
        """Get the path to the clipboard history file"""
        profile_dir = os.path.join(STORAGE_DIR, "profiles", self.profile_manager.current_profile)
        os.makedirs(profile_dir, exist_ok=True)
        return os.path.join(profile_dir, "clipboard_history.json")
    
    def on_clipboard_changed(self):
        """Handle clipboard change event"""
        try:
            mime_data = self.clipboard.mimeData()
            if mime_data.hasText():
                text = mime_data.text().strip()
                if text and text != self.last_clipboard_content:
                    self.add_to_history(text)
                    self.last_clipboard_content = text
                    self.clipboard_changed.emit(text)
        except Exception as e:
            print(f"Error handling clipboard change: {e}")
    
    def check_clipboard(self):
        """Periodically check clipboard content (backup method)"""
        try:
            current_text = self.clipboard.text().strip()
            if current_text and current_text != self.last_clipboard_content:
                self.add_to_history(current_text)
                self.last_clipboard_content = current_text
                self.clipboard_changed.emit(current_text)
        except Exception as e:
            print(f"Error checking clipboard: {e}")
    
    def add_to_history(self, text):
        """Add text to clipboard history"""
        if not text or len(text.strip()) == 0:
            return
        
        # Remove if already exists (move to top)
        self.clipboard_history = [item for item in self.clipboard_history if item.get('content') != text]
        
        # Add new item at the beginning
        clipboard_item = {
            'content': text,
            'timestamp': datetime.now().isoformat(),
            'length': len(text),
            'preview': text[:100] + "..." if len(text) > 100 else text
        }
        
        self.clipboard_history.insert(0, clipboard_item)
        
        # Limit history size
        if len(self.clipboard_history) > self.max_history_items:
            self.clipboard_history = self.clipboard_history[:self.max_history_items]
        
        # Save to file
        self.save()
    
    def get_history(self):
        """Get clipboard history list"""
        return self.clipboard_history.copy()
    
    def get_item(self, index):
        """Get clipboard item by index"""
        if 0 <= index < len(self.clipboard_history):
            return self.clipboard_history[index]
        return None
    
    def copy_item_to_clipboard(self, index):
        """Copy a history item back to clipboard"""
        item = self.get_item(index)
        if item:
            # Temporarily disconnect to avoid adding it again
            self.clipboard.dataChanged.disconnect(self.on_clipboard_changed)
            self.clipboard.setText(item['content'])
            self.last_clipboard_content = item['content']
            # Reconnect after a short delay
            QTimer.singleShot(100, lambda: self.clipboard.dataChanged.connect(self.on_clipboard_changed))
            return True
        return False
    
    def delete_item(self, index):
        """Delete item from history"""
        if 0 <= index < len(self.clipboard_history):
            del self.clipboard_history[index]
            self.save()
            return True
        return False
    
    def clear_history(self):
        """Clear all clipboard history"""
        self.clipboard_history = []
        self.save()
    
    def search_history(self, query):
        """Search clipboard history for items containing query"""
        query = query.lower()
        results = []
        for i, item in enumerate(self.clipboard_history):
            if query in item['content'].lower():
                results.append((i, item))
        return results
    
    def get_stats(self):
        """Get clipboard statistics"""
        if not self.clipboard_history:
            return {
                'total_items': 0,
                'total_characters': 0,
                'average_length': 0,
                'oldest_item': None,
                'newest_item': None
            }
        
        total_chars = sum(item['length'] for item in self.clipboard_history)
        avg_length = total_chars / len(self.clipboard_history)
        
        return {
            'total_items': len(self.clipboard_history),
            'total_characters': total_chars,
            'average_length': round(avg_length, 1),
            'oldest_item': self.clipboard_history[-1]['timestamp'] if self.clipboard_history else None,
            'newest_item': self.clipboard_history[0]['timestamp'] if self.clipboard_history else None
        }
    
    def load(self):
        """Load clipboard history from file"""
        try:
            clipboard_file = self.get_clipboard_file_path()
            if os.path.exists(clipboard_file):
                with open(clipboard_file, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                    self.clipboard_history = data.get('history', [])
                    self.max_history_items = data.get('max_items', 100)
        except Exception as e:
            print(f"Error loading clipboard history: {e}")
            self.clipboard_history = []
    
    def save(self):
        """Save clipboard history to file"""
        try:
            clipboard_file = self.get_clipboard_file_path()
            data = {
                'history': self.clipboard_history,
                'max_items': self.max_history_items,
                'last_updated': datetime.now().isoformat()
            }
            with open(clipboard_file, 'w', encoding='utf-8') as f:
                json.dump(data, f, indent=2, ensure_ascii=False)
        except Exception as e:
            print(f"Error saving clipboard history: {e}")
    
    def set_max_items(self, max_items):
        """Set maximum number of items to store"""
        self.max_history_items = max_items
        if len(self.clipboard_history) > max_items:
            self.clipboard_history = self.clipboard_history[:max_items]
            self.save()