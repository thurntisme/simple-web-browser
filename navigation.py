"""
Navigation functionality for the browser.
Handles URL navigation, welcome page generation, and external browser integration.
"""

from PyQt5.QtCore import *
from PyQt5.QtWidgets import *
from PyQt5.QtGui import *
from urllib.parse import quote
from constants import *
import browser_utils


class NavigationManager:
    """Manages browser navigation functionality"""
    
    def __init__(self, main_window):
        self.main_window = main_window
    
    def navigate_home(self):
        """Navigate to home page"""
        browser = self.main_window.tab_manager.get_current_browser()
        if browser:
            use_welcome = self.main_window.config_manager.get("use_welcome_page", True)
            if use_welcome:
                browser.setUrl(self.get_welcome_page_url())
            else:
                home_url = self.main_window.config_manager.get("home_url", DEFAULT_HOME_URL)
                browser.setUrl(QUrl(home_url))

    def navigate_to_url(self):
        """Navigate to URL from address bar"""
        text = self.main_window.urlbar.text().strip()
        browser = self.main_window.tab_manager.get_current_browser()
        if not browser:
            return
        
        # Check for special "welcome" keyword
        if text.lower() == "welcome":
            browser.setUrl(self.get_welcome_page_url())
            return
        
        # Check if it looks like a URL (has dots and no spaces)
        if "." in text and " " not in text:
            q = QUrl(text)
            if q.scheme() == "":
                q.setScheme(DEFAULT_PROTOCOL)
            browser.setUrl(q)
        else:
            # Treat as search query - use configured search engine
            search_engine = self.main_window.config_manager.get("search_engine", SEARCH_ENGINE_URL)
            search_url = search_engine.format(text.replace(" ", "+"))
            browser.setUrl(QUrl(search_url))
    
    def get_welcome_page_url(self):
        """Generate welcome page with session stats"""
        # Read welcome page template
        with open('welcome_page.html', 'r', encoding='utf-8') as f:
            html_content = f.read()
        
        # Replace placeholders with actual data
        session_start = self.main_window.session_tracker.session_start.strftime("%I:%M %p")
        sessions_today = self.main_window.session_tracker.get_sessions_today()
        
        html_content = html_content.replace('SESSION_START_PLACEHOLDER', session_start)
        html_content = html_content.replace('SESSIONS_TODAY_PLACEHOLDER', str(sessions_today))
        
        # Create a data URL
        data_url = f"data:text/html;charset=utf-8,{quote(html_content)}"
        return QUrl(data_url)
    
    def reload_page(self):
        """Reload current page"""
        browser = self.main_window.tab_manager.get_current_browser()
        if browser:
            browser.reload()
    
    def create_open_with_menu(self):
        """Create dropdown menu for opening in external browsers"""
        menu = QMenu(self.main_window)
        
        # Detect available browsers
        browsers = browser_utils.get_available_browsers()
        
        if browsers:
            for browser_name, browser_path in browsers.items():
                action = QAction(browser_name, self.main_window)
                action.triggered.connect(
                    lambda checked, name=browser_name, path=browser_path: 
                    self.open_current_url_in_browser(path)
                )
                menu.addAction(action)
        else:
            no_browser_action = QAction("No browsers found", self.main_window)
            no_browser_action.setEnabled(False)
            menu.addAction(no_browser_action)
        
        return menu
    
    def open_current_url_in_browser(self, browser_path):
        """Open current URL in external browser"""
        browser = self.main_window.tab_manager.get_current_browser()
        if browser:
            url = browser.url().toString()
            if url and url != "about:blank":
                browser_utils.open_in_external_browser(url, browser_path, self.main_window)
            else:
                QMessageBox.information(self.main_window, "No URL", "No valid URL to open.")