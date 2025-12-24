"""
Main entry point for the browser application.
Simplified main.py that imports and uses the refactored modules.
"""

import sys
from PyQt5.QtWidgets import QApplication
from constants import APP_NAME
from browser_window import MainWindow
import styles


def main():
    """Main application entry point"""
    app = QApplication(sys.argv)
    app.setApplicationName(APP_NAME)
    
    # Apply minimal light theme by default
    styles.apply_theme(app, "light")

    window = MainWindow()
    
    # Setup initial tab after all managers are initialized
    window.setup_initial_tab()

    app.exec_()


if __name__ == "__main__":
    main()