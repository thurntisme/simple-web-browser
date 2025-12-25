"""
Simple test script to verify command line tool functionality
"""

import sys
from PyQt5.QtWidgets import QApplication, QMainWindow, QVBoxLayout, QWidget
from command_line_tool import CommandLineWidget


class TestWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Command Line Tool Test")
        self.setGeometry(100, 100, 800, 600)
        
        # Setup UI
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        layout = QVBoxLayout(central_widget)
        
        # Add command line widget
        self.cmd_widget = CommandLineWidget(self)
        layout.addWidget(self.cmd_widget)


if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = TestWindow()
    window.show()
    sys.exit(app.exec_())