"""
Browser utility functions for external browser detection and launching.
"""

import os
import platform
import subprocess
from PyQt5.QtWidgets import QMessageBox


def get_available_browsers():
    """Detect available browsers on the system (cross-platform)"""
    browsers = {}
    system = platform.system()
    
    if system == "Windows":
        # Windows browser paths
        browser_paths = {
            "Google Chrome": [
                r"C:\Program Files\Google\Chrome\Application\chrome.exe",
                r"C:\Program Files (x86)\Google\Chrome\Application\chrome.exe",
            ],
            "Microsoft Edge": [
                r"C:\Program Files (x86)\Microsoft\Edge\Application\msedge.exe",
                r"C:\Program Files\Microsoft\Edge\Application\msedge.exe",
            ],
            "Mozilla Firefox": [
                r"C:\Program Files\Mozilla Firefox\firefox.exe",
                r"C:\Program Files (x86)\Mozilla Firefox\firefox.exe",
            ],
            "Opera": [
                r"C:\Program Files\Opera\launcher.exe",
                r"C:\Program Files (x86)\Opera\launcher.exe",
            ],
            "Brave": [
                r"C:\Program Files\BraveSoftware\Brave-Browser\Application\brave.exe",
                r"C:\Program Files (x86)\BraveSoftware\Brave-Browser\Application\brave.exe",
            ],
        }
        
        # Check which browsers are installed
        for browser_name, paths in browser_paths.items():
            for path in paths:
                if os.path.exists(path):
                    browsers[browser_name] = path
                    break
    
    elif system == "Darwin":  # macOS
        # macOS browser paths
        browser_paths = {
            "Safari": ["/Applications/Safari.app"],
            "Google Chrome": ["/Applications/Google Chrome.app"],
            "Mozilla Firefox": ["/Applications/Firefox.app"],
            "Opera": ["/Applications/Opera.app"],
            "Brave": ["/Applications/Brave Browser.app"],
            "Microsoft Edge": ["/Applications/Microsoft Edge.app"],
        }
        
        # Check which browsers are installed
        for browser_name, paths in browser_paths.items():
            for path in paths:
                if os.path.exists(path):
                    browsers[browser_name] = path
                    break
    
    elif system == "Linux":
        # Linux - try to find browsers in PATH
        browser_commands = {
            "Google Chrome": ["google-chrome", "google-chrome-stable"],
            "Mozilla Firefox": ["firefox"],
            "Opera": ["opera"],
            "Brave": ["brave-browser", "brave"],
            "Chromium": ["chromium", "chromium-browser"],
        }
        
        # Check which browsers are available
        for browser_name, commands in browser_commands.items():
            for cmd in commands:
                try:
                    result = subprocess.run(["which", cmd], 
                                          capture_output=True, 
                                          text=True, 
                                          timeout=1)
                    if result.returncode == 0 and result.stdout.strip():
                        browsers[browser_name] = result.stdout.strip()
                        break
                except:
                    continue
    
    return browsers


def open_in_external_browser(url, browser_path, parent_widget=None):
    """Open URL in external browser (cross-platform)"""
    try:
        system = platform.system()
        
        if system == "Darwin":  # macOS
            # Use 'open' command for .app bundles
            subprocess.Popen(["open", "-a", browser_path, url])
        else:
            # Windows and Linux
            subprocess.Popen([browser_path, url])
    except Exception as e:
        if parent_widget:
            QMessageBox.warning(parent_widget, "Error", f"Failed to open browser:\n{str(e)}")
        else:
            print(f"Failed to open browser: {str(e)}")