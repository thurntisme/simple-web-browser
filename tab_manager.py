"""
Tab management functionality for the browser.
Handles tab creation, navigation, and developer tools.
"""

from PyQt5.QtCore import *
from PyQt5.QtWidgets import *
from PyQt5.QtWebEngineWidgets import *
from PyQt5.QtGui import QPixmap
from constants import *
import browser_utils


class TabManager:
    """Manages browser tabs and their functionality"""
    
    def __init__(self, main_window):
        self.main_window = main_window
        self.tabs = main_window.tabs
    
    def add_new_tab(self, qurl=None, label=DEFAULT_TAB_LABEL):
        """Add a new tab with browser and dev tools"""
        if qurl is None:
            qurl = QUrl('')

        # Create a splitter to hold browser and dev tools
        splitter = QSplitter(Qt.Horizontal)
        
        browser = QWebEngineView()
        browser.setUrl(qurl)
        
        # Apply font size from settings
        font_size = self.main_window.config_manager.get("font_size", 16)
        settings = browser.settings()
        settings.setFontSize(settings.DefaultFontSize, font_size)
        
        # Enable context menu for dev tools
        browser.setContextMenuPolicy(Qt.CustomContextMenu)
        browser.customContextMenuRequested.connect(
            lambda pos, b=browser, s=splitter: self.show_context_menu(pos, b, s)
        )
        
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
        browser.urlChanged.connect(
            lambda qurl, browser=browser: self.main_window.update_urlbar(qurl, browser)
        )

        browser.loadFinished.connect(
            lambda _, i=i, browser=browser: self.tabs.setTabText(i, browser.page().title())
        )
        
        browser.loadStarted.connect(self.main_window.on_load_started)
        browser.loadProgress.connect(self.main_window.on_load_progress)
        browser.loadFinished.connect(self.main_window.on_load_finished)
    
    def get_current_browser(self):
        """Get the current browser view from the tab"""
        current_widget = self.tabs.currentWidget()
        if isinstance(current_widget, QSplitter):
            return current_widget.browser
        return current_widget
    
    def tab_open_doubleclick(self, i):
        """Handle double-click on tab bar to create new tab"""
        if i == -1:
            self.add_new_tab()

    def current_tab_changed(self, i):
        """Handle tab change event"""
        browser = self.get_current_browser()
        if browser and hasattr(browser, 'url'):
            # This is a web browser tab
            qurl = browser.url()
            self.main_window.update_urlbar(qurl, browser)
            self.main_window.update_title(browser)
        else:
            # This might be an API tab, command line tab, or other non-browser tab
            current_widget = self.tabs.currentWidget()
            if current_widget and hasattr(self.main_window, 'api_tab_widget') and current_widget == self.main_window.api_tab_widget:
                # This is the API tab
                self.main_window.urlbar.setText("API Testing Mode")
                self.main_window.setWindowTitle(f"API Tester - {APP_NAME}")
                self.main_window.status_title.setText("API Testing Mode")
                self.main_window.status_info.setText("Ready for API testing")
            elif current_widget and hasattr(self.main_window, 'cmd_tab_widget') and current_widget == self.main_window.cmd_tab_widget:
                # This is the command line tab
                self.main_window.urlbar.setText("Command Line Mode")
                self.main_window.setWindowTitle(f"Terminal - {APP_NAME}")
                self.main_window.status_title.setText("Command Line Mode")
                self.main_window.status_info.setText("Ready for terminal commands")

    def close_current_tab(self, i):
        """Close tab if more than minimum tabs exist"""
        if self.tabs.count() <= MIN_TABS:
            return
        self.tabs.removeTab(i)
    
    def show_context_menu(self, pos, browser, splitter):
        """Show context menu with dev tools option"""
        menu = QMenu(self.main_window)
        
        # Add dev tools toggle action
        if splitter.dev_tools_visible:
            dev_tools_action = QAction("🔍 Hide Dev Tools", self.main_window)
        else:
            dev_tools_action = QAction("🔍 Inspect Element (Dev Tools)", self.main_window)
        
        dev_tools_action.triggered.connect(lambda: self.toggle_dev_tools(splitter))
        menu.addAction(dev_tools_action)
        
        menu.addSeparator()
        
        # Add "Open with" submenu
        current_url = browser.url().toString()
        if current_url and current_url != "about:blank":
            open_with_menu = menu.addMenu("🌐 Open with")
            
            # Detect available browsers
            browsers = browser_utils.get_available_browsers()
            for browser_name, browser_path in browsers.items():
                action = QAction(f"🌐 {browser_name}", self.main_window)
                action.triggered.connect(
                    lambda checked, url=current_url, path=browser_path: 
                    browser_utils.open_in_external_browser(url, path, self.main_window)
                )
                open_with_menu.addAction(action)
            
            if not browsers:
                no_browser_action = QAction("❌ No browsers found", self.main_window)
                no_browser_action.setEnabled(False)
                open_with_menu.addAction(no_browser_action)
        
        menu.addSeparator()
        
        # Add screenshot option (only in web browser mode)
        if not (self.main_window.api_mode_enabled or self.main_window.cmd_mode_enabled or self.main_window.pdf_mode_enabled):
            screenshot_action = QAction("📸 Take Screenshot", self.main_window)
            screenshot_action.triggered.connect(lambda: self.take_screenshot(browser))
            menu.addAction(screenshot_action)
        
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
    
    def take_screenshot(self, browser):
        """Take a screenshot of the current web page"""
        try:
            # Get the current page
            page = browser.page()
            
            # Get page title for filename
            title = page.title() or "webpage"
            # Clean title for filename (remove invalid characters)
            import re
            clean_title = re.sub(r'[<>:"/\\|?*]', '_', title)[:50]  # Limit length
            
            # Generate filename with timestamp
            from datetime import datetime
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            filename = f"screenshot_{clean_title}_{timestamp}.png"
            
            # Show save dialog
            from PyQt5.QtWidgets import QFileDialog
            file_path, _ = QFileDialog.getSaveFileName(
                self.main_window,
                "Save Screenshot",
                filename,
                "PNG Images (*.png);;JPEG Images (*.jpg);;All Files (*.*)"
            )
            
            if file_path:
                # Take screenshot of web content only (excluding scrollbars and UI elements)
                page = browser.page()
                
                # Use QWebEnginePage's built-in screenshot functionality
                # This captures only the web content without browser UI elements
                def on_screenshot_ready(pixmap):
                    if not pixmap.isNull():
                        # Save the screenshot
                        if pixmap.save(file_path):
                            # Show success message
                            self.main_window.status_info.setText(f"📸 Screenshot saved: {file_path}")
                            QTimer.singleShot(3000, lambda: self.main_window.status_info.setText(""))
                            
                            # Optional: Show notification dialog
                            from PyQt5.QtWidgets import QMessageBox
                            reply = QMessageBox.question(
                                self.main_window,
                                "Screenshot Saved",
                                f"Screenshot saved successfully!\n\n{file_path}\n\nWould you like to open the image?",
                                QMessageBox.Yes | QMessageBox.No,
                                QMessageBox.No
                            )
                            
                            if reply == QMessageBox.Yes:
                                # Open the screenshot file directly
                                import os
                                import subprocess
                                import platform
                                
                                if platform.system() == "Windows":
                                    os.startfile(file_path)
                                elif platform.system() == "Darwin":  # macOS
                                    subprocess.run(["open", file_path])
                                else:  # Linux
                                    subprocess.run(["xdg-open", file_path])
                        else:
                            # Show error message
                            self.main_window.status_info.setText("❌ Failed to save screenshot")
                            QTimer.singleShot(3000, lambda: self.main_window.status_info.setText(""))
                    else:
                        # Show error message for null pixmap
                        self.main_window.status_info.setText("❌ Failed to capture screenshot")
                        QTimer.singleShot(3000, lambda: self.main_window.status_info.setText(""))
                
                # Capture screenshot of web content only (excluding scrollbars and UI elements)
                # Use a more aggressive approach to ensure scrollbars are completely removed
                try:
                    # Get the full browser screenshot first
                    full_pixmap = browser.grab()
                    
                    # Get browser and page dimensions
                    browser_size = browser.size()
                    page_size = page.contentsSize().toSize()
                    
                    # Calculate scrollbar presence and dimensions more accurately
                    style = browser.style()
                    scrollbar_width = style.pixelMetric(style.PM_ScrollBarExtent)
                    
                    # Determine if scrollbars are present
                    has_vertical_scrollbar = page_size.width() > browser_size.width()
                    has_horizontal_scrollbar = page_size.height() > browser_size.height()
                    
                    # Calculate the clean content area
                    content_width = browser_size.width()
                    content_height = browser_size.height()
                    
                    # Remove scrollbar areas more aggressively
                    if has_vertical_scrollbar:
                        content_width -= (scrollbar_width + 2)  # Add extra margin for safety
                    if has_horizontal_scrollbar:
                        content_height -= (scrollbar_width + 2)  # Add extra margin for safety
                    
                    # Also remove a few extra pixels to ensure clean edges
                    content_width = max(content_width - 5, content_width * 0.95)  # Remove 5px or 5% margin
                    content_height = max(content_height - 5, content_height * 0.95)  # Remove 5px or 5% margin
                    
                    # Create the crop rectangle
                    crop_rect = QRect(0, 0, int(content_width), int(content_height))
                    
                    # Crop the screenshot to remove scrollbars
                    clean_pixmap = full_pixmap.copy(crop_rect)
                    
                    on_screenshot_ready(clean_pixmap)
                        
                except Exception as e:
                    print(f"Screenshot capture error: {e}")
                    # Ultimate fallback: aggressive cropping
                    try:
                        full_pixmap = browser.grab()
                        width = full_pixmap.width()
                        height = full_pixmap.height()
                        
                        # Remove 25 pixels from right and bottom to ensure scrollbars are gone
                        crop_width = max(width - 25, int(width * 0.92))  # Remove 25px or 8%
                        crop_height = max(height - 25, int(height * 0.92))  # Remove 25px or 8%
                        
                        crop_rect = QRect(0, 0, crop_width, crop_height)
                        cropped_pixmap = full_pixmap.copy(crop_rect)
                        on_screenshot_ready(cropped_pixmap)
                    except Exception as final_e:
                        print(f"Final fallback failed: {final_e}")
                        # Last resort: use original pixmap
                        on_screenshot_ready(browser.grab())
                    
        except Exception as e:
            # Show error message
            self.main_window.status_info.setText(f"❌ Screenshot error: {str(e)}")
            QTimer.singleShot(3000, lambda: self.main_window.status_info.setText(""))
    
    def apply_font_size(self, font_size):
        """Apply font size to all open tabs"""
        for i in range(self.tabs.count()):
            widget = self.tabs.widget(i)
            if isinstance(widget, QSplitter):
                browser = widget.browser
                settings = browser.settings()
                settings.setFontSize(settings.DefaultFontSize, font_size)