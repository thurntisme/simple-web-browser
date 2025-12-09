from PyQt5.QtCore import *
from PyQt5.QtWidgets import *
from PyQt5.QtGui import *
from PyQt5.QtWebEngineWidgets import *
from PyQt5.QtPrintSupport import *

import os
import sys

from constants import *
from profile_manager import ProfileManager
from history_manager import HistoryManager
from bookmark_manager import BookmarkManager
from config_manager import ConfigManager
import ui_helpers


class AboutDialog(QDialog):
    def __init__(self, *args, **kwargs):
        super(AboutDialog, self).__init__(*args, **kwargs)

        QBtn = QDialogButtonBox.Ok
        self.buttonBox = QDialogButtonBox(QBtn)
        self.buttonBox.accepted.connect(self.accept)
        self.buttonBox.rejected.connect(self.reject)

        layout = QVBoxLayout()

        title = QLabel(APP_NAME)
        font = title.font()
        font.setPointSize(ABOUT_TITLE_FONT_SIZE)
        title.setFont(font)

        layout.addWidget(title)

        logo = QLabel()
        logo.setPixmap(QPixmap(os.path.join(IMAGES_DIR, ICON_APP_128)))
        layout.addWidget(logo)

        layout.addWidget(QLabel(f"Version {APP_VERSION}"))
        layout.addWidget(QLabel(APP_COPYRIGHT))

        for i in range(0, layout.count()):
            layout.itemAt(i).setAlignment(Qt.AlignHCenter)

        layout.addWidget(self.buttonBox)
        self.setLayout(layout)


