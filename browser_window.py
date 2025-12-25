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
from clipboard_manager import ClipboardManager
from clipboard_dialog import ClipboardHistoryDialog
from ping_tool import PingDialog
from curl_tool import CurlDialog
from command_line_tool import CommandLineWidget
import ui_helpers
import styles

from dialogs import AboutDialog, BrowserSettingsDialog
from tab_manager import TabManager
from navigation import NavigationManager
from pdf_viewer import PDFViewerWidget
from sidebar_widget import SidebarWidget


class MainWindow(QMainWindow):
    """Main browser window"""
    
    def __init__(self, *args, **kwargs):
        super(MainWindow, self).__init__(*args, **kwargs)

        # Initialize managers
        self.profile_manager = ProfileManager()
        self.config_manager = ConfigManager(self.profile_manager)
        self.config_manager.load()
        
        # Mode states
        self.api_mode_enabled = False
        self.api_tab_widget = None
        self.api_tab_index = None
        self.cmd_mode_enabled = False
        self.cmd_tab_widget = None
        self.cmd_tab_index = None
        self.pdf_mode_enabled = False
        self.pdf_tab_widget = None
        self.pdf_tab_index = None
        self.stored_web_tabs = []  # Store web tabs when in special modes
        
        # Sidebar state
        self.sidebar_visible = False
        self.sidebar_widget = None
        
        self.history_manager = HistoryManager(self.profile_manager)
        self.history_manager.enabled = self.config_manager.get("history_enabled", False)
        self.history_manager.load()
        
        self.bookmark_manager = BookmarkManager(self.profile_manager)
        self.bookmark_manager.load()
        
        self.clipboard_manager = ClipboardManager(self.profile_manager)
        self.clipboard_dialog = None  # Will be created when needed
        self.ping_dialog = None  # Will be created when needed
        self.curl_dialog = None  # Will be created when needed
        
        self.session_tracker = SessionTracker(self.profile_manager)

        # Initialize UI components
        self.setup_tabs()
        self.setup_status_bar()
        self.setup_toolbar()
        self.setup_menus()
        
        # Initialize managers that depend on UI
        self.tab_manager = TabManager(self)
        self.navigation_manager = NavigationManager(self)
        
        # Connect clipboard manager signals
        self.clipboard_manager.clipboard_changed.connect(self.on_clipboard_changed)
        
        # Load initial page
        self.load_initial_page()
        
        # Window setup
        self.setWindowTitle(WINDOW_TITLE)
        self.setWindowIcon(QIcon(os.path.join(IMAGES_DIR, ICON_APP_64)))

    def setup_tabs(self):
        """Setup tab widget with sidebar"""
        # Create main horizontal layout
        main_widget = QWidget()
        main_layout = QHBoxLayout(main_widget)
        main_layout.setContentsMargins(0, 0, 0, 0)
        main_layout.setSpacing(0)
        
        # Create sidebar
        self.sidebar_widget = SidebarWidget(self)
        self.sidebar_widget.setVisible(self.sidebar_visible)  # Set initial visibility
        main_layout.addWidget(self.sidebar_widget)
        
        # Create container for tabs and sidebar toggle
        tabs_container = QWidget()
        tabs_container_layout = QVBoxLayout(tabs_container)
        tabs_container_layout.setContentsMargins(0, 0, 0, 0)
        tabs_container_layout.setSpacing(0)
        
        # Create top bar with sidebar toggle button
        self.top_bar = QWidget()
        self.top_bar.setFixedHeight(32)
        self.top_bar.setStyleSheet("""
            QWidget {
                background-color: #f8f9fa;
                border-bottom: 1px solid #dee2e6;
            }
        """)
        top_bar_layout = QHBoxLayout(self.top_bar)
        top_bar_layout.setContentsMargins(8, 4, 8, 4)
        top_bar_layout.setSpacing(8)
        
        # Sidebar toggle button
        self.sidebar_toggle_btn = QPushButton("📋")
        self.sidebar_toggle_btn.setObjectName("sidebarToggleBtn")
        self.sidebar_toggle_btn.setFixedSize(24, 24)
        self.sidebar_toggle_btn.setStatusTip("Toggle sidebar")
        self.sidebar_toggle_btn.setCheckable(True)
        self.sidebar_toggle_btn.setChecked(False)
        self.sidebar_toggle_btn.clicked.connect(self.toggle_sidebar)
        self.sidebar_toggle_btn.setStyleSheet("""
            QPushButton {
                background-color: #ffffff;
                border: 1px solid #ced4da;
                border-radius: 4px;
                font-size: 11px;
                padding: 2px;
            }
            QPushButton:hover {
                background-color: #e9ecef;
                border-color: #adb5bd;
            }
            QPushButton:checked {
                background-color: #007bff;
                color: white;
                border-color: #0056b3;
            }
            QPushButton:checked:hover {
                background-color: #0056b3;
            }
        """)
        top_bar_layout.addWidget(self.sidebar_toggle_btn)
        
        # Add title label
        self.title_label = QLabel("Browser Tabs (Sidebar Hidden)")
        self.title_label.setStyleSheet("""
            QLabel {
                font-size: 11px;
                font-weight: 600;
                color: #495057;
                padding-left: 4px;
            }
        """)
        top_bar_layout.addWidget(self.title_label)
        
        # Add stretch to push everything to the left
        top_bar_layout.addStretch()
        
        # Add top bar to container
        tabs_container_layout.addWidget(self.top_bar)
        
        # Initially show top bar only in web mode (default mode)
        self.top_bar.setVisible(True)
        
        # Create tabs
        self.tabs = QTabWidget()
        self.tabs.setDocumentMode(True)
        self.tabs.tabBarDoubleClicked.connect(self.tab_open_doubleclick)
        self.tabs.currentChanged.connect(self.current_tab_changed)
        self.tabs.setTabsClosable(False)
        tabs_container_layout.addWidget(self.tabs)
        
        # Add tabs container to main layout
        main_layout.addWidget(tabs_container)
        
        self.setCentralWidget(main_widget)

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
        """Setup navigation toolbar with icons"""
        self.navigation_toolbar = QToolBar("Navigation")
        self.addToolBar(self.navigation_toolbar)

        # Home button with emoji icon
        home_btn = QAction("🏠 Home", self)
        home_btn.setStatusTip("Go home")
        home_btn.triggered.connect(self.navigate_home)
        self.navigation_toolbar.addAction(home_btn)

        # Reload button with emoji icon
        reload_btn = QAction("🔄 Reload", self)
        reload_btn.setStatusTip("Reload page")
        reload_btn.triggered.connect(self.reload_page)
        self.navigation_toolbar.addAction(reload_btn)

        self.navigation_toolbar.addSeparator()

        # URL bar
        self.urlbar = QLineEdit()
        self.urlbar.setPlaceholderText("Enter URL or search...")
        self.urlbar.returnPressed.connect(self.navigate_to_url)
        self.urlbar.setContextMenuPolicy(Qt.CustomContextMenu)
        self.urlbar.customContextMenuRequested.connect(self.show_urlbar_context_menu)
        self.navigation_toolbar.addWidget(self.urlbar)
        
        # Open with browser dropdown button
        self.open_with_btn = QPushButton("🌐")
        self.open_with_btn.setObjectName("openWithBtn")
        self.open_with_btn.setMaximumWidth(35)
        self.open_with_btn.setStatusTip("Open in external browser")
        self.navigation_toolbar.addWidget(self.open_with_btn)
        
        # Bookmark button
        self.bookmark_btn = QPushButton("☆")
        self.bookmark_btn.setObjectName("bookmarkBtn")
        self.bookmark_btn.setMaximumWidth(30)
        self.bookmark_btn.setStatusTip("Add/Remove bookmark")
        self.bookmark_btn.clicked.connect(lambda: ui_helpers.toggle_bookmark(self))
        self.navigation_toolbar.addWidget(self.bookmark_btn)
        
        # History toggle button
        self.history_toggle_btn = QPushButton()
        self.history_toggle_btn.setMaximumWidth(100)  # Increased width for icon
        self.history_toggle_btn.setMinimumHeight(32)  # Set minimum height
        self.history_toggle_btn.setMaximumHeight(32)  # Set maximum height
        self.history_toggle_btn.setCheckable(True)
        self.history_toggle_btn.setChecked(self.history_manager.enabled)
        # Apply initial styling
        self.history_toggle_btn.setStyleSheet(styles.get_history_button_style(self.history_manager.enabled))
        ui_helpers.update_history_toggle_button(self)
        self.history_toggle_btn.clicked.connect(lambda: ui_helpers.toggle_history(self))
        self.navigation_toolbar.addWidget(self.history_toggle_btn)

    def setup_menus(self):
        """Setup application menus with icons"""
        # Bookmarks menu
        self.bookmarks_menu = self.menuBar().addMenu("📚 &Bookmarks")
        ui_helpers.update_bookmarks_menu(self)

        # History menu
        self.history_menu = self.menuBar().addMenu("📜 &History")
        ui_helpers.update_history_menu(self)

        # Tools menu
        tools_menu = self.menuBar().addMenu("🔧 &Tools")
        
        dev_tools_action = QAction("🔍 Toggle Dev Tools", self)
        dev_tools_action.setShortcut("F12")
        dev_tools_action.setStatusTip("Show/Hide Developer Tools")
        dev_tools_action.triggered.connect(self.toggle_current_dev_tools)
        tools_menu.addAction(dev_tools_action)
        
        tools_menu.addSeparator()
        
        # Theme toggle action
        theme_action = QAction("🎨 Toggle Theme (Dark/Light)", self)
        theme_action.setShortcut("Ctrl+T")
        theme_action.setStatusTip("Switch between dark and light themes")
        theme_action.triggered.connect(self.toggle_theme)
        tools_menu.addAction(theme_action)
        
        tools_menu.addSeparator()
        
        # Clipboard Manager action
        clipboard_action = QAction("📋 Clipboard Manager", self)
        clipboard_action.setShortcut("Ctrl+Shift+V")
        clipboard_action.setStatusTip("Open clipboard history manager")
        clipboard_action.triggered.connect(self.show_clipboard_manager)
        tools_menu.addAction(clipboard_action)
        
        # Ping Tool action
        ping_action = QAction("🏓 Ping Tool", self)
        ping_action.setShortcut("Ctrl+P")
        ping_action.setStatusTip("Test domain/IP connectivity")
        ping_action.triggered.connect(self.show_ping_tool)
        tools_menu.addAction(ping_action)
        
        # Curl Tool action
        curl_action = QAction("🌐 Curl Tool", self)
        curl_action.setShortcut("Ctrl+U")
        curl_action.setStatusTip("Make HTTP requests and test APIs")
        curl_action.triggered.connect(self.show_curl_tool)
        tools_menu.addAction(curl_action)
        
        # Screenshot submenu
        screenshot_menu = tools_menu.addMenu("📸 Screenshot")
        
        viewport_action = QAction("📸 Current View", self)
        viewport_action.setShortcut("Ctrl+Shift+S")
        viewport_action.setStatusTip("Take a screenshot of the current viewport")
        viewport_action.triggered.connect(self.take_viewport_screenshot)
        screenshot_menu.addAction(viewport_action)
        
        fullpage_action = QAction("📄 Full Page", self)
        fullpage_action.setShortcut("Ctrl+Shift+F")
        fullpage_action.setStatusTip("Take a screenshot of the entire page")
        fullpage_action.triggered.connect(self.take_fullpage_screenshot)
        screenshot_menu.addAction(fullpage_action)
        
        tools_menu.addSeparator()
        
        # Mode switching actions
        pdf_mode_action = QAction("📄 PDF Reader Mode", self)
        pdf_mode_action.setShortcut("Ctrl+Shift+P")
        pdf_mode_action.setStatusTip("Switch to PDF reader mode")
        pdf_mode_action.triggered.connect(self.switch_to_pdf_mode)
        tools_menu.addAction(pdf_mode_action)
        
        api_mode_action = QAction("🔧 API Tester Mode", self)
        api_mode_action.setShortcut("Ctrl+Shift+A")
        api_mode_action.setStatusTip("Switch to API testing mode")
        api_mode_action.triggered.connect(self.switch_to_api_mode)
        tools_menu.addAction(api_mode_action)
        
        cmd_mode_action = QAction("💻 Command Line Mode", self)
        cmd_mode_action.setShortcut("Ctrl+Shift+C")
        cmd_mode_action.setStatusTip("Switch to command line mode")
        cmd_mode_action.triggered.connect(self.switch_to_cmd_mode)
        tools_menu.addAction(cmd_mode_action)
        
        web_mode_action = QAction("🌐 Web Browser Mode", self)
        web_mode_action.setShortcut("Ctrl+Shift+W")
        web_mode_action.setStatusTip("Switch to web browser mode")
        web_mode_action.triggered.connect(self.switch_to_web_mode)
        tools_menu.addAction(web_mode_action)
        
        tools_menu.addSeparator()
        
        # Sidebar actions
        sidebar_toggle_action = QAction("📋 Toggle Sidebar", self)
        sidebar_toggle_action.setShortcut("Ctrl+B")
        sidebar_toggle_action.setStatusTip("Show/Hide sidebar")
        sidebar_toggle_action.triggered.connect(self.toggle_sidebar)
        tools_menu.addAction(sidebar_toggle_action)
        
        add_to_sidebar_action = QAction("➕ Add Current Page to Sidebar", self)
        add_to_sidebar_action.setShortcut("Ctrl+Shift+B")
        add_to_sidebar_action.setStatusTip("Add current page to sidebar")
        add_to_sidebar_action.triggered.connect(self.add_current_to_sidebar)
        tools_menu.addAction(add_to_sidebar_action)

        # Profile menu
        self.profile_menu = self.menuBar().addMenu("👤 &Profile")
        ui_helpers.update_profile_menu(self)

        # Help menu
        help_menu = self.menuBar().addMenu("❓ &Help")
        about_action = QAction("ℹ️ About " + APP_NAME, self)
        about_action.setStatusTip(f"Find out more about {APP_NAME}")
        about_action.triggered.connect(self.about)
        help_menu.addAction(about_action)

        help_menu.addSeparator()

        settings_action = QAction("⚙️ Browser Settings", self)
        settings_action.setStatusTip("Configure browser settings")
        settings_action.triggered.connect(self.show_browser_settings)
        help_menu.addAction(settings_action)

        reset_action = QAction("🔄 Reset to Default", self)
        reset_action.setStatusTip("Clear all profile data (history, bookmarks, config)")
        reset_action.triggered.connect(self.reset_profile)
        help_menu.addAction(reset_action)

        help_menu.addSeparator()

        quit_action = QAction("🚪 Quit App", self)
        quit_action.setShortcut("Ctrl+Q")
        quit_action.setStatusTip("Exit the application")
        quit_action.triggered.connect(self.quit_application)
        help_menu.addAction(quit_action)
        
        # Add browser mode dropdown to the right side of menu bar
        self.setup_browser_mode_dropdown()
    
    def setup_browser_mode_dropdown(self):
        """Setup browser mode dropdown in menu bar"""
        # Create a widget to hold the dropdown
        mode_widget = QWidget()
        mode_layout = QHBoxLayout(mode_widget)
        mode_layout.setContentsMargins(10, 0, 10, 0)
        
        # Mode label
        mode_label = QLabel("Mode:")
        mode_label.setStyleSheet("QLabel { color: #666; font-weight: bold; }")
        mode_layout.addWidget(mode_label)
        
        # Mode dropdown
        self.mode_dropdown = QComboBox()
        self.mode_dropdown.addItem("🌐 Web Browser", "web")
        self.mode_dropdown.addItem("🔧 API Tester", "api")
        self.mode_dropdown.addItem("💻 Command Line", "cmd")
        self.mode_dropdown.addItem("📄 PDF Reader", "pdf")
        self.mode_dropdown.setCurrentIndex(0)  # Default to web mode
        self.mode_dropdown.setMinimumWidth(140)  # Increased width for new option
        self.update_dropdown_style()
        self.mode_dropdown.currentTextChanged.connect(self.on_mode_changed)
        mode_layout.addWidget(self.mode_dropdown)
        
        # Add the widget to the right side of the menu bar
        self.menuBar().setCornerWidget(mode_widget, Qt.TopRightCorner)
    
    def update_dropdown_style(self):
        """Update dropdown styling based on current theme"""
        if hasattr(styles, 'current_theme') and styles.current_theme == "dark":
            # Dark theme styling
            self.mode_dropdown.setStyleSheet("""
                QComboBox {
                    padding: 4px 8px;
                    border: 1px solid #555;
                    border-radius: 4px;
                    background-color: #2c3e50;
                    color: #ecf0f1;
                    font-weight: bold;
                }
                QComboBox:hover {
                    border: 1px solid #7f8c8d;
                    background-color: #34495e;
                }
                QComboBox::drop-down {
                    border: none;
                    width: 20px;
                }
                QComboBox::down-arrow {
                    image: none;
                    border-left: 4px solid transparent;
                    border-right: 4px solid transparent;
                    border-top: 4px solid #bdc3c7;
                    margin-right: 4px;
                }
                QComboBox QAbstractItemView {
                    background-color: #2c3e50;
                    color: #ecf0f1;
                    border: 1px solid #555;
                    selection-background-color: #34495e;
                    selection-color: #ecf0f1;
                    outline: none;
                }
                QComboBox QAbstractItemView::item {
                    padding: 4px 8px;
                    color: #ecf0f1;
                }
                QComboBox QAbstractItemView::item:hover {
                    background-color: #34495e;
                    color: #ecf0f1;
                }
                QComboBox QAbstractItemView::item:selected {
                    background-color: #34495e;
                    color: #ecf0f1;
                }
            """)
        else:
            # Light theme styling
            self.mode_dropdown.setStyleSheet("""
                QComboBox {
                    padding: 4px 8px;
                    border: 1px solid #ccc;
                    border-radius: 4px;
                    background-color: white;
                    color: #333;
                    font-weight: bold;
                }
                QComboBox:hover {
                    border: 1px solid #999;
                    background-color: #f8f9fa;
                }
                QComboBox::drop-down {
                    border: none;
                    width: 20px;
                }
                QComboBox::down-arrow {
                    image: none;
                    border-left: 4px solid transparent;
                    border-right: 4px solid transparent;
                    border-top: 4px solid #666;
                    margin-right: 4px;
                }
                QComboBox QAbstractItemView {
                    background-color: white;
                    color: #333;
                    border: 1px solid #ccc;
                    selection-background-color: #e3f2fd;
                    selection-color: #333;
                    outline: none;
                }
                QComboBox QAbstractItemView::item {
                    padding: 4px 8px;
                    color: #333;
                }
                QComboBox QAbstractItemView::item:hover {
                    background-color: #e3f2fd;
                    color: #333;
                }
                QComboBox QAbstractItemView::item:selected {
                    background-color: #e3f2fd;
                    color: #333;
                }
            """)

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
        
        # Update dropdown style
        self.update_dropdown_style()
        
        # Update profile label style
        self.status_profile.setStyleSheet(styles.get_profile_label_style())
        
        # Show notification
        theme_name = "Light" if new_theme == "light" else "Dark"
        self.status_info.setText(f"Switched to {theme_name} theme")
    
    def on_mode_changed(self, mode_text):
        """Handle browser mode change from dropdown"""
        if "API Tester" in mode_text:
            # Switch to API mode
            self.api_mode_enabled = True
            self.cmd_mode_enabled = False
            self.pdf_mode_enabled = False
            self.status_info.setText("API Mode: Ready for testing")
            
            # Hide navigation toolbar (home, reload, URL bar)
            self.navigation_toolbar.setVisible(False)
            
            # Hide top bar (sidebar toggle and title) in non-web modes
            self.top_bar.setVisible(False)
            
            # Hide sidebar in non-web modes
            if self.sidebar_widget:
                self.sidebar_widget.setVisible(False)
            
            # Store current web tabs and remove them
            self.store_and_remove_web_tabs()
            
            # Remove other mode tabs
            self.remove_cmd_tabs()
            self.remove_pdf_tabs()
            
            # Add API tab
            self.add_api_tab()
        elif "Command Line" in mode_text:
            # Switch to command line mode
            self.cmd_mode_enabled = True
            self.api_mode_enabled = False
            self.pdf_mode_enabled = False
            self.status_info.setText("Command Line Mode: Ready for terminal commands")
            
            # Hide navigation toolbar
            self.navigation_toolbar.setVisible(False)
            
            # Hide top bar (sidebar toggle and title) in non-web modes
            self.top_bar.setVisible(False)
            
            # Hide sidebar in non-web modes
            if self.sidebar_widget:
                self.sidebar_widget.setVisible(False)
            
            # Store current web tabs and remove them
            self.store_and_remove_web_tabs()
            
            # Remove other mode tabs
            self.remove_api_tabs()
            self.remove_pdf_tabs()
            
            # Add command line tab
            self.add_cmd_tab()
        elif "PDF Reader" in mode_text:
            # Switch to PDF reader mode
            self.pdf_mode_enabled = True
            self.api_mode_enabled = False
            self.cmd_mode_enabled = False
            self.status_info.setText("PDF Mode: Ready for document viewing")
            
            # Hide navigation toolbar
            self.navigation_toolbar.setVisible(False)
            
            # Hide top bar (sidebar toggle and title) in non-web modes
            self.top_bar.setVisible(False)
            
            # Hide sidebar in non-web modes
            if self.sidebar_widget:
                self.sidebar_widget.setVisible(False)
            
            # Store current web tabs and remove them
            self.store_and_remove_web_tabs()
            
            # Remove other mode tabs
            self.remove_api_tabs()
            self.remove_cmd_tabs()
            
            # Add PDF reader tab
            self.add_pdf_tab()
        else:
            # Switch to web mode
            self.api_mode_enabled = False
            self.cmd_mode_enabled = False
            self.pdf_mode_enabled = False
            self.status_info.setText("Web Mode: Ready for browsing")
            
            # Show navigation toolbar
            self.navigation_toolbar.setVisible(True)
            
            # Show top bar (sidebar toggle and title) in web mode
            self.top_bar.setVisible(True)
            
            # Show sidebar only in web mode
            if self.sidebar_widget:
                self.sidebar_widget.setVisible(self.sidebar_visible)
            
            # Remove special mode tabs and restore web tabs
            self.remove_api_tabs()
            self.remove_cmd_tabs()
            self.remove_pdf_tabs()
            self.restore_web_tabs()
    
    def toggle_api_mode(self):
        """Toggle API testing mode (for backward compatibility)"""
        current_index = self.mode_dropdown.currentIndex()
        new_index = 1 if current_index == 0 else 0
        self.mode_dropdown.setCurrentIndex(new_index)
    
    def switch_to_pdf_mode(self):
        """Switch to PDF reader mode"""
        self.mode_dropdown.setCurrentIndex(3)  # PDF Reader is at index 3
    
    def switch_to_api_mode(self):
        """Switch to API testing mode"""
        self.mode_dropdown.setCurrentIndex(1)  # API Tester is at index 1
    
    def switch_to_cmd_mode(self):
        """Switch to command line mode"""
        self.mode_dropdown.setCurrentIndex(2)  # Command Line is at index 2
    
    def switch_to_web_mode(self):
        """Switch to web browser mode"""
        self.mode_dropdown.setCurrentIndex(0)  # Web Browser is at index 0
    
    def store_and_remove_web_tabs(self):
        """Store current web tabs and remove them from view"""
        self.stored_web_tabs = []
        
        # Store all current tabs (except special mode tabs)
        for i in range(self.tabs.count()):
            widget = self.tabs.widget(i)
            tab_text = self.tabs.tabText(i)
            
            # Skip if it's already a special mode tab
            if (hasattr(self, 'api_tab_widget') and widget == self.api_tab_widget) or \
               (hasattr(self, 'cmd_tab_widget') and widget == self.cmd_tab_widget) or \
               (hasattr(self, 'pdf_tab_widget') and widget == self.pdf_tab_widget):
                continue
                
            # Store tab info
            tab_info = {
                'widget': widget,
                'text': tab_text,
                'index': i
            }
            self.stored_web_tabs.append(tab_info)
        
        # Remove all tabs (they'll be restored later)
        while self.tabs.count() > 0:
            widget = self.tabs.widget(0)
            if (hasattr(self, 'api_tab_widget') and widget == self.api_tab_widget) or \
               (hasattr(self, 'cmd_tab_widget') and widget == self.cmd_tab_widget) or \
               (hasattr(self, 'pdf_tab_widget') and widget == self.pdf_tab_widget):
                break
            self.tabs.removeTab(0)
    
    def restore_web_tabs(self):
        """Restore previously stored web tabs"""
        if not self.stored_web_tabs:
            # If no stored tabs, load the welcome page or home page based on settings
            use_welcome = self.config_manager.get("use_welcome_page", True)
            if use_welcome:
                self.add_new_tab(self.get_welcome_page_url(), "Welcome")
            else:
                home_url = self.config_manager.get("home_url", DEFAULT_HOME_URL)
                self.add_new_tab(QUrl(home_url), DEFAULT_NEW_TAB_LABEL)
            return
            
        # Restore all stored tabs
        for tab_info in self.stored_web_tabs:
            widget = tab_info['widget']
            text = tab_info['text']
            self.tabs.addTab(widget, text)
        
        # Switch to first tab
        if self.tabs.count() > 0:
            self.tabs.setCurrentIndex(0)
            self.current_tab_changed(0)
        
        # Clear stored tabs
        self.stored_web_tabs = []
    
    def add_api_tab(self):
        """Add a new API testing tab"""
        # Create API interface widget
        api_widget = QWidget()
        layout = QVBoxLayout(api_widget)
        
        # Placeholder content
        label = QLabel("🔧 API Testing Mode")
        label.setAlignment(Qt.AlignCenter)
        label.setStyleSheet("font-size: 24px; font-weight: bold; margin: 50px;")
        layout.addWidget(label)
        
        info_label = QLabel("API testing interface will be implemented here.\nFeatures coming soon:\n• HTTP Methods (GET, POST, PUT, DELETE)\n• Request/Response viewer\n• Headers and parameters\n• Collections and history")
        info_label.setAlignment(Qt.AlignCenter)
        info_label.setStyleSheet("font-size: 14px; color: #666; line-height: 1.5;")
        layout.addWidget(info_label)
        
        # Add the API tab
        tab_index = self.tabs.addTab(api_widget, "🔧 API Tester")
        self.tabs.setCurrentIndex(tab_index)
        
        # Store reference to API tab
        self.api_tab_widget = api_widget
        self.api_tab_index = tab_index
    
    def remove_api_tabs(self):
        """Remove API testing tabs"""
        if hasattr(self, 'api_tab_index') and self.api_tab_index is not None:
            self.tabs.removeTab(self.api_tab_index)
            self.api_tab_widget = None
            self.api_tab_index = None
    
    def add_cmd_tab(self):
        """Add a new command line tab"""
        # Create command line interface widget
        self.cmd_tab_widget = CommandLineWidget(self)
        
        # Add the command line tab
        tab_index = self.tabs.addTab(self.cmd_tab_widget, "💻 Terminal")
        self.tabs.setCurrentIndex(tab_index)
        
        # Store reference to command line tab
        self.cmd_tab_index = tab_index
    
    def remove_cmd_tabs(self):
        """Remove command line tabs"""
        if hasattr(self, 'cmd_tab_index') and self.cmd_tab_index is not None:
            self.tabs.removeTab(self.cmd_tab_index)
            if self.cmd_tab_widget:
                # Properly clean up any running processes
                self.cmd_tab_widget.stop_command()
            self.cmd_tab_widget = None
            self.cmd_tab_index = None
    
    def add_pdf_tab(self):
        """Add a new PDF reader tab"""
        # Create PDF viewer widget
        self.pdf_tab_widget = PDFViewerWidget(self)
        
        # Add the PDF tab
        tab_index = self.tabs.addTab(self.pdf_tab_widget, "📄 PDF Reader")
        self.tabs.setCurrentIndex(tab_index)
        
        # Store reference to PDF tab
        self.pdf_tab_index = tab_index
    
    def remove_pdf_tabs(self):
        """Remove PDF reader tabs"""
        if hasattr(self, 'pdf_tab_index') and self.pdf_tab_index is not None:
            self.tabs.removeTab(self.pdf_tab_index)
            self.pdf_tab_widget = None
            self.pdf_tab_index = None
    
    def show_clipboard_manager(self):
        """Show clipboard manager dialog"""
        if self.clipboard_dialog is None or not self.clipboard_dialog.isVisible():
            self.clipboard_dialog = ClipboardHistoryDialog(self.clipboard_manager, self)
            self.clipboard_dialog.show()
        else:
            # Bring existing dialog to front
            self.clipboard_dialog.raise_()
            self.clipboard_dialog.activateWindow()
    
    def show_ping_tool(self):
        """Show ping tool dialog"""
        if self.ping_dialog is None or not self.ping_dialog.isVisible():
            self.ping_dialog = PingDialog(self)
            self.ping_dialog.show()
        else:
            # Bring existing dialog to front
            self.ping_dialog.raise_()
            self.ping_dialog.activateWindow()
    
    def show_curl_tool(self):
        """Show curl tool dialog"""
        if self.curl_dialog is None or not self.curl_dialog.isVisible():
            self.curl_dialog = CurlDialog(self)
            self.curl_dialog.show()
        else:
            # Bring existing dialog to front
            self.curl_dialog.raise_()
            self.curl_dialog.activateWindow()
    
    def take_screenshot(self, screenshot_type="viewport"):
        """Take a screenshot of the current page (only works in web mode)"""
        # Only allow screenshot in web mode
        if self.api_mode_enabled or self.cmd_mode_enabled or self.pdf_mode_enabled:
            self.status_info.setText("Screenshot only available in Web Browser mode")
            QTimer.singleShot(2000, lambda: self.status_info.setText(""))
            return
        
        # Get current browser
        current_browser = self.get_current_browser()
        if current_browser and self.tab_manager:
            self.tab_manager.take_screenshot(current_browser, screenshot_type)
        else:
            self.status_info.setText("❌ No active web page for screenshot")
            QTimer.singleShot(2000, lambda: self.status_info.setText(""))
    
    def take_viewport_screenshot(self):
        """Take a screenshot of the current viewport"""
        self.take_screenshot("viewport")
    
    def take_fullpage_screenshot(self):
        """Take a screenshot of the full page"""
        self.take_screenshot("fullpage")
    
    def show_urlbar_context_menu(self, position):
        """Show context menu for URL bar"""
        menu = QMenu(self)
        
        # Standard edit actions
        if self.urlbar.hasSelectedText():
            cut_action = menu.addAction("✂️ Cut")
            cut_action.triggered.connect(self.urlbar.cut)
            
            copy_action = menu.addAction("📋 Copy")
            copy_action.triggered.connect(self.urlbar.copy)
        
        paste_action = menu.addAction("📄 Paste")
        paste_action.triggered.connect(self.urlbar.paste)
        paste_action.setEnabled(QApplication.clipboard().text() != "")
        
        menu.addSeparator()
        
        select_all_action = menu.addAction("🔘 Select All")
        select_all_action.triggered.connect(self.urlbar.selectAll)
        
        # Network testing actions if there's text
        url_text = self.urlbar.text().strip()
        if url_text:
            menu.addSeparator()
            ping_action = menu.addAction("🏓 Ping this domain")
            ping_action.triggered.connect(lambda: self.ping_from_urlbar(url_text))
            
            curl_action = menu.addAction("🌐 Test this URL")
            curl_action.triggered.connect(lambda: self.curl_from_urlbar(url_text))
        
        menu.exec_(self.urlbar.mapToGlobal(position))
    
    def ping_from_urlbar(self, url_text):
        """Ping domain from URL bar"""
        # Extract domain from URL
        domain = url_text
        if "://" in domain:
            domain = domain.split("://")[1]
        if "/" in domain:
            domain = domain.split("/")[0]
        if ":" in domain:
            domain = domain.split(":")[0]
        
        # Open ping tool with pre-filled domain
        self.show_ping_tool()
        if self.ping_dialog:
            self.ping_dialog.set_target(domain)
    
    def curl_from_urlbar(self, url_text):
        """Test URL with curl tool from URL bar"""
        # Ensure URL has protocol
        if not url_text.startswith(('http://', 'https://')):
            url_text = 'https://' + url_text
        
        # Open curl tool with pre-filled URL
        self.show_curl_tool()
        if self.curl_dialog:
            self.curl_dialog.url_input.setText(url_text)
            self.curl_dialog.url_input.setFocus()
    
    def on_clipboard_changed(self, content):
        """Handle clipboard content change"""
        # Show brief notification in status
        preview = content[:30] + "..." if len(content) > 30 else content
        self.status_info.setText(f"📋 Copied: {preview}")
        
        # Reset after 3 seconds
        QTimer.singleShot(3000, self.reset_clipboard_status)
    
    def reset_clipboard_status(self):
        """Reset clipboard status"""
        if "📋 Copied:" in self.status_info.text():
            self.status_info.setText("")
    
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

    def quit_application(self):
        """Quit the application with confirmation"""
        reply = QMessageBox.question(
            self,
            "Quit Application",
            f"Are you sure you want to quit {APP_NAME}?\n\n"
            "All open tabs will be closed and your session will end.",
            QMessageBox.Yes | QMessageBox.No,
            QMessageBox.No
        )
        
        if reply == QMessageBox.Yes:
            # End session and save data
            self.session_tracker.end_session()
            # Close the application
            QApplication.instance().quit()

    def closeEvent(self, event):
        """Handle application closing with confirmation"""
        reply = QMessageBox.question(
            self,
            "Quit Application",
            f"Are you sure you want to quit {APP_NAME}?\n\n"
            "All open tabs will be closed and your session will end.",
            QMessageBox.Yes | QMessageBox.No,
            QMessageBox.No
        )
        
        if reply == QMessageBox.Yes:
            # End session and save data
            self.session_tracker.end_session()
            event.accept()
        else:
            event.ignore()
    
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
    
    def toggle_sidebar(self):
        """Toggle sidebar visibility (only works in web mode)"""
        # Only allow sidebar toggle in web mode
        if self.api_mode_enabled or self.cmd_mode_enabled or self.pdf_mode_enabled:
            self.status_info.setText("Sidebar only available in Web Browser mode")
            QTimer.singleShot(2000, lambda: self.status_info.setText(""))
            return
        
        self.sidebar_visible = not self.sidebar_visible
        
        if self.sidebar_widget:
            self.sidebar_widget.setVisible(self.sidebar_visible)
            
        # Update button state
        self.sidebar_toggle_btn.setChecked(self.sidebar_visible)
        
        # Update title label to reflect sidebar state
        if hasattr(self, 'title_label'):
            if self.sidebar_visible:
                self.title_label.setText("Browser Tabs")
            else:
                self.title_label.setText("Browser Tabs (Sidebar Hidden)")
        
        # Update status
        status = "shown" if self.sidebar_visible else "hidden"
        self.status_info.setText(f"Sidebar {status}")
        
        # Reset status after 2 seconds
        QTimer.singleShot(2000, lambda: self.status_info.setText(""))
    
    def add_current_to_sidebar(self):
        """Add current page to sidebar (only works in web mode)"""
        # Only allow adding to sidebar in web mode
        if self.api_mode_enabled or self.cmd_mode_enabled or self.pdf_mode_enabled:
            self.status_info.setText("Sidebar only available in Web Browser mode")
            QTimer.singleShot(2000, lambda: self.status_info.setText(""))
            return
        
        if self.sidebar_widget and self.sidebar_widget.add_current_page():
            self.status_info.setText("Added to sidebar")
            QTimer.singleShot(2000, lambda: self.status_info.setText(""))
        else:
            self.status_info.setText("Failed to add to sidebar")
            QTimer.singleShot(2000, lambda: self.status_info.setText(""))
    
    def replace_current_tab(self, url, title):
        """Replace current tab content with new URL"""
        current_browser = self.get_current_browser()
        if current_browser:
            # Navigate to new URL
            current_browser.setUrl(QUrl(url))
            
            # Update tab title
            current_index = self.tabs.currentIndex()
            if current_index >= 0:
                self.tabs.setTabText(current_index, title[:20] + "..." if len(title) > 20 else title)
            
            # Show status
            self.status_info.setText(f"Loading: {title}")
            QTimer.singleShot(3000, lambda: self.status_info.setText(""))