"""
Clipboard history dialog for viewing and managing clipboard content.
"""

from PyQt5.QtCore import *
from PyQt5.QtWidgets import *
from PyQt5.QtGui import *
from datetime import datetime
import styles


class ClipboardHistoryDialog(QDialog):
    """Dialog for viewing and managing clipboard history"""
    
    def __init__(self, clipboard_manager, parent=None):
        super().__init__(parent)
        self.clipboard_manager = clipboard_manager
        self.setup_ui()
        self.load_history()
        
        # Connect to clipboard changes
        self.clipboard_manager.clipboard_changed.connect(self.on_clipboard_changed)
    
    def setup_ui(self):
        """Setup the dialog UI"""
        self.setWindowTitle("📋 Clipboard Manager")
        self.setModal(False)
        self.resize(600, 500)
        
        layout = QVBoxLayout(self)
        
        # Header with stats and controls
        header_layout = QHBoxLayout()
        
        # Stats label
        self.stats_label = QLabel()
        self.update_stats()
        header_layout.addWidget(self.stats_label)
        
        header_layout.addStretch()
        
        # Search box
        self.search_box = QLineEdit()
        self.search_box.setPlaceholderText("🔍 Search clipboard history...")
        self.search_box.textChanged.connect(self.filter_history)
        self.search_box.setMaximumWidth(200)
        header_layout.addWidget(self.search_box)
        
        # Clear button
        clear_btn = QPushButton("🗑️ Clear All")
        clear_btn.clicked.connect(self.clear_history)
        clear_btn.setMaximumWidth(100)
        header_layout.addWidget(clear_btn)
        
        layout.addLayout(header_layout)
        
        # Clipboard history list
        self.history_list = QListWidget()
        self.history_list.setAlternatingRowColors(True)
        self.history_list.itemDoubleClicked.connect(self.copy_selected_item)
        self.history_list.setContextMenuPolicy(Qt.CustomContextMenu)
        self.history_list.customContextMenuRequested.connect(self.show_context_menu)
        layout.addWidget(self.history_list)
        
        # Bottom buttons
        button_layout = QHBoxLayout()
        
        copy_btn = QPushButton("📋 Copy Selected")
        copy_btn.clicked.connect(self.copy_selected_item)
        button_layout.addWidget(copy_btn)
        
        delete_btn = QPushButton("🗑️ Delete Selected")
        delete_btn.clicked.connect(self.delete_selected_item)
        button_layout.addWidget(delete_btn)
        
        button_layout.addStretch()
        
        settings_btn = QPushButton("⚙️ Settings")
        settings_btn.clicked.connect(self.show_settings)
        button_layout.addWidget(settings_btn)
        
        close_btn = QPushButton("✖️ Close")
        close_btn.clicked.connect(self.close)
        button_layout.addWidget(close_btn)
        
        layout.addLayout(button_layout)
        
        # Status bar
        self.status_label = QLabel("Ready")
        layout.addWidget(self.status_label)
    
    def load_history(self):
        """Load clipboard history into the list"""
        self.history_list.clear()
        history = self.clipboard_manager.get_history()
        
        for i, item in enumerate(history):
            # Create list item
            list_item = QListWidgetItem()
            
            # Format timestamp
            try:
                timestamp = datetime.fromisoformat(item['timestamp'])
                time_str = timestamp.strftime("%H:%M:%S")
                date_str = timestamp.strftime("%Y-%m-%d")
            except:
                time_str = "Unknown"
                date_str = "Unknown"
            
            # Create item text
            preview = item['preview']
            length = item['length']
            
            # Format the display text
            display_text = f"[{time_str}] {preview}"
            if length > 100:
                display_text += f" ({length} chars)"
            
            list_item.setText(display_text)
            list_item.setData(Qt.UserRole, i)  # Store index
            
            # Set tooltip with full content (limited)
            tooltip_content = item['content'][:500]
            if len(item['content']) > 500:
                tooltip_content += "..."
            list_item.setToolTip(f"Date: {date_str}\nTime: {time_str}\nLength: {length} characters\n\nContent:\n{tooltip_content}")
            
            self.history_list.addItem(list_item)
        
        self.update_stats()
    
    def filter_history(self):
        """Filter history based on search query"""
        query = self.search_box.text().strip()
        
        if not query:
            self.load_history()
            return
        
        self.history_list.clear()
        results = self.clipboard_manager.search_history(query)
        
        for original_index, item in results:
            list_item = QListWidgetItem()
            
            # Format timestamp
            try:
                timestamp = datetime.fromisoformat(item['timestamp'])
                time_str = timestamp.strftime("%H:%M:%S")
                date_str = timestamp.strftime("%Y-%m-%d")
            except:
                time_str = "Unknown"
                date_str = "Unknown"
            
            # Highlight search term in preview
            preview = item['preview']
            length = item['length']
            
            display_text = f"[{time_str}] {preview}"
            if length > 100:
                display_text += f" ({length} chars)"
            
            list_item.setText(display_text)
            list_item.setData(Qt.UserRole, original_index)
            
            # Set tooltip
            tooltip_content = item['content'][:500]
            if len(item['content']) > 500:
                tooltip_content += "..."
            list_item.setToolTip(f"Date: {date_str}\nTime: {time_str}\nLength: {length} characters\n\nContent:\n{tooltip_content}")
            
            self.history_list.addItem(list_item)
        
        self.status_label.setText(f"Found {len(results)} items matching '{query}'")
    
    def copy_selected_item(self):
        """Copy selected item to clipboard"""
        current_item = self.history_list.currentItem()
        if current_item:
            index = current_item.data(Qt.UserRole)
            if self.clipboard_manager.copy_item_to_clipboard(index):
                self.status_label.setText("✅ Copied to clipboard")
                QTimer.singleShot(2000, lambda: self.status_label.setText("Ready"))
    
    def delete_selected_item(self):
        """Delete selected item from history"""
        current_item = self.history_list.currentItem()
        if current_item:
            reply = QMessageBox.question(
                self, 
                "Delete Item", 
                "Are you sure you want to delete this clipboard item?",
                QMessageBox.Yes | QMessageBox.No,
                QMessageBox.No
            )
            
            if reply == QMessageBox.Yes:
                index = current_item.data(Qt.UserRole)
                if self.clipboard_manager.delete_item(index):
                    self.load_history()
                    self.status_label.setText("🗑️ Item deleted")
                    QTimer.singleShot(2000, lambda: self.status_label.setText("Ready"))
    
    def clear_history(self):
        """Clear all clipboard history"""
        reply = QMessageBox.question(
            self, 
            "Clear History", 
            "Are you sure you want to clear all clipboard history?\n\nThis action cannot be undone!",
            QMessageBox.Yes | QMessageBox.No,
            QMessageBox.No
        )
        
        if reply == QMessageBox.Yes:
            self.clipboard_manager.clear_history()
            self.load_history()
            self.status_label.setText("🗑️ History cleared")
            QTimer.singleShot(2000, lambda: self.status_label.setText("Ready"))
    
    def show_context_menu(self, position):
        """Show context menu for list items"""
        item = self.history_list.itemAt(position)
        if not item:
            return
        
        menu = QMenu(self)
        
        copy_action = menu.addAction("📋 Copy to Clipboard")
        copy_action.triggered.connect(self.copy_selected_item)
        
        menu.addSeparator()
        
        delete_action = menu.addAction("🗑️ Delete Item")
        delete_action.triggered.connect(self.delete_selected_item)
        
        menu.addSeparator()
        
        view_action = menu.addAction("👁️ View Full Content")
        view_action.triggered.connect(self.view_full_content)
        
        menu.exec_(self.history_list.mapToGlobal(position))
    
    def view_full_content(self):
        """View full content of selected item"""
        current_item = self.history_list.currentItem()
        if current_item:
            index = current_item.data(Qt.UserRole)
            item = self.clipboard_manager.get_item(index)
            if item:
                dialog = QDialog(self)
                dialog.setWindowTitle("📄 Full Content")
                dialog.resize(500, 400)
                
                layout = QVBoxLayout(dialog)
                
                # Info label
                try:
                    timestamp = datetime.fromisoformat(item['timestamp'])
                    time_str = timestamp.strftime("%Y-%m-%d %H:%M:%S")
                except:
                    time_str = "Unknown"
                
                info_label = QLabel(f"Copied: {time_str} | Length: {item['length']} characters")
                layout.addWidget(info_label)
                
                # Content text area
                text_area = QTextEdit()
                text_area.setPlainText(item['content'])
                text_area.setReadOnly(True)
                layout.addWidget(text_area)
                
                # Close button
                close_btn = QPushButton("Close")
                close_btn.clicked.connect(dialog.close)
                layout.addWidget(close_btn)
                
                dialog.exec_()
    
    def show_settings(self):
        """Show clipboard manager settings"""
        dialog = QDialog(self)
        dialog.setWindowTitle("⚙️ Clipboard Settings")
        dialog.resize(300, 200)
        
        layout = QVBoxLayout(dialog)
        
        # Max items setting
        max_items_layout = QHBoxLayout()
        max_items_layout.addWidget(QLabel("Maximum items to store:"))
        
        max_items_spin = QSpinBox()
        max_items_spin.setRange(10, 1000)
        max_items_spin.setValue(self.clipboard_manager.max_history_items)
        max_items_layout.addWidget(max_items_spin)
        
        layout.addLayout(max_items_layout)
        
        # Buttons
        button_layout = QHBoxLayout()
        
        save_btn = QPushButton("💾 Save")
        save_btn.clicked.connect(lambda: self.save_settings(max_items_spin.value(), dialog))
        button_layout.addWidget(save_btn)
        
        cancel_btn = QPushButton("❌ Cancel")
        cancel_btn.clicked.connect(dialog.close)
        button_layout.addWidget(cancel_btn)
        
        layout.addLayout(button_layout)
        
        dialog.exec_()
    
    def save_settings(self, max_items, dialog):
        """Save clipboard settings"""
        self.clipboard_manager.set_max_items(max_items)
        self.status_label.setText("⚙️ Settings saved")
        QTimer.singleShot(2000, lambda: self.status_label.setText("Ready"))
        dialog.close()
    
    def update_stats(self):
        """Update statistics display"""
        stats = self.clipboard_manager.get_stats()
        self.stats_label.setText(f"📊 {stats['total_items']} items | {stats['total_characters']} chars | Avg: {stats['average_length']}")
    
    def on_clipboard_changed(self, content):
        """Handle clipboard change signal"""
        # Reload history to show new item
        if not self.search_box.text().strip():  # Only if not searching
            self.load_history()
        self.status_label.setText("📋 New clipboard item added")
        QTimer.singleShot(2000, lambda: self.status_label.setText("Ready"))