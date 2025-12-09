from PyQt5.QtCore import *
from PyQt5.QtWidgets import *
from PyQt5.QtGui import *
from PyQt5.QtWebEngineWidgets import *
from PyQt5.QtPrintSupport import *

import os
import sys
import json
from datetime import datetime

from constants import *


class AboutDialog(QDialog):
    def __init__(self, *args, **kwargs):
        super(AboutDialog, self).__init__(*args, **kwargs)

        QBtn = QDialogButtonBox.Ok  # No cancel
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

        self.history = self.load_history()
        self.bookmarks = self.load_bookmarks()

        self.tabs = QTabWidget()
        self.tabs.setDocumentMode(True)
        self.tabs.tabBarDoubleClicked.connect(self.tab_open_doubleclick)
        self.tabs.currentChanged.connect(self.current_tab_changed)
        self.tabs.setTabsClosable(False)

        self.setCentralWidget(self.tabs)

        self.status = QStatusBar()
        self.setStatusBar(self.status)
        
        # Status bar widgets
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
        reload_btn.triggered.connect(lambda: self.tabs.currentWidget().reload())
        navtb.addAction(reload_btn)

        navtb.addSeparator()

        self.urlbar = QLineEdit()
        self.urlbar.returnPressed.connect(self.navigate_to_url)
        navtb.addWidget(self.urlbar)
        
        self.bookmark_btn = QPushButton("☆")
        self.bookmark_btn.setMaximumWidth(30)
        self.bookmark_btn.setStatusTip("Add/Remove bookmark")
        self.bookmark_btn.clicked.connect(self.toggle_bookmark)
        navtb.addWidget(self.bookmark_btn)

        # Uncomment to disable native menubar on Mac
        # self.menuBar().setNativeMenuBar(False)

        file_menu = self.menuBar().addMenu("&File")

        new_tab_action = QAction(QIcon(os.path.join(IMAGES_DIR, ICON_NEW_TAB)), "New Tab", self)
        new_tab_action.setStatusTip("Open a new tab")
        new_tab_action.triggered.connect(lambda _: self.add_new_tab())
        file_menu.addAction(new_tab_action)

        open_file_action = QAction(QIcon(os.path.join(IMAGES_DIR, ICON_OPEN_FILE)), "Open file...", self)
        open_file_action.setStatusTip("Open from file")
        open_file_action.triggered.connect(self.open_file)
        file_menu.addAction(open_file_action)

        save_file_action = QAction(QIcon(os.path.join(IMAGES_DIR, ICON_SAVE_FILE)), "Save Page As...", self)
        save_file_action.setStatusTip("Save current page to file")
        save_file_action.triggered.connect(self.save_file)
        file_menu.addAction(save_file_action)

        print_action = QAction(QIcon(os.path.join(IMAGES_DIR, ICON_PRINT)), "Print...", self)
        print_action.setStatusTip("Print current page")
        print_action.triggered.connect(self.print_page)
        file_menu.addAction(print_action)

        self.bookmarks_menu = self.menuBar().addMenu("&Bookmarks")
        self.update_bookmarks_menu()

        self.history_menu = self.menuBar().addMenu("&History")
        self.update_history_menu()

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

        self.add_new_tab(QUrl(DEFAULT_HOME_URL), DEFAULT_NEW_TAB_LABEL)

        self.setWindowTitle(WINDOW_TITLE)
        self.setWindowIcon(QIcon(os.path.join(IMAGES_DIR, ICON_APP_64)))
        
        self.showMaximized()

    def add_new_tab(self, qurl=None, label=DEFAULT_TAB_LABEL):

        if qurl is None:
            qurl = QUrl('')

        browser = QWebEngineView()
        browser.setUrl(qurl)
        i = self.tabs.addTab(browser, label)

        self.tabs.setCurrentIndex(i)

        # Connect signals
        browser.urlChanged.connect(lambda qurl, browser=browser:
                                   self.update_urlbar(qurl, browser))

        browser.loadFinished.connect(lambda _, i=i, browser=browser:
                                     self.tabs.setTabText(i, browser.page().title()))
        
        browser.loadStarted.connect(self.on_load_started)
        browser.loadProgress.connect(self.on_load_progress)
        browser.loadFinished.connect(self.on_load_finished)

    def tab_open_doubleclick(self, i):
        if i == -1:  # No tab under the click
            self.add_new_tab()

    def current_tab_changed(self, i):
        qurl = self.tabs.currentWidget().url()
        self.update_urlbar(qurl, self.tabs.currentWidget())
        self.update_title(self.tabs.currentWidget())

    def close_current_tab(self, i):
        if self.tabs.count() <= MIN_TABS:
            return

        self.tabs.removeTab(i)

    def update_title(self, browser):
        if browser != self.tabs.currentWidget():
            # If this signal is not from the current tab, ignore
            return

        title = self.tabs.currentWidget().page().title()
        self.setWindowTitle(f"{title} - {APP_NAME}")
        self.status_title.setText(f"Title: {title}")

    def navigate_mozarella(self):
        self.tabs.currentWidget().setUrl(QUrl(COMPANY_URL))

    def about(self):
        dlg = AboutDialog()
        dlg.exec_()

    def open_file(self):
        filename, _ = QFileDialog.getOpenFileName(self, "Open file", "",
                                                  HTML_FILE_FILTER)

        if filename:
            with open(filename, 'r') as f:
                html = f.read()

            self.tabs.currentWidget().setHtml(html)
            self.urlbar.setText(filename)

    def save_file(self):
        filename, _ = QFileDialog.getSaveFileName(self, "Save Page As", "",
                                                  HTML_FILE_FILTER)

        if filename:
            html = self.tabs.currentWidget().page().mainFrame().toHtml()
            with open(filename, 'w') as f:
                f.write(html.encode('utf8'))

    def print_page(self):
        dlg = QPrintPreviewDialog()
        dlg.paintRequested.connect(self.browser.print_)
        dlg.exec_()

    def navigate_home(self):
        self.tabs.currentWidget().setUrl(QUrl(DEFAULT_HOME_URL))

    def navigate_to_url(self):  # Does not receive the Url
        text = self.urlbar.text().strip()
        
        # Check if it looks like a URL (has dots and no spaces)
        if "." in text and " " not in text:
            q = QUrl(text)
            if q.scheme() == "":
                q.setScheme(DEFAULT_PROTOCOL)
            self.tabs.currentWidget().setUrl(q)
        else:
            # Treat as search query
            search_url = SEARCH_ENGINE_URL.format(text.replace(" ", "+"))
            self.tabs.currentWidget().setUrl(QUrl(search_url))

    def update_urlbar(self, q, browser=None):

        if browser != self.tabs.currentWidget():
            # If this signal is not from the current tab, ignore
            return

        # Add to history
        self.add_to_history(q.toString(), browser.page().title())

        self.urlbar.setText(q.toString())
        self.urlbar.setCursorPosition(0)
        
        # Update bookmark button
        self.update_bookmark_button()
        
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
            browser = self.tabs.currentWidget()
            title = browser.page().title()
            self.status_title.setText(f"Title: {title}")
        else:
            self.status_title.setText("Failed to load")

    def load_history(self):
        """Load browsing history from JSON file"""
        try:
            if os.path.exists(HISTORY_FILE):
                with open(HISTORY_FILE, 'r', encoding='utf-8') as f:
                    return json.load(f)
        except Exception as e:
            print(f"Error loading history: {e}")
        return []

    def save_history(self):
        """Save browsing history to JSON file"""
        try:
            with open(HISTORY_FILE, 'w', encoding='utf-8') as f:
                json.dump(self.history, f, indent=2, ensure_ascii=False)
        except Exception as e:
            print(f"Error saving history: {e}")

    def add_to_history(self, url, title):
        """Add a URL to browsing history (keeps last 20 entries)"""
        if not url or url == "about:blank":
            return
        
        entry = {
            "url": url,
            "title": title if title else url,
            "timestamp": datetime.now().isoformat()
        }
        
        # Avoid duplicate consecutive entries
        if self.history and self.history[-1].get("url") == url:
            return
        
        self.history.append(entry)
        
        # Keep only last 20 entries
        if len(self.history) > MAX_HISTORY_ENTRIES:
            self.history = self.history[-MAX_HISTORY_ENTRIES:]
        
        self.save_history()
        self.update_history_menu()

    def update_history_menu(self):
        """Update the History menu with recent entries"""
        self.history_menu.clear()
        
        clear_action = QAction("Clear History", self)
        clear_action.triggered.connect(self.clear_history)
        self.history_menu.addAction(clear_action)
        
        if self.history:
            self.history_menu.addSeparator()
            
            # Show history in reverse order (most recent first)
            for entry in reversed(self.history):
                title = entry.get("title", entry.get("url"))
                url = entry.get("url")
                
                # Truncate long titles
                if len(title) > 50:
                    title = title[:47] + "..."
                
                action = QAction(title, self)
                action.setStatusTip(url)
                action.triggered.connect(lambda checked, u=url: self.navigate_to_history_url(u))
                self.history_menu.addAction(action)
        else:
            empty_action = QAction("No history", self)
            empty_action.setEnabled(False)
            self.history_menu.addAction(empty_action)

    def navigate_to_history_url(self, url):
        """Navigate to a URL from history"""
        self.tabs.currentWidget().setUrl(QUrl(url))

    def clear_history(self):
        """Clear all browsing history"""
        self.history = []
        self.save_history()
        self.update_history_menu()

    def load_bookmarks(self):
        """Load bookmarks from JSON file"""
        try:
            if os.path.exists(BOOKMARKS_FILE):
                with open(BOOKMARKS_FILE, 'r', encoding='utf-8') as f:
                    return json.load(f)
        except Exception as e:
            print(f"Error loading bookmarks: {e}")
        return []

    def save_bookmarks(self):
        """Save bookmarks to JSON file"""
        try:
            with open(BOOKMARKS_FILE, 'w', encoding='utf-8') as f:
                json.dump(self.bookmarks, f, indent=2, ensure_ascii=False)
        except Exception as e:
            print(f"Error saving bookmarks: {e}")

    def update_bookmarks_menu(self):
        """Update the Bookmarks menu"""
        self.bookmarks_menu.clear()
        
        add_action = QAction("Add Bookmark...", self)
        add_action.setShortcut("Ctrl+D")
        add_action.triggered.connect(self.add_bookmark)
        self.bookmarks_menu.addAction(add_action)
        
        manage_action = QAction("Manage Bookmarks...", self)
        manage_action.triggered.connect(self.manage_bookmarks)
        self.bookmarks_menu.addAction(manage_action)
        
        if self.bookmarks:
            self.bookmarks_menu.addSeparator()
            
            for bookmark in self.bookmarks:
                title = bookmark.get("title", bookmark.get("url"))
                url = bookmark.get("url")
                
                # Truncate long titles
                if len(title) > 50:
                    title = title[:47] + "..."
                
                action = QAction(title, self)
                action.setStatusTip(url)
                action.triggered.connect(lambda checked, u=url: self.navigate_to_bookmark(u))
                self.bookmarks_menu.addAction(action)
        else:
            empty_action = QAction("No bookmarks", self)
            empty_action.setEnabled(False)
            self.bookmarks_menu.addAction(empty_action)

    def is_bookmarked(self, url):
        """Check if URL is bookmarked"""
        for bookmark in self.bookmarks:
            if bookmark.get("url") == url:
                return True
        return False

    def update_bookmark_button(self):
        """Update bookmark button appearance based on current page"""
        browser = self.tabs.currentWidget()
        if browser:
            url = browser.url().toString()
            if self.is_bookmarked(url):
                self.bookmark_btn.setText("★")  # Filled star
                self.bookmark_btn.setStatusTip("Remove bookmark")
            else:
                self.bookmark_btn.setText("☆")  # Empty star
                self.bookmark_btn.setStatusTip("Add bookmark")

    def toggle_bookmark(self):
        """Toggle bookmark for current page"""
        browser = self.tabs.currentWidget()
        if browser:
            url = browser.url().toString()
            
            # Check if already bookmarked
            for i, bookmark in enumerate(self.bookmarks):
                if bookmark.get("url") == url:
                    # Remove bookmark
                    del self.bookmarks[i]
                    self.save_bookmarks()
                    self.update_bookmarks_menu()
                    self.update_bookmark_button()
                    return
            
            # Add bookmark
            title = browser.page().title()
            new_title, ok = QInputDialog.getText(self, "Add Bookmark", 
                                                  "Bookmark name:", 
                                                  QLineEdit.Normal, 
                                                  title)
            
            if ok and new_title:
                bookmark = {
                    "title": new_title,
                    "url": url,
                    "timestamp": datetime.now().isoformat()
                }
                self.bookmarks.append(bookmark)
                self.save_bookmarks()
                self.update_bookmarks_menu()
                self.update_bookmark_button()

    def add_bookmark(self):
        """Add current page to bookmarks (called from menu)"""
        self.toggle_bookmark()

    def navigate_to_bookmark(self, url):
        """Navigate to a bookmarked URL"""
        self.tabs.currentWidget().setUrl(QUrl(url))

    def manage_bookmarks(self):
        """Open bookmark management dialog"""
        dialog = BookmarkManagerDialog(self.bookmarks, self)
        if dialog.exec_() == QDialog.Accepted:
            self.bookmarks = dialog.get_bookmarks()
            self.save_bookmarks()
            self.update_bookmarks_menu()


