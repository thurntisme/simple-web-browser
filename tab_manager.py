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
        
        # Add screenshot options (only in web browser mode)
        if not (self.main_window.api_mode_enabled or self.main_window.cmd_mode_enabled or self.main_window.pdf_mode_enabled):
            screenshot_menu = menu.addMenu("📸 Screenshot")
            
            # Screenshot current viewport
            viewport_action = QAction("📸 Current View", self.main_window)
            viewport_action.triggered.connect(lambda: self.take_screenshot(browser, "viewport"))
            screenshot_menu.addAction(viewport_action)
            
            # Screenshot full page
            fullpage_action = QAction("📄 Full Page", self.main_window)
            fullpage_action.triggered.connect(lambda: self.take_screenshot(browser, "fullpage"))
            screenshot_menu.addAction(fullpage_action)
            
            menu.addSeparator()
            
            # Add broken link scanner (only for web pages)
            if current_url and current_url != "about:blank" and not current_url.startswith("data:"):
                link_scanner_action = QAction("🔗 Scan for Broken Links", self.main_window)
                link_scanner_action.triggered.connect(lambda: self.scan_broken_links(browser))
                menu.addAction(link_scanner_action)
        
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
    
    def take_screenshot(self, browser, screenshot_type="viewport"):
        """Take a screenshot of the current web page
        
        Args:
            browser: The QWebEngineView to capture
            screenshot_type: "viewport" for current view, "fullpage" for entire page
        """
        try:
            # Get the current page
            page = browser.page()
            
            # Get page title for filename
            title = page.title() or "webpage"
            # Clean title for filename (remove invalid characters)
            import re
            clean_title = re.sub(r'[<>:"/\\|?*]', '_', title)[:50]  # Limit length
            
            # Generate filename with timestamp and type
            from datetime import datetime
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            type_suffix = "viewport" if screenshot_type == "viewport" else "fullpage"
            filename = f"screenshot_{clean_title}_{type_suffix}_{timestamp}.png"
            
            # Show save dialog
            from PyQt5.QtWidgets import QFileDialog
            file_path, _ = QFileDialog.getSaveFileName(
                self.main_window,
                f"Save Screenshot ({type_suffix.title()})",
                filename,
                "PNG Images (*.png);;JPEG Images (*.jpg);;All Files (*.*)"
            )
            
            if file_path:
                def on_screenshot_ready(pixmap):
                    if not pixmap.isNull():
                        # Save the screenshot
                        if pixmap.save(file_path):
                            # Show success message
                            self.main_window.status_info.setText(f"📸 {type_suffix.title()} screenshot saved: {file_path}")
                            QTimer.singleShot(3000, lambda: self.main_window.status_info.setText(""))
                            
                            # Optional: Show notification dialog
                            from PyQt5.QtWidgets import QMessageBox
                            reply = QMessageBox.question(
                                self.main_window,
                                "Screenshot Saved",
                                f"{type_suffix.title()} screenshot saved successfully!\n\n{file_path}\n\nWould you like to open the image?",
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
                
                if screenshot_type == "fullpage":
                    # Full page screenshot - capture the entire scrollable content
                    try:
                        # Method 1: Try using QWebEnginePage's built-in screenshot capability
                        # This should capture the full page content
                        
                        def capture_with_page_method():
                            # Use the page's built-in screenshot method if available
                            if hasattr(page, 'save'):
                                # Some versions have a direct save method
                                if page.save(file_path):
                                    on_screenshot_ready(QPixmap(file_path))
                                    return
                            
                            # Fallback: scroll-based capture
                            capture_by_scrolling()
                        
                        def capture_by_scrolling():
                            # Get current scroll position to restore later
                            page.runJavaScript("window.pageYOffset", lambda y: 
                                page.runJavaScript("window.pageXOffset", lambda x: 
                                    perform_scroll_capture(x, y)))
                        
                        def perform_scroll_capture(original_x, original_y):
                            # Scroll to top-left corner
                            page.runJavaScript("window.scrollTo(0, 0);")
                            
                            # Wait for scroll animation to complete
                            def take_shot_after_scroll():
                                # Capture the current view
                                shot = browser.grab()
                                
                                # Restore original scroll position
                                page.runJavaScript(f"window.scrollTo({original_x}, {original_y});")
                                
                                # Clean up the screenshot (remove scrollbars)
                                try:
                                    browser_size = browser.size()
                                    style = browser.style()
                                    scrollbar_width = style.pixelMetric(style.PM_ScrollBarExtent)
                                    
                                    # Calculate clean content area
                                    clean_width = browser_size.width() - scrollbar_width - 3
                                    clean_height = browser_size.height() - scrollbar_width - 3
                                    
                                    # Ensure positive dimensions
                                    clean_width = max(clean_width, int(browser_size.width() * 0.9))
                                    clean_height = max(clean_height, int(browser_size.height() * 0.9))
                                    
                                    crop_rect = QRect(0, 0, clean_width, clean_height)
                                    clean_shot = shot.copy(crop_rect)
                                    
                                    on_screenshot_ready(clean_shot)
                                except Exception as e:
                                    print(f"Full page screenshot cleanup error: {e}")
                                    on_screenshot_ready(shot)
                            
                            # Wait for scroll to complete
                            QTimer.singleShot(600, take_shot_after_scroll)
                        
                        # Start with the page method, fallback to scrolling
                        capture_with_page_method()
                        
                    except Exception as e:
                        print(f"Full page screenshot error: {e}")
                        # Ultimate fallback: treat as viewport screenshot
                        self.take_screenshot(browser, "viewport")
                    
                else:
                    # Viewport screenshot (current view) - remove scrollbars
                    try:
                        # Get the browser screenshot
                        full_pixmap = browser.grab()
                        
                        # Get browser and page dimensions
                        browser_size = browser.size()
                        page_size = page.contentsSize().toSize()
                        
                        # Calculate scrollbar presence and dimensions
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
                        content_width = max(content_width - 5, int(content_width * 0.95))  # Remove 5px or 5% margin
                        content_height = max(content_height - 5, int(content_height * 0.95))  # Remove 5px or 5% margin
                        
                        # Create the crop rectangle
                        crop_rect = QRect(0, 0, int(content_width), int(content_height))
                        
                        # Crop the screenshot to remove scrollbars
                        clean_pixmap = full_pixmap.copy(crop_rect)
                        
                        on_screenshot_ready(clean_pixmap)
                            
                    except Exception as e:
                        print(f"Viewport screenshot error: {e}")
                        # Fallback: aggressive cropping
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
    
    def scan_broken_links(self, browser):
        """Scan the current page for broken links"""
        try:
            page = browser.page()
            current_url = browser.url().toString()
            
            # Show initial status
            self.main_window.status_info.setText("🔗 Scanning for broken links...")
            
            # JavaScript to extract all links from the page
            js_code = """
            (function() {
                var links = [];
                var anchors = document.getElementsByTagName('a');
                for (var i = 0; i < anchors.length; i++) {
                    var href = anchors[i].href;
                    if (href && href.trim() !== '' && !href.startsWith('javascript:') && !href.startsWith('mailto:') && !href.startsWith('tel:')) {
                        links.push({
                            url: href,
                            text: anchors[i].textContent.trim() || anchors[i].innerText.trim() || '[No text]',
                            title: anchors[i].title || ''
                        });
                    }
                }
                return links;
            })();
            """
            
            def process_links(links):
                if not links:
                    self.main_window.status_info.setText("ℹ️ No links found on this page")
                    QTimer.singleShot(3000, lambda: self.main_window.status_info.setText(""))
                    return
                
                # Create and show the broken link scanner dialog
                self.show_broken_link_dialog(links, current_url)
            
            # Execute JavaScript to get all links
            page.runJavaScript(js_code, process_links)
            
        except Exception as e:
            self.main_window.status_info.setText(f"❌ Link scan error: {str(e)}")
            QTimer.singleShot(3000, lambda: self.main_window.status_info.setText(""))
    
    def show_broken_link_dialog(self, links, base_url):
        """Show dialog with broken link scanner results"""
        from PyQt5.QtWidgets import QDialog, QVBoxLayout, QHBoxLayout, QLabel, QTextEdit, QPushButton, QProgressBar, QSplitter
        from PyQt5.QtCore import QThread, pyqtSignal
        import urllib.request
        import urllib.parse
        from urllib.error import URLError, HTTPError
        import ssl
        
        class LinkCheckerThread(QThread):
            """Thread to check links without blocking UI"""
            progress_updated = pyqtSignal(int, int, str)  # current, total, status
            link_checked = pyqtSignal(dict)  # link result
            finished_checking = pyqtSignal()
            
            def __init__(self, links, base_url):
                super().__init__()
                self.links = links
                self.base_url = base_url
                self.should_stop = False
            
            def stop(self):
                self.should_stop = True
            
            def run(self):
                total_links = len(self.links)
                broken_links = []
                working_links = []
                
                # Create SSL context that doesn't verify certificates (for testing)
                ssl_context = ssl.create_default_context()
                ssl_context.check_hostname = False
                ssl_context.verify_mode = ssl.CERT_NONE
                
                for i, link in enumerate(self.links):
                    if self.should_stop:
                        break
                    
                    url = link['url']
                    self.progress_updated.emit(i + 1, total_links, f"Checking: {url[:50]}...")
                    
                    try:
                        # Handle relative URLs
                        if not url.startswith(('http://', 'https://')):
                            url = urllib.parse.urljoin(self.base_url, url)
                        
                        # Create request with headers to avoid being blocked
                        req = urllib.request.Request(url)
                        req.add_header('User-Agent', 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36')
                        req.add_header('Accept', 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8')
                        
                        # Try to open the URL
                        with urllib.request.urlopen(req, timeout=10, context=ssl_context) as response:
                            status_code = response.getcode()
                            if status_code >= 400:
                                link['status'] = f"Error {status_code}"
                                link['working'] = False
                                broken_links.append(link)
                            else:
                                link['status'] = f"OK ({status_code})"
                                link['working'] = True
                                working_links.append(link)
                    
                    except HTTPError as e:
                        link['status'] = f"HTTP Error {e.code}"
                        link['working'] = False
                        broken_links.append(link)
                    except URLError as e:
                        link['status'] = f"URL Error: {str(e.reason)}"
                        link['working'] = False
                        broken_links.append(link)
                    except Exception as e:
                        link['status'] = f"Error: {str(e)}"
                        link['working'] = False
                        broken_links.append(link)
                    
                    self.link_checked.emit(link)
                
                self.finished_checking.emit()
        
        # Create dialog
        dialog = QDialog(self.main_window)
        dialog.setWindowTitle(f"🔗 Link Scanner - {len(links)} links found")
        dialog.setMinimumSize(800, 600)
        dialog.resize(1000, 700)
        
        layout = QVBoxLayout(dialog)
        
        # Header
        header_label = QLabel(f"Scanning {len(links)} links from: {base_url}")
        header_label.setStyleSheet("font-weight: bold; padding: 10px; background-color: #f0f0f0; border-radius: 5px;")
        layout.addWidget(header_label)
        
        # Progress bar
        progress_bar = QProgressBar()
        progress_bar.setMaximum(len(links))
        progress_bar.setValue(0)
        layout.addWidget(progress_bar)
        
        # Status label
        status_label = QLabel("Starting scan...")
        layout.addWidget(status_label)
        
        # Splitter for results
        splitter = QSplitter(Qt.Horizontal)
        layout.addWidget(splitter)
        
        # Broken links area
        broken_widget = QWidget()
        broken_layout = QVBoxLayout(broken_widget)
        broken_layout.addWidget(QLabel("🚫 Broken Links:"))
        broken_text = QTextEdit()
        broken_text.setReadOnly(True)
        broken_text.setStyleSheet("background-color: #ffe6e6; font-family: monospace;")
        broken_layout.addWidget(broken_text)
        splitter.addWidget(broken_widget)
        
        # Working links area
        working_widget = QWidget()
        working_layout = QVBoxLayout(working_widget)
        working_layout.addWidget(QLabel("✅ Working Links:"))
        working_text = QTextEdit()
        working_text.setReadOnly(True)
        working_text.setStyleSheet("background-color: #e6ffe6; font-family: monospace;")
        working_layout.addWidget(working_text)
        splitter.addWidget(working_widget)
        
        # Set equal sizes
        splitter.setSizes([400, 400])
        
        # Buttons
        button_layout = QHBoxLayout()
        
        stop_button = QPushButton("⏹️ Stop Scan")
        stop_button.setEnabled(True)
        
        close_button = QPushButton("❌ Close")
        close_button.setEnabled(False)
        
        export_button = QPushButton("💾 Export Results")
        export_button.setEnabled(False)
        
        button_layout.addWidget(stop_button)
        button_layout.addStretch()
        button_layout.addWidget(export_button)
        button_layout.addWidget(close_button)
        layout.addWidget(QWidget())  # Spacer
        layout.addLayout(button_layout)
        
        # Create and start checker thread
        checker_thread = LinkCheckerThread(links, base_url)
        
        broken_count = 0
        working_count = 0
        
        def on_progress_updated(current, total, status):
            progress_bar.setValue(current)
            status_label.setText(f"Progress: {current}/{total} - {status}")
        
        def on_link_checked(link):
            nonlocal broken_count, working_count
            
            if link['working']:
                working_count += 1
                working_text.append(f"✅ {link['status']} - {link['text'][:50]}\n   {link['url']}\n")
            else:
                broken_count += 1
                broken_text.append(f"🚫 {link['status']} - {link['text'][:50]}\n   {link['url']}\n")
            
            # Update header with counts
            header_label.setText(f"Scanned {working_count + broken_count}/{len(links)} links - "
                               f"✅ {working_count} working, 🚫 {broken_count} broken")
        
        def on_finished():
            status_label.setText(f"✅ Scan complete! Found {broken_count} broken links out of {len(links)} total.")
            stop_button.setEnabled(False)
            close_button.setEnabled(True)
            export_button.setEnabled(True)
            
            # Show summary in main window
            if broken_count > 0:
                self.main_window.status_info.setText(f"🔗 Scan complete: {broken_count} broken links found")
            else:
                self.main_window.status_info.setText(f"🔗 Scan complete: All {len(links)} links are working!")
            QTimer.singleShot(5000, lambda: self.main_window.status_info.setText(""))
        
        def stop_scan():
            checker_thread.stop()
            status_label.setText("⏹️ Scan stopped by user")
            stop_button.setEnabled(False)
            close_button.setEnabled(True)
        
        def export_results():
            from PyQt5.QtWidgets import QFileDialog
            from datetime import datetime
            
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            filename = f"broken_links_scan_{timestamp}.txt"
            
            file_path, _ = QFileDialog.getSaveFileName(
                dialog,
                "Export Link Scan Results",
                filename,
                "Text Files (*.txt);;All Files (*.*)"
            )
            
            if file_path:
                try:
                    with open(file_path, 'w', encoding='utf-8') as f:
                        f.write(f"Link Scan Results\n")
                        f.write(f"Scanned URL: {base_url}\n")
                        f.write(f"Scan Date: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
                        f.write(f"Total Links: {len(links)}\n")
                        f.write(f"Working Links: {working_count}\n")
                        f.write(f"Broken Links: {broken_count}\n")
                        f.write("="*80 + "\n\n")
                        
                        if broken_count > 0:
                            f.write("BROKEN LINKS:\n")
                            f.write("-" * 40 + "\n")
                            f.write(broken_text.toPlainText())
                            f.write("\n\n")
                        
                        f.write("WORKING LINKS:\n")
                        f.write("-" * 40 + "\n")
                        f.write(working_text.toPlainText())
                    
                    status_label.setText(f"✅ Results exported to: {file_path}")
                except Exception as e:
                    status_label.setText(f"❌ Export failed: {str(e)}")
        
        # Connect signals
        checker_thread.progress_updated.connect(on_progress_updated)
        checker_thread.link_checked.connect(on_link_checked)
        checker_thread.finished_checking.connect(on_finished)
        
        stop_button.clicked.connect(stop_scan)
        close_button.clicked.connect(dialog.accept)
        export_button.clicked.connect(export_results)
        
        # Start the scan
        checker_thread.start()
        
        # Show dialog
        dialog.exec_()
        
        # Clean up
        if checker_thread.isRunning():
            checker_thread.stop()
            checker_thread.wait()
    
    def apply_font_size(self, font_size):
        """Apply font size to all open tabs"""
        for i in range(self.tabs.count()):
            widget = self.tabs.widget(i)
            if isinstance(widget, QSplitter):
                browser = widget.browser
                settings = browser.settings()
                settings.setFontSize(settings.DefaultFontSize, font_size)