"""
Simple test script to verify clipboard manager functionality
"""

import sys
from PyQt5.QtWidgets import QApplication, QMainWindow, QPushButton, QVBoxLayout, QWidget, QTextEdit
from PyQt5.QtCore import QTimer
from clipboard_manager import ClipboardManager
from clipboard_dialog import ClipboardHistoryDialog
from profile_manager import ProfileManager


class TestWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Clipboard Manager Test")
        self.setGeometry(100, 100, 400, 300)
        
        # Initialize managers
        self.profile_manager = ProfileManager()
        self.clipboard_manager = ClipboardManager(self.profile_manager)
        
        # Setup UI
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        layout = QVBoxLayout(central_widget)
        
        # Text area for testing
        self.text_area = QTextEdit()
        self.text_area.setPlainText("Copy this text to test clipboard manager!\n\nTry copying different text snippets.")
        layout.addWidget(self.text_area)
        
        # Button to open clipboard manager
        open_btn = QPushButton("📋 Open Clipboard Manager")
        open_btn.clicked.connect(self.open_clipboard_manager)
        layout.addWidget(open_btn)
        
        # Button to add test data
        test_btn = QPushButton("🧪 Add Test Data")
        test_btn.clicked.connect(self.add_test_data)
        layout.addWidget(test_btn)
        
        self.clipboard_dialog = None
    
    def open_clipboard_manager(self):
        """Open clipboard manager dialog"""
        if self.clipboard_dialog is None or not self.clipboard_dialog.isVisible():
            self.clipboard_dialog = ClipboardHistoryDialog(self.clipboard_manager, self)
            self.clipboard_dialog.show()
        else:
            self.clipboard_dialog.raise_()
            self.clipboard_dialog.activateWindow()
    
    def add_test_data(self):
        """Add some test data to clipboard history"""
        test_items = [
            "https://www.example.com",
            "This is a test clipboard item",
            "{'key': 'value', 'number': 42}",
            "SELECT * FROM users WHERE active = 1;",
            "Lorem ipsum dolor sit amet, consectetur adipiscing elit."
        ]
        
        clipboard = QApplication.clipboard()
        for i, item in enumerate(test_items):
            clipboard.setText(item)
            # Small delay to ensure each item is processed
            QTimer.singleShot(i * 100, lambda: None)


if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = TestWindow()
    window.show()
    sys.exit(app.exec_())