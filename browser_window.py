"""
Main browser window class.
Contains the primary application window and UI setup.
"""

from PyQt5.QtCore import *
from PyQt5.QtWidgets import *
from PyQt5.QtGui import *
from PyQt5.QtWebEngineWidgets import *
import os

from constants import *
from profile_manager import ProfileManager
from history_manager import HistoryManager
from bookmark_manager import BookmarkManager
from config_manager import ConfigManager
from session_tracker import SessionTracker
import ui_helpers
import styles

from dialogs import AboutDialog, BrowserSettingsDialog
from tab_manager import TabManager
from navigation import NavigationManager


class MainWindow(QMainWindow):
    """Main browser window"""
    
    def __init__(self, *args, **kwargs):
        super(MainWindow, self).__init__(*args, **kwargs)

        # Initialize managers
        self.profile_manager = ProfileManager()
        self.config_manager = ConfigManager(self.profile_manager)
        self.config_manager.load()
        
        self.history_manager = HistoryManager(self.profile_manager)
        self.history_manager.enabled = self.config_manager.get("history_enabled", False)
        self.history_manager.load()
        
        self.bookmark_manager = BookmarkManager(self.profile_manager)
        self.bookmark_manager.load()
        
        self.session_tracker = SessionTracker(self.profile_manager)

        # Initialize UI components
        self.setup_tabs()
        self.setup_status_bar()
        self.setup_toolbar()
        self.setup_menus()
        
        # Initialize managers that depend on UI
        self.tab_manager = TabManager(self)
        self.navigation_manager = NavigationManager(self)
        
        # Load initial page
        self.load_initial_page()
        
        # Window setup
        self.setWindowTitle(WINDOW_TITLE)
        self.setWindowIcon(QIcon(os.path.join(IMAGES_DIR, ICON_APP_64)))

    def setup_tabs(self):
        """Setup tab widget"""
        self.tabs = QTabWidget()
        self.tabs.setDocumentMode(True)
        self.tabs.tabBarDoubleClicked.connect(self.tab_open_doubleclick)
        self.tabs.currentChanged.connect(self.current_tab_changed)
        self.tabs.setTabsClosable(False)
        self.setCentralWidget(self.tabs)

    def setup_status_bar(self):
        """Setup status bar with widgets"""
        self.status = QStatusBar()
        self.setStatusBar(self.status)
        
        # Status bar widgets with modern styling
        self.status_profile = QLabel()
        self.status_profile.setStyleSheet(styles.get_profile_label_style())
        self.status_profile.setMinimumWidth(80)
        self.status_profile.setText(f"Profile: {self.profile_manager.current_profile}")
        self.status.addWidget(self.status_profile)
        
        self.status_title = QLabel()
        self.status_title.setMinimumWidth(200)
        self.status.addWidget(self.status_title)
        
        self.status_progress = QProgressBar()
        self.status_progress.setMaximumWidth(150)
        self.status_progress.setVisible(False)
        self.status.addPermanentWidget(self.status_progress)
        
        self.status_info = QLabel()
        self.status.addPermanentWidget(self.status_info)

    def setup_toolbar(self):
        """Setup navigation toolbar"""
        navtb = QToolBar("Navigation")
        self.addToolBar(navtb)

        # Home button
        home_btn = QAction("Home", self)
        home_btn.setStatusTip("Go home")
        home_btn.triggered.connect(self.navigate_home)
        navtb.addAction(home_btn)

        # Reload button
        reload_btn = QAction("Reload", self)
        reload_btn.setStatusTip("Reload page")
        reload_btn.triggered.connect(self.reload_page)
        navtb.addAction(reload_btn)

        navtb.addSeparator()

        # URL bar
        self.urlbar = QLineEdit()
        self.urlbar.returnPressed.connect(self.navigate_to_url)
        navtb.addWidget(self.urlbar)
        
        # Open with browser dropdown button
        self.open_with_btn = QPushButton("🌐")
        self.open_with_btn.setObjectName("openWithBtn")
        self.open_with_btn.setMaximumWidth(35)
        self.open_with_btn.setStatusTip("Open in external browser")
        navtb.addWidget(self.open_with_btn)
        
        # Bookmark button
        self.bookmark_btn = QPushButton("☆")
        self.bookmark_btn.setObjectName("bookmarkBtn")
        self.bookmark_btn.setMaximumWidth(30)
        self.bookmark_btn.setStatusTip("Add/Remove bookmark")
        self.bookmark_btn.clicked.connect(lambda: ui_helpers.toggle_bookmark(self))
        navtb.addWidget(self.bookmark_btn)
        
        # History toggle button
        self.history_toggle_btn = QPushButton()
        self.history_toggle_btn.setMaximumWidth(80)
        self.history_toggle_btn.setCheckable(True)
        self.history_toggle_btn.setChecked(self.history_manager.enabled)
        # Apply initial styling
        self.history_toggle_btn.setStyleSheet(styles.get_history_button_style(self.history_manager.enabled))
        ui_helpers.update_history_toggle_button(self)
        self.history_toggle_btn.clicked.connect(lambda: ui_helpers.toggle_history(self))
        navtb.addWidget(self.history_toggle_btn)

    def setup_menus(self):
        """Setup application menus"""
        # Bookmarks menu
        self.bookmarks_menu = self.menuBar().addMenu("&Bookmarks")
        ui_helpers.update_bookmarks_menu(self)

        # History menu
        self.history_menu = self.menuBar().addMenu("&History")
        ui_helpers.update_history_menu(self)

        # Tools menu
        tools_menu = self.menuBar().addMenu("&Tools")
        
        dev_tools_action = QAction("Toggle Dev Tools", self)
        dev_tools_action.setShortcut("F12")
        dev_tools_action.setStatusTip("Show/Hide Developer Tools")
        dev_tools_action.triggered.connect(self.toggle_current_dev_tools)
        tools_menu.addAction(dev_tools_action)
        
        tools_menu.addSeparator()
        
        # Theme toggle action
        theme_action = QAction("Toggle Theme (Dark/Light)", self)
        theme_action.setShortcut("Ctrl+T")
        theme_action.setStatusTip("Switch between dark and light themes")
        theme_action.triggered.connect(self.toggle_theme)
        tools_menu.addAction(theme_action)

        # Profile menu
        self.profile_menu = self.menuBar().addMenu("&Profile")
        ui_helpers.update_profile_menu(self)

        # Help menu
        help_menu = self.menuBar().addMenu("&Help")
        about_action = QAction(QIcon(os.path.join(IMAGES_DIR, ICON_ABOUT)), f"About {APP_NAME}", self)
        about_action.setStatusTip(f"Find out more about {APP_NAME}")
        about_action.triggered.connect(self.about)
        help_menu.addAction(about_action)

        help_menu.addSeparator()

        settings_action = QAction("Browser Settings", self)
        settings_action.setStatusTip("Configure browser settings")
        settings_action.triggered.connect(self.show_browser_settings)
        help_menu.addAction(settings_action)

        reset_action = QAction("Reset to Default", self)
        reset_action.setStatusTip("Clear all profile data (history, bookmarks, config)")
        reset_action.triggered.connect(self.reset_profile)
        help_menu.addAction(reset_action)

    def load_initial_page(self):
        """Load home page (welcome or custom URL)"""
        use_welcome = self.config_manager.get("use_welcome_page", True)
        if use_welcome:
            # Will be set after tab_manager is initialized
            pass
        else:
            home_url = self.config_manager.get("home_url", DEFAULT_HOME_URL)
            # Will be set after tab_manager is initialized
            pass
    
    # Delegate methods to managers
    def navigate_home(self):
        """Navigate to home page"""
        self.navigation_manager.navigate_home()
    
    def navigate_to_url(self):
        """Navigate to URL from address bar"""
        self.navigation_manager.navigate_to_url()
    
    def reload_page(self):
        """Reload current page"""
        self.navigation_manager.reload_page()
    
    def tab_open_doubleclick(self, i):
        """Handle double-click on tab bar"""
        self.tab_manager.tab_open_doubleclick(i)

    def current_tab_changed(self, i):
        """Handle tab change event"""
        self.tab_manager.current_tab_changed(i)
    
    def toggle_current_dev_tools(self):
        """Toggle dev tools for current tab"""
        self.tab_manager.toggle_current_dev_tools()
    
    def toggle_theme(self):
        """Toggle between light and dark themes"""
        from PyQt5.QtWidgets import QApplication
        app = QApplication.instance()
        new_theme = styles.toggle_theme(app)
        
        # Update button styles to match new theme
        ui_helpers.update_history_toggle_button(self)
        ui_helpers.update_bookmark_button(self)
        
        # Update profile label style
        self.status_profile.setStyleSheet(styles.get_profile_label_style())
        
        # Show notification
        theme_name = "Light" if new_theme == "light" else "Dark"
        self.status_info.setText(f"Switched to {theme_name} theme")
    
    def get_current_browser(self):
        """Get current browser view"""
        return self.tab_manager.get_current_browser()
    
    def add_new_tab(self, qurl=None, label=DEFAULT_TAB_LABEL):
        """Add new tab"""
        self.tab_manager.add_new_tab(qurl, label)
    
    def get_welcome_page_url(self):
        """Get welcome page URL"""
        return self.navigation_manager.get_welcome_page_url()
    
    def apply_font_size(self, font_size):
        """Apply font size to all tabs"""
        self.tab_manager.apply_font_size(font_size)
    
    # UI update methods
    def update_title(self, browser):
        """Update window title"""
        current_browser = self.get_current_browser()
        if browser != current_browser:
            return

        title = browser.page().title()
        self.setWindowTitle(f"{title} - {APP_NAME}")
        self.status_title.setText(f"Title: {title}")

    def update_urlbar(self, q, browser=None):
        """Update URL bar and related UI elements"""
        current_browser = self.get_current_browser()
        if browser != current_browser:
            return

        # Add to history
        self.history_manager.add(q.toString(), browser.page().title())
        ui_helpers.update_history_menu(self)

        # Check if it's the welcome page (data URL)
        url_string = q.toString()
        if url_string.startswith("data:text/html") and "Welcome to MonoGuard" in url_string:
            self.urlbar.setText("welcome")
        else:
            self.urlbar.setText(url_string)
        
        self.urlbar.setCursorPosition(0)
        
        # Update bookmark button
        ui_helpers.update_bookmark_button(self)
        
        # Update status bar info
        if url_string.startswith("data:text/html"):
            self.status_info.setText("Welcome Page")
        else:
            protocol = "Secure (HTTPS)" if q.scheme() == 'https' else "HTTP"
            self.status_info.setText(f"{protocol} | {q.host()}")

    def on_load_started(self):
        """Called when page starts loading"""
        self.status_progress.setVisible(True)
        self.status_progress.setValue(0)
        self.status_title.setText("Loading...")

    def on_load_progress(self, progress):
        """Called during page loading"""
        self.status_progress.setValue(progress)

    def on_load_finished(self, success):
        """Called when page finishes loading"""
        self.status_progress.setVisible(False)
        if success:
            browser = self.get_current_browser()
            if browser:
                title = browser.page().title()
                self.status_title.setText(f"Title: {title}")
        else:
            self.status_title.setText("Failed to load")

    # Dialog methods
    def about(self):
        """Show about dialog"""
        dlg = AboutDialog()
        dlg.exec_()

    def show_browser_settings(self):
        """Show browser settings dialog"""
        dialog = BrowserSettingsDialog(self)
        if dialog.exec_() == QDialog.Accepted:
            # Apply settings
            settings = dialog.get_settings()
            
            # Update home URL
            if settings.get("home_url"):
                self.config_manager.set("home_url", settings["home_url"])
            
            # Update search engine
            if settings.get("search_engine"):
                self.config_manager.set("search_engine", settings["search_engine"])
            
            # Update font size
            if settings.get("font_size"):
                self.config_manager.set("font_size", settings["font_size"])
                self.apply_font_size(settings["font_size"])
            
            # Update welcome page setting
            self.config_manager.set("use_welcome_page", settings.get("use_welcome_page", True))
            
            QMessageBox.information(self, "Settings Saved", "Browser settings have been updated.")

    def reset_profile(self):
        """Reset current profile to default (clear all data)"""
        reply = QMessageBox.question(
            self, 
            "Reset Profile", 
            f"Are you sure you want to reset profile '{self.profile_manager.current_profile}'?\n\n"
            "This will clear:\n"
            "- All browsing history\n"
            "- All bookmarks\n"
            "- All configuration settings\n\n"
            "This action cannot be undone!",
            QMessageBox.Yes | QMessageBox.No,
            QMessageBox.No
        )
        
        if reply == QMessageBox.Yes:
            # Clear all data
            self.history_manager.clear()
            self.bookmark_manager.bookmarks = []
            self.bookmark_manager.save()
            self.config_manager.config = {}
            self.config_manager.save()
            
            # Reset history enabled to default (False)
            self.history_manager.enabled = False
            self.config_manager.set("history_enabled", False)
            
            # Update UI
            self.history_toggle_btn.setChecked(False)
            ui_helpers.update_history_toggle_button(self)
            ui_helpers.update_bookmarks_menu(self)
            ui_helpers.update_history_menu(self)
            
            QMessageBox.information(self, "Reset Complete", 
                                   f"Profile '{self.profile_manager.current_profile}' has been reset to default.")

    def closeEvent(self, event):
        """Handle application closing"""
        # End session and save data
        self.session_tracker.end_session()
        event.accept()
    
    def setup_initial_tab(self):
        """Setup the initial tab after managers are initialized"""
        use_welcome = self.config_manager.get("use_welcome_page", True)
        if use_welcome:
            self.add_new_tab(self.get_welcome_page_url(), "Welcome")
        else:
            home_url = self.config_manager.get("home_url", DEFAULT_HOME_URL)
            self.add_new_tab(QUrl(home_url), DEFAULT_NEW_TAB_LABEL)
        
        # Set up the open with menu after navigation manager is ready
        self.open_with_btn.setMenu(self.navigation_manager.create_open_with_menu())
        
        # Show window maximized after everything is set up
        self.showMaximized()