class MainWindow(QMainWindow):
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

        self.tabs = QTabWidget()
        self.tabs.setDocumentMode(True)
        self.tabs.tabBarDoubleClicked.connect(self.tab_open_doubleclick)
        self.tabs.currentChanged.connect(self.current_tab_changed)
        self.tabs.setTabsClosable(False)

        self.setCentralWidget(self.tabs)

        self.status = QStatusBar()
        self.setStatusBar(self.status)
        
        # Status bar widgets
        self.status_profile = QLabel()
        self.status_profile.setStyleSheet("QLabel { background-color: #4CAF50; color: white; padding: 3px 8px; border-radius: 3px; font-weight: bold; }")
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

        navtb = QToolBar("Navigation")
        self.addToolBar(navtb)

        home_btn = QAction("Home", self)
        home_btn.setStatusTip("Go home")
        home_btn.triggered.connect(self.navigate_home)
        navtb.addAction(home_btn)

        reload_btn = QAction("Reload", self)
        reload_btn.setStatusTip("Reload page")
        reload_btn.triggered.connect(self.reload_page)
        navtb.addAction(reload_btn)

        navtb.addSeparator()

        self.urlbar = QLineEdit()
        self.urlbar.returnPressed.connect(self.navigate_to_url)
        navtb.addWidget(self.urlbar)
        
        # Open with browser dropdown button
        self.open_with_btn = QPushButton("🌐")
        self.open_with_btn.setMaximumWidth(35)
        self.open_with_btn.setStatusTip("Open in external browser")
        self.open_with_btn.setMenu(self.create_open_with_menu())
        navtb.addWidget(self.open_with_btn)
        
        self.bookmark_btn = QPushButton("☆")
        self.bookmark_btn.setMaximumWidth(30)
        self.bookmark_btn.setStatusTip("Add/Remove bookmark")
        self.bookmark_btn.clicked.connect(lambda: ui_helpers.toggle_bookmark(self))
        navtb.addWidget(self.bookmark_btn)
        
        self.history_toggle_btn = QPushButton()
        self.history_toggle_btn.setMaximumWidth(80)
        self.history_toggle_btn.setCheckable(True)
        self.history_toggle_btn.setChecked(self.history_manager.enabled)
        ui_helpers.update_history_toggle_button(self)
        self.history_toggle_btn.clicked.connect(lambda: ui_helpers.toggle_history(self))
        navtb.addWidget(self.history_toggle_btn)

        # Menus
        self.bookmarks_menu = self.menuBar().addMenu("&Bookmarks")
        ui_helpers.update_bookmarks_menu(self)

        self.history_menu = self.menuBar().addMenu("&History")
        ui_helpers.update_history_menu(self)

        tools_menu = self.menuBar().addMenu("&Tools")
        
        dev_tools_action = QAction("Toggle Dev Tools", self)
        dev_tools_action.setShortcut("F12")
        dev_tools_action.setStatusTip("Show/Hide Developer Tools")
        dev_tools_action.triggered.connect(self.toggle_current_dev_tools)
        tools_menu.addAction(dev_tools_action)

        self.profile_menu = self.menuBar().addMenu("&Profile")
        ui_helpers.update_profile_menu(self)

        help_menu = self.menuBar().addMenu("&Help")

        about_action = QAction(QIcon(os.path.join(IMAGES_DIR, ICON_ABOUT)), f"About {APP_NAME}", self)
        about_action.setStatusTip(f"Find out more about {APP_NAME}")
        about_action.triggered.connect(self.about)
        help_menu.addAction(about_action)

        navigate_mozarella_action = QAction(QIcon(os.path.join(IMAGES_DIR, ICON_HELP)),
                                            f"{APP_ORGANIZATION} Homepage", self)
        navigate_mozarella_action.setStatusTip(f"Go to {APP_ORGANIZATION} Homepage")
        navigate_mozarella_action.triggered.connect(self.navigate_mozarella)
        help_menu.addAction(navigate_mozarella_action)

        help_menu.addSeparator()

        reset_action = QAction("Reset to Default", self)
        reset_action.setStatusTip("Clear all profile data (history, bookmarks, config)")
        reset_action.triggered.connect(self.reset_profile)
        help_menu.addAction(reset_action)

        self.add_new_tab(QUrl(DEFAULT_HOME_URL), DEFAULT_NEW_TAB_LABEL)

        self.setWindowTitle(WINDOW_TITLE)
        self.setWindowIcon(QIcon(os.path.join(IMAGES_DIR, ICON_APP_64)))
        
        self.showMaximized()

    def add_new_tab(self, qurl=None, label=DEFAULT_TAB_LABEL):
        if qurl is None:
            qurl = QUrl('')

        # Create a splitter to hold browser and dev tools
        splitter = QSplitter(Qt.Horizontal)
        
        browser = QWebEngineView()
        browser.setUrl(qurl)
        
        # Enable context menu for dev tools
        browser.setContextMenuPolicy(Qt.CustomContextMenu)
        browser.customContextMenuRequested.connect(lambda pos, b=browser, s=splitter: self.show_context_menu(pos, b, s))
        
        # Create dev tools view (hidden by default)
        dev_view = QWebEngineView()
        dev_view.setVisible(False)
        browser.page().setDevToolsPage(dev_view.page())
        
        # Add to splitter
        splitter.addWidget(browser)
        splitter.addWidget(dev_view)
        splitter.setStretchFactor(0, 3)  # Browser takes 75%
        splitter.setStretchFactor(1, 1)  # Dev tools takes 25%
        
        # Store references
        splitter.browser = browser
        splitter.dev_view = dev_view
        splitter.dev_tools_visible = False
        
        i = self.tabs.addTab(splitter, label)
        self.tabs.setCurrentIndex(i)

        # Connect signals
        browser.urlChanged.connect(lambda qurl, browser=browser:
                                   self.update_urlbar(qurl, browser))

        browser.loadFinished.connect(lambda _, i=i, browser=browser:
                                     self.tabs.setTabText(i, browser.page().title()))
        
        browser.loadStarted.connect(self.on_load_started)
        browser.loadProgress.connect(self.on_load_progress)
        browser.loadFinished.connect(self.on_load_finished)
    
    def get_current_browser(self):
        """Get the current browser view from the tab"""
        current_widget = self.tabs.currentWidget()
        if isinstance(current_widget, QSplitter):
            return current_widget.browser
        return current_widget

    def tab_open_doubleclick(self, i):
        if i == -1:
            self.add_new_tab()

    def current_tab_changed(self, i):
        browser = self.get_current_browser()
        if browser:
            qurl = browser.url()
            self.update_urlbar(qurl, browser)
            self.update_title(browser)

    def close_current_tab(self, i):
        if self.tabs.count() <= MIN_TABS:
            return
        self.tabs.removeTab(i)

    def update_title(self, browser):
        current_browser = self.get_current_browser()
        if browser != current_browser:
            return

        title = browser.page().title()
        self.setWindowTitle(f"{title} - {APP_NAME}")
        self.status_title.setText(f"Title: {title}")

    def navigate_mozarella(self):
        browser = self.get_current_browser()
        if browser:
            browser.setUrl(QUrl(COMPANY_URL))

    def about(self):
        dlg = AboutDialog()
        dlg.exec_()

    def open_file(self):
        filename, _ = QFileDialog.getOpenFileName(self, "Open file", "", HTML_FILE_FILTER)

        if filename:
            with open(filename, 'r') as f:
                html = f.read()

            browser = self.get_current_browser()
            if browser:
                browser.setHtml(html)
                self.urlbar.setText(filename)

    def save_file(self):
        filename, _ = QFileDialog.getSaveFileName(self, "Save Page As", "", HTML_FILE_FILTER)

        if filename:
            html = self.tabs.currentWidget().page().mainFrame().toHtml()
            with open(filename, 'w') as f:
                f.write(html.encode('utf8'))

    def print_page(self):
        dlg = QPrintPreviewDialog()
        dlg.paintRequested.connect(self.browser.print_)
        dlg.exec_()

    def reload_page(self):
        """Reload current page"""
        browser = self.get_current_browser()
        if browser:
            browser.reload()
    
    def navigate_home(self):
        browser = self.get_current_browser()
        if browser:
            browser.setUrl(QUrl(DEFAULT_HOME_URL))

    def navigate_to_url(self):
        text = self.urlbar.text().strip()
        browser = self.get_current_browser()
        if not browser:
            return
        
        # Check if it looks like a URL (has dots and no spaces)
        if "." in text and " " not in text:
            q = QUrl(text)
            if q.scheme() == "":
                q.setScheme(DEFAULT_PROTOCOL)
            browser.setUrl(q)
        else:
            # Treat as search query
            search_url = SEARCH_ENGINE_URL.format(text.replace(" ", "+"))
            browser.setUrl(QUrl(search_url))

    def update_urlbar(self, q, browser=None):
        current_browser = self.get_current_browser()
        if browser != current_browser:
            return

        # Add to history
        self.history_manager.add(q.toString(), browser.page().title())
        ui_helpers.update_history_menu(self)

        self.urlbar.setText(q.toString())
        self.urlbar.setCursorPosition(0)
        
        # Update bookmark button
        ui_helpers.update_bookmark_button(self)
        
        # Update status bar info
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

    def show_context_menu(self, pos, browser, splitter):
        """Show context menu with dev tools option"""
        menu = QMenu(self)
        
        # Add dev tools toggle action
        if splitter.dev_tools_visible:
            dev_tools_action = QAction("Hide Dev Tools", self)
        else:
            dev_tools_action = QAction("Inspect Element (Dev Tools)", self)
        
        dev_tools_action.triggered.connect(lambda: self.toggle_dev_tools(splitter))
        menu.addAction(dev_tools_action)
        
        menu.addSeparator()
        
        # Add "Open with" submenu
        current_url = browser.url().toString()
        if current_url and current_url != "about:blank":
            open_with_menu = menu.addMenu("Open with")
            
            # Detect available browsers
            browsers = self.get_available_browsers()
            for browser_name, browser_path in browsers.items():
                action = QAction(browser_name, self)
                action.triggered.connect(lambda checked, url=current_url, path=browser_path: 
                                       self.open_in_external_browser(url, path))
                open_with_menu.addAction(action)
            
            if not browsers:
                no_browser_action = QAction("No browsers found", self)
                no_browser_action.setEnabled(False)
                open_with_menu.addAction(no_browser_action)
        
        # Show menu at cursor position
        menu.exec_(browser.mapToGlobal(pos))
    
    def toggle_dev_tools(self, splitter):
        """Toggle developer tools visibility"""
        splitter.dev_tools_visible = not splitter.dev_tools_visible
        splitter.dev_view.setVisible(splitter.dev_tools_visible)
        
        if splitter.dev_tools_visible:
            # Set splitter sizes when showing dev tools
            total_width = splitter.width()
            splitter.setSizes([int(total_width * 0.6), int(total_width * 0.4)])
    
    def toggle_current_dev_tools(self):
        """Toggle dev tools for current tab"""
        current_widget = self.tabs.currentWidget()
        if isinstance(current_widget, QSplitter):
            self.toggle_dev_tools(current_widget)
    
    def create_open_with_menu(self):
        """Create dropdown menu for opening in external browsers"""
        menu = QMenu(self)
        
        # Detect available browsers
        browsers = self.get_available_browsers()
        
        if browsers:
            for browser_name, browser_path in browsers.items():
                action = QAction(browser_name, self)
                action.triggered.connect(lambda checked, name=browser_name, path=browser_path: 
                                       self.open_current_url_in_browser(path))
                menu.addAction(action)
        else:
            no_browser_action = QAction("No browsers found", self)
            no_browser_action.setEnabled(False)
            menu.addAction(no_browser_action)
        
        return menu
    
    def open_current_url_in_browser(self, browser_path):
        """Open current URL in external browser"""
        browser = self.get_current_browser()
        if browser:
            url = browser.url().toString()
            if url and url != "about:blank":
                self.open_in_external_browser(url, browser_path)
            else:
                QMessageBox.information(self, "No URL", "No valid URL to open.")
    
    def get_available_browsers(self):
        """Detect available browsers on the system (cross-platform)"""
        import platform
        import subprocess
        
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
    
    def open_in_external_browser(self, url, browser_path):
        """Open URL in external browser (cross-platform)"""
        import subprocess
        import platform
        
        try:
            system = platform.system()
            
            if system == "Darwin":  # macOS
                # Use 'open' command for .app bundles
                subprocess.Popen(["open", "-a", browser_path, url])
            else:
                # Windows and Linux
                subprocess.Popen([browser_path, url])
        except Exception as e:
            QMessageBox.warning(self, "Error", f"Failed to open browser:\n{str(e)}")

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


app = QApplication(sys.argv)
app.setApplicationName(APP_NAME)
app.setOrganizationName(APP_ORGANIZATION)
app.setOrganizationDomain(APP_DOMAIN)

window = MainWindow()

app.exec_()
