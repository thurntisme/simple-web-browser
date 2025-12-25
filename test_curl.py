"""
Simple test script to verify curl tool functionality
"""

import sys
from PyQt5.QtWidgets import QApplication, QMainWindow, QPushButton, QVBoxLayout, QWidget
from curl_tool import CurlDialog


class TestWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Curl Tool Test")
        self.setGeometry(100, 100, 300, 200)
        
        # Setup UI
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        layout = QVBoxLayout(central_widget)
        
        # Button to open curl tool
        open_btn = QPushButton("🌐 Open Curl Tool")
        open_btn.clicked.connect(self.open_curl_tool)
        layout.addWidget(open_btn)
        
        self.curl_dialog = None
    
    def open_curl_tool(self):
        """Open curl tool dialog"""
        if self.curl_dialog is None or not self.curl_dialog.isVisible():
            self.curl_dialog = CurlDialog(self)
            self.curl_dialog.show()
        else:
            self.curl_dialog.raise_()
            self.curl_dialog.activateWindow()


if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = TestWindow()
    window.show()
    sys.exit(app.exec_())