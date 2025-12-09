"""
Bookmark management functionality
"""
import os
import json
from datetime import datetime
from PyQt5.QtWidgets import (QDialog, QVBoxLayout, QHBoxLayout, QListWidget, 
                             QPushButton, QInputDialog, QLineEdit, QMessageBox)
from constants import *


class BookmarkManager:
    """Manages bookmarks"""
    
    def __init__(self, profile_manager):
        self.profile_manager = profile_manager
        self.bookmarks = []
    
    def load(self):
        """Load bookmarks from JSON file"""
        bookmarks_file = self.profile_manager.get_profile_path(BOOKMARKS_FILE)
        try:
            if os.path.exists(bookmarks_file):
                with open(bookmarks_file, 'r', encoding='utf-8') as f:
                    self.bookmarks = json.load(f)
        except Exception as e:
            print(f"Error loading bookmarks: {e}")
            self.bookmarks = []
    
    def save(self):
        """Save bookmarks to JSON file"""
        bookmarks_file = self.profile_manager.get_profile_path(BOOKMARKS_FILE)
        try:
            with open(bookmarks_file, 'w', encoding='utf-8') as f:
                json.dump(self.bookmarks, f, indent=2, ensure_ascii=False)
        except Exception as e:
            print(f"Error saving bookmarks: {e}")
    
    def add(self, url, title):
        """Add a bookmark"""
        bookmark = {
            "title": title,
            "url": url,
            "timestamp": datetime.now().isoformat()
        }
        self.bookmarks.append(bookmark)
        self.save()
    
    def remove(self, index):
        """Remove a bookmark by index"""
        if 0 <= index < len(self.bookmarks):
            del self.bookmarks[index]
            self.save()
    
    def update(self, index, title):
        """Update bookmark title"""
        if 0 <= index < len(self.bookmarks):
            self.bookmarks[index]["title"] = title
            self.save()
    
    def is_bookmarked(self, url):
        """Check if URL is bookmarked"""
        for bookmark in self.bookmarks:
            if bookmark.get("url") == url:
                return True
        return False
    
    def find_by_url(self, url):
        """Find bookmark index by URL"""
        for i, bookmark in enumerate(self.bookmarks):
            if bookmark.get("url") == url:
                return i
        return -1
    
    def get_all(self):
        """Get all bookmarks"""
        return self.bookmarks


class BookmarkManagerDialog(QDialog):
    """Dialog for managing bookmarks"""
    def __init__(self, bookmarks, parent=None):
        super().__init__(parent)
        self.bookmarks = bookmarks.copy()
        self.setWindowTitle("Manage Bookmarks")
        self.setMinimumSize(600, 400)
        
        layout = QVBoxLayout()
        
        # List widget
        self.list_widget = QListWidget()
        self.update_list()
        layout.addWidget(self.list_widget)
        
        # Buttons
        button_layout = QHBoxLayout()
        
        edit_btn = QPushButton("Edit")
        edit_btn.clicked.connect(self.edit_bookmark)
        button_layout.addWidget(edit_btn)
        
        delete_btn = QPushButton("Delete")
        delete_btn.clicked.connect(self.delete_bookmark)
        button_layout.addWidget(delete_btn)
        
        button_layout.addStretch()
        
        close_btn = QPushButton("Close")
        close_btn.clicked.connect(self.accept)
        button_layout.addWidget(close_btn)
        
        layout.addLayout(button_layout)
        self.setLayout(layout)
    
    def update_list(self):
        """Update the bookmark list"""
        self.list_widget.clear()
        for bookmark in self.bookmarks:
            title = bookmark.get("title", "Untitled")
            url = bookmark.get("url", "")
            self.list_widget.addItem(f"{title} - {url}")
    
    def edit_bookmark(self):
        """Edit selected bookmark"""
        current_row = self.list_widget.currentRow()
        if current_row < 0:
            QMessageBox.warning(self, "Edit Bookmark", "Please select a bookmark to edit.")
            return
        
        bookmark = self.bookmarks[current_row]
        new_title, ok = QInputDialog.getText(self, "Edit Bookmark", 
                                              "Bookmark name:", 
                                              QLineEdit.Normal, 
                                              bookmark.get("title", ""))
        
        if ok and new_title:
            self.bookmarks[current_row]["title"] = new_title
            self.update_list()
    
    def delete_bookmark(self):
        """Delete selected bookmark"""
        current_row = self.list_widget.currentRow()
        if current_row < 0:
            QMessageBox.warning(self, "Delete Bookmark", "Please select a bookmark to delete.")
            return
        
        reply = QMessageBox.question(self, "Delete Bookmark", 
                                      "Are you sure you want to delete this bookmark?",
                                      QMessageBox.Yes | QMessageBox.No)
        
        if reply == QMessageBox.Yes:
            del self.bookmarks[current_row]
            self.update_list()
    
    def get_bookmarks(self):
        """Return the modified bookmarks list"""
        return self.bookmarks