class BookmarkManagerDialog(QDialog):
    """Dialog for managing bookmarks"""
    def __init__(self, bookmarks, parent=None):
        super().__init__(parent)
        self.bookmarks = bookmarks.copy()
        self.setWindowTitle("Manage Bookmarks")
        self.setMinimumSize(600, 400)
        
        layout = QVBoxLayout()
        
        # List widget
        self.list_widget = QListWidget()
        self.update_list()
        layout.addWidget(self.list_widget)
        
        # Buttons
        button_layout = QHBoxLayout()
        
        edit_btn = QPushButton("Edit")
        edit_btn.clicked.connect(self.edit_bookmark)
        button_layout.addWidget(edit_btn)
        
        delete_btn = QPushButton("Delete")
        delete_btn.clicked.connect(self.delete_bookmark)
        button_layout.addWidget(delete_btn)
        
        button_layout.addStretch()
        
        close_btn = QPushButton("Close")
        close_btn.clicked.connect(self.accept)
        button_layout.addWidget(close_btn)
        
        layout.addLayout(button_layout)
        self.setLayout(layout)
    
    def update_list(self):
        """Update the bookmark list"""
        self.list_widget.clear()
        for bookmark in self.bookmarks:
            title = bookmark.get("title", "Untitled")
            url = bookmark.get("url", "")
            self.list_widget.addItem(f"{title} - {url}")
    
    def edit_bookmark(self):
        """Edit selected bookmark"""
        current_row = self.list_widget.currentRow()
        if current_row < 0:
            QMessageBox.warning(self, "Edit Bookmark", "Please select a bookmark to edit.")
            return
        
        bookmark = self.bookmarks[current_row]
        new_title, ok = QInputDialog.getText(self, "Edit Bookmark", 
                                              "Bookmark name:", 
                                              QLineEdit.Normal, 
                                              bookmark.get("title", ""))
        
        if ok and new_title:
            self.bookmarks[current_row]["title"] = new_title
            self.update_list()
    
    def delete_bookmark(self):
        """Delete selected bookmark"""
        current_row = self.list_widget.currentRow()
        if current_row < 0:
            QMessageBox.warning(self, "Delete Bookmark", "Please select a bookmark to delete.")
            return
        
        reply = QMessageBox.question(self, "Delete Bookmark", 
                                      "Are you sure you want to delete this bookmark?",
                                      QMessageBox.Yes | QMessageBox.No)
        
        if reply == QMessageBox.Yes:
            del self.bookmarks[current_row]
            self.update_list()
    
    def get_bookmarks(self):
        """Return the modified bookmarks list"""
        return self.bookmarks


app = QApplication(sys.argv)
app.setApplicationName(APP_NAME)
app.setOrganizationName(APP_ORGANIZATION)
app.setOrganizationDomain(APP_DOMAIN)

window = MainWindow()

app.exec_()