"""
Tab management functionality for the browser.
Handles tab creation, navigation, and developer tools.
"""

from PyQt5.QtCore import *
from PyQt5.QtWidgets import *
from PyQt5.QtWebEngineWidgets import *
from PyQt5.QtGui import QPixmap, QColor, QPainter, QPen, QBrush, QFont
from constants import *
import browser_utils


class NetworkTimelineWidget(QWidget):
    """Custom widget for displaying network request timeline waterfall chart"""
    
    def __init__(self):
        super().__init__()
        self.requests = []
        self.setMinimumHeight(400)
        self.setStyleSheet("background-color: white;")
        
        # Timeline settings
        self.row_height = 25
        self.left_margin = 200
        self.right_margin = 50
        self.top_margin = 30
        self.bottom_margin = 20
        
        # Colors for different phases
        self.colors = {
            'dns': QColor(255, 193, 7),      # Yellow - DNS lookup
            'tcp': QColor(40, 167, 69),      # Green - TCP connect
            'tls': QColor(220, 53, 69),      # Red - TLS handshake
            'request': QColor(0, 123, 255),  # Blue - Request
            'response': QColor(108, 117, 125) # Gray - Response
        }
    
    def update_requests(self, requests):
        """Update the requests data and repaint"""
        self.requests = requests
        self.update_size()
        self.update()
    
    def clear_requests(self):
        """Clear all requests"""
        self.requests = []
        self.update()
    
    def update_size(self):
        """Update widget size based on number of requests"""
        if self.requests:
            height = self.top_margin + len(self.requests) * self.row_height + self.bottom_margin
            self.setMinimumHeight(max(400, height))
    
    def paintEvent(self, event):
        """Paint the waterfall chart"""
        painter = QPainter(self)
        painter.setRenderHint(QPainter.Antialiasing)
        
        if not self.requests:
            # Draw empty state
            painter.setPen(QPen(QColor(108, 117, 125), 1))
            painter.drawText(self.rect(), Qt.AlignCenter, "No network requests recorded yet.\nClick 'Start Recording' to begin monitoring.")
            return
        
        # Calculate time range
        start_times = [r.get('startTime', 0) for r in self.requests if r.get('startTime')]
        end_times = [r.get('endTime', r.get('startTime', 0)) for r in self.requests if r.get('startTime')]
        
        if not start_times:
            return
        
        min_time = min(start_times)
        max_time = max(end_times) if end_times else min_time + 1000
        time_range = max_time - min_time
        
        if time_range <= 0:
            time_range = 1000  # Default 1 second range
        
        # Calculate chart dimensions
        chart_width = self.width() - self.left_margin - self.right_margin
        chart_height = len(self.requests) * self.row_height
        
        # Draw time axis
        self.draw_time_axis(painter, min_time, max_time, time_range, chart_width)
        
        # Draw requests
        for i, request in enumerate(self.requests):
            y = self.top_margin + i * self.row_height
            self.draw_request_bar(painter, request, y, min_time, time_range, chart_width)
            self.draw_request_label(painter, request, y)
    
    def draw_time_axis(self, painter, min_time, max_time, time_range, chart_width):
        """Draw the time axis at the top"""
        painter.setPen(QPen(QColor(108, 117, 125), 1))
        
        # Draw axis line
        y = self.top_margin - 10
        painter.drawLine(self.left_margin, y, self.left_margin + chart_width, y)
        
        # Draw time markers
        num_markers = 10
        for i in range(num_markers + 1):
            x = self.left_margin + (i * chart_width / num_markers)
            time_ms = min_time + (i * time_range / num_markers)
            
            # Draw tick
            painter.drawLine(x, y - 3, x, y + 3)
            
            # Draw time label
            if time_ms < 1000:
                time_text = f"{time_ms:.0f}ms"
            else:
                time_text = f"{time_ms/1000:.1f}s"
            
            painter.drawText(x - 20, y - 15, 40, 12, Qt.AlignCenter, time_text)
    
    def draw_request_bar(self, painter, request, y, min_time, time_range, chart_width):
        """Draw a single request bar with timing phases"""
        start_time = request.get('startTime', 0)
        end_time = request.get('endTime', start_time)
        timing = request.get('timing', {})
        
        if start_time == 0:
            return
        
        # Calculate position and width
        start_x = self.left_margin + ((start_time - min_time) / time_range) * chart_width
        
        if end_time > start_time:
            total_width = ((end_time - start_time) / time_range) * chart_width
        else:
            total_width = 5  # Minimum width for pending requests
        
        bar_height = self.row_height - 4
        bar_y = y + 2
        
        if timing:
            # Draw detailed timing phases
            current_x = start_x
            
            phases = [
                ('dns', timing.get('dns', 0)),
                ('tcp', timing.get('tcp', 0)),
                ('tls', timing.get('tls', 0)),
                ('request', timing.get('request', 0)),
                ('response', timing.get('response', 0))
            ]
            
            total_timing = sum(phase[1] for phase in phases)
            
            if total_timing > 0:
                for phase_name, phase_time in phases:
                    if phase_time > 0:
                        phase_width = (phase_time / total_timing) * total_width
                        
                        # Draw phase bar
                        painter.fillRect(current_x, bar_y, phase_width, bar_height, 
                                       QBrush(self.colors.get(phase_name, QColor(200, 200, 200))))
                        
                        # Draw phase border
                        painter.setPen(QPen(QColor(255, 255, 255), 1))
                        painter.drawRect(current_x, bar_y, phase_width, bar_height)
                        
                        current_x += phase_width
            else:
                # No timing data, draw simple bar
                color = QColor(108, 117, 125) if end_time > start_time else QColor(255, 193, 7)
                painter.fillRect(start_x, bar_y, total_width, bar_height, QBrush(color))
        else:
            # No timing data, draw simple bar
            color = QColor(108, 117, 125) if end_time > start_time else QColor(255, 193, 7)
            painter.fillRect(start_x, bar_y, total_width, bar_height, QBrush(color))
        
        # Draw status indicator
        status = request.get('status', 0)
        if status:
            if status < 300:
                status_color = QColor(40, 167, 69)  # Green
            elif status < 400:
                status_color = QColor(255, 193, 7)  # Yellow
            else:
                status_color = QColor(220, 53, 69)  # Red
            
            painter.fillRect(start_x - 3, bar_y, 3, bar_height, QBrush(status_color))
    
    def draw_request_label(self, painter, request, y):
        """Draw request label on the left side"""
        url = request.get('url', '')
        method = request.get('method', 'GET')
        
        # Truncate URL if too long
        if len(url) > 30:
            url = '...' + url[-27:]
        
        # Draw method
        painter.setPen(QPen(QColor(0, 123, 255), 1))
        painter.drawText(5, y + 2, 40, self.row_height - 4, Qt.AlignLeft | Qt.AlignVCenter, method)
        
        # Draw URL
        painter.setPen(QPen(QColor(33, 37, 41), 1))
        painter.drawText(50, y + 2, self.left_margin - 55, self.row_height - 4, 
                        Qt.AlignLeft | Qt.AlignVCenter, url)
        
        # Draw timing info
        start_time = request.get('startTime', 0)
        end_time = request.get('endTime', 0)
        if end_time > start_time:
            duration = end_time - start_time
            timing_text = f"{duration:.0f}ms"
            painter.setPen(QPen(QColor(108, 117, 125), 1))
            painter.drawText(self.width() - self.right_margin + 5, y + 2, 
                           self.right_margin - 10, self.row_height - 4, 
                           Qt.AlignLeft | Qt.AlignVCenter, timing_text)


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
            elif current_widget and hasattr(self.main_window, 'malware_tab_widget') and current_widget == self.main_window.malware_tab_widget:
                # This is the malware scanner tab
                self.main_window.urlbar.setText("Malware Scanner Mode")
                self.main_window.setWindowTitle(f"Malware Scanner - {APP_NAME}")
                self.main_window.status_title.setText("Malware Scanner Mode")
                self.main_window.status_info.setText("Ready for security analysis")

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
        
        # Add "Set as Homepage" feature (only for valid web pages)
        if (current_url and current_url != "about:blank" and not current_url.startswith("data:") and 
            not (self.main_window.api_mode_enabled or self.main_window.cmd_mode_enabled or self.main_window.pdf_mode_enabled)):
            homepage_action = QAction("🏠 Set as Homepage", self.main_window)
            homepage_action.triggered.connect(lambda: self.set_as_homepage(browser))
            menu.addAction(homepage_action)
            
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
                # Create Scan Tools submenu
                scan_menu = menu.addMenu("🔍 Scan Tools")
                
                link_scanner_action = QAction("🔗 Scan for Broken Links", self.main_window)
                link_scanner_action.triggered.connect(lambda: self.scan_broken_links(browser))
                scan_menu.addAction(link_scanner_action)
                
                script_scanner_action = QAction("📜 Scan Scripts (Inline, External)", self.main_window)
                script_scanner_action.triggered.connect(lambda: self.scan_scripts(browser))
                scan_menu.addAction(script_scanner_action)
                
                # Add advanced script analysis
                advanced_script_action = QAction("🔍 Advanced Script Analysis", self.main_window)
                advanced_script_action.triggered.connect(lambda: self.advanced_script_analysis(browser))
                scan_menu.addAction(advanced_script_action)
                
                scan_menu.addSeparator()
                
                # Add ad blocker features
                ad_scanner_action = QAction("🚫 Scan & Remove Ads", self.main_window)
                ad_scanner_action.triggered.connect(lambda: self.scan_and_remove_ads(browser))
                scan_menu.addAction(ad_scanner_action)
                
                ad_analysis_action = QAction("📊 Ad Analysis Report", self.main_window)
                ad_analysis_action.triggered.connect(lambda: self.analyze_ads(browser))
                scan_menu.addAction(ad_analysis_action)
                
                # Add page speed analyzer
                speed_analyzer_action = QAction("⚡ Page Speed Analyzer", self.main_window)
                speed_analyzer_action.triggered.connect(lambda: self.analyze_page_speed(browser))
                scan_menu.addAction(speed_analyzer_action)
                security_score_action = QAction("🛡️ Security Score", self.main_window)
                security_score_action.triggered.connect(lambda: self.analyze_security_score(browser))
                scan_menu.addAction(security_score_action)
                
                menu.addSeparator()
                
                # Create Security Tools submenu
                security_menu = menu.addMenu("🛡️ Security Tools")
                
                # Move Privacy Score to Security Tools
                privacy_score_action = QAction("🔒 Privacy Score", self.main_window)
                privacy_score_action.triggered.connect(lambda: self.analyze_privacy_score(browser))
                security_menu.addAction(privacy_score_action)
                
                # Move Security Score to Security Tools
                security_score_action = QAction("🛡️ Security Score", self.main_window)
                security_score_action.triggered.connect(lambda: self.analyze_security_score(browser))
                security_menu.addAction(security_score_action)
                
                # Add Header Policy Simulator
                header_policy_action = QAction("🛡️ Header Policy Simulator", self.main_window)
                header_policy_action.triggered.connect(lambda: self.show_header_policy_simulator(browser))
                security_menu.addAction(header_policy_action)
                
                # Add CSRF/CORS Visual Tester feature
                csrf_cors_tester_action = QAction("🛡️ CSRF/CORS Visual Tester", self.main_window)
                csrf_cors_tester_action.triggered.connect(lambda: self.test_csrf_cors(browser))
                security_menu.addAction(csrf_cors_tester_action)
                
                # Add Network Request Timeline feature
                network_timeline_action = QAction("📊 Network Request Timeline", self.main_window)
                network_timeline_action.triggered.connect(lambda: self.show_network_timeline(browser))
                menu.addAction(network_timeline_action)
                
                # Add SEO Analyzer feature
                seo_analyzer_action = QAction("🔍 SEO Analyzer", self.main_window)
                seo_analyzer_action.triggered.connect(lambda: self.analyze_seo(browser))
                menu.addAction(seo_analyzer_action)
                
                # Create Detector Tools submenu
                detector_menu = menu.addMenu("🔍 Detector Tools")
                
                # Add Font Detector feature
                font_detector_action = QAction("🔤 Font Detector", self.main_window)
                font_detector_action.triggered.connect(lambda: self.detect_fonts(browser))
                detector_menu.addAction(font_detector_action)
                
                # Add Technology Detector feature
                tech_detector_action = QAction("🔧 Technology Detector", self.main_window)
                tech_detector_action.triggered.connect(lambda: self.detect_technologies(browser))
                detector_menu.addAction(tech_detector_action)
                
                # Add Store Management feature
                store_management_action = QAction("💾 Store Management", self.main_window)
                store_management_action.triggered.connect(lambda: self.manage_storage(browser))
                menu.addAction(store_management_action)
        
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
    
    def set_as_homepage(self, browser):
        """Set the current page as homepage"""
        try:
            current_url = browser.url().toString()
            current_title = browser.page().title()
            
            if not current_url or current_url == "about:blank" or current_url.startswith("data:"):
                self.main_window.status_info.setText("❌ Cannot set this page as homepage")
                QTimer.singleShot(3000, lambda: self.main_window.status_info.setText(""))
                return
            
            # Show confirmation dialog
            from PyQt5.QtWidgets import QMessageBox
            reply = QMessageBox.question(
                self.main_window,
                "Set as Homepage",
                f"Set this page as your homepage?\n\n"
                f"Title: {current_title}\n"
                f"URL: {current_url}\n\n"
                f"This will replace your current homepage setting.",
                QMessageBox.Yes | QMessageBox.No,
                QMessageBox.Yes
            )
            
            if reply == QMessageBox.Yes:
                # Save the URL as homepage in config
                self.main_window.config_manager.set("home_url", current_url)
                self.main_window.config_manager.set("use_welcome_page", False)  # Disable welcome page
                self.main_window.config_manager.save()
                
                # Show success message
                self.main_window.status_info.setText(f"🏠 Homepage set to: {current_title}")
                QTimer.singleShot(4000, lambda: self.main_window.status_info.setText(""))
                
                # Show info message
                QMessageBox.information(
                    self.main_window,
                    "Homepage Updated",
                    f"Homepage has been set to:\n{current_title}\n\n"
                    f"This will be loaded when you:\n"
                    f"• Click the Home button\n"
                    f"• Open a new tab (if configured)\n"
                    f"• Start the browser"
                )
            
        except Exception as e:
            self.main_window.status_info.setText(f"❌ Error setting homepage: {str(e)}")
            QTimer.singleShot(3000, lambda: self.main_window.status_info.setText(""))
    
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
    
    def scan_scripts(self, browser):
        """Scan the current page for inline scripts and external script links"""
        try:
            page = browser.page()
            current_url = browser.url().toString()
            
            # Show initial status
            self.main_window.status_info.setText("📜 Scanning for scripts...")
            
            # JavaScript to extract all scripts from the page
            js_code = """
            (function() {
                var scripts = {
                    inline: [],
                    external: []
                };
                
                var scriptTags = document.getElementsByTagName('script');
                
                for (var i = 0; i < scriptTags.length; i++) {
                    var script = scriptTags[i];
                    
                    if (script.src) {
                        // External script
                        scripts.external.push({
                            src: script.src,
                            type: script.type || 'text/javascript',
                            async: script.async || false,
                            defer: script.defer || false,
                            crossorigin: script.crossOrigin || '',
                            integrity: script.integrity || '',
                            id: script.id || '',
                            className: script.className || ''
                        });
                    } else if (script.textContent || script.innerHTML) {
                        // Inline script
                        var content = script.textContent || script.innerHTML;
                        scripts.inline.push({
                            content: content.trim(),
                            type: script.type || 'text/javascript',
                            id: script.id || '',
                            className: script.className || '',
                            length: content.trim().length,
                            preview: content.trim().substring(0, 100) + (content.trim().length > 100 ? '...' : '')
                        });
                    }
                }
                
                return scripts;
            })();
            """
            
            def process_scripts(scripts):
                if not scripts or (not scripts.get('inline') and not scripts.get('external')):
                    self.main_window.status_info.setText("ℹ️ No scripts found on this page")
                    QTimer.singleShot(3000, lambda: self.main_window.status_info.setText(""))
                    return
                
                # Create and show the script scanner dialog
                self.show_script_scanner_dialog(scripts, current_url)
            
            # Execute JavaScript to get all scripts
            page.runJavaScript(js_code, process_scripts)
            
        except Exception as e:
            self.main_window.status_info.setText(f"❌ Script scan error: {str(e)}")
            QTimer.singleShot(3000, lambda: self.main_window.status_info.setText(""))
    
    def show_script_scanner_dialog(self, scripts, base_url):
        """Show dialog with script scanner results"""
        from PyQt5.QtWidgets import (QDialog, QVBoxLayout, QHBoxLayout, QLabel, 
                                   QTextEdit, QPushButton, QTabWidget, QWidget,
                                   QSplitter, QTreeWidget, QTreeWidgetItem, 
                                   QHeaderView, QFileDialog)
        from PyQt5.QtCore import Qt
        from datetime import datetime
        import urllib.parse
        
        inline_scripts = scripts.get('inline', [])
        external_scripts = scripts.get('external', [])
        
        # Create dialog
        dialog = QDialog(self.main_window)
        dialog.setWindowTitle(f"📜 Script Scanner - {len(inline_scripts)} inline, {len(external_scripts)} external")
        dialog.setMinimumSize(900, 700)
        dialog.resize(1200, 800)
        
        layout = QVBoxLayout(dialog)
        
        # Header
        header_label = QLabel(f"Scripts found on: {base_url}")
        header_label.setStyleSheet("font-weight: bold; padding: 10px; background-color: #f0f0f0; border-radius: 5px;")
        layout.addWidget(header_label)
        
        # Summary
        summary_label = QLabel(f"📊 Summary: {len(inline_scripts)} inline scripts, {len(external_scripts)} external scripts")
        summary_label.setStyleSheet("padding: 5px; background-color: #e8f4fd; border-radius: 3px;")
        layout.addWidget(summary_label)
        
        # Tab widget for different views
        tab_widget = QTabWidget()
        layout.addWidget(tab_widget)
        
        # External Scripts Tab
        external_widget = QWidget()
        external_layout = QVBoxLayout(external_widget)
        
        external_label = QLabel(f"🌐 External Scripts ({len(external_scripts)})")
        external_label.setStyleSheet("font-weight: bold; color: #0066cc;")
        external_layout.addWidget(external_label)
        
        # Tree widget for external scripts
        external_tree = QTreeWidget()
        external_tree.setHeaderLabels(['Source URL', 'Type', 'Attributes', 'Security', 'Actions'])
        external_tree.header().setSectionResizeMode(0, QHeaderView.Stretch)
        external_tree.header().setSectionResizeMode(1, QHeaderView.ResizeToContents)
        external_tree.header().setSectionResizeMode(2, QHeaderView.ResizeToContents)
        external_tree.header().setSectionResizeMode(3, QHeaderView.ResizeToContents)
        external_tree.header().setSectionResizeMode(4, QHeaderView.ResizeToContents)
        
        for script in external_scripts:
            item = QTreeWidgetItem()
            
            # Source URL
            src = script.get('src', '')
            if not src.startswith(('http://', 'https://')):
                src = urllib.parse.urljoin(base_url, src)
            item.setText(0, src)
            
            # Type
            item.setText(1, script.get('type', 'text/javascript'))
            
            # Attributes
            attrs = []
            if script.get('async'):
                attrs.append('async')
            if script.get('defer'):
                attrs.append('defer')
            if script.get('crossorigin'):
                attrs.append(f"crossorigin={script['crossorigin']}")
            if script.get('id'):
                attrs.append(f"id={script['id']}")
            if script.get('className'):
                attrs.append(f"class={script['className']}")
            item.setText(2, ', '.join(attrs) if attrs else 'none')
            
            # Security analysis
            security_issues = []
            if src.startswith('http://'):
                security_issues.append('HTTP (insecure)')
            if not script.get('integrity'):
                security_issues.append('No integrity check')
            if not script.get('crossorigin') and src and not src.startswith('/'.join(base_url.split('/')[0:3])):
                security_issues.append('No CORS policy')
            
            if security_issues:
                item.setText(3, '⚠️ ' + ', '.join(security_issues))
                item.setBackground(3, Qt.yellow)
            else:
                item.setText(3, '✅ Looks secure')
                item.setBackground(3, Qt.green)
            
            # Actions - View button
            item.setText(4, '👁️ View Source')
            
            # Store script data for later use
            item.setData(0, Qt.UserRole, script)
            item.setData(0, Qt.UserRole + 1, src)  # Store full URL
            
            external_tree.addTopLevelItem(item)
        
        external_layout.addWidget(external_tree)
        
        # Add double-click handler for external scripts
        def on_external_item_double_clicked(item, column):
            if column == 4 or column == 0:  # Actions column or URL column
                script_data = item.data(0, Qt.UserRole)
                full_url = item.data(0, Qt.UserRole + 1)
                self.show_external_script_viewer(full_url, script_data, dialog)
        
        external_tree.itemDoubleClicked.connect(on_external_item_double_clicked)
        
        tab_widget.addTab(external_widget, f"🌐 External ({len(external_scripts)})")
        
        # Inline Scripts Tab
        inline_widget = QWidget()
        inline_layout = QVBoxLayout(inline_widget)
        
        inline_label = QLabel(f"📝 Inline Scripts ({len(inline_scripts)})")
        inline_label.setStyleSheet("font-weight: bold; color: #cc6600;")
        inline_layout.addWidget(inline_label)
        
        # Tree widget for inline scripts
        inline_tree = QTreeWidget()
        inline_tree.setHeaderLabels(['Preview', 'Type', 'Size', 'ID/Class', 'Security', 'Actions'])
        inline_tree.header().setSectionResizeMode(0, QHeaderView.Stretch)
        inline_tree.header().setSectionResizeMode(1, QHeaderView.ResizeToContents)
        inline_tree.header().setSectionResizeMode(2, QHeaderView.ResizeToContents)
        inline_tree.header().setSectionResizeMode(3, QHeaderView.ResizeToContents)
        inline_tree.header().setSectionResizeMode(4, QHeaderView.ResizeToContents)
        inline_tree.header().setSectionResizeMode(5, QHeaderView.ResizeToContents)
        
        for i, script in enumerate(inline_scripts):
            item = QTreeWidgetItem()
            
            # Preview
            preview = script.get('preview', '')[:80] + ('...' if len(script.get('preview', '')) > 80 else '')
            item.setText(0, preview)
            
            # Type
            item.setText(1, script.get('type', 'text/javascript'))
            
            # Size
            size = script.get('length', 0)
            if size > 1024:
                size_str = f"{size // 1024}KB"
            else:
                size_str = f"{size}B"
            item.setText(2, size_str)
            
            # ID/Class
            id_class = []
            if script.get('id'):
                id_class.append(f"#{script['id']}")
            if script.get('className'):
                id_class.append(f".{script['className']}")
            item.setText(3, ' '.join(id_class) if id_class else 'none')
            
            # Security analysis for inline scripts
            content = script.get('content', '').lower()
            security_issues = []
            
            # Check for potentially dangerous patterns
            dangerous_patterns = [
                ('eval(', 'Uses eval()'),
                ('document.write(', 'Uses document.write()'),
                ('innerhtml', 'Modifies innerHTML'),
                ('outerhtml', 'Modifies outerHTML'),
                ('javascript:', 'JavaScript protocol'),
                ('data:', 'Data protocol'),
                ('vbscript:', 'VBScript protocol')
            ]
            
            for pattern, issue in dangerous_patterns:
                if pattern in content:
                    security_issues.append(issue)
            
            if security_issues:
                item.setText(4, '⚠️ ' + ', '.join(security_issues[:2]))  # Show first 2 issues
                item.setBackground(4, Qt.yellow)
            else:
                item.setText(4, '✅ No obvious issues')
                item.setBackground(4, Qt.green)
            
            # Actions - View button
            item.setText(5, '👁️ View Full Script')
            
            # Store script data for later use
            item.setData(0, Qt.UserRole, script)
            
            inline_tree.addTopLevelItem(item)
        
        inline_layout.addWidget(inline_tree)
        
        # Add double-click handler for inline scripts
        def on_inline_item_double_clicked(item, column):
            if column == 5 or column == 0:  # Actions column or Preview column
                script_data = item.data(0, Qt.UserRole)
                self.show_inline_script_viewer(script_data, dialog)
        
        inline_tree.itemDoubleClicked.connect(on_inline_item_double_clicked)
        
        tab_widget.addTab(inline_widget, f"📝 Inline ({len(inline_scripts)})")
        
        # Detailed view tab
        detail_widget = QWidget()
        detail_layout = QVBoxLayout(detail_widget)
        
        detail_text = QTextEdit()
        detail_text.setReadOnly(True)
        detail_text.setStyleSheet("font-family: monospace; background-color: #f8f8f8;")
        
        # Generate detailed report
        report = []
        report.append("SCRIPT ANALYSIS REPORT")
        report.append("=" * 50)
        report.append(f"URL: {base_url}")
        report.append(f"Scan Time: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        report.append(f"Total Scripts: {len(inline_scripts) + len(external_scripts)}")
        report.append("")
        
        if external_scripts:
            report.append("EXTERNAL SCRIPTS:")
            report.append("-" * 30)
            for i, script in enumerate(external_scripts, 1):
                report.append(f"{i}. {script.get('src', 'Unknown')}")
                report.append(f"   Type: {script.get('type', 'text/javascript')}")
                if script.get('async'):
                    report.append("   Loading: Async")
                elif script.get('defer'):
                    report.append("   Loading: Deferred")
                else:
                    report.append("   Loading: Blocking")
                
                if script.get('integrity'):
                    report.append(f"   Integrity: {script['integrity']}")
                else:
                    report.append("   Integrity: None (⚠️ Security risk)")
                
                if script.get('crossorigin'):
                    report.append(f"   CORS: {script['crossorigin']}")
                report.append("")
        
        if inline_scripts:
            report.append("INLINE SCRIPTS:")
            report.append("-" * 30)
            for i, script in enumerate(inline_scripts, 1):
                report.append(f"{i}. Inline Script ({script.get('length', 0)} characters)")
                report.append(f"   Type: {script.get('type', 'text/javascript')}")
                if script.get('id'):
                    report.append(f"   ID: {script['id']}")
                if script.get('className'):
                    report.append(f"   Class: {script['className']}")
                
                # Show first few lines of content
                content_lines = script.get('content', '').split('\n')[:3]
                report.append("   Content preview:")
                for line in content_lines:
                    if line.strip():
                        report.append(f"     {line.strip()[:60]}...")
                report.append("")
        
        detail_text.setPlainText('\n'.join(report))
        detail_layout.addWidget(detail_text)
        tab_widget.addTab(detail_widget, "📋 Detailed Report")
        
        # Buttons
        button_layout = QHBoxLayout()
        
        export_button = QPushButton("💾 Export Report")
        close_button = QPushButton("❌ Close")
        
        button_layout.addStretch()
        button_layout.addWidget(export_button)
        button_layout.addWidget(close_button)
        layout.addLayout(button_layout)
        
        def export_report():
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            filename = f"script_analysis_{timestamp}.txt"
            
            file_path, _ = QFileDialog.getSaveFileName(
                dialog,
                "Export Script Analysis Report",
                filename,
                "Text Files (*.txt);;All Files (*.*)"
            )
            
            if file_path:
                try:
                    with open(file_path, 'w', encoding='utf-8') as f:
                        f.write(detail_text.toPlainText())
                    
                    self.main_window.status_info.setText(f"✅ Report exported to: {file_path}")
                    QTimer.singleShot(3000, lambda: self.main_window.status_info.setText(""))
                except Exception as e:
                    self.main_window.status_info.setText(f"❌ Export failed: {str(e)}")
                    QTimer.singleShot(3000, lambda: self.main_window.status_info.setText(""))
        
        # Connect buttons
        export_button.clicked.connect(export_report)
        close_button.clicked.connect(dialog.accept)
        
        # Show dialog
        dialog.exec_()
        
        # Update main window status
        total_scripts = len(inline_scripts) + len(external_scripts)
        self.main_window.status_info.setText(f"📜 Script scan complete: {total_scripts} scripts found")
        QTimer.singleShot(5000, lambda: self.main_window.status_info.setText(""))
    
    def show_external_script_viewer(self, script_url, script_data, parent_dialog):
        """Show dialog to view external script content"""
        from PyQt5.QtWidgets import (QDialog, QVBoxLayout, QHBoxLayout, QLabel, 
                                   QTextEdit, QPushButton, QProgressBar, QSplitter)
        from PyQt5.QtCore import QThread, pyqtSignal
        import urllib.request
        import ssl
        
        class ScriptFetcherThread(QThread):
            """Thread to fetch script content without blocking UI"""
            content_fetched = pyqtSignal(str, str)  # content, error_message
            progress_updated = pyqtSignal(str)  # status message
            
            def __init__(self, url):
                super().__init__()
                self.url = url
                self.should_stop = False
            
            def stop(self):
                self.should_stop = True
            
            def run(self):
                try:
                    self.progress_updated.emit(f"Fetching script from: {self.url}")
                    
                    # Create SSL context that doesn't verify certificates (for testing)
                    ssl_context = ssl.create_default_context()
                    ssl_context.check_hostname = False
                    ssl_context.verify_mode = ssl.CERT_NONE
                    
                    # Create request with headers
                    req = urllib.request.Request(self.url)
                    req.add_header('User-Agent', 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36')
                    req.add_header('Accept', 'application/javascript, text/javascript, */*')
                    
                    # Fetch the script
                    with urllib.request.urlopen(req, timeout=15, context=ssl_context) as response:
                        content = response.read().decode('utf-8', errors='replace')
                        self.content_fetched.emit(content, "")
                        
                except Exception as e:
                    error_msg = f"Failed to fetch script: {str(e)}"
                    self.content_fetched.emit("", error_msg)
        
        # Create dialog
        dialog = QDialog(parent_dialog)
        dialog.setWindowTitle(f"📜 External Script Viewer")
        dialog.setMinimumSize(800, 600)
        dialog.resize(1000, 700)
        
        layout = QVBoxLayout(dialog)
        
        # Header with script info
        header_label = QLabel(f"External Script: {script_url}")
        header_label.setStyleSheet("font-weight: bold; padding: 10px; background-color: #e8f4fd; border-radius: 5px;")
        header_label.setWordWrap(True)
        layout.addWidget(header_label)
        
        # Script metadata
        metadata_text = []
        metadata_text.append(f"URL: {script_url}")
        metadata_text.append(f"Type: {script_data.get('type', 'text/javascript')}")
        if script_data.get('async'):
            metadata_text.append("Loading: Async")
        elif script_data.get('defer'):
            metadata_text.append("Loading: Deferred")
        else:
            metadata_text.append("Loading: Blocking")
        
        if script_data.get('integrity'):
            metadata_text.append(f"Integrity: {script_data['integrity']}")
        if script_data.get('crossorigin'):
            metadata_text.append(f"CORS: {script_data['crossorigin']}")
        
        metadata_label = QLabel(" | ".join(metadata_text))
        metadata_label.setStyleSheet("padding: 5px; background-color: #f0f0f0; border-radius: 3px; font-family: monospace;")
        metadata_label.setWordWrap(True)
        layout.addWidget(metadata_label)
        
        # Progress bar
        progress_bar = QProgressBar()
        progress_bar.setRange(0, 0)  # Indeterminate progress
        layout.addWidget(progress_bar)
        
        # Status label
        status_label = QLabel("Fetching script content...")
        layout.addWidget(status_label)
        
        # Content area
        content_text = QTextEdit()
        content_text.setReadOnly(True)
        content_text.setStyleSheet("font-family: 'Consolas', 'Monaco', 'Courier New', monospace; font-size: 12px;")
        content_text.setPlainText("Loading script content...")
        layout.addWidget(content_text)
        
        # Buttons
        button_layout = QHBoxLayout()
        
        stop_button = QPushButton("⏹️ Stop Loading")
        stop_button.setEnabled(True)
        
        save_button = QPushButton("💾 Save Script")
        save_button.setEnabled(False)
        
        close_button = QPushButton("❌ Close")
        
        button_layout.addStretch()
        button_layout.addWidget(stop_button)
        button_layout.addWidget(save_button)
        button_layout.addWidget(close_button)
        layout.addLayout(button_layout)
        
        # Create and start fetcher thread
        fetcher_thread = ScriptFetcherThread(script_url)
        
        def on_content_fetched(content, error_message):
            progress_bar.setVisible(False)
            stop_button.setEnabled(False)
            save_button.setEnabled(True)
            
            if error_message:
                status_label.setText(f"❌ {error_message}")
                content_text.setPlainText(f"Error loading script:\n{error_message}")
                content_text.setStyleSheet("font-family: monospace; color: red;")
            else:
                status_label.setText(f"✅ Script loaded successfully ({len(content)} characters)")
                content_text.setPlainText(content)
                content_text.setStyleSheet("font-family: 'Consolas', 'Monaco', 'Courier New', monospace; font-size: 12px;")
        
        def on_progress_updated(status):
            status_label.setText(status)
        
        def stop_loading():
            fetcher_thread.stop()
            progress_bar.setVisible(False)
            status_label.setText("⏹️ Loading stopped by user")
            stop_button.setEnabled(False)
        
        def save_script():
            from PyQt5.QtWidgets import QFileDialog
            from datetime import datetime
            import os
            
            # Generate filename from URL
            filename = os.path.basename(script_url.split('?')[0]) or "external_script.js"
            if not filename.endswith('.js'):
                filename += '.js'
            
            file_path, _ = QFileDialog.getSaveFileName(
                dialog,
                "Save External Script",
                filename,
                "JavaScript Files (*.js);;Text Files (*.txt);;All Files (*.*)"
            )
            
            if file_path:
                try:
                    with open(file_path, 'w', encoding='utf-8') as f:
                        f.write(f"// External Script from: {script_url}\n")
                        f.write(f"// Downloaded on: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n\n")
                        f.write(content_text.toPlainText())
                    
                    status_label.setText(f"✅ Script saved to: {file_path}")
                except Exception as e:
                    status_label.setText(f"❌ Save failed: {str(e)}")
        
        # Connect signals
        fetcher_thread.content_fetched.connect(on_content_fetched)
        fetcher_thread.progress_updated.connect(on_progress_updated)
        
        stop_button.clicked.connect(stop_loading)
        save_button.clicked.connect(save_script)
        close_button.clicked.connect(dialog.accept)
        
        # Start fetching
        fetcher_thread.start()
        
        # Show dialog
        dialog.exec_()
        
        # Clean up
        if fetcher_thread.isRunning():
            fetcher_thread.stop()
            fetcher_thread.wait()
    
    def show_inline_script_viewer(self, script_data, parent_dialog):
        """Show dialog to view inline script content"""
        from PyQt5.QtWidgets import (QDialog, QVBoxLayout, QHBoxLayout, QLabel, 
                                   QTextEdit, QPushButton, QCheckBox)
        from datetime import datetime
        
        # Create dialog
        dialog = QDialog(parent_dialog)
        dialog.setWindowTitle(f"📝 Inline Script Viewer")
        dialog.setMinimumSize(800, 600)
        dialog.resize(1000, 700)
        
        layout = QVBoxLayout(dialog)
        
        # Header with script info
        script_info = []
        if script_data.get('id'):
            script_info.append(f"ID: {script_data['id']}")
        if script_data.get('className'):
            script_info.append(f"Class: {script_data['className']}")
        script_info.append(f"Type: {script_data.get('type', 'text/javascript')}")
        script_info.append(f"Size: {script_data.get('length', 0)} characters")
        
        header_label = QLabel(f"Inline Script - {' | '.join(script_info)}")
        header_label.setStyleSheet("font-weight: bold; padding: 10px; background-color: #fff3cd; border-radius: 5px;")
        header_label.setWordWrap(True)
        layout.addWidget(header_label)
        
        # Security analysis display
        content = script_data.get('content', '').lower()
        security_issues = []
        
        dangerous_patterns = [
            ('eval(', 'Uses eval() - potential security risk'),
            ('document.write(', 'Uses document.write() - can cause XSS'),
            ('innerhtml', 'Modifies innerHTML - potential XSS risk'),
            ('outerhtml', 'Modifies outerHTML - potential XSS risk'),
            ('javascript:', 'Uses JavaScript protocol'),
            ('data:', 'Uses data protocol'),
            ('vbscript:', 'Uses VBScript protocol')
        ]
        
        for pattern, issue in dangerous_patterns:
            if pattern in content:
                security_issues.append(issue)
        
        if security_issues:
            security_label = QLabel(f"⚠️ Security Issues Found: {', '.join(security_issues[:3])}")
            security_label.setStyleSheet("padding: 8px; background-color: #f8d7da; color: #721c24; border-radius: 3px; font-weight: bold;")
        else:
            security_label = QLabel("✅ No obvious security issues detected")
            security_label.setStyleSheet("padding: 8px; background-color: #d4edda; color: #155724; border-radius: 3px; font-weight: bold;")
        
        security_label.setWordWrap(True)
        layout.addWidget(security_label)
        
        # Options
        options_layout = QHBoxLayout()
        
        line_numbers_cb = QCheckBox("Show line numbers")
        line_numbers_cb.setChecked(True)
        
        word_wrap_cb = QCheckBox("Word wrap")
        word_wrap_cb.setChecked(False)
        
        options_layout.addWidget(line_numbers_cb)
        options_layout.addWidget(word_wrap_cb)
        options_layout.addStretch()
        
        layout.addLayout(options_layout)
        
        # Content area
        content_text = QTextEdit()
        content_text.setReadOnly(True)
        content_text.setStyleSheet("font-family: 'Consolas', 'Monaco', 'Courier New', monospace; font-size: 12px;")
        
        def update_content_display():
            script_content = script_data.get('content', '')
            
            if line_numbers_cb.isChecked():
                lines = script_content.split('\n')
                numbered_lines = []
                for i, line in enumerate(lines, 1):
                    numbered_lines.append(f"{i:4d} | {line}")
                display_content = '\n'.join(numbered_lines)
            else:
                display_content = script_content
            
            content_text.setPlainText(display_content)
            content_text.setLineWrapMode(QTextEdit.WidgetWidth if word_wrap_cb.isChecked() else QTextEdit.NoWrap)
        
        # Initial content display
        update_content_display()
        
        # Connect option changes
        line_numbers_cb.toggled.connect(update_content_display)
        word_wrap_cb.toggled.connect(update_content_display)
        
        layout.addWidget(content_text)
        
        # Stats
        stats_text = f"Lines: {len(script_data.get('content', '').split())}, " \
                    f"Characters: {script_data.get('length', 0)}, " \
                    f"Words: {len(script_data.get('content', '').split())}"
        
        stats_label = QLabel(stats_text)
        stats_label.setStyleSheet("padding: 5px; background-color: #f8f9fa; border-radius: 3px; font-family: monospace;")
        layout.addWidget(stats_label)
        
        # Buttons
        button_layout = QHBoxLayout()
        
        save_button = QPushButton("💾 Save Script")
        copy_button = QPushButton("📋 Copy to Clipboard")
        close_button = QPushButton("❌ Close")
        
        button_layout.addStretch()
        button_layout.addWidget(copy_button)
        button_layout.addWidget(save_button)
        button_layout.addWidget(close_button)
        layout.addLayout(button_layout)
        
        def save_script():
            from PyQt5.QtWidgets import QFileDialog
            
            # Generate filename
            script_id = script_data.get('id', 'inline_script')
            filename = f"{script_id}.js" if script_id != 'inline_script' else "inline_script.js"
            
            file_path, _ = QFileDialog.getSaveFileName(
                dialog,
                "Save Inline Script",
                filename,
                "JavaScript Files (*.js);;Text Files (*.txt);;All Files (*.*)"
            )
            
            if file_path:
                try:
                    with open(file_path, 'w', encoding='utf-8') as f:
                        f.write(f"// Inline Script extracted on: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
                        if script_data.get('id'):
                            f.write(f"// Script ID: {script_data['id']}\n")
                        if script_data.get('className'):
                            f.write(f"// Script Class: {script_data['className']}\n")
                        f.write(f"// Script Type: {script_data.get('type', 'text/javascript')}\n")
                        f.write(f"// Script Size: {script_data.get('length', 0)} characters\n\n")
                        f.write(script_data.get('content', ''))
                    
                    self.main_window.status_info.setText(f"✅ Inline script saved to: {file_path}")
                    QTimer.singleShot(3000, lambda: self.main_window.status_info.setText(""))
                except Exception as e:
                    self.main_window.status_info.setText(f"❌ Save failed: {str(e)}")
                    QTimer.singleShot(3000, lambda: self.main_window.status_info.setText(""))
        
        def copy_to_clipboard():
            from PyQt5.QtWidgets import QApplication
            clipboard = QApplication.clipboard()
            clipboard.setText(script_data.get('content', ''))
            self.main_window.status_info.setText("📋 Script copied to clipboard")
            QTimer.singleShot(2000, lambda: self.main_window.status_info.setText(""))
        
        # Connect buttons
        save_button.clicked.connect(save_script)
        copy_button.clicked.connect(copy_to_clipboard)
        close_button.clicked.connect(dialog.accept)
        
        # Show dialog
        dialog.exec_()

    def analyze_page_speed(self, browser):
        """Analyze page speed and performance metrics"""
        try:
            page = browser.page()
            current_url = browser.url().toString()
            
            # Show initial status
            self.main_window.status_info.setText("⚡ Analyzing page speed...")
            
            # JavaScript to collect performance metrics and page analysis
            js_code = """
            (function() {
                var metrics = {
                    timing: {},
                    resources: [],
                    pageInfo: {},
                    performance: {}
                };
                
                // Navigation Timing API
                if (window.performance && window.performance.timing) {
                    var timing = window.performance.timing;
                    var navigationStart = timing.navigationStart;
                    
                    metrics.timing = {
                        domainLookup: timing.domainLookupEnd - timing.domainLookupStart,
                        tcpConnect: timing.connectEnd - timing.connectStart,
                        request: timing.responseStart - timing.requestStart,
                        response: timing.responseEnd - timing.responseStart,
                        domProcessing: timing.domComplete - timing.domLoading,
                        domContentLoaded: timing.domContentLoadedEventEnd - navigationStart,
                        loadComplete: timing.loadEventEnd - navigationStart,
                        totalTime: timing.loadEventEnd - navigationStart
                    };
                }
                
                // Resource Timing API
                if (window.performance && window.performance.getEntriesByType) {
                    var resources = window.performance.getEntriesByType('resource');
                    metrics.resources = resources.map(function(resource) {
                        return {
                            name: resource.name,
                            type: resource.initiatorType || 'other',
                            size: resource.transferSize || 0,
                            duration: Math.round(resource.duration),
                            startTime: Math.round(resource.startTime),
                            blocked: Math.round(resource.domainLookupStart - resource.fetchStart),
                            dns: Math.round(resource.domainLookupEnd - resource.domainLookupStart),
                            connect: Math.round(resource.connectEnd - resource.connectStart),
                            send: Math.round(resource.responseStart - resource.requestStart),
                            wait: Math.round(resource.responseStart - resource.requestStart),
                            receive: Math.round(resource.responseEnd - resource.responseStart)
                        };
                    });
                }
                
                // Page Information
                metrics.pageInfo = {
                    title: document.title,
                    url: window.location.href,
                    doctype: document.doctype ? document.doctype.name : 'unknown',
                    charset: document.characterSet || document.charset,
                    referrer: document.referrer,
                    images: document.images.length,
                    links: document.links.length,
                    scripts: document.scripts.length,
                    stylesheets: document.styleSheets.length,
                    forms: document.forms.length
                };
                
                // DOM Analysis
                var allElements = document.getElementsByTagName('*');
                var elementCounts = {};
                for (var i = 0; i < allElements.length; i++) {
                    var tagName = allElements[i].tagName.toLowerCase();
                    elementCounts[tagName] = (elementCounts[tagName] || 0) + 1;
                }
                metrics.pageInfo.totalElements = allElements.length;
                metrics.pageInfo.elementCounts = elementCounts;
                
                // Performance Metrics
                if (window.performance) {
                    metrics.performance = {
                        memory: window.performance.memory ? {
                            used: window.performance.memory.usedJSHeapSize,
                            total: window.performance.memory.totalJSHeapSize,
                            limit: window.performance.memory.jsHeapSizeLimit
                        } : null,
                        navigation: window.performance.navigation ? {
                            type: window.performance.navigation.type,
                            redirectCount: window.performance.navigation.redirectCount
                        } : null
                    };
                }
                
                // Additional metrics
                metrics.pageInfo.bodySize = document.body ? document.body.innerHTML.length : 0;
                metrics.pageInfo.headSize = document.head ? document.head.innerHTML.length : 0;
                
                return metrics;
            })();
            """
            
            def process_metrics(metrics):
                if not metrics:
                    self.main_window.status_info.setText("❌ Could not collect performance metrics")
                    QTimer.singleShot(3000, lambda: self.main_window.status_info.setText(""))
                    return
                
                # Create and show the page speed analyzer dialog
                self.show_page_speed_dialog(metrics, current_url)
            
            # Execute JavaScript to get performance metrics
            page.runJavaScript(js_code, process_metrics)
            
        except Exception as e:
            self.main_window.status_info.setText(f"❌ Page speed analysis error: {str(e)}")
            QTimer.singleShot(3000, lambda: self.main_window.status_info.setText(""))
    
    def show_page_speed_dialog(self, metrics, page_url):
        """Show dialog with page speed analysis results"""
        from PyQt5.QtWidgets import (QDialog, QVBoxLayout, QHBoxLayout, QLabel, 
                                   QTextEdit, QPushButton, QTabWidget, QWidget,
                                   QTreeWidget, QTreeWidgetItem, QHeaderView, 
                                   QProgressBar, QFileDialog, QSplitter)
        from PyQt5.QtCore import Qt
        from PyQt5.QtGui import QFont
        from datetime import datetime
        import json
        
        timing = metrics.get('timing', {})
        resources = metrics.get('resources', [])
        page_info = metrics.get('pageInfo', {})
        performance = metrics.get('performance', {})
        
        # Create dialog
        dialog = QDialog(self.main_window)
        dialog.setWindowTitle(f"⚡ Page Speed Analysis")
        dialog.setMinimumSize(1000, 800)
        dialog.resize(1200, 900)
        
        layout = QVBoxLayout(dialog)
        
        # Header
        header_label = QLabel(f"Page Speed Analysis: {page_info.get('title', 'Unknown Page')}")
        header_label.setStyleSheet("font-weight: bold; padding: 10px; background-color: #e8f5e8; border-radius: 5px;")
        header_label.setWordWrap(True)
        layout.addWidget(header_label)
        
        # URL and basic info
        url_label = QLabel(f"URL: {page_url}")
        url_label.setStyleSheet("padding: 5px; background-color: #f0f0f0; border-radius: 3px; font-family: monospace;")
        url_label.setWordWrap(True)
        layout.addWidget(url_label)
        
        # Tab widget for different analysis views
        tab_widget = QTabWidget()
        layout.addWidget(tab_widget)
        
        # Performance Overview Tab
        overview_widget = QWidget()
        overview_layout = QVBoxLayout(overview_widget)
        
        # Performance Score Calculation
        def calculate_performance_score():
            score = 100
            total_time = timing.get('totalTime', 0)
            
            # Deduct points based on load time
            if total_time > 5000:  # > 5 seconds
                score -= 40
            elif total_time > 3000:  # > 3 seconds
                score -= 25
            elif total_time > 1000:  # > 1 second
                score -= 10
            
            # Deduct points for large number of resources
            if len(resources) > 100:
                score -= 15
            elif len(resources) > 50:
                score -= 10
            
            # Deduct points for large resources
            large_resources = [r for r in resources if r.get('size', 0) > 1024 * 1024]  # > 1MB
            score -= len(large_resources) * 5
            
            return max(0, min(100, score))
        
        perf_score = calculate_performance_score()
        
        # Score display
        score_label = QLabel(f"Performance Score: {perf_score}/100")
        if perf_score >= 90:
            score_color = "#28a745"  # Green
            score_text = "Excellent"
        elif perf_score >= 70:
            score_color = "#ffc107"  # Yellow
            score_text = "Good"
        elif perf_score >= 50:
            score_color = "#fd7e14"  # Orange
            score_text = "Needs Improvement"
        else:
            score_color = "#dc3545"  # Red
            score_text = "Poor"
        
        score_label.setStyleSheet(f"font-size: 18px; font-weight: bold; color: {score_color}; padding: 10px; background-color: #f8f9fa; border-radius: 5px;")
        overview_layout.addWidget(score_label)
        
        grade_label = QLabel(f"Grade: {score_text}")
        grade_label.setStyleSheet(f"font-size: 14px; color: {score_color}; padding: 5px;")
        overview_layout.addWidget(grade_label)
        
        # Key Metrics
        metrics_text = QTextEdit()
        metrics_text.setReadOnly(True)
        metrics_text.setMaximumHeight(300)
        metrics_text.setStyleSheet("font-family: monospace; background-color: #f8f9fa;")
        
        metrics_content = []
        metrics_content.append("⏱️  TIMING METRICS")
        metrics_content.append("=" * 50)
        
        if timing:
            metrics_content.append(f"Total Load Time:        {timing.get('totalTime', 0):,} ms")
            metrics_content.append(f"DOM Content Loaded:     {timing.get('domContentLoaded', 0):,} ms")
            metrics_content.append(f"DOM Processing:         {timing.get('domProcessing', 0):,} ms")
            metrics_content.append(f"DNS Lookup:             {timing.get('domainLookup', 0):,} ms")
            metrics_content.append(f"TCP Connection:         {timing.get('tcpConnect', 0):,} ms")
            metrics_content.append(f"Request Time:           {timing.get('request', 0):,} ms")
            metrics_content.append(f"Response Time:          {timing.get('response', 0):,} ms")
        else:
            metrics_content.append("❌ Timing data not available")
        
        metrics_content.append("")
        metrics_content.append("📊  PAGE STATISTICS")
        metrics_content.append("=" * 50)
        metrics_content.append(f"Total Elements:         {page_info.get('totalElements', 0):,}")
        metrics_content.append(f"Images:                 {page_info.get('images', 0):,}")
        metrics_content.append(f"Scripts:                {page_info.get('scripts', 0):,}")
        metrics_content.append(f"Stylesheets:            {page_info.get('stylesheets', 0):,}")
        metrics_content.append(f"Links:                  {page_info.get('links', 0):,}")
        metrics_content.append(f"Forms:                  {page_info.get('forms', 0):,}")
        metrics_content.append(f"Body Size:              {page_info.get('bodySize', 0):,} characters")
        metrics_content.append(f"Head Size:              {page_info.get('headSize', 0):,} characters")
        
        if performance.get('memory'):
            memory = performance['memory']
            metrics_content.append("")
            metrics_content.append("🧠  MEMORY USAGE")
            metrics_content.append("=" * 50)
            metrics_content.append(f"Used JS Heap:           {memory.get('used', 0) / 1024 / 1024:.2f} MB")
            metrics_content.append(f"Total JS Heap:          {memory.get('total', 0) / 1024 / 1024:.2f} MB")
            metrics_content.append(f"JS Heap Limit:          {memory.get('limit', 0) / 1024 / 1024:.2f} MB")
        
        metrics_text.setPlainText('\n'.join(metrics_content))
        overview_layout.addWidget(metrics_text)
        
        tab_widget.addTab(overview_widget, "📊 Overview")
        
        # Resources Tab
        resources_widget = QWidget()
        resources_layout = QVBoxLayout(resources_widget)
        
        resources_label = QLabel(f"🔗 Resources Analysis ({len(resources)} resources)")
        resources_label.setStyleSheet("font-weight: bold; color: #0066cc;")
        resources_layout.addWidget(resources_label)
        
        # Resources tree
        resources_tree = QTreeWidget()
        resources_tree.setHeaderLabels(['Resource', 'Type', 'Size', 'Duration', 'Timeline'])
        resources_tree.header().setSectionResizeMode(0, QHeaderView.Stretch)
        resources_tree.header().setSectionResizeMode(1, QHeaderView.ResizeToContents)
        resources_tree.header().setSectionResizeMode(2, QHeaderView.ResizeToContents)
        resources_tree.header().setSectionResizeMode(3, QHeaderView.ResizeToContents)
        resources_tree.header().setSectionResizeMode(4, QHeaderView.ResizeToContents)
        
        # Sort resources by size (largest first)
        sorted_resources = sorted(resources, key=lambda x: x.get('size', 0), reverse=True)
        
        for resource in sorted_resources:
            item = QTreeWidgetItem()
            
            # Resource name (shortened)
            name = resource.get('name', 'Unknown')
            if len(name) > 60:
                display_name = name[:57] + "..."
            else:
                display_name = name
            item.setText(0, display_name)
            item.setToolTip(0, name)  # Full name in tooltip
            
            # Type
            res_type = resource.get('type', 'other')
            item.setText(1, res_type)
            
            # Size
            size = resource.get('size', 0)
            if size > 1024 * 1024:  # MB
                size_str = f"{size / 1024 / 1024:.2f} MB"
                item.setBackground(2, Qt.red if size > 5 * 1024 * 1024 else Qt.yellow)
            elif size > 1024:  # KB
                size_str = f"{size / 1024:.1f} KB"
            else:
                size_str = f"{size} B"
            item.setText(2, size_str)
            
            # Duration
            duration = resource.get('duration', 0)
            item.setText(3, f"{duration} ms")
            if duration > 1000:
                item.setBackground(3, Qt.red)
            elif duration > 500:
                item.setBackground(3, Qt.yellow)
            
            # Timeline breakdown
            dns = resource.get('dns', 0)
            connect = resource.get('connect', 0)
            send = resource.get('send', 0)
            receive = resource.get('receive', 0)
            timeline = f"DNS:{dns}ms | Connect:{connect}ms | Send:{send}ms | Receive:{receive}ms"
            item.setText(4, timeline)
            
            resources_tree.addTopLevelItem(item)
        
        resources_layout.addWidget(resources_tree)
        
        # Resource summary
        total_size = sum(r.get('size', 0) for r in resources)
        avg_duration = sum(r.get('duration', 0) for r in resources) / len(resources) if resources else 0
        
        resource_summary = QLabel(f"Total Size: {total_size / 1024 / 1024:.2f} MB | "
                                f"Average Duration: {avg_duration:.1f} ms | "
                                f"Largest Resource: {max((r.get('size', 0) for r in resources), default=0) / 1024:.1f} KB")
        resource_summary.setStyleSheet("padding: 5px; background-color: #f0f0f0; border-radius: 3px; font-family: monospace;")
        resources_layout.addWidget(resource_summary)
        
        tab_widget.addTab(resources_widget, f"🔗 Resources ({len(resources)})")
        
        # Recommendations Tab
        recommendations_widget = QWidget()
        recommendations_layout = QVBoxLayout(recommendations_widget)
        
        recommendations_text = QTextEdit()
        recommendations_text.setReadOnly(True)
        recommendations_text.setStyleSheet("font-family: Arial; font-size: 12px;")
        
        # Generate recommendations
        recommendations = []
        recommendations.append("🚀 PERFORMANCE RECOMMENDATIONS")
        recommendations.append("=" * 60)
        recommendations.append("")
        
        # Timing-based recommendations
        total_time = timing.get('totalTime', 0)
        if total_time > 3000:
            recommendations.append("🔴 CRITICAL: Page load time is very slow (>3s)")
            recommendations.append("   • Optimize images and compress resources")
            recommendations.append("   • Enable browser caching")
            recommendations.append("   • Use a Content Delivery Network (CDN)")
            recommendations.append("   • Minimize HTTP requests")
            recommendations.append("")
        elif total_time > 1000:
            recommendations.append("🟡 WARNING: Page load time could be improved (>1s)")
            recommendations.append("   • Compress images and resources")
            recommendations.append("   • Enable gzip compression")
            recommendations.append("   • Optimize CSS and JavaScript")
            recommendations.append("")
        
        # Resource-based recommendations
        large_resources = [r for r in resources if r.get('size', 0) > 1024 * 1024]
        if large_resources:
            recommendations.append(f"🔴 CRITICAL: {len(large_resources)} large resources found (>1MB)")
            for res in large_resources[:3]:  # Show top 3
                recommendations.append(f"   • {res.get('name', 'Unknown')[:50]}... ({res.get('size', 0) / 1024 / 1024:.2f} MB)")
            recommendations.append("   • Compress these resources or load them asynchronously")
            recommendations.append("")
        
        # Too many resources
        if len(resources) > 100:
            recommendations.append(f"🟡 WARNING: Many resources loaded ({len(resources)})")
            recommendations.append("   • Combine CSS and JavaScript files")
            recommendations.append("   • Use image sprites for small images")
            recommendations.append("   • Implement lazy loading for images")
            recommendations.append("")
        
        # Script recommendations
        script_count = page_info.get('scripts', 0)
        if script_count > 20:
            recommendations.append(f"🟡 WARNING: Many script files ({script_count})")
            recommendations.append("   • Combine and minify JavaScript files")
            recommendations.append("   • Use async/defer attributes for non-critical scripts")
            recommendations.append("   • Consider removing unused scripts")
            recommendations.append("")
        
        # Memory recommendations
        if performance.get('memory'):
            memory = performance['memory']
            used_mb = memory.get('used', 0) / 1024 / 1024
            if used_mb > 50:
                recommendations.append(f"🟡 WARNING: High memory usage ({used_mb:.1f} MB)")
                recommendations.append("   • Check for memory leaks in JavaScript")
                recommendations.append("   • Optimize DOM manipulation")
                recommendations.append("   • Remove unused event listeners")
                recommendations.append("")
        
        # General recommendations
        recommendations.append("✅ GENERAL OPTIMIZATION TIPS")
        recommendations.append("-" * 40)
        recommendations.append("• Enable browser caching with proper cache headers")
        recommendations.append("• Use WebP format for images when possible")
        recommendations.append("• Minimize CSS and JavaScript files")
        recommendations.append("• Remove unused CSS and JavaScript code")
        recommendations.append("• Use a Content Delivery Network (CDN)")
        recommendations.append("• Enable gzip/brotli compression on server")
        recommendations.append("• Optimize database queries (if applicable)")
        recommendations.append("• Use lazy loading for images and content")
        recommendations.append("• Implement service workers for caching")
        recommendations.append("• Consider using HTTP/2 or HTTP/3")
        
        recommendations_text.setPlainText('\n'.join(recommendations))
        recommendations_layout.addWidget(recommendations_text)
        
        tab_widget.addTab(recommendations_widget, "💡 Recommendations")
        
        # Detailed Report Tab
        report_widget = QWidget()
        report_layout = QVBoxLayout(report_widget)
        
        report_text = QTextEdit()
        report_text.setReadOnly(True)
        report_text.setStyleSheet("font-family: monospace; background-color: #f8f8f8;")
        
        # Generate detailed report
        report_content = []
        report_content.append("PAGE SPEED ANALYSIS REPORT")
        report_content.append("=" * 80)
        report_content.append(f"URL: {page_url}")
        report_content.append(f"Analysis Time: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        report_content.append(f"Performance Score: {perf_score}/100 ({score_text})")
        report_content.append("")
        
        # Add all metrics in JSON format for detailed analysis
        report_content.append("DETAILED METRICS (JSON):")
        report_content.append("-" * 40)
        report_content.append(json.dumps(metrics, indent=2, default=str))
        
        report_text.setPlainText('\n'.join(report_content))
        report_layout.addWidget(report_text)
        
        tab_widget.addTab(report_widget, "📋 Detailed Report")
        
        # Buttons
        button_layout = QHBoxLayout()
        
        export_button = QPushButton("💾 Export Report")
        reanalyze_button = QPushButton("🔄 Re-analyze")
        close_button = QPushButton("❌ Close")
        
        button_layout.addStretch()
        button_layout.addWidget(reanalyze_button)
        button_layout.addWidget(export_button)
        button_layout.addWidget(close_button)
        layout.addLayout(button_layout)
        
        def export_report():
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            filename = f"page_speed_analysis_{timestamp}.txt"
            
            file_path, _ = QFileDialog.getSaveFileName(
                dialog,
                "Export Page Speed Analysis Report",
                filename,
                "Text Files (*.txt);;JSON Files (*.json);;All Files (*.*)"
            )
            
            if file_path:
                try:
                    if file_path.endswith('.json'):
                        # Export as JSON
                        export_data = {
                            'url': page_url,
                            'analysis_time': datetime.now().isoformat(),
                            'performance_score': perf_score,
                            'grade': score_text,
                            'metrics': metrics
                        }
                        with open(file_path, 'w', encoding='utf-8') as f:
                            json.dump(export_data, f, indent=2, default=str)
                    else:
                        # Export as text
                        with open(file_path, 'w', encoding='utf-8') as f:
                            f.write(report_text.toPlainText())
                    
                    self.main_window.status_info.setText(f"✅ Report exported to: {file_path}")
                    QTimer.singleShot(3000, lambda: self.main_window.status_info.setText(""))
                except Exception as e:
                    self.main_window.status_info.setText(f"❌ Export failed: {str(e)}")
                    QTimer.singleShot(3000, lambda: self.main_window.status_info.setText(""))
        
        # Connect buttons
        export_button.clicked.connect(export_report)
        close_button.clicked.connect(dialog.accept)
        
        # Show dialog
        dialog.exec_()
        
        # Update main window status
        self.main_window.status_info.setText(f"⚡ Page speed analysis complete - Score: {perf_score}/100")
        QTimer.singleShot(5000, lambda: self.main_window.status_info.setText(""))
    
    def advanced_script_analysis(self, browser):
        """Perform advanced analysis of all scripts on the page"""
        try:
            page = browser.page()
            current_url = browser.url().toString()
            
            # Show initial status
            self.main_window.status_info.setText("🔍 Performing advanced script analysis...")
            
            # Enhanced JavaScript to extract detailed script information
            js_code = """
            (function() {
                var analysis = {
                    scripts: {
                        inline: [],
                        external: []
                    },
                    security: {
                        csp: null,
                        nonce_usage: false,
                        sri_usage: 0,
                        total_external: 0
                    },
                    performance: {
                        blocking_scripts: 0,
                        async_scripts: 0,
                        defer_scripts: 0,
                        total_size_estimate: 0
                    },
                    dependencies: {
                        libraries: [],
                        frameworks: []
                    }
                };
                
                // Check for Content Security Policy
                var metaTags = document.getElementsByTagName('meta');
                for (var i = 0; i < metaTags.length; i++) {
                    if (metaTags[i].getAttribute('http-equiv') === 'Content-Security-Policy') {
                        analysis.security.csp = metaTags[i].getAttribute('content');
                        break;
                    }
                }
                
                var scriptTags = document.getElementsByTagName('script');
                
                // Common library patterns
                var libraryPatterns = [
                    { name: 'jQuery', patterns: ['jquery', 'jQuery', '$'] },
                    { name: 'React', patterns: ['react', 'React', 'ReactDOM'] },
                    { name: 'Vue.js', patterns: ['vue', 'Vue'] },
                    { name: 'Angular', patterns: ['angular', 'ng-'] },
                    { name: 'Bootstrap', patterns: ['bootstrap'] },
                    { name: 'Lodash', patterns: ['lodash', '_'] },
                    { name: 'D3.js', patterns: ['d3'] },
                    { name: 'Three.js', patterns: ['three', 'THREE'] },
                    { name: 'Moment.js', patterns: ['moment'] },
                    { name: 'Axios', patterns: ['axios'] },
                    { name: 'Chart.js', patterns: ['chart.js', 'Chart'] },
                    { name: 'Google Analytics', patterns: ['gtag', 'ga(', 'google-analytics'] },
                    { name: 'Google Tag Manager', patterns: ['gtm', 'googletagmanager'] }
                ];
                
                for (var i = 0; i < scriptTags.length; i++) {
                    var script = scriptTags[i];
                    
                    // Check for nonce usage
                    if (script.nonce) {
                        analysis.security.nonce_usage = true;
                    }
                    
                    if (script.src) {
                        // External script analysis
                        analysis.security.total_external++;
                        
                        var scriptInfo = {
                            src: script.src,
                            type: script.type || 'text/javascript',
                            async: script.async || false,
                            defer: script.defer || false,
                            crossorigin: script.crossOrigin || '',
                            integrity: script.integrity || '',
                            nonce: script.nonce || '',
                            id: script.id || '',
                            className: script.className || '',
                            loading_type: script.async ? 'async' : (script.defer ? 'defer' : 'blocking')
                        };
                        
                        // Check for SRI usage
                        if (script.integrity) {
                            analysis.security.sri_usage++;
                        }
                        
                        // Performance analysis
                        if (script.async) {
                            analysis.performance.async_scripts++;
                        } else if (script.defer) {
                            analysis.performance.defer_scripts++;
                        } else {
                            analysis.performance.blocking_scripts++;
                        }
                        
                        // Library detection
                        var src_lower = script.src.toLowerCase();
                        for (var j = 0; j < libraryPatterns.length; j++) {
                            var lib = libraryPatterns[j];
                            for (var k = 0; k < lib.patterns.length; k++) {
                                if (src_lower.includes(lib.patterns[k].toLowerCase())) {
                                    if (!analysis.dependencies.libraries.includes(lib.name)) {
                                        analysis.dependencies.libraries.push(lib.name);
                                    }
                                    break;
                                }
                            }
                        }
                        
                        analysis.scripts.external.push(scriptInfo);
                        
                    } else if (script.textContent || script.innerHTML) {
                        // Inline script analysis
                        var content = script.textContent || script.innerHTML;
                        var content_lower = content.toLowerCase();
                        
                        var scriptInfo = {
                            content: content.trim(),
                            type: script.type || 'text/javascript',
                            nonce: script.nonce || '',
                            id: script.id || '',
                            className: script.className || '',
                            length: content.trim().length,
                            preview: content.trim().substring(0, 100) + (content.trim().length > 100 ? '...' : ''),
                            security_issues: [],
                            api_calls: [],
                            dom_manipulations: []
                        };
                        
                        // Enhanced security analysis
                        var securityPatterns = [
                            { pattern: 'eval(', issue: 'eval() usage', severity: 'high' },
                            { pattern: 'document.write(', issue: 'document.write() usage', severity: 'medium' },
                            { pattern: 'innerhtml', issue: 'innerHTML manipulation', severity: 'medium' },
                            { pattern: 'outerhtml', issue: 'outerHTML manipulation', severity: 'medium' },
                            { pattern: 'javascript:', issue: 'JavaScript protocol', severity: 'high' },
                            { pattern: 'data:', issue: 'Data protocol', severity: 'medium' },
                            { pattern: 'vbscript:', issue: 'VBScript protocol', severity: 'high' },
                            { pattern: 'settimeout(', issue: 'setTimeout with string', severity: 'medium' },
                            { pattern: 'setinterval(', issue: 'setInterval with string', severity: 'medium' },
                            { pattern: 'function constructor', issue: 'Function constructor', severity: 'high' },
                            { pattern: 'location.href', issue: 'Location manipulation', severity: 'low' },
                            { pattern: 'window.open(', issue: 'Popup creation', severity: 'low' }
                        ];
                        
                        for (var j = 0; j < securityPatterns.length; j++) {
                            var pattern = securityPatterns[j];
                            if (content_lower.includes(pattern.pattern)) {
                                scriptInfo.security_issues.push({
                                    issue: pattern.issue,
                                    severity: pattern.severity,
                                    pattern: pattern.pattern
                                });
                            }
                        }
                        
                        // API call detection
                        var apiPatterns = [
                            'fetch(', 'xmlhttprequest', 'axios.', '$.ajax', '$.get', '$.post',
                            'navigator.geolocation', 'navigator.camera', 'navigator.microphone',
                            'localstorage', 'sessionstorage', 'indexeddb', 'websocket'
                        ];
                        
                        for (var j = 0; j < apiPatterns.length; j++) {
                            if (content_lower.includes(apiPatterns[j])) {
                                scriptInfo.api_calls.push(apiPatterns[j]);
                            }
                        }
                        
                        // DOM manipulation detection
                        var domPatterns = [
                            'getelementbyid', 'getelementsbytagname', 'queryselector',
                            'addeventlistener', 'removeeventlistener', 'createelement',
                            'appendchild', 'removechild', 'insertbefore'
                        ];
                        
                        for (var j = 0; j < domPatterns.length; j++) {
                            if (content_lower.includes(domPatterns[j])) {
                                scriptInfo.dom_manipulations.push(domPatterns[j]);
                            }
                        }
                        
                        // Library detection in inline scripts
                        for (var j = 0; j < libraryPatterns.length; j++) {
                            var lib = libraryPatterns[j];
                            for (var k = 0; k < lib.patterns.length; k++) {
                                if (content_lower.includes(lib.patterns[k].toLowerCase()) || 
                                    content.includes(lib.patterns[k])) {
                                    if (!analysis.dependencies.libraries.includes(lib.name)) {
                                        analysis.dependencies.libraries.push(lib.name);
                                    }
                                    break;
                                }
                            }
                        }
                        
                        analysis.scripts.inline.push(scriptInfo);
                    }
                }
                
                return analysis;
            })();
            """
            
            def process_analysis(analysis_data):
                if not analysis_data:
                    self.main_window.status_info.setText("ℹ️ No script analysis data available")
                    QTimer.singleShot(3000, lambda: self.main_window.status_info.setText(""))
                    return
                
                # Create and show the advanced analysis dialog
                self.show_advanced_analysis_dialog(analysis_data, current_url, browser)
            
            # Execute JavaScript to get analysis data
            page.runJavaScript(js_code, process_analysis)
            
        except Exception as e:
            self.main_window.status_info.setText(f"❌ Advanced analysis error: {str(e)}")
            QTimer.singleShot(3000, lambda: self.main_window.status_info.setText(""))
    
    def show_advanced_analysis_dialog(self, analysis_data, base_url, browser):
        """Show dialog with advanced script analysis results"""
        from PyQt5.QtWidgets import (QDialog, QVBoxLayout, QHBoxLayout, QLabel, 
                                   QTextEdit, QPushButton, QTabWidget, QWidget,
                                   QTreeWidget, QTreeWidgetItem, QHeaderView,
                                   QProgressBar, QGroupBox, QGridLayout, QFileDialog)
        from PyQt5.QtCore import Qt
        from PyQt5.QtGui import QFont, QColor
        from datetime import datetime
        
        scripts = analysis_data.get('scripts', {})
        security = analysis_data.get('security', {})
        performance = analysis_data.get('performance', {})
        dependencies = analysis_data.get('dependencies', {})
        
        inline_scripts = scripts.get('inline', [])
        external_scripts = scripts.get('external', [])
        
        # Create dialog
        dialog = QDialog(self.main_window)
        dialog.setWindowTitle(f"🔍 Advanced Script Analysis")
        dialog.setMinimumSize(1000, 800)
        dialog.resize(1400, 900)
        
        layout = QVBoxLayout(dialog)
        
        # Header
        header_label = QLabel(f"Advanced Script Analysis for: {base_url}")
        header_label.setStyleSheet("font-weight: bold; font-size: 14px; padding: 10px; background-color: #e8f4fd; border-radius: 5px;")
        header_label.setWordWrap(True)
        layout.addWidget(header_label)
        
        # Tab widget for different analysis views
        tab_widget = QTabWidget()
        layout.addWidget(tab_widget)
        
        # 1. Security Analysis Tab
        security_widget = QWidget()
        security_layout = QVBoxLayout(security_widget)
        
        # Security overview
        security_group = QGroupBox("🔒 Security Overview")
        security_grid = QGridLayout(security_group)
        
        # CSP Status
        csp_status = "✅ Present" if security.get('csp') else "❌ Missing"
        csp_label = QLabel(f"Content Security Policy: {csp_status}")
        if not security.get('csp'):
            csp_label.setStyleSheet("color: red; font-weight: bold;")
        security_grid.addWidget(csp_label, 0, 0)
        
        # SRI Usage
        sri_count = security.get('sri_usage', 0)
        total_external = security.get('total_external', 0)
        sri_percentage = (sri_count / total_external * 100) if total_external > 0 else 0
        sri_label = QLabel(f"Subresource Integrity: {sri_count}/{total_external} scripts ({sri_percentage:.1f}%)")
        if sri_percentage < 50:
            sri_label.setStyleSheet("color: orange; font-weight: bold;")
        elif sri_percentage < 100:
            sri_label.setStyleSheet("color: blue;")
        else:
            sri_label.setStyleSheet("color: green;")
        security_grid.addWidget(sri_label, 0, 1)
        
        # Nonce Usage
        nonce_status = "✅ Used" if security.get('nonce_usage') else "❌ Not used"
        nonce_label = QLabel(f"Nonce Usage: {nonce_status}")
        if not security.get('nonce_usage'):
            nonce_label.setStyleSheet("color: orange;")
        security_grid.addWidget(nonce_label, 1, 0)
        
        security_layout.addWidget(security_group)
        
        # Security issues tree
        security_tree = QTreeWidget()
        security_tree.setHeaderLabels(['Script', 'Issue', 'Severity', 'Pattern'])
        security_tree.header().setSectionResizeMode(0, QHeaderView.Stretch)
        
        high_severity_count = 0
        medium_severity_count = 0
        low_severity_count = 0
        
        for i, script in enumerate(inline_scripts):
            for issue in script.get('security_issues', []):
                item = QTreeWidgetItem()
                item.setText(0, f"Inline Script #{i+1}")
                item.setText(1, issue.get('issue', ''))
                item.setText(2, issue.get('severity', '').upper())
                item.setText(3, issue.get('pattern', ''))
                
                # Color code by severity
                severity = issue.get('severity', '').lower()
                if severity == 'high':
                    item.setBackground(2, QColor(255, 200, 200))
                    high_severity_count += 1
                elif severity == 'medium':
                    item.setBackground(2, QColor(255, 255, 200))
                    medium_severity_count += 1
                else:
                    item.setBackground(2, QColor(200, 255, 200))
                    low_severity_count += 1
                
                security_tree.addTopLevelItem(item)
        
        security_summary = QLabel(f"Security Issues Found: {high_severity_count} High, {medium_severity_count} Medium, {low_severity_count} Low")
        if high_severity_count > 0:
            security_summary.setStyleSheet("color: red; font-weight: bold;")
        elif medium_severity_count > 0:
            security_summary.setStyleSheet("color: orange; font-weight: bold;")
        else:
            security_summary.setStyleSheet("color: green;")
        
        security_layout.addWidget(security_summary)
        security_layout.addWidget(security_tree)
        
        tab_widget.addTab(security_widget, f"🔒 Security ({high_severity_count + medium_severity_count + low_severity_count})")
        
        # 2. Performance Analysis Tab
        performance_widget = QWidget()
        performance_layout = QVBoxLayout(performance_widget)
        
        perf_group = QGroupBox("⚡ Performance Analysis")
        perf_grid = QGridLayout(perf_group)
        
        blocking_count = performance.get('blocking_scripts', 0)
        async_count = performance.get('async_scripts', 0)
        defer_count = performance.get('defer_scripts', 0)
        
        perf_grid.addWidget(QLabel(f"Blocking Scripts: {blocking_count}"), 0, 0)
        perf_grid.addWidget(QLabel(f"Async Scripts: {async_count}"), 0, 1)
        perf_grid.addWidget(QLabel(f"Deferred Scripts: {defer_count}"), 1, 0)
        
        # Performance recommendations
        recommendations = []
        if blocking_count > 3:
            recommendations.append("⚠️ Consider using async/defer for non-critical scripts")
        if async_count == 0 and defer_count == 0:
            recommendations.append("💡 Consider using async/defer attributes for better performance")
        if len(external_scripts) > 10:
            recommendations.append("📦 Consider bundling scripts to reduce HTTP requests")
        
        if recommendations:
            rec_text = QTextEdit()
            rec_text.setMaximumHeight(100)
            rec_text.setPlainText('\n'.join(recommendations))
            rec_text.setStyleSheet("background-color: #fff3cd; border: 1px solid #ffeaa7;")
            perf_grid.addWidget(rec_text, 2, 0, 1, 2)
        
        performance_layout.addWidget(perf_group)
        
        # Script loading visualization
        loading_tree = QTreeWidget()
        loading_tree.setHeaderLabels(['Script', 'Loading Type', 'Impact', 'Recommendation'])
        
        for script in external_scripts:
            item = QTreeWidgetItem()
            item.setText(0, script.get('src', '')[-50:])  # Last 50 chars
            loading_type = script.get('loading_type', 'blocking')
            item.setText(1, loading_type.title())
            
            if loading_type == 'blocking':
                item.setText(2, "High - Blocks page rendering")
                item.setText(3, "Consider async/defer")
                item.setBackground(1, QColor(255, 200, 200))
            elif loading_type == 'defer':
                item.setText(2, "Low - Executes after DOM")
                item.setText(3, "Good for DOM manipulation")
                item.setBackground(1, QColor(200, 255, 200))
            else:  # async
                item.setText(2, "Medium - Non-blocking")
                item.setText(3, "Good for independent scripts")
                item.setBackground(1, QColor(200, 200, 255))
            
            loading_tree.addTopLevelItem(item)
        
        performance_layout.addWidget(loading_tree)
        tab_widget.addTab(performance_widget, f"⚡ Performance")
        
        # 3. Dependencies Tab
        deps_widget = QWidget()
        deps_layout = QVBoxLayout(deps_widget)
        
        deps_group = QGroupBox("📚 Detected Libraries & Frameworks")
        deps_grid = QGridLayout(deps_group)
        
        libraries = dependencies.get('libraries', [])
        if libraries:
            libs_text = QTextEdit()
            libs_text.setMaximumHeight(150)
            libs_content = []
            for lib in libraries:
                libs_content.append(f"✅ {lib}")
            libs_text.setPlainText('\n'.join(libs_content))
            libs_text.setStyleSheet("background-color: #e8f5e8; font-family: monospace;")
            deps_grid.addWidget(libs_text, 0, 0)
        else:
            no_libs_label = QLabel("No common libraries detected")
            no_libs_label.setStyleSheet("color: gray; font-style: italic;")
            deps_grid.addWidget(no_libs_label, 0, 0)
        
        deps_layout.addWidget(deps_group)
        
        # API Usage Analysis
        api_group = QGroupBox("🔌 API Usage Analysis")
        api_layout = QVBoxLayout(api_group)
        
        api_tree = QTreeWidget()
        api_tree.setHeaderLabels(['Script', 'API Calls', 'DOM Manipulations'])
        
        for i, script in enumerate(inline_scripts):
            if script.get('api_calls') or script.get('dom_manipulations'):
                item = QTreeWidgetItem()
                item.setText(0, f"Inline Script #{i+1}")
                item.setText(1, ', '.join(script.get('api_calls', [])))
                item.setText(2, ', '.join(script.get('dom_manipulations', [])))
                api_tree.addTopLevelItem(item)
        
        api_layout.addWidget(api_tree)
        deps_layout.addWidget(api_group)
        
        tab_widget.addTab(deps_widget, f"📚 Dependencies ({len(libraries)})")
        
        # Buttons
        button_layout = QHBoxLayout()
        
        export_button = QPushButton("📊 Export Full Report")
        close_button = QPushButton("❌ Close")
        
        button_layout.addStretch()
        button_layout.addWidget(export_button)
        button_layout.addWidget(close_button)
        layout.addLayout(button_layout)
        
        def export_full_report():
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            filename = f"advanced_script_analysis_{timestamp}.txt"
            
            file_path, _ = QFileDialog.getSaveFileName(
                dialog,
                "Export Advanced Script Analysis Report",
                filename,
                "Text Files (*.txt);;All Files (*.*)"
            )
            
            if file_path:
                try:
                    # Generate comprehensive report
                    report_lines = []
                    report_lines.append("ADVANCED SCRIPT ANALYSIS REPORT")
                    report_lines.append("=" * 60)
                    report_lines.append(f"URL: {base_url}")
                    report_lines.append(f"Analysis Date: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
                    report_lines.append("")
                    
                    # Security Summary
                    report_lines.append("SECURITY ANALYSIS")
                    report_lines.append("-" * 30)
                    report_lines.append(f"Content Security Policy: {'Present' if security.get('csp') else 'Missing'}")
                    report_lines.append(f"Subresource Integrity: {sri_count}/{total_external} scripts ({sri_percentage:.1f}%)")
                    report_lines.append(f"Nonce Usage: {'Yes' if security.get('nonce_usage') else 'No'}")
                    report_lines.append(f"Security Issues: {high_severity_count} High, {medium_severity_count} Medium, {low_severity_count} Low")
                    report_lines.append("")
                    
                    # Performance Summary
                    report_lines.append("PERFORMANCE ANALYSIS")
                    report_lines.append("-" * 30)
                    report_lines.append(f"Blocking Scripts: {blocking_count}")
                    report_lines.append(f"Async Scripts: {async_count}")
                    report_lines.append(f"Deferred Scripts: {defer_count}")
                    report_lines.append("")
                    
                    # Dependencies
                    report_lines.append("DETECTED LIBRARIES")
                    report_lines.append("-" * 30)
                    if libraries:
                        for lib in libraries:
                            report_lines.append(f"- {lib}")
                    else:
                        report_lines.append("No common libraries detected")
                    report_lines.append("")
                    
                    with open(file_path, 'w', encoding='utf-8') as f:
                        f.write('\n'.join(report_lines))
                    
                    self.main_window.status_info.setText(f"✅ Advanced report exported to: {file_path}")
                    QTimer.singleShot(3000, lambda: self.main_window.status_info.setText(""))
                except Exception as e:
                    self.main_window.status_info.setText(f"❌ Export failed: {str(e)}")
                    QTimer.singleShot(3000, lambda: self.main_window.status_info.setText(""))
        
        # Connect buttons
        export_button.clicked.connect(export_full_report)
        close_button.clicked.connect(dialog.accept)
        
        # Show dialog
        dialog.exec_()
        
        # Update main window status
        total_issues = high_severity_count + medium_severity_count + low_severity_count
        self.main_window.status_info.setText(f"🔍 Advanced analysis complete: {total_issues} security issues found")
        QTimer.singleShot(5000, lambda: self.main_window.status_info.setText(""))
    
    def scan_and_remove_ads(self, browser):
        """Scan for advertisements and remove them from the page"""
        try:
            page = browser.page()
            current_url = browser.url().toString()
            
            # Show initial status
            self.main_window.status_info.setText("🚫 Scanning and removing ads...")
            
            # Comprehensive JavaScript for ad detection and removal
            js_code = """
            (function() {
                var adBlocker = {
                    removed: {
                        elements: 0,
                        scripts: 0,
                        iframes: 0,
                        images: 0,
                        divs: 0
                    },
                    detected: [],
                    
                    // Common ad-related selectors
                    adSelectors: [
                        // Generic ad classes and IDs
                        '[class*="ad-"]', '[class*="ads-"]', '[class*="_ad_"]', '[class*="_ads_"]',
                        '[id*="ad-"]', '[id*="ads-"]', '[id*="_ad_"]', '[id*="_ads_"]',
                        '.advertisement', '.ads', '.ad', '.advert', '.adsystem',
                        '#advertisement', '#ads', '#ad', '#advert',
                        
                        // Google Ads
                        '.google-ads', '.googleads', '.adsbygoogle', 'ins.adsbygoogle',
                        '[data-ad-client]', '[data-ad-slot]', '.google-ad',
                        
                        // Common ad networks
                        '.doubleclick', '.googlesyndication', '.amazon-ads', '.facebook-ads',
                        '.outbrain', '.taboola', '.revcontent', '.content-ads',
                        
                        // Banner and display ads
                        '.banner', '.banner-ad', '.display-ad', '.sidebar-ad',
                        '.header-ad', '.footer-ad', '.popup-ad', '.overlay-ad',
                        
                        // Video ads
                        '.video-ad', '.preroll', '.midroll', '.postroll',
                        
                        // Sponsored content
                        '.sponsored', '.sponsor', '.promoted', '.native-ad',
                        
                        // Pop-up and modal ads
                        '.popup', '.modal-ad', '.overlay', '.interstitial',
                        
                        // Social media ads
                        '[data-testid*="ad"]', '[aria-label*="Sponsored"]',
                        
                        // Generic suspicious containers
                        '[style*="position: fixed"]', '[style*="z-index: 999"]'
                    ],
                    
                    // Ad-related domains and URLs
                    adDomains: [
                        'doubleclick.net', 'googlesyndication.com', 'googleadservices.com',
                        'amazon-adsystem.com', 'facebook.com/tr', 'google-analytics.com',
                        'outbrain.com', 'taboola.com', 'revcontent.com', 'criteo.com',
                        'adsystem.com', 'adscdn.com', 'ads.yahoo.com', 'bing.com/ads',
                        'scorecardresearch.com', 'quantserve.com', 'addthis.com'
                    ],
                    
                    // Text patterns that indicate ads
                    adTextPatterns: [
                        /sponsored/i, /advertisement/i, /promoted/i, /ads by/i,
                        /buy now/i, /click here/i, /limited time/i, /special offer/i,
                        /discount/i, /sale/i, /free trial/i, /sign up now/i
                    ],
                    
                    removeElement: function(element, type) {
                        if (element && element.parentNode) {
                            var info = {
                                type: type,
                                tag: element.tagName,
                                className: element.className,
                                id: element.id,
                                src: element.src || '',
                                text: element.textContent ? element.textContent.substring(0, 50) : ''
                            };
                            
                            this.detected.push(info);
                            element.style.display = 'none';
                            element.remove();
                            this.removed[type]++;
                            this.removed.elements++;
                        }
                    },
                    
                    scanBySelectors: function() {
                        for (var i = 0; i < this.adSelectors.length; i++) {
                            try {
                                var elements = document.querySelectorAll(this.adSelectors[i]);
                                for (var j = 0; j < elements.length; j++) {
                                    this.removeElement(elements[j], 'divs');
                                }
                            } catch (e) {
                                // Ignore invalid selectors
                            }
                        }
                    },
                    
                    scanScripts: function() {
                        var scripts = document.getElementsByTagName('script');
                        for (var i = scripts.length - 1; i >= 0; i--) {
                            var script = scripts[i];
                            if (script.src) {
                                for (var j = 0; j < this.adDomains.length; j++) {
                                    if (script.src.includes(this.adDomains[j])) {
                                        this.removeElement(script, 'scripts');
                                        break;
                                    }
                                }
                            }
                        }
                    },
                    
                    scanIframes: function() {
                        var iframes = document.getElementsByTagName('iframe');
                        for (var i = iframes.length - 1; i >= 0; i--) {
                            var iframe = iframes[i];
                            if (iframe.src) {
                                for (var j = 0; j < this.adDomains.length; j++) {
                                    if (iframe.src.includes(this.adDomains[j])) {
                                        this.removeElement(iframe, 'iframes');
                                        break;
                                    }
                                }
                            }
                            
                            // Check iframe dimensions (common ad sizes)
                            var width = iframe.width || iframe.offsetWidth;
                            var height = iframe.height || iframe.offsetHeight;
                            
                            // Common ad sizes: 728x90, 300x250, 160x600, 320x50, etc.
                            var commonAdSizes = [
                                [728, 90], [300, 250], [160, 600], [320, 50],
                                [468, 60], [234, 60], [120, 600], [336, 280],
                                [970, 250], [300, 600], [320, 100]
                            ];
                            
                            for (var k = 0; k < commonAdSizes.length; k++) {
                                if (width == commonAdSizes[k][0] && height == commonAdSizes[k][1]) {
                                    this.removeElement(iframe, 'iframes');
                                    break;
                                }
                            }
                        }
                    },
                    
                    scanImages: function() {
                        var images = document.getElementsByTagName('img');
                        for (var i = images.length - 1; i >= 0; i--) {
                            var img = images[i];
                            
                            // Check image source for ad domains
                            if (img.src) {
                                for (var j = 0; j < this.adDomains.length; j++) {
                                    if (img.src.includes(this.adDomains[j])) {
                                        this.removeElement(img, 'images');
                                        break;
                                    }
                                }
                            }
                            
                            // Check alt text for ad patterns
                            if (img.alt) {
                                for (var k = 0; k < this.adTextPatterns.length; k++) {
                                    if (this.adTextPatterns[k].test(img.alt)) {
                                        this.removeElement(img, 'images');
                                        break;
                                    }
                                }
                            }
                        }
                    },
                    
                    scanByText: function() {
                        var walker = document.createTreeWalker(
                            document.body,
                            NodeFilter.SHOW_ELEMENT,
                            null,
                            false
                        );
                        
                        var elementsToRemove = [];
                        var node;
                        
                        while (node = walker.nextNode()) {
                            var text = node.textContent || '';
                            
                            // Skip if element is too large (likely not an ad)
                            if (text.length > 500) continue;
                            
                            for (var i = 0; i < this.adTextPatterns.length; i++) {
                                if (this.adTextPatterns[i].test(text)) {
                                    // Check if it's likely an ad container
                                    if (node.children.length < 5 && text.length < 200) {
                                        elementsToRemove.push(node);
                                        break;
                                    }
                                }
                            }
                        }
                        
                        for (var j = 0; j < elementsToRemove.length; j++) {
                            this.removeElement(elementsToRemove[j], 'divs');
                        }
                    },
                    
                    removePopups: function() {
                        // Remove fixed position elements that might be popups
                        var allElements = document.querySelectorAll('*');
                        for (var i = 0; i < allElements.length; i++) {
                            var element = allElements[i];
                            var style = window.getComputedStyle(element);
                            
                            if (style.position === 'fixed' && 
                                (parseInt(style.zIndex) > 1000 || style.zIndex === 'auto')) {
                                
                                // Check if it covers a significant portion of the screen
                                var rect = element.getBoundingClientRect();
                                var screenArea = window.innerWidth * window.innerHeight;
                                var elementArea = rect.width * rect.height;
                                
                                if (elementArea > screenArea * 0.1) { // More than 10% of screen
                                    this.removeElement(element, 'divs');
                                }
                            }
                        }
                    },
                    
                    blockFutureAds: function() {
                        // Override common ad loading functions
                        if (window.googletag) {
                            window.googletag.display = function() {};
                            window.googletag.enableServices = function() {};
                        }
                        
                        // Block Google AdSense
                        if (window.adsbygoogle) {
                            window.adsbygoogle = [];
                        }
                        
                        // Override setTimeout and setInterval for ad-related calls
                        var originalSetTimeout = window.setTimeout;
                        var originalSetInterval = window.setInterval;
                        
                        window.setTimeout = function(func, delay) {
                            var funcStr = func.toString();
                            for (var i = 0; i < adBlocker.adDomains.length; i++) {
                                if (funcStr.includes(adBlocker.adDomains[i])) {
                                    return; // Block ad-related timeouts
                                }
                            }
                            return originalSetTimeout.apply(this, arguments);
                        };
                        
                        window.setInterval = function(func, delay) {
                            var funcStr = func.toString();
                            for (var i = 0; i < adBlocker.adDomains.length; i++) {
                                if (funcStr.includes(adBlocker.adDomains[i])) {
                                    return; // Block ad-related intervals
                                }
                            }
                            return originalSetInterval.apply(this, arguments);
                        };
                    },
                    
                    run: function() {
                        console.log('🚫 Starting ad removal process...');
                        
                        // Run all scanning methods
                        this.scanBySelectors();
                        this.scanScripts();
                        this.scanIframes();
                        this.scanImages();
                        this.scanByText();
                        this.removePopups();
                        this.blockFutureAds();
                        
                        console.log('🚫 Ad removal complete:', this.removed);
                        
                        return {
                            removed: this.removed,
                            detected: this.detected,
                            summary: 'Removed ' + this.removed.elements + ' ad elements'
                        };
                    }
                };
                
                return adBlocker.run();
            })();
            """
            
            def process_ad_removal(result):
                if not result:
                    self.main_window.status_info.setText("ℹ️ No ads detected on this page")
                    QTimer.singleShot(3000, lambda: self.main_window.status_info.setText(""))
                    return
                
                removed = result.get('removed', {})
                total_removed = removed.get('elements', 0)
                
                if total_removed > 0:
                    # Show success message
                    self.main_window.status_info.setText(f"🚫 Removed {total_removed} ad elements!")
                    QTimer.singleShot(5000, lambda: self.main_window.status_info.setText(""))
                    
                    # Show detailed results dialog
                    self.show_ad_removal_dialog(result, current_url)
                else:
                    self.main_window.status_info.setText("✅ No ads found on this page")
                    QTimer.singleShot(3000, lambda: self.main_window.status_info.setText(""))
            
            # Execute JavaScript to remove ads
            page.runJavaScript(js_code, process_ad_removal)
            
        except Exception as e:
            self.main_window.status_info.setText(f"❌ Ad removal error: {str(e)}")
            QTimer.singleShot(3000, lambda: self.main_window.status_info.setText(""))
    
    def show_ad_removal_dialog(self, result, base_url):
        """Show dialog with ad removal results"""
        from PyQt5.QtWidgets import (QDialog, QVBoxLayout, QHBoxLayout, QLabel, 
                                   QTextEdit, QPushButton, QTreeWidget, QTreeWidgetItem,
                                   QHeaderView, QGroupBox, QGridLayout, QFileDialog)
        from PyQt5.QtCore import Qt
        from PyQt5.QtGui import QColor
        from datetime import datetime
        
        removed = result.get('removed', {})
        detected = result.get('detected', [])
        
        # Create dialog
        dialog = QDialog(self.main_window)
        dialog.setWindowTitle(f"🚫 Ad Removal Results - {removed.get('elements', 0)} ads removed")
        dialog.setMinimumSize(800, 600)
        dialog.resize(1000, 700)
        
        layout = QVBoxLayout(dialog)
        
        # Header
        header_label = QLabel(f"Ad Removal Results for: {base_url}")
        header_label.setStyleSheet("font-weight: bold; padding: 10px; background-color: #e8f5e8; border-radius: 5px;")
        header_label.setWordWrap(True)
        layout.addWidget(header_label)
        
        # Summary statistics
        summary_group = QGroupBox("📊 Removal Summary")
        summary_grid = QGridLayout(summary_group)
        
        summary_grid.addWidget(QLabel(f"Total Elements Removed: {removed.get('elements', 0)}"), 0, 0)
        summary_grid.addWidget(QLabel(f"Ad Scripts Blocked: {removed.get('scripts', 0)}"), 0, 1)
        summary_grid.addWidget(QLabel(f"Ad Iframes Removed: {removed.get('iframes', 0)}"), 1, 0)
        summary_grid.addWidget(QLabel(f"Ad Images Removed: {removed.get('images', 0)}"), 1, 1)
        summary_grid.addWidget(QLabel(f"Ad Containers Removed: {removed.get('divs', 0)}"), 2, 0)
        
        layout.addWidget(summary_group)
        
        # Detailed list of removed elements
        details_label = QLabel("🗑️ Removed Elements Details:")
        details_label.setStyleSheet("font-weight: bold; margin-top: 10px;")
        layout.addWidget(details_label)
        
        details_tree = QTreeWidget()
        details_tree.setHeaderLabels(['Type', 'Tag', 'Class/ID', 'Source/Text'])
        details_tree.header().setSectionResizeMode(0, QHeaderView.ResizeToContents)
        details_tree.header().setSectionResizeMode(1, QHeaderView.ResizeToContents)
        details_tree.header().setSectionResizeMode(2, QHeaderView.Stretch)
        details_tree.header().setSectionResizeMode(3, QHeaderView.Stretch)
        
        for ad in detected:
            item = QTreeWidgetItem()
            item.setText(0, ad.get('type', '').title())
            item.setText(1, ad.get('tag', ''))
            
            # Combine class and ID info
            class_id = []
            if ad.get('className'):
                class_id.append(f"class: {ad['className'][:30]}")
            if ad.get('id'):
                class_id.append(f"id: {ad['id']}")
            item.setText(2, ' | '.join(class_id) if class_id else 'none')
            
            # Show source or text content
            content = ad.get('src') or ad.get('text', '')
            item.setText(3, content[:60] + ('...' if len(content) > 60 else ''))
            
            # Color code by type
            ad_type = ad.get('type', '').lower()
            if ad_type == 'scripts':
                item.setBackground(0, QColor(255, 200, 200))
            elif ad_type == 'iframes':
                item.setBackground(0, QColor(255, 255, 200))
            elif ad_type == 'images':
                item.setBackground(0, QColor(200, 255, 200))
            else:
                item.setBackground(0, QColor(200, 200, 255))
            
            details_tree.addTopLevelItem(item)
        
        layout.addWidget(details_tree)
        
        # Recommendations
        recommendations_text = QTextEdit()
        recommendations_text.setMaximumHeight(120)
        recommendations = []
        
        if removed.get('elements', 0) > 0:
            recommendations.append("✅ Successfully removed detected advertisements")
            recommendations.append("💡 Consider installing a browser extension for permanent ad blocking")
            recommendations.append("🔄 You can re-run this tool if new ads appear dynamically")
            
            if removed.get('scripts', 0) > 0:
                recommendations.append("⚠️ Some ad scripts were blocked - page functionality should be preserved")
        else:
            recommendations.append("🎉 This page appears to be ad-free!")
            recommendations.append("💡 The site may be using ethical advertising or no ads at all")
        
        recommendations_text.setPlainText('\n'.join(recommendations))
        recommendations_text.setStyleSheet("background-color: #f0f8ff; border: 1px solid #b0d4f1; padding: 5px;")
        layout.addWidget(recommendations_text)
        
        # Buttons
        button_layout = QHBoxLayout()
        
        export_button = QPushButton("📊 Export Report")
        refresh_button = QPushButton("🔄 Scan Again")
        close_button = QPushButton("❌ Close")
        
        button_layout.addStretch()
        button_layout.addWidget(refresh_button)
        button_layout.addWidget(export_button)
        button_layout.addWidget(close_button)
        layout.addLayout(button_layout)
        
        def export_report():
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            filename = f"ad_removal_report_{timestamp}.txt"
            
            file_path, _ = QFileDialog.getSaveFileName(
                dialog,
                "Export Ad Removal Report",
                filename,
                "Text Files (*.txt);;All Files (*.*)"
            )
            
            if file_path:
                try:
                    report_lines = []
                    report_lines.append("AD REMOVAL REPORT")
                    report_lines.append("=" * 50)
                    report_lines.append(f"URL: {base_url}")
                    report_lines.append(f"Scan Date: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
                    report_lines.append("")
                    
                    report_lines.append("REMOVAL SUMMARY")
                    report_lines.append("-" * 30)
                    report_lines.append(f"Total Elements Removed: {removed.get('elements', 0)}")
                    report_lines.append(f"Ad Scripts Blocked: {removed.get('scripts', 0)}")
                    report_lines.append(f"Ad Iframes Removed: {removed.get('iframes', 0)}")
                    report_lines.append(f"Ad Images Removed: {removed.get('images', 0)}")
                    report_lines.append(f"Ad Containers Removed: {removed.get('divs', 0)}")
                    report_lines.append("")
                    
                    if detected:
                        report_lines.append("DETAILED REMOVAL LIST")
                        report_lines.append("-" * 30)
                        for i, ad in enumerate(detected, 1):
                            report_lines.append(f"{i}. {ad.get('type', '').title()} - {ad.get('tag', '')}")
                            if ad.get('className'):
                                report_lines.append(f"   Class: {ad['className']}")
                            if ad.get('id'):
                                report_lines.append(f"   ID: {ad['id']}")
                            if ad.get('src'):
                                report_lines.append(f"   Source: {ad['src']}")
                            elif ad.get('text'):
                                report_lines.append(f"   Text: {ad['text'][:100]}")
                            report_lines.append("")
                    
                    with open(file_path, 'w', encoding='utf-8') as f:
                        f.write('\n'.join(report_lines))
                    
                    self.main_window.status_info.setText(f"✅ Report exported to: {file_path}")
                    QTimer.singleShot(3000, lambda: self.main_window.status_info.setText(""))
                except Exception as e:
                    self.main_window.status_info.setText(f"❌ Export failed: {str(e)}")
                    QTimer.singleShot(3000, lambda: self.main_window.status_info.setText(""))
        
        def scan_again():
            dialog.accept()
            # Re-run the ad removal
            self.scan_and_remove_ads(browser)
        
        # Connect buttons
        export_button.clicked.connect(export_report)
        refresh_button.clicked.connect(scan_again)
        close_button.clicked.connect(dialog.accept)
        
        # Show dialog
        dialog.exec_()
    
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
    
    def analyze_privacy_score(self, browser):
        """Analyze privacy score of the current website"""
        try:
            page = browser.page()
            current_url = browser.url().toString()
            
            # Show initial status
            self.main_window.status_info.setText("🔒 Analyzing privacy score...")
            
            # JavaScript to collect privacy-related information
            js_code = """
            (function() {
                var privacy = {
                    cookies: [],
                    localStorage: {},
                    sessionStorage: {},
                    trackers: [],
                    thirdPartyRequests: [],
                    forms: [],
                    security: {},
                    permissions: {},
                    fingerprinting: {}
                };
                
                // Analyze cookies
                try {
                    var cookies = document.cookie.split(';');
                    privacy.cookies = cookies.map(function(cookie) {
                        var parts = cookie.trim().split('=');
                        return {
                            name: parts[0] || '',
                            value: parts[1] || '',
                            length: cookie.length,
                            hasSecure: cookie.toLowerCase().includes('secure'),
                            hasHttpOnly: cookie.toLowerCase().includes('httponly'),
                            hasSameSite: cookie.toLowerCase().includes('samesite')
                        };
                    }).filter(function(c) { return c.name; });
                } catch(e) {
                    privacy.cookies = [];
                }
                
                // Analyze local storage
                try {
                    privacy.localStorage = {
                        itemCount: localStorage.length,
                        totalSize: JSON.stringify(localStorage).length,
                        keys: Object.keys(localStorage)
                    };
                } catch(e) {
                    privacy.localStorage = { itemCount: 0, totalSize: 0, keys: [] };
                }
                
                // Analyze session storage
                try {
                    privacy.sessionStorage = {
                        itemCount: sessionStorage.length,
                        totalSize: JSON.stringify(sessionStorage).length,
                        keys: Object.keys(sessionStorage)
                    };
                } catch(e) {
                    privacy.sessionStorage = { itemCount: 0, totalSize: 0, keys: [] };
                }
                
                // Analyze forms for sensitive data collection
                var forms = document.forms;
                for (var i = 0; i < forms.length; i++) {
                    var form = forms[i];
                    var inputs = form.querySelectorAll('input, textarea, select');
                    var sensitiveFields = [];
                    
                    for (var j = 0; j < inputs.length; j++) {
                        var input = inputs[j];
                        var type = input.type ? input.type.toLowerCase() : '';
                        var name = input.name ? input.name.toLowerCase() : '';
                        var id = input.id ? input.id.toLowerCase() : '';
                        var placeholder = input.placeholder ? input.placeholder.toLowerCase() : '';
                        
                        // Check for sensitive field types
                        var isSensitive = type === 'password' || type === 'email' || 
                                        name.includes('password') || name.includes('email') || 
                                        name.includes('phone') || name.includes('credit') || 
                                        name.includes('card') || name.includes('ssn') || 
                                        id.includes('password') || id.includes('email') ||
                                        placeholder.includes('password') || placeholder.includes('email');
                        
                        if (isSensitive) {
                            sensitiveFields.push({
                                type: type,
                                name: name,
                                id: id,
                                placeholder: placeholder
                            });
                        }
                    }
                    
                    privacy.forms.push({
                        action: form.action || '',
                        method: form.method || 'get',
                        isHttps: (form.action || '').startsWith('https://'),
                        inputCount: inputs.length,
                        sensitiveFields: sensitiveFields,
                        hasAutoComplete: form.autocomplete !== 'off'
                    });
                }
                
                // Security analysis
                privacy.security = {
                    isHttps: window.location.protocol === 'https:',
                    hasMixedContent: false, // Will be detected by checking resources
                    hasCSP: !!document.querySelector('meta[http-equiv="Content-Security-Policy"]'),
                    hasXFrameOptions: false, // Server-side header, can't detect from JS
                    referrerPolicy: document.querySelector('meta[name="referrer"]') ? 
                                  document.querySelector('meta[name="referrer"]').content : 'default'
                };
                
                // Fingerprinting detection
                privacy.fingerprinting = {
                    canvasFingerprinting: !!document.querySelector('canvas'),
                    webglFingerprinting: !!(window.WebGLRenderingContext || window.WebGL2RenderingContext),
                    audioFingerprinting: !!(window.AudioContext || window.webkitAudioContext),
                    fontFingerprinting: document.fonts ? document.fonts.size > 0 : false,
                    screenFingerprinting: true, // Screen properties always available
                    timezoneFingerprinting: true, // Timezone always detectable
                    languageFingerprinting: navigator.languages ? navigator.languages.length > 1 : false
                };
                
                // Detect potential trackers (common tracking domains and scripts)
                var scripts = document.scripts;
                var trackingDomains = [
                    'google-analytics.com', 'googletagmanager.com', 'doubleclick.net',
                    'facebook.com', 'facebook.net', 'connect.facebook.net',
                    'twitter.com', 'ads.twitter.com', 'analytics.twitter.com',
                    'amazon-adsystem.com', 'googlesyndication.com', 'adsystem.amazon.com',
                    'scorecardresearch.com', 'quantserve.com', 'outbrain.com',
                    'taboola.com', 'addthis.com', 'sharethis.com'
                ];
                
                for (var i = 0; i < scripts.length; i++) {
                    var src = scripts[i].src;
                    if (src) {
                        for (var j = 0; j < trackingDomains.length; j++) {
                            if (src.includes(trackingDomains[j])) {
                                privacy.trackers.push({
                                    domain: trackingDomains[j],
                                    url: src,
                                    type: 'script'
                                });
                                break;
                            }
                        }
                    }
                }
                
                // Check for third-party requests (images, iframes, etc.)
                var images = document.images;
                var currentDomain = window.location.hostname;
                
                for (var i = 0; i < images.length; i++) {
                    var imgSrc = images[i].src;
                    if (imgSrc && !imgSrc.includes(currentDomain) && imgSrc.startsWith('http')) {
                        var domain = new URL(imgSrc).hostname;
                        privacy.thirdPartyRequests.push({
                            domain: domain,
                            url: imgSrc,
                            type: 'image'
                        });
                    }
                }
                
                // Check iframes
                var iframes = document.iframes || document.querySelectorAll('iframe');
                for (var i = 0; i < iframes.length; i++) {
                    var iframeSrc = iframes[i].src;
                    if (iframeSrc && !iframeSrc.includes(currentDomain) && iframeSrc.startsWith('http')) {
                        var domain = new URL(iframeSrc).hostname;
                        privacy.thirdPartyRequests.push({
                            domain: domain,
                            url: iframeSrc,
                            type: 'iframe'
                        });
                    }
                }
                
                return privacy;
            })();
            """
            
            def process_privacy_data(privacy_data):
                if not privacy_data:
                    self.main_window.status_info.setText("❌ Could not collect privacy data")
                    QTimer.singleShot(3000, lambda: self.main_window.status_info.setText(""))
                    return
                
                # Create and show the privacy score dialog
                self.show_privacy_score_dialog(privacy_data, current_url)
            
            # Execute JavaScript to get privacy data
            page.runJavaScript(js_code, process_privacy_data)
            
        except Exception as e:
            self.main_window.status_info.setText(f"❌ Privacy analysis error: {str(e)}")
            QTimer.singleShot(3000, lambda: self.main_window.status_info.setText(""))
    
    def show_privacy_score_dialog(self, privacy_data, page_url):
        """Show dialog with privacy score analysis results"""
        from PyQt5.QtWidgets import (QDialog, QVBoxLayout, QHBoxLayout, QLabel, 
                                   QTextEdit, QPushButton, QTabWidget, QWidget,
                                   QTreeWidget, QTreeWidgetItem, QHeaderView, 
                                   QProgressBar, QFileDialog, QSplitter, QFrame)
        from PyQt5.QtCore import Qt
        from PyQt5.QtGui import QFont
        from datetime import datetime
        import json
        
        # Calculate privacy score
        score, issues, recommendations = self.calculate_privacy_score(privacy_data)
        
        # Create dialog
        dialog = QDialog(self.main_window)
        dialog.setWindowTitle(f"🔒 Privacy Score: {score}/100 - {page_url}")
        dialog.setMinimumSize(800, 600)
        dialog.resize(1000, 700)
        
        layout = QVBoxLayout(dialog)
        
        # Header with score
        header_frame = QFrame()
        header_frame.setStyleSheet("background-color: #f0f8ff; border: 1px solid #d0d0d0; border-radius: 8px; padding: 15px;")
        header_layout = QVBoxLayout(header_frame)
        
        # Score display
        score_label = QLabel(f"🔒 Privacy Score: {score}/100")
        score_font = QFont()
        score_font.setPointSize(18)
        score_font.setBold(True)
        score_label.setFont(score_font)
        
        # Color code the score
        if score >= 80:
            score_label.setStyleSheet("color: #28a745;")  # Green
            score_text = "Excellent Privacy"
        elif score >= 60:
            score_label.setStyleSheet("color: #ffc107;")  # Yellow
            score_text = "Good Privacy"
        elif score >= 40:
            score_label.setStyleSheet("color: #fd7e14;")  # Orange
            score_text = "Fair Privacy"
        else:
            score_label.setStyleSheet("color: #dc3545;")  # Red
            score_text = "Poor Privacy"
        
        header_layout.addWidget(score_label)
        
        score_desc = QLabel(f"📊 {score_text} - {len(issues)} privacy issues found")
        score_desc.setStyleSheet("font-size: 14px; color: #666;")
        header_layout.addWidget(score_desc)
        
        layout.addWidget(header_frame)
        
        # Tab widget for different categories
        tab_widget = QTabWidget()
        layout.addWidget(tab_widget)
        
        # Issues Tab
        issues_widget = QWidget()
        issues_layout = QVBoxLayout(issues_widget)
        
        issues_label = QLabel(f"⚠️ Privacy Issues ({len(issues)})")
        issues_label.setStyleSheet("font-weight: bold; color: #dc3545; font-size: 14px;")
        issues_layout.addWidget(issues_label)
        
        issues_text = QTextEdit()
        issues_text.setReadOnly(True)
        if issues:
            issues_content = "\n".join([f"• {issue}" for issue in issues])
        else:
            issues_content = "✅ No significant privacy issues detected!"
        issues_text.setPlainText(issues_content)
        issues_layout.addWidget(issues_text)
        
        tab_widget.addTab(issues_widget, f"Issues ({len(issues)})")
        
        # Recommendations Tab
        recommendations_widget = QWidget()
        recommendations_layout = QVBoxLayout(recommendations_widget)
        
        rec_label = QLabel(f"💡 Recommendations ({len(recommendations)})")
        rec_label.setStyleSheet("font-weight: bold; color: #0066cc; font-size: 14px;")
        recommendations_layout.addWidget(rec_label)
        
        rec_text = QTextEdit()
        rec_text.setReadOnly(True)
        if recommendations:
            rec_content = "\n".join([f"• {rec}" for rec in recommendations])
        else:
            rec_content = "✅ No additional recommendations - your privacy looks good!"
        rec_text.setPlainText(rec_content)
        recommendations_layout.addWidget(rec_text)
        
        tab_widget.addTab(recommendations_widget, f"Recommendations ({len(recommendations)})")
        
        # Details Tab
        details_widget = QWidget()
        details_layout = QVBoxLayout(details_widget)
        
        details_label = QLabel("📋 Detailed Analysis")
        details_label.setStyleSheet("font-weight: bold; color: #333; font-size: 14px;")
        details_layout.addWidget(details_label)
        
        details_text = QTextEdit()
        details_text.setReadOnly(True)
        details_content = self.format_privacy_details(privacy_data)
        details_text.setPlainText(details_content)
        details_layout.addWidget(details_text)
        
        tab_widget.addTab(details_widget, "Details")
        
        # Buttons
        button_layout = QHBoxLayout()
        
        # Export button
        export_btn = QPushButton("💾 Export Report")
        export_btn.clicked.connect(lambda: self.export_privacy_report(privacy_data, score, issues, recommendations, page_url))
        button_layout.addWidget(export_btn)
        
        button_layout.addStretch()
        
        # Close button
        close_btn = QPushButton("❌ Close")
        close_btn.clicked.connect(dialog.close)
        button_layout.addWidget(close_btn)
        
        layout.addLayout(button_layout)
        
        # Update status
        self.main_window.status_info.setText(f"🔒 Privacy Score: {score}/100 ({score_text})")
        QTimer.singleShot(5000, lambda: self.main_window.status_info.setText(""))
        
        # Show dialog
        dialog.exec_()
    
    def calculate_privacy_score(self, privacy_data):
        """Calculate privacy score based on various factors"""
        score = 100
        issues = []
        recommendations = []
        
        # Check HTTPS
        security = privacy_data.get('security', {})
        if not security.get('isHttps', False):
            score -= 20
            issues.append("Website is not using HTTPS encryption")
            recommendations.append("Use HTTPS to encrypt data transmission")
        
        # Check cookies
        cookies = privacy_data.get('cookies', [])
        if len(cookies) > 10:
            score -= 10
            issues.append(f"High number of cookies ({len(cookies)}) may indicate excessive tracking")
            recommendations.append("Review and limit cookie usage")
        
        # Check for insecure cookies
        insecure_cookies = [c for c in cookies if not c.get('hasSecure', False)]
        if insecure_cookies and security.get('isHttps', False):
            score -= 5
            issues.append(f"{len(insecure_cookies)} cookies lack Secure flag on HTTPS site")
            recommendations.append("Set Secure flag on all cookies for HTTPS sites")
        
        # Check local storage usage
        localStorage = privacy_data.get('localStorage', {})
        if localStorage.get('totalSize', 0) > 50000:  # 50KB
            score -= 5
            issues.append("Large amount of data stored in browser local storage")
            recommendations.append("Minimize local storage usage and clear unnecessary data")
        
        # Check for trackers
        trackers = privacy_data.get('trackers', [])
        if len(trackers) > 0:
            score -= min(len(trackers) * 5, 25)  # Max 25 points deduction
            issues.append(f"Detected {len(trackers)} tracking scripts")
            recommendations.append("Consider blocking tracking scripts or using privacy-focused alternatives")
        
        # Check third-party requests
        third_party = privacy_data.get('thirdPartyRequests', [])
        if len(third_party) > 5:
            score -= min(len(third_party) * 2, 15)  # Max 15 points deduction
            issues.append(f"High number of third-party requests ({len(third_party)})")
            recommendations.append("Minimize third-party content to reduce data sharing")
        
        # Check forms for sensitive data
        forms = privacy_data.get('forms', [])
        insecure_forms = [f for f in forms if f.get('sensitiveFields') and not f.get('isHttps', True)]
        if insecure_forms:
            score -= 15
            issues.append("Sensitive form data transmitted over insecure connection")
            recommendations.append("Ensure all forms with sensitive data use HTTPS")
        
        # Check fingerprinting potential
        fingerprinting = privacy_data.get('fingerprinting', {})
        fingerprint_methods = sum([1 for method, detected in fingerprinting.items() if detected])
        if fingerprint_methods > 4:
            score -= 10
            issues.append(f"High fingerprinting potential ({fingerprint_methods} methods available)")
            recommendations.append("Consider using browser extensions to limit fingerprinting")
        
        # Check Content Security Policy
        if not security.get('hasCSP', False):
            score -= 5
            issues.append("No Content Security Policy detected")
            recommendations.append("Implement Content Security Policy to prevent XSS attacks")
        
        # Ensure score doesn't go below 0
        score = max(score, 0)
        
        return score, issues, recommendations
    
    def format_privacy_details(self, privacy_data):
        """Format privacy data for detailed view"""
        details = []
        
        # Security details
        security = privacy_data.get('security', {})
        details.append("🔐 SECURITY ANALYSIS:")
        details.append(f"  • HTTPS: {'✅ Yes' if security.get('isHttps') else '❌ No'}")
        details.append(f"  • Content Security Policy: {'✅ Yes' if security.get('hasCSP') else '❌ No'}")
        details.append(f"  • Referrer Policy: {security.get('referrerPolicy', 'default')}")
        details.append("")
        
        # Cookies details
        cookies = privacy_data.get('cookies', [])
        details.append(f"🍪 COOKIES ({len(cookies)}):")
        if cookies:
            for cookie in cookies[:5]:  # Show first 5 cookies
                secure = "🔒" if cookie.get('hasSecure') else "🔓"
                details.append(f"  • {cookie.get('name', 'unnamed')} {secure} ({cookie.get('length', 0)} chars)")
            if len(cookies) > 5:
                details.append(f"  • ... and {len(cookies) - 5} more cookies")
        else:
            details.append("  • No cookies found")
        details.append("")
        
        # Storage details
        localStorage = privacy_data.get('localStorage', {})
        sessionStorage = privacy_data.get('sessionStorage', {})
        details.append("💾 BROWSER STORAGE:")
        details.append(f"  • Local Storage: {localStorage.get('itemCount', 0)} items ({localStorage.get('totalSize', 0)} bytes)")
        details.append(f"  • Session Storage: {sessionStorage.get('itemCount', 0)} items ({sessionStorage.get('totalSize', 0)} bytes)")
        details.append("")
        
        # Trackers details
        trackers = privacy_data.get('trackers', [])
        details.append(f"📊 TRACKING SCRIPTS ({len(trackers)}):")
        if trackers:
            for tracker in trackers:
                details.append(f"  • {tracker.get('domain', 'unknown')} ({tracker.get('type', 'unknown')})")
        else:
            details.append("  • No known tracking scripts detected")
        details.append("")
        
        # Third-party requests
        third_party = privacy_data.get('thirdPartyRequests', [])
        details.append(f"🌐 THIRD-PARTY REQUESTS ({len(third_party)}):")
        if third_party:
            # Group by domain
            domains = {}
            for req in third_party:
                domain = req.get('domain', 'unknown')
                if domain not in domains:
                    domains[domain] = []
                domains[domain].append(req.get('type', 'unknown'))
            
            for domain, types in list(domains.items())[:10]:  # Show first 10 domains
                type_counts = {}
                for t in types:
                    type_counts[t] = type_counts.get(t, 0) + 1
                type_str = ", ".join([f"{count} {type}" for type, count in type_counts.items()])
                details.append(f"  • {domain}: {type_str}")
            
            if len(domains) > 10:
                details.append(f"  • ... and {len(domains) - 10} more domains")
        else:
            details.append("  • No third-party requests detected")
        details.append("")
        
        # Forms details
        forms = privacy_data.get('forms', [])
        details.append(f"📝 FORMS ({len(forms)}):")
        if forms:
            for i, form in enumerate(forms):
                secure = "🔒" if form.get('isHttps') else "🔓"
                sensitive_count = len(form.get('sensitiveFields', []))
                details.append(f"  • Form {i+1}: {form.get('method', 'GET').upper()} {secure} ({sensitive_count} sensitive fields)")
        else:
            details.append("  • No forms found")
        details.append("")
        
        # Fingerprinting details
        fingerprinting = privacy_data.get('fingerprinting', {})
        details.append("🔍 FINGERPRINTING POTENTIAL:")
        for method, detected in fingerprinting.items():
            status = "✅ Possible" if detected else "❌ Not detected"
            method_name = method.replace('Fingerprinting', '').replace('fingerprinting', '').title()
            details.append(f"  • {method_name}: {status}")
        
        return "\n".join(details)
    
    def export_privacy_report(self, privacy_data, score, issues, recommendations, page_url):
        """Export privacy analysis report to file"""
        try:
            from PyQt5.QtWidgets import QFileDialog
            from datetime import datetime
            import json
            
            # Generate filename
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            domain = page_url.split('/')[2] if '://' in page_url else 'unknown'
            filename = f"privacy_report_{domain}_{timestamp}.json"
            
            # Show save dialog
            file_path, _ = QFileDialog.getSaveFileName(
                self.main_window,
                "Export Privacy Report",
                filename,
                "JSON Files (*.json);;Text Files (*.txt);;All Files (*.*)"
            )
            
            if file_path:
                report = {
                    'url': page_url,
                    'timestamp': datetime.now().isoformat(),
                    'privacy_score': score,
                    'issues': issues,
                    'recommendations': recommendations,
                    'raw_data': privacy_data
                }
                
                if file_path.endswith('.txt'):
                    # Export as readable text
                    with open(file_path, 'w', encoding='utf-8') as f:
                        f.write(f"Privacy Analysis Report\n")
                        f.write(f"{'=' * 50}\n\n")
                        f.write(f"URL: {page_url}\n")
                        f.write(f"Date: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
                        f.write(f"Privacy Score: {score}/100\n\n")
                        
                        f.write(f"Issues ({len(issues)}):\n")
                        for issue in issues:
                            f.write(f"  • {issue}\n")
                        f.write("\n")
                        
                        f.write(f"Recommendations ({len(recommendations)}):\n")
                        for rec in recommendations:
                            f.write(f"  • {rec}\n")
                        f.write("\n")
                        
                        f.write("Detailed Analysis:\n")
                        f.write(self.format_privacy_details(privacy_data))
                else:
                    # Export as JSON
                    with open(file_path, 'w', encoding='utf-8') as f:
                        json.dump(report, f, indent=2, ensure_ascii=False)
                
                self.main_window.status_info.setText(f"📄 Privacy report exported: {file_path}")
                QTimer.singleShot(3000, lambda: self.main_window.status_info.setText(""))
                
        except Exception as e:
            self.main_window.status_info.setText(f"❌ Export error: {str(e)}")
            QTimer.singleShot(3000, lambda: self.main_window.status_info.setText(""))
    
    def analyze_security_score(self, browser):
        """Analyze security score of the current website"""
        try:
            page = browser.page()
            current_url = browser.url().toString()
            
            # Show initial status
            self.main_window.status_info.setText("🛡️ Analyzing security score...")
            
            # JavaScript to collect security-related information
            js_code = """
            (function() {
                var security = {
                    connection: {},
                    headers: {},
                    certificates: {},
                    vulnerabilities: [],
                    forms: [],
                    scripts: [],
                    resources: [],
                    csp: {},
                    mixedContent: [],
                    permissions: {}
                };
                
                // Connection security
                security.connection = {
                    protocol: window.location.protocol,
                    isHttps: window.location.protocol === 'https:',
                    port: window.location.port || (window.location.protocol === 'https:' ? '443' : '80'),
                    hostname: window.location.hostname
                };
                
                // Check for mixed content
                var allResources = [];
                
                // Check images
                var images = document.images;
                for (var i = 0; i < images.length; i++) {
                    var src = images[i].src;
                    if (src && src.startsWith('http://') && window.location.protocol === 'https:') {
                        security.mixedContent.push({
                            type: 'image',
                            url: src,
                            element: 'img'
                        });
                    }
                    if (src) allResources.push({ type: 'image', url: src });
                }
                
                // Check scripts
                var scripts = document.scripts;
                for (var i = 0; i < scripts.length; i++) {
                    var src = scripts[i].src;
                    if (src) {
                        if (src.startsWith('http://') && window.location.protocol === 'https:') {
                            security.mixedContent.push({
                                type: 'script',
                                url: src,
                                element: 'script',
                                severity: 'high'
                            });
                        }
                        allResources.push({ type: 'script', url: src });
                        
                        // Check for potentially dangerous script patterns
                        if (src.includes('eval') || src.includes('innerHTML') || src.includes('document.write')) {
                            security.vulnerabilities.push({
                                type: 'dangerous_script_pattern',
                                description: 'Script URL contains potentially dangerous patterns',
                                url: src,
                                severity: 'medium'
                            });
                        }
                    } else {
                        // Inline script - check content
                        var content = scripts[i].textContent || scripts[i].innerHTML;
                        if (content) {
                            // Check for dangerous patterns in inline scripts
                            if (content.includes('eval(') || content.includes('innerHTML') || 
                                content.includes('document.write') || content.includes('setTimeout(') ||
                                content.includes('setInterval(')) {
                                security.vulnerabilities.push({
                                    type: 'dangerous_inline_script',
                                    description: 'Inline script contains potentially dangerous functions',
                                    severity: 'medium',
                                    patterns: []
                                });
                            }
                            
                            // Check for hardcoded credentials or API keys
                            var credentialPatterns = [
                                /password\\s*[:=]\\s*['""][^'""]+['""]|/gi,
                                /api[_-]?key\\s*[:=]\\s*['""][^'""]+['""]|/gi,
                                /secret\\s*[:=]\\s*['""][^'""]+['""]|/gi,
                                /token\\s*[:=]\\s*['""][^'""]+['""]|/gi
                            ];
                            
                            for (var p = 0; p < credentialPatterns.length; p++) {
                                if (credentialPatterns[p].test(content)) {
                                    security.vulnerabilities.push({
                                        type: 'hardcoded_credentials',
                                        description: 'Potential hardcoded credentials found in script',
                                        severity: 'high'
                                    });
                                    break;
                                }
                            }
                        }
                    }
                }
                
                // Check stylesheets for mixed content
                var stylesheets = document.styleSheets;
                for (var i = 0; i < stylesheets.length; i++) {
                    try {
                        var href = stylesheets[i].href;
                        if (href && href.startsWith('http://') && window.location.protocol === 'https:') {
                            security.mixedContent.push({
                                type: 'stylesheet',
                                url: href,
                                element: 'link'
                            });
                        }
                        if (href) allResources.push({ type: 'stylesheet', url: href });
                    } catch(e) {
                        // Cross-origin stylesheet, skip
                    }
                }
                
                // Check iframes
                var iframes = document.querySelectorAll('iframe');
                for (var i = 0; i < iframes.length; i++) {
                    var src = iframes[i].src;
                    if (src) {
                        if (src.startsWith('http://') && window.location.protocol === 'https:') {
                            security.mixedContent.push({
                                type: 'iframe',
                                url: src,
                                element: 'iframe',
                                severity: 'high'
                            });
                        }
                        allResources.push({ type: 'iframe', url: src });
                        
                        // Check for potentially unsafe iframe sources
                        if (src.includes('javascript:') || src.includes('data:')) {
                            security.vulnerabilities.push({
                                type: 'unsafe_iframe',
                                description: 'Iframe with potentially unsafe source',
                                url: src,
                                severity: 'medium'
                            });
                        }
                    }
                }
                
                security.resources = allResources;
                
                // Analyze forms for security issues
                var forms = document.forms;
                for (var i = 0; i < forms.length; i++) {
                    var form = forms[i];
                    var formData = {
                        action: form.action || window.location.href,
                        method: form.method || 'GET',
                        isHttps: (form.action || window.location.href).startsWith('https://'),
                        hasAutoComplete: form.autocomplete !== 'off',
                        inputs: [],
                        vulnerabilities: []
                    };
                    
                    // Check form action security
                    if (!formData.isHttps && window.location.protocol === 'https:') {
                        formData.vulnerabilities.push({
                            type: 'insecure_form_action',
                            description: 'Form submits to insecure HTTP endpoint from HTTPS page',
                            severity: 'high'
                        });
                    }
                    
                    // Analyze form inputs
                    var inputs = form.querySelectorAll('input, textarea, select');
                    for (var j = 0; j < inputs.length; j++) {
                        var input = inputs[j];
                        var inputData = {
                            type: input.type || 'text',
                            name: input.name || '',
                            id: input.id || '',
                            hasAutoComplete: input.autocomplete !== 'off',
                            isSensitive: false
                        };
                        
                        // Check for sensitive input types
                        var sensitiveTypes = ['password', 'email', 'tel', 'credit-card', 'cc-number'];
                        var sensitiveName = input.name && (
                            input.name.toLowerCase().includes('password') ||
                            input.name.toLowerCase().includes('email') ||
                            input.name.toLowerCase().includes('phone') ||
                            input.name.toLowerCase().includes('credit') ||
                            input.name.toLowerCase().includes('card') ||
                            input.name.toLowerCase().includes('ssn')
                        );
                        
                        if (sensitiveTypes.includes(input.type) || sensitiveName) {
                            inputData.isSensitive = true;
                            
                            // Check if sensitive input lacks proper security
                            if (input.autocomplete !== 'off' && input.type === 'password') {
                                formData.vulnerabilities.push({
                                    type: 'password_autocomplete',
                                    description: 'Password field allows autocomplete',
                                    severity: 'low'
                                });
                            }
                        }
                        
                        formData.inputs.push(inputData);
                    }
                    
                    security.forms.push(formData);
                }
                
                // Check for Content Security Policy
                var cspMeta = document.querySelector('meta[http-equiv="Content-Security-Policy"]');
                if (cspMeta) {
                    security.csp = {
                        present: true,
                        content: cspMeta.content,
                        directives: cspMeta.content.split(';').map(function(d) { return d.trim(); })
                    };
                } else {
                    security.csp = { present: false };
                }
                
                // Check for X-Frame-Options equivalent
                var frameOptions = document.querySelector('meta[http-equiv="X-Frame-Options"]');
                security.frameOptions = frameOptions ? frameOptions.content : null;
                
                // Check for dangerous global variables or functions
                var dangerousFunctions = ['eval', 'setTimeout', 'setInterval', 'Function'];
                var exposedDangerous = [];
                for (var i = 0; i < dangerousFunctions.length; i++) {
                    if (typeof window[dangerousFunctions[i]] === 'function') {
                        exposedDangerous.push(dangerousFunctions[i]);
                    }
                }
                
                if (exposedDangerous.length > 0) {
                    security.vulnerabilities.push({
                        type: 'exposed_dangerous_functions',
                        description: 'Potentially dangerous functions are accessible: ' + exposedDangerous.join(', '),
                        severity: 'low',
                        functions: exposedDangerous
                    });
                }
                
                // Check for console errors (security-related)
                security.consoleErrors = [];
                
                // Check for outdated libraries (basic detection)
                var libraryChecks = [
                    { name: 'jQuery', check: function() { return typeof window.jQuery !== 'undefined' ? window.jQuery.fn.jquery : null; }},
                    { name: 'Bootstrap', check: function() { return typeof window.bootstrap !== 'undefined' ? 'detected' : null; }},
                    { name: 'Angular', check: function() { return typeof window.angular !== 'undefined' ? window.angular.version.full : null; }}
                ];
                
                security.libraries = [];
                for (var i = 0; i < libraryChecks.length; i++) {
                    var version = libraryChecks[i].check();
                    if (version) {
                        security.libraries.push({
                            name: libraryChecks[i].name,
                            version: version
                        });
                    }
                }
                
                // Check for clickjacking protection
                security.clickjackingProtection = {
                    frameOptions: !!frameOptions,
                    cspFrameAncestors: security.csp.present && security.csp.content.includes('frame-ancestors')
                };
                
                return security;
            })();
            """
            
            def process_security_data(security_data):
                if not security_data:
                    self.main_window.status_info.setText("❌ Could not collect security data")
                    QTimer.singleShot(3000, lambda: self.main_window.status_info.setText(""))
                    return
                
                # Create and show the security score dialog
                self.show_security_score_dialog(security_data, current_url)
            
            # Execute JavaScript to get security data
            page.runJavaScript(js_code, process_security_data)
            
        except Exception as e:
            self.main_window.status_info.setText(f"❌ Security analysis error: {str(e)}")
            QTimer.singleShot(3000, lambda: self.main_window.status_info.setText(""))
    
    def show_security_score_dialog(self, security_data, page_url):
        """Show dialog with security score analysis results"""
        from PyQt5.QtWidgets import (QDialog, QVBoxLayout, QHBoxLayout, QLabel, 
                                   QTextEdit, QPushButton, QTabWidget, QWidget,
                                   QTreeWidget, QTreeWidgetItem, QHeaderView, 
                                   QProgressBar, QFileDialog, QSplitter, QFrame)
        from PyQt5.QtCore import Qt
        from PyQt5.QtGui import QFont
        from datetime import datetime
        import json
        
        # Calculate security score
        score, vulnerabilities, recommendations = self.calculate_security_score(security_data)
        
        # Create dialog
        dialog = QDialog(self.main_window)
        dialog.setWindowTitle(f"🛡️ Security Score: {score}/100 - {page_url}")
        dialog.setMinimumSize(800, 600)
        dialog.resize(1000, 700)
        
        layout = QVBoxLayout(dialog)
        
        # Header with score
        header_frame = QFrame()
        header_frame.setStyleSheet("background-color: #f8f9fa; border: 1px solid #d0d0d0; border-radius: 8px; padding: 15px;")
        header_layout = QVBoxLayout(header_frame)
        
        # Score display
        score_label = QLabel(f"🛡️ Security Score: {score}/100")
        score_font = QFont()
        score_font.setPointSize(18)
        score_font.setBold(True)
        score_label.setFont(score_font)
        
        # Color code the score
        if score >= 80:
            score_label.setStyleSheet("color: #28a745;")  # Green
            score_text = "Excellent Security"
        elif score >= 60:
            score_label.setStyleSheet("color: #ffc107;")  # Yellow
            score_text = "Good Security"
        elif score >= 40:
            score_label.setStyleSheet("color: #fd7e14;")  # Orange
            score_text = "Fair Security"
        else:
            score_label.setStyleSheet("color: #dc3545;")  # Red
            score_text = "Poor Security"
        
        header_layout.addWidget(score_label)
        
        score_desc = QLabel(f"🔍 {score_text} - {len(vulnerabilities)} security issues found")
        score_desc.setStyleSheet("font-size: 14px; color: #666;")
        header_layout.addWidget(score_desc)
        
        layout.addWidget(header_frame)
        
        # Tab widget for different categories
        tab_widget = QTabWidget()
        layout.addWidget(tab_widget)
        
        # Vulnerabilities Tab
        vuln_widget = QWidget()
        vuln_layout = QVBoxLayout(vuln_widget)
        
        vuln_label = QLabel(f"⚠️ Security Vulnerabilities ({len(vulnerabilities)})")
        vuln_label.setStyleSheet("font-weight: bold; color: #dc3545; font-size: 14px;")
        vuln_layout.addWidget(vuln_label)
        
        vuln_text = QTextEdit()
        vuln_text.setReadOnly(True)
        if vulnerabilities:
            vuln_content = "\n".join([f"• {vuln}" for vuln in vulnerabilities])
        else:
            vuln_content = "✅ No significant security vulnerabilities detected!"
        vuln_text.setPlainText(vuln_content)
        vuln_layout.addWidget(vuln_text)
        
        tab_widget.addTab(vuln_widget, f"Vulnerabilities ({len(vulnerabilities)})")
        
        # Recommendations Tab
        recommendations_widget = QWidget()
        recommendations_layout = QVBoxLayout(recommendations_widget)
        
        rec_label = QLabel(f"💡 Security Recommendations ({len(recommendations)})")
        rec_label.setStyleSheet("font-weight: bold; color: #0066cc; font-size: 14px;")
        recommendations_layout.addWidget(rec_label)
        
        rec_text = QTextEdit()
        rec_text.setReadOnly(True)
        if recommendations:
            rec_content = "\n".join([f"• {rec}" for rec in recommendations])
        else:
            rec_content = "✅ No additional security recommendations - your security looks good!"
        rec_text.setPlainText(rec_content)
        recommendations_layout.addWidget(rec_text)
        
        tab_widget.addTab(recommendations_widget, f"Recommendations ({len(recommendations)})")
        
        # Details Tab
        details_widget = QWidget()
        details_layout = QVBoxLayout(details_widget)
        
        details_label = QLabel("📋 Detailed Security Analysis")
        details_label.setStyleSheet("font-weight: bold; color: #333; font-size: 14px;")
        details_layout.addWidget(details_label)
        
        details_text = QTextEdit()
        details_text.setReadOnly(True)
        details_content = self.format_security_details(security_data)
        details_text.setPlainText(details_content)
        details_layout.addWidget(details_text)
        
        tab_widget.addTab(details_widget, "Details")
        
        # Buttons
        button_layout = QHBoxLayout()
        
        # Export button
        export_btn = QPushButton("💾 Export Report")
        export_btn.clicked.connect(lambda: self.export_security_report(security_data, score, vulnerabilities, recommendations, page_url))
        button_layout.addWidget(export_btn)
        
        button_layout.addStretch()
        
        # Close button
        close_btn = QPushButton("❌ Close")
        close_btn.clicked.connect(dialog.close)
        button_layout.addWidget(close_btn)
        
        layout.addLayout(button_layout)
        
        # Update status
        self.main_window.status_info.setText(f"🛡️ Security Score: {score}/100 ({score_text})")
        QTimer.singleShot(5000, lambda: self.main_window.status_info.setText(""))
        
        # Show dialog
        dialog.exec_()
    
    def calculate_security_score(self, security_data):
        """Calculate security score based on various factors"""
        score = 100
        vulnerabilities = []
        recommendations = []
        
        # Check HTTPS
        connection = security_data.get('connection', {})
        if not connection.get('isHttps', False):
            score -= 25
            vulnerabilities.append("Website is not using HTTPS encryption")
            recommendations.append("Implement HTTPS to encrypt all data transmission")
        
        # Check for mixed content
        mixed_content = security_data.get('mixedContent', [])
        if mixed_content:
            high_severity = [mc for mc in mixed_content if mc.get('severity') == 'high']
            if high_severity:
                score -= 20
                vulnerabilities.append(f"High-risk mixed content detected ({len(high_severity)} items)")
                recommendations.append("Fix all mixed content by using HTTPS for all resources")
            else:
                score -= 10
                vulnerabilities.append(f"Mixed content detected ({len(mixed_content)} items)")
                recommendations.append("Update all HTTP resources to use HTTPS")
        
        # Check Content Security Policy
        csp = security_data.get('csp', {})
        if not csp.get('present', False):
            score -= 15
            vulnerabilities.append("No Content Security Policy (CSP) implemented")
            recommendations.append("Implement Content Security Policy to prevent XSS attacks")
        else:
            # Check CSP quality
            csp_content = csp.get('content', '').lower()
            if 'unsafe-inline' in csp_content:
                score -= 5
                vulnerabilities.append("CSP allows unsafe-inline scripts/styles")
                recommendations.append("Remove 'unsafe-inline' from CSP and use nonces or hashes")
            if 'unsafe-eval' in csp_content:
                score -= 5
                vulnerabilities.append("CSP allows unsafe-eval")
                recommendations.append("Remove 'unsafe-eval' from CSP to prevent code injection")
        
        # Check clickjacking protection
        clickjacking = security_data.get('clickjackingProtection', {})
        if not clickjacking.get('frameOptions', False) and not clickjacking.get('cspFrameAncestors', False):
            score -= 10
            vulnerabilities.append("No clickjacking protection detected")
            recommendations.append("Add X-Frame-Options header or CSP frame-ancestors directive")
        
        # Check form security
        forms = security_data.get('forms', [])
        insecure_forms = []
        for form in forms:
            form_vulns = form.get('vulnerabilities', [])
            for vuln in form_vulns:
                if vuln.get('severity') == 'high':
                    insecure_forms.append(vuln)
        
        if insecure_forms:
            score -= 15
            vulnerabilities.append(f"Insecure form submissions detected ({len(insecure_forms)} forms)")
            recommendations.append("Ensure all forms with sensitive data submit to HTTPS endpoints")
        
        # Check for script vulnerabilities
        script_vulns = [v for v in security_data.get('vulnerabilities', []) if 'script' in v.get('type', '')]
        if script_vulns:
            high_script_vulns = [v for v in script_vulns if v.get('severity') == 'high']
            if high_script_vulns:
                score -= 15
                vulnerabilities.append(f"High-risk script vulnerabilities detected ({len(high_script_vulns)} issues)")
                recommendations.append("Review and secure all script code, remove dangerous patterns")
            else:
                score -= 8
                vulnerabilities.append(f"Script security issues detected ({len(script_vulns)} issues)")
                recommendations.append("Review script code for potential security improvements")
        
        # Check for hardcoded credentials
        cred_vulns = [v for v in security_data.get('vulnerabilities', []) if v.get('type') == 'hardcoded_credentials']
        if cred_vulns:
            score -= 20
            vulnerabilities.append("Hardcoded credentials or API keys detected in scripts")
            recommendations.append("Remove all hardcoded credentials and use secure configuration")
        
        # Check for unsafe iframes
        iframe_vulns = [v for v in security_data.get('vulnerabilities', []) if v.get('type') == 'unsafe_iframe']
        if iframe_vulns:
            score -= 10
            vulnerabilities.append(f"Unsafe iframe sources detected ({len(iframe_vulns)} iframes)")
            recommendations.append("Review iframe sources and avoid javascript: or data: URLs")
        
        # Check for exposed dangerous functions
        dangerous_funcs = [v for v in security_data.get('vulnerabilities', []) if v.get('type') == 'exposed_dangerous_functions']
        if dangerous_funcs:
            score -= 5
            vulnerabilities.append("Potentially dangerous JavaScript functions are accessible")
            recommendations.append("Consider restricting access to eval() and similar functions")
        
        # Check for outdated libraries
        libraries = security_data.get('libraries', [])
        if libraries:
            # This is a basic check - in a real implementation, you'd check against known vulnerable versions
            for lib in libraries:
                if lib.get('name') == 'jQuery' and lib.get('version'):
                    version = lib.get('version')
                    # Basic version check for demonstration
                    if version.startswith('1.') or version.startswith('2.'):
                        score -= 8
                        vulnerabilities.append(f"Outdated {lib.get('name')} version ({version}) may have security vulnerabilities")
                        recommendations.append(f"Update {lib.get('name')} to the latest secure version")
        
        # Check resource security
        resources = security_data.get('resources', [])
        external_resources = [r for r in resources if not self.is_same_origin(r.get('url', ''), security_data.get('connection', {}).get('hostname', ''))]
        if len(external_resources) > 10:
            score -= 5
            vulnerabilities.append(f"High number of external resources ({len(external_resources)}) increases attack surface")
            recommendations.append("Minimize external dependencies and use Subresource Integrity (SRI)")
        
        # Ensure score doesn't go below 0
        score = max(score, 0)
        
        return score, vulnerabilities, recommendations
    
    def is_same_origin(self, url, hostname):
        """Check if URL is from the same origin"""
        try:
            if not url or not hostname:
                return False
            if url.startswith('//'):
                return hostname in url
            if url.startswith('/'):
                return True
            if url.startswith('http'):
                return hostname in url
            return True  # Relative URLs are same origin
        except:
            return False
    
    def format_security_details(self, security_data):
        """Format security data for detailed view"""
        details = []
        
        # Connection details
        connection = security_data.get('connection', {})
        details.append("🔐 CONNECTION SECURITY:")
        details.append(f"  • Protocol: {connection.get('protocol', 'unknown')}")
        details.append(f"  • HTTPS: {'✅ Yes' if connection.get('isHttps') else '❌ No'}")
        details.append(f"  • Port: {connection.get('port', 'unknown')}")
        details.append(f"  • Hostname: {connection.get('hostname', 'unknown')}")
        details.append("")
        
        # Mixed content details
        mixed_content = security_data.get('mixedContent', [])
        details.append(f"⚠️ MIXED CONTENT ({len(mixed_content)}):")
        if mixed_content:
            for mc in mixed_content[:5]:  # Show first 5
                severity = f" ({mc.get('severity', 'medium')} risk)" if mc.get('severity') else ""
                details.append(f"  • {mc.get('type', 'unknown')}: {mc.get('url', 'unknown')}{severity}")
            if len(mixed_content) > 5:
                details.append(f"  • ... and {len(mixed_content) - 5} more mixed content items")
        else:
            details.append("  • No mixed content detected")
        details.append("")
        
        # CSP details
        csp = security_data.get('csp', {})
        details.append("🛡️ CONTENT SECURITY POLICY:")
        if csp.get('present'):
            details.append("  • Status: ✅ Present")
            directives = csp.get('directives', [])
            details.append(f"  • Directives: {len(directives)}")
            for directive in directives[:3]:  # Show first 3 directives
                details.append(f"    - {directive}")
            if len(directives) > 3:
                details.append(f"    - ... and {len(directives) - 3} more directives")
        else:
            details.append("  • Status: ❌ Not implemented")
        details.append("")
        
        # Form security details
        forms = security_data.get('forms', [])
        details.append(f"📝 FORM SECURITY ({len(forms)}):")
        if forms:
            for i, form in enumerate(forms):
                secure = "🔒" if form.get('isHttps') else "🔓"
                method = form.get('method', 'GET').upper()
                vuln_count = len(form.get('vulnerabilities', []))
                sensitive_count = sum(1 for inp in form.get('inputs', []) if inp.get('isSensitive'))
                details.append(f"  • Form {i+1}: {method} {secure} ({sensitive_count} sensitive fields, {vuln_count} issues)")
        else:
            details.append("  • No forms found")
        details.append("")
        
        # Vulnerabilities details
        vulnerabilities = security_data.get('vulnerabilities', [])
        details.append(f"🚨 DETECTED VULNERABILITIES ({len(vulnerabilities)}):")
        if vulnerabilities:
            vuln_types = {}
            for vuln in vulnerabilities:
                vuln_type = vuln.get('type', 'unknown')
                severity = vuln.get('severity', 'unknown')
                if vuln_type not in vuln_types:
                    vuln_types[vuln_type] = []
                vuln_types[vuln_type].append(severity)
            
            for vuln_type, severities in vuln_types.items():
                severity_counts = {}
                for s in severities:
                    severity_counts[s] = severity_counts.get(s, 0) + 1
                severity_str = ", ".join([f"{count} {sev}" for sev, count in severity_counts.items()])
                details.append(f"  • {vuln_type.replace('_', ' ').title()}: {severity_str}")
        else:
            details.append("  • No vulnerabilities detected")
        details.append("")
        
        # Libraries details
        libraries = security_data.get('libraries', [])
        details.append(f"📚 DETECTED LIBRARIES ({len(libraries)}):")
        if libraries:
            for lib in libraries:
                details.append(f"  • {lib.get('name', 'unknown')}: {lib.get('version', 'unknown version')}")
        else:
            details.append("  • No JavaScript libraries detected")
        details.append("")
        
        # Resources summary
        resources = security_data.get('resources', [])
        if resources:
            resource_types = {}
            for resource in resources:
                res_type = resource.get('type', 'unknown')
                resource_types[res_type] = resource_types.get(res_type, 0) + 1
            
            details.append(f"🌐 RESOURCES SUMMARY ({len(resources)} total):")
            for res_type, count in resource_types.items():
                details.append(f"  • {res_type.title()}: {count}")
        
        return "\n".join(details)
    
    def export_security_report(self, security_data, score, vulnerabilities, recommendations, page_url):
        """Export security analysis report to file"""
        try:
            from PyQt5.QtWidgets import QFileDialog
            from datetime import datetime
            import json
            
            # Generate filename
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            domain = page_url.split('/')[2] if '://' in page_url else 'unknown'
            filename = f"security_report_{domain}_{timestamp}.json"
            
            # Show save dialog
            file_path, _ = QFileDialog.getSaveFileName(
                self.main_window,
                "Export Security Report",
                filename,
                "JSON Files (*.json);;Text Files (*.txt);;All Files (*.*)"
            )
            
            if file_path:
                report = {
                    'url': page_url,
                    'timestamp': datetime.now().isoformat(),
                    'security_score': score,
                    'vulnerabilities': vulnerabilities,
                    'recommendations': recommendations,
                    'raw_data': security_data
                }
                
                if file_path.endswith('.txt'):
                    # Export as readable text
                    with open(file_path, 'w', encoding='utf-8') as f:
                        f.write(f"Security Analysis Report\n")
                        f.write(f"{'=' * 50}\n\n")
                        f.write(f"URL: {page_url}\n")
                        f.write(f"Date: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
                        f.write(f"Security Score: {score}/100\n\n")
                        
                        f.write(f"Vulnerabilities ({len(vulnerabilities)}):\n")
                        for vuln in vulnerabilities:
                            f.write(f"  • {vuln}\n")
                        f.write("\n")
                        
                        f.write(f"Recommendations ({len(recommendations)}):\n")
                        for rec in recommendations:
                            f.write(f"  • {rec}\n")
                        f.write("\n")
                        
                        f.write("Detailed Analysis:\n")
                        f.write(self.format_security_details(security_data))
                else:
                    # Export as JSON
                    with open(file_path, 'w', encoding='utf-8') as f:
                        json.dump(report, f, indent=2, ensure_ascii=False)
                
                self.main_window.status_info.setText(f"📄 Security report exported: {file_path}")
                QTimer.singleShot(3000, lambda: self.main_window.status_info.setText(""))
                
        except Exception as e:
            self.main_window.status_info.setText(f"❌ Export error: {str(e)}")
            QTimer.singleShot(3000, lambda: self.main_window.status_info.setText(""))
    
    def show_header_policy_simulator(self, browser):
        """Show Header Policy Simulator dialog"""
        try:
            from header_policy_simulator import show_header_policy_simulator
            
            # Show status
            self.main_window.status_info.setText("🛡️ Opening Header Policy Simulator...")
            
            # Show the simulator dialog
            dialog = show_header_policy_simulator(browser, self.main_window)
            
            # Update status
            QTimer.singleShot(1000, lambda: self.main_window.status_info.setText("🛡️ Header Policy Simulator opened"))
            QTimer.singleShot(3000, lambda: self.main_window.status_info.setText(""))
            
        except Exception as e:
            self.main_window.status_info.setText(f"❌ Failed to open Header Policy Simulator: {str(e)}")
            QTimer.singleShot(3000, lambda: self.main_window.status_info.setText(""))
    
    def show_network_timeline(self, browser):
        """Show network request timeline with waterfall visualization"""
        try:
            page = browser.page()
            current_url = browser.url().toString()
            
            # Show initial status
            self.main_window.status_info.setText("📊 Loading Network Request Timeline...")
            
            # Create and show the network timeline dialog
            self.create_network_timeline_dialog(browser, current_url)
            
        except Exception as e:
            # Show error in a message box for debugging
            from PyQt5.QtWidgets import QMessageBox
            QMessageBox.critical(self.main_window, "Network Timeline Error", f"Error: {str(e)}")
            self.main_window.status_info.setText(f"❌ Network timeline error: {str(e)}")
            QTimer.singleShot(3000, lambda: self.main_window.status_info.setText(""))
    
    def create_network_timeline_dialog(self, browser, page_url):
        """Create network timeline dialog with real-time waterfall visualization"""
        from PyQt5.QtWidgets import (QDialog, QVBoxLayout, QHBoxLayout, QLabel, 
                                   QPushButton, QTabWidget, QWidget, QTreeWidget, 
                                   QTreeWidgetItem, QHeaderView, QSplitter, QFrame,
                                   QScrollArea, QProgressBar, QComboBox, QCheckBox,
                                   QSpinBox, QGroupBox, QTextEdit)
        from PyQt5.QtCore import Qt, QTimer, pyqtSignal, QThread, QObject
        from PyQt5.QtGui import QFont, QPainter, QPen, QBrush, QColor, QPixmap
        from datetime import datetime
        import json
        
        try:
            # Create dialog
            dialog = QDialog(self.main_window)
            dialog.setWindowTitle(f"📊 Network Request Timeline - {page_url}")
            dialog.setMinimumSize(1200, 800)
            dialog.resize(1400, 900)
            
            layout = QVBoxLayout(dialog)
            
            # Header with controls
            header_frame = QFrame()
            header_frame.setStyleSheet("background-color: #f8f9fa; border: 1px solid #d0d0d0; border-radius: 8px; padding: 10px;")
            header_layout = QHBoxLayout(header_frame)
            
            # Title
            title_label = QLabel("📊 Network Request Timeline")
            title_font = QFont()
            title_font.setPointSize(16)
            title_font.setBold(True)
            title_label.setFont(title_font)
            header_layout.addWidget(title_label)
            
            header_layout.addStretch()
            
            # Controls
            self.timeline_recording = False
            self.timeline_requests = []
            
            # Record button
            self.record_btn = QPushButton("🔴 Start Recording")
            self.record_btn.setStyleSheet("""
                QPushButton {
                    background-color: #dc3545;
                    color: white;
                    border: none;
                    border-radius: 6px;
                    font-weight: bold;
                    padding: 8px 16px;
                }
                QPushButton:hover {
                    background-color: #c82333;
                }
            """)
            self.record_btn.clicked.connect(lambda: self.toggle_timeline_recording(browser, dialog))
            header_layout.addWidget(self.record_btn)
            
            # Clear button
            clear_btn = QPushButton("🗑️ Clear")
            clear_btn.setStyleSheet("""
                QPushButton {
                    background-color: #6c757d;
                    color: white;
                    border: none;
                    border-radius: 6px;
                    font-weight: bold;
                    padding: 8px 16px;
                }
                QPushButton:hover {
                    background-color: #5a6268;
                }
            """)
            clear_btn.clicked.connect(lambda: self.clear_timeline_data(dialog))
            header_layout.addWidget(clear_btn)
            
            # Export button
            export_btn = QPushButton("💾 Export")
            export_btn.clicked.connect(lambda: self.export_timeline_data())
            header_layout.addWidget(export_btn)
            
            layout.addWidget(header_frame)
            
            # Main content area
            main_splitter = QSplitter(Qt.Vertical)
            layout.addWidget(main_splitter)
            
            # Timeline visualization area
            timeline_frame = QFrame()
            timeline_frame.setStyleSheet("border: 1px solid #d0d0d0; border-radius: 4px;")
            timeline_layout = QVBoxLayout(timeline_frame)
            
            # Timeline header
            timeline_header = QLabel("🌊 Waterfall Chart")
            timeline_header.setStyleSheet("font-weight: bold; font-size: 14px; padding: 5px;")
            timeline_layout.addWidget(timeline_header)
            
            # Scroll area for timeline
            self.timeline_scroll = QScrollArea()
            self.timeline_scroll.setWidgetResizable(True)
            self.timeline_scroll.setMinimumHeight(400)
            
            # Timeline widget
            self.timeline_widget = NetworkTimelineWidget()
            self.timeline_scroll.setWidget(self.timeline_widget)
            timeline_layout.addWidget(self.timeline_scroll)
            
            main_splitter.addWidget(timeline_frame)
            
            # Request details area
            details_frame = QFrame()
            details_frame.setStyleSheet("border: 1px solid #d0d0d0; border-radius: 4px;")
            details_layout = QVBoxLayout(details_frame)
            
            # Details header
            details_header = QLabel("📋 Request Details")
            details_header.setStyleSheet("font-weight: bold; font-size: 14px; padding: 5px;")
            details_layout.addWidget(details_header)
            
            # Request list
            self.request_tree = QTreeWidget()
            self.request_tree.setHeaderLabels(['URL', 'Method', 'Status', 'Type', 'Size', 'Time', 'Timeline'])
            self.request_tree.header().setSectionResizeMode(0, QHeaderView.Stretch)
            self.request_tree.itemClicked.connect(self.on_request_selected)
            details_layout.addWidget(self.request_tree)
            
            main_splitter.addWidget(details_frame)
            
            # Set splitter proportions
            main_splitter.setSizes([500, 300])
            
            # Status and statistics
            stats_frame = QFrame()
            stats_frame.setStyleSheet("background-color: #f8f9fa; border: 1px solid #d0d0d0; border-radius: 4px; padding: 10px;")
            stats_layout = QHBoxLayout(stats_frame)
            
            self.stats_label = QLabel("📊 Ready to record network requests")
            stats_layout.addWidget(self.stats_label)
            
            stats_layout.addStretch()
            
            # Close button
            close_btn = QPushButton("❌ Close")
            close_btn.clicked.connect(dialog.close)
            stats_layout.addWidget(close_btn)
            
            layout.addWidget(stats_frame)
            
            # Store dialog reference and UI elements
            self.timeline_dialog = dialog
            self.timeline_stats_label = self.stats_label  # Store reference to avoid deletion issues
            
            # Update status
            self.main_window.status_info.setText("📊 Network Timeline ready - Click 'Start Recording' to begin")
            QTimer.singleShot(3000, lambda: self.main_window.status_info.setText(""))
            
            # Show dialog
            dialog.show()
            
        except Exception as e:
            from PyQt5.QtWidgets import QMessageBox
            QMessageBox.critical(self.main_window, "Timeline Dialog Error", f"Error creating dialog: {str(e)}")
            raise e
    
    def toggle_timeline_recording(self, browser, dialog):
        """Toggle network request recording"""
        if not self.timeline_recording:
            # Start recording
            self.timeline_recording = True
            self.timeline_requests = []
            self.record_btn.setText("⏹️ Stop Recording")
            self.record_btn.setStyleSheet("""
                QPushButton {
                    background-color: #28a745;
                    color: white;
                    border: none;
                    border-radius: 6px;
                    font-weight: bold;
                    padding: 8px 16px;
                }
                QPushButton:hover {
                    background-color: #218838;
                }
            """)
            self.timeline_stats_label.setText("🔴 Recording network requests...")
            
            # Start monitoring network requests
            self.start_network_monitoring(browser)
            
        else:
            # Stop recording
            self.timeline_recording = False
            self.record_btn.setText("🔴 Start Recording")
            self.record_btn.setStyleSheet("""
                QPushButton {
                    background-color: #dc3545;
                    color: white;
                    border: none;
                    border-radius: 6px;
                    font-weight: bold;
                    padding: 8px 16px;
                }
                QPushButton:hover {
                    background-color: #c82333;
                }
            """)
            self.timeline_stats_label.setText(f"⏹️ Recording stopped - {len(self.timeline_requests)} requests captured")
            
            # Stop monitoring
            self.stop_network_monitoring()
    
    def start_network_monitoring(self, browser):
        """Start monitoring network requests using JavaScript"""
        page = browser.page()
        
        # JavaScript to monitor network requests
        js_code = """
        (function() {
            if (window.networkMonitor) {
                return; // Already monitoring
            }
            
            window.networkMonitor = {
                requests: [],
                startTime: performance.now(),
                observer: null
            };
            
            // Override fetch
            const originalFetch = window.fetch;
            window.fetch = function(...args) {
                const startTime = performance.now();
                const url = args[0];
                const options = args[1] || {};
                
                const requestData = {
                    id: Math.random().toString(36).substr(2, 9),
                    url: url,
                    method: options.method || 'GET',
                    startTime: startTime,
                    type: 'fetch'
                };
                
                window.networkMonitor.requests.push(requestData);
                
                return originalFetch.apply(this, args).then(response => {
                    requestData.endTime = performance.now();
                    requestData.status = response.status;
                    requestData.statusText = response.statusText;
                    requestData.size = response.headers.get('content-length') || 0;
                    requestData.contentType = response.headers.get('content-type') || 'unknown';
                    return response;
                }).catch(error => {
                    requestData.endTime = performance.now();
                    requestData.error = error.message;
                    throw error;
                });
            };
            
            // Override XMLHttpRequest
            const originalXHROpen = XMLHttpRequest.prototype.open;
            const originalXHRSend = XMLHttpRequest.prototype.send;
            
            XMLHttpRequest.prototype.open = function(method, url, async, user, password) {
                this._requestData = {
                    id: Math.random().toString(36).substr(2, 9),
                    url: url,
                    method: method,
                    startTime: performance.now(),
                    type: 'xhr'
                };
                return originalXHROpen.apply(this, arguments);
            };
            
            XMLHttpRequest.prototype.send = function(data) {
                if (this._requestData) {
                    window.networkMonitor.requests.push(this._requestData);
                    
                    this.addEventListener('loadend', () => {
                        this._requestData.endTime = performance.now();
                        this._requestData.status = this.status;
                        this._requestData.statusText = this.statusText;
                        this._requestData.size = this.getResponseHeader('content-length') || this.responseText.length || 0;
                        this._requestData.contentType = this.getResponseHeader('content-type') || 'unknown';
                    });
                    
                    this.addEventListener('error', () => {
                        this._requestData.endTime = performance.now();
                        this._requestData.error = 'Network error';
                    });
                }
                return originalXHRSend.apply(this, arguments);
            };
            
            // Monitor resource loading
            if (window.PerformanceObserver) {
                window.networkMonitor.observer = new PerformanceObserver((list) => {
                    for (const entry of list.getEntries()) {
                        if (entry.entryType === 'resource') {
                            const requestData = {
                                id: Math.random().toString(36).substr(2, 9),
                                url: entry.name,
                                method: 'GET',
                                startTime: entry.startTime,
                                endTime: entry.startTime + entry.duration,
                                type: entry.initiatorType || 'resource',
                                size: entry.transferSize || 0,
                                // Timing breakdown
                                timing: {
                                    dns: entry.domainLookupEnd - entry.domainLookupStart,
                                    tcp: entry.connectEnd - entry.connectStart,
                                    tls: entry.secureConnectionStart > 0 ? entry.connectEnd - entry.secureConnectionStart : 0,
                                    request: entry.responseStart - entry.requestStart,
                                    response: entry.responseEnd - entry.responseStart,
                                    total: entry.duration
                                }
                            };
                            window.networkMonitor.requests.push(requestData);
                        }
                    }
                });
                
                window.networkMonitor.observer.observe({entryTypes: ['resource']});
            }
            
            return 'Network monitoring started';
        })();
        """
        
        page.runJavaScript(js_code, lambda result: self.on_monitoring_started(result))
        
        # Start periodic updates
        self.timeline_timer = QTimer()
        self.timeline_timer.timeout.connect(lambda: self.update_timeline_data(browser))
        self.timeline_timer.start(1000)  # Update every second
    
    def on_monitoring_started(self, result):
        """Handle monitoring start result"""
        if result:
            self.main_window.status_info.setText("📊 Network monitoring active")
            QTimer.singleShot(2000, lambda: self.main_window.status_info.setText(""))
    
    def update_timeline_data(self, browser):
        """Update timeline with new network request data"""
        if not self.timeline_recording:
            return
            
        page = browser.page()
        
        # JavaScript to get current network data
        js_code = """
        (function() {
            if (!window.networkMonitor) {
                return [];
            }
            
            const requests = window.networkMonitor.requests.slice();
            // Clear processed requests to avoid duplicates
            window.networkMonitor.requests = [];
            
            return requests;
        })();
        """
        
        page.runJavaScript(js_code, self.process_timeline_update)
    
    def process_timeline_update(self, new_requests):
        """Process new network requests and update timeline"""
        if not new_requests or not self.timeline_recording:
            return
            
        # Add new requests to our collection
        for request in new_requests:
            self.timeline_requests.append(request)
            self.add_request_to_tree(request)
        
        # Update timeline visualization
        self.timeline_widget.update_requests(self.timeline_requests)
        
        # Update statistics
        total_requests = len(self.timeline_requests)
        completed_requests = len([r for r in self.timeline_requests if r.get('endTime')])
        self.timeline_stats_label.setText(f"🔴 Recording: {total_requests} requests ({completed_requests} completed)")
    
    def add_request_to_tree(self, request):
        """Add a request to the tree widget"""
        item = QTreeWidgetItem()
        
        # URL
        url = request.get('url', '')
        if len(url) > 80:
            url = url[:77] + '...'
        item.setText(0, url)
        
        # Method
        item.setText(1, request.get('method', 'GET'))
        
        # Status
        status = request.get('status', '')
        if status:
            status_text = f"{status} {request.get('statusText', '')}"
            if status < 300:
                item.setBackground(2, QColor(212, 237, 218))  # Green
            elif status < 400:
                item.setBackground(2, QColor(255, 243, 205))  # Yellow
            else:
                item.setBackground(2, QColor(248, 215, 218))  # Red
        else:
            status_text = 'Pending...'
            item.setBackground(2, QColor(230, 230, 230))  # Gray
        item.setText(2, str(status_text))
        
        # Type
        item.setText(3, request.get('type', 'unknown'))
        
        # Size
        size = request.get('size', 0)
        if size:
            if size > 1024 * 1024:
                size_text = f"{size / (1024 * 1024):.1f} MB"
            elif size > 1024:
                size_text = f"{size / 1024:.1f} KB"
            else:
                size_text = f"{size} B"
        else:
            size_text = '-'
        item.setText(4, size_text)
        
        # Time
        start_time = request.get('startTime', 0)
        end_time = request.get('endTime', 0)
        if end_time:
            duration = end_time - start_time
            item.setText(5, f"{duration:.0f}ms")
        else:
            item.setText(5, 'Pending...')
        
        # Timeline (visual representation)
        timeline_text = self.create_timeline_text(request)
        item.setText(6, timeline_text)
        
        # Store request data
        item.setData(0, Qt.UserRole, request)
        
        self.request_tree.addTopLevelItem(item)
        
        # Auto-scroll to bottom
        self.request_tree.scrollToBottom()
    
    def create_timeline_text(self, request):
        """Create a simple text-based timeline representation"""
        timing = request.get('timing', {})
        if not timing:
            return '▓▓▓▓▓'
        
        # Create a simple bar representation
        dns = timing.get('dns', 0)
        tcp = timing.get('tcp', 0)
        tls = timing.get('tls', 0)
        req = timing.get('request', 0)
        resp = timing.get('response', 0)
        
        total = dns + tcp + tls + req + resp
        if total == 0:
            return '▓▓▓▓▓'
        
        # Scale to 20 characters
        scale = 20 / max(total, 1)
        
        dns_chars = max(1, int(dns * scale)) if dns > 0 else 0
        tcp_chars = max(1, int(tcp * scale)) if tcp > 0 else 0
        tls_chars = max(1, int(tls * scale)) if tls > 0 else 0
        req_chars = max(1, int(req * scale)) if req > 0 else 0
        resp_chars = max(1, int(resp * scale)) if resp > 0 else 0
        
        timeline = ''
        timeline += '🔍' * dns_chars  # DNS
        timeline += '🔗' * tcp_chars  # TCP
        timeline += '🔒' * tls_chars  # TLS
        timeline += '📤' * req_chars  # Request
        timeline += '📥' * resp_chars  # Response
        
        return timeline[:20]  # Limit to 20 characters
    
    def on_request_selected(self, item, column):
        """Handle request selection in tree"""
        request_data = item.data(0, Qt.UserRole)
        if request_data:
            # Show detailed timing information
            self.show_request_details(request_data)
    
    def show_request_details(self, request_data):
        """Show detailed information about a selected request"""
        # This could open a detailed dialog or update a details panel
        # For now, just update the status
        url = request_data.get('url', 'Unknown')
        method = request_data.get('method', 'GET')
        status = request_data.get('status', 'Pending')
        
        self.main_window.status_info.setText(f"📋 Selected: {method} {url} - Status: {status}")
        QTimer.singleShot(3000, lambda: self.main_window.status_info.setText(""))
    
    def stop_network_monitoring(self):
        """Stop network monitoring"""
        if hasattr(self, 'timeline_timer'):
            self.timeline_timer.stop()
    
    def clear_timeline_data(self, dialog):
        """Clear all timeline data"""
        self.timeline_requests = []
        self.request_tree.clear()
        self.timeline_widget.clear_requests()
        self.timeline_stats_label.setText("📊 Timeline cleared - Ready to record")
    
    def export_timeline_data(self):
        """Export timeline data to file"""
        try:
            from PyQt5.QtWidgets import QFileDialog
            from datetime import datetime
            import json
            
            if not self.timeline_requests:
                self.main_window.status_info.setText("❌ No timeline data to export")
                QTimer.singleShot(3000, lambda: self.main_window.status_info.setText(""))
                return
            
            # Generate filename
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            filename = f"network_timeline_{timestamp}.json"
            
            # Show save dialog
            file_path, _ = QFileDialog.getSaveFileName(
                self.timeline_dialog,
                "Export Network Timeline",
                filename,
                "JSON Files (*.json);;CSV Files (*.csv);;All Files (*.*)"
            )
            
            if file_path:
                if file_path.endswith('.csv'):
                    # Export as CSV
                    import csv
                    with open(file_path, 'w', newline='', encoding='utf-8') as f:
                        writer = csv.writer(f)
                        writer.writerow(['URL', 'Method', 'Status', 'Type', 'Size', 'Start Time', 'End Time', 'Duration', 'DNS', 'TCP', 'TLS', 'Request', 'Response'])
                        
                        for req in self.timeline_requests:
                            timing = req.get('timing', {})
                            duration = (req.get('endTime', 0) - req.get('startTime', 0)) if req.get('endTime') else 0
                            
                            writer.writerow([
                                req.get('url', ''),
                                req.get('method', 'GET'),
                                req.get('status', ''),
                                req.get('type', ''),
                                req.get('size', 0),
                                req.get('startTime', 0),
                                req.get('endTime', 0),
                                duration,
                                timing.get('dns', 0),
                                timing.get('tcp', 0),
                                timing.get('tls', 0),
                                timing.get('request', 0),
                                timing.get('response', 0)
                            ])
                else:
                    # Export as JSON
                    export_data = {
                        'timestamp': datetime.now().isoformat(),
                        'total_requests': len(self.timeline_requests),
                        'requests': self.timeline_requests
                    }
                    
                    with open(file_path, 'w', encoding='utf-8') as f:
                        json.dump(export_data, f, indent=2, ensure_ascii=False)
                
                self.main_window.status_info.setText(f"📄 Timeline exported: {file_path}")
                QTimer.singleShot(3000, lambda: self.main_window.status_info.setText(""))
                
        except Exception as e:
            self.main_window.status_info.setText(f"❌ Export error: {str(e)}")
            QTimer.singleShot(3000, lambda: self.main_window.status_info.setText(""))
    
    def analyze_ads(self, browser):
        """Analyze advertisements without removing them"""
        try:
            page = browser.page()
            current_url = browser.url().toString()
            
            # Show initial status
            self.main_window.status_info.setText("📊 Analyzing advertisements...")
            
            # JavaScript for ad analysis (detection only, no removal)
            js_code = """
            (function() {
                var adAnalyzer = {
                    detected: {
                        scripts: [],
                        iframes: [],
                        images: [],
                        containers: [],
                        trackers: []
                    },
                    
                    stats: {
                        totalAds: 0,
                        adNetworks: [],
                        trackingScripts: 0,
                        suspiciousElements: 0
                    },
                    
                    // Ad network detection patterns
                    adNetworks: {
                        'Google Ads': ['googlesyndication.com', 'doubleclick.net', 'googleadservices.com'],
                        'Facebook Ads': ['facebook.com/tr', 'connect.facebook.net'],
                        'Amazon Ads': ['amazon-adsystem.com', 'assoc-amazon.com'],
                        'Outbrain': ['outbrain.com', 'widgets.outbrain.com'],
                        'Taboola': ['taboola.com', 'trc.taboola.com'],
                        'Criteo': ['criteo.com', 'static.criteo.net'],
                        'AppNexus': ['adnxs.com', 'ib.adnxs.com'],
                        'Bing Ads': ['bat.bing.com', 'ads.yahoo.com'],
                        'Twitter Ads': ['ads-twitter.com', 'analytics.twitter.com'],
                        'LinkedIn Ads': ['ads.linkedin.com', 'snap.licdn.com']
                    },
                    
                    // Common ad selectors for detection
                    adSelectors: [
                        '[class*="ad-"]', '[class*="ads-"]', '[class*="_ad_"]',
                        '[id*="ad-"]', '[id*="ads-"]', '[id*="_ad_"]',
                        '.advertisement', '.ads', '.ad', '.advert',
                        '.google-ads', '.adsbygoogle', '.sponsored', '.promoted'
                    ],
                    
                    analyzeScripts: function() {
                        var scripts = document.getElementsByTagName('script');
                        for (var i = 0; i < scripts.length; i++) {
                            var script = scripts[i];
                            if (script.src) {
                                var isAd = false;
                                var network = 'Unknown';
                                
                                // Check against known ad networks
                                for (var networkName in this.adNetworks) {
                                    var domains = this.adNetworks[networkName];
                                    for (var j = 0; j < domains.length; j++) {
                                        if (script.src.includes(domains[j])) {
                                            isAd = true;
                                            network = networkName;
                                            if (!this.stats.adNetworks.includes(networkName)) {
                                                this.stats.adNetworks.push(networkName);
                                            }
                                            break;
                                        }
                                    }
                                    if (isAd) break;
                                }
                                
                                if (isAd) {
                                    this.detected.scripts.push({
                                        src: script.src,
                                        network: network,
                                        async: script.async,
                                        defer: script.defer,
                                        type: script.type || 'text/javascript'
                                    });
                                    this.stats.totalAds++;
                                }
                                
                                // Check for tracking scripts
                                var trackingPatterns = ['analytics', 'tracking', 'pixel', 'beacon'];
                                for (var k = 0; k < trackingPatterns.length; k++) {
                                    if (script.src.toLowerCase().includes(trackingPatterns[k])) {
                                        this.stats.trackingScripts++;
                                        this.detected.trackers.push({
                                            src: script.src,
                                            type: 'tracking_script'
                                        });
                                        break;
                                    }
                                }
                            }
                        }
                    },
                    
                    analyzeIframes: function() {
                        var iframes = document.getElementsByTagName('iframe');
                        for (var i = 0; i < iframes.length; i++) {
                            var iframe = iframes[i];
                            if (iframe.src) {
                                var isAd = false;
                                var network = 'Unknown';
                                
                                // Check against ad networks
                                for (var networkName in this.adNetworks) {
                                    var domains = this.adNetworks[networkName];
                                    for (var j = 0; j < domains.length; j++) {
                                        if (iframe.src.includes(domains[j])) {
                                            isAd = true;
                                            network = networkName;
                                            break;
                                        }
                                    }
                                    if (isAd) break;
                                }
                                
                                // Check common ad sizes
                                var width = iframe.width || iframe.offsetWidth;
                                var height = iframe.height || iframe.offsetHeight;
                                var commonAdSizes = [
                                    [728, 90], [300, 250], [160, 600], [320, 50],
                                    [468, 60], [234, 60], [120, 600], [336, 280]
                                ];
                                
                                var isCommonAdSize = false;
                                for (var k = 0; k < commonAdSizes.length; k++) {
                                    if (width == commonAdSizes[k][0] && height == commonAdSizes[k][1]) {
                                        isCommonAdSize = true;
                                        isAd = true;
                                        break;
                                    }
                                }
                                
                                if (isAd) {
                                    this.detected.iframes.push({
                                        src: iframe.src,
                                        network: network,
                                        width: width,
                                        height: height,
                                        isCommonAdSize: isCommonAdSize
                                    });
                                    this.stats.totalAds++;
                                }
                            }
                        }
                    },
                    
                    analyzeImages: function() {
                        var images = document.getElementsByTagName('img');
                        for (var i = 0; i < images.length; i++) {
                            var img = images[i];
                            if (img.src) {
                                var isAd = false;
                                var network = 'Unknown';
                                
                                // Check against ad networks
                                for (var networkName in this.adNetworks) {
                                    var domains = this.adNetworks[networkName];
                                    for (var j = 0; j < domains.length; j++) {
                                        if (img.src.includes(domains[j])) {
                                            isAd = true;
                                            network = networkName;
                                            break;
                                        }
                                    }
                                    if (isAd) break;
                                }
                                
                                // Check for tracking pixels (1x1 images)
                                if ((img.width === 1 && img.height === 1) || 
                                    (img.naturalWidth === 1 && img.naturalHeight === 1)) {
                                    this.detected.trackers.push({
                                        src: img.src,
                                        type: 'tracking_pixel',
                                        network: network
                                    });
                                    this.stats.trackingScripts++;
                                }
                                
                                if (isAd) {
                                    this.detected.images.push({
                                        src: img.src,
                                        network: network,
                                        width: img.width || img.naturalWidth,
                                        height: img.height || img.naturalHeight,
                                        alt: img.alt
                                    });
                                    this.stats.totalAds++;
                                }
                            }
                        }
                    },
                    
                    analyzeContainers: function() {
                        for (var i = 0; i < this.adSelectors.length; i++) {
                            try {
                                var elements = document.querySelectorAll(this.adSelectors[i]);
                                for (var j = 0; j < elements.length; j++) {
                                    var element = elements[j];
                                    this.detected.containers.push({
                                        tag: element.tagName,
                                        className: element.className,
                                        id: element.id,
                                        selector: this.adSelectors[i],
                                        width: element.offsetWidth,
                                        height: element.offsetHeight,
                                        visible: element.offsetParent !== null
                                    });
                                    this.stats.suspiciousElements++;
                                }
                            } catch (e) {
                                // Ignore invalid selectors
                            }
                        }
                    },
                    
                    run: function() {
                        console.log('📊 Starting ad analysis...');
                        
                        this.analyzeScripts();
                        this.analyzeIframes();
                        this.analyzeImages();
                        this.analyzeContainers();
                        
                        console.log('📊 Ad analysis complete:', this.stats);
                        
                        return {
                            detected: this.detected,
                            stats: this.stats,
                            summary: 'Found ' + this.stats.totalAds + ' advertisements'
                        };
                    }
                };
                
                return adAnalyzer.run();
            })();
            """
            
            def process_ad_analysis(result):
                if not result:
                    self.main_window.status_info.setText("ℹ️ No ad analysis data available")
                    QTimer.singleShot(3000, lambda: self.main_window.status_info.setText(""))
                    return
                
                stats = result.get('stats', {})
                total_ads = stats.get('totalAds', 0)
                
                # Show analysis results dialog
                self.show_ad_analysis_dialog(result, current_url, browser)
                
                # Update status
                if total_ads > 0:
                    self.main_window.status_info.setText(f"📊 Analysis complete: {total_ads} ads detected")
                else:
                    self.main_window.status_info.setText("📊 Analysis complete: No ads detected")
                QTimer.singleShot(5000, lambda: self.main_window.status_info.setText(""))
            
            # Execute JavaScript to analyze ads
            page.runJavaScript(js_code, process_ad_analysis)
            
        except Exception as e:
            self.main_window.status_info.setText(f"❌ Ad analysis error: {str(e)}")
            QTimer.singleShot(3000, lambda: self.main_window.status_info.setText(""))
    
    def show_ad_analysis_dialog(self, result, base_url, browser):
        """Show dialog with ad analysis results"""
        from PyQt5.QtWidgets import (QDialog, QVBoxLayout, QHBoxLayout, QLabel, 
                                   QTextEdit, QPushButton, QTabWidget, QWidget,
                                   QTreeWidget, QTreeWidgetItem, QHeaderView,
                                   QGroupBox, QGridLayout, QFileDialog)
        from PyQt5.QtCore import Qt
        from PyQt5.QtGui import QColor
        from datetime import datetime
        
        detected = result.get('detected', {})
        stats = result.get('stats', {})
        
        # Create dialog
        dialog = QDialog(self.main_window)
        dialog.setWindowTitle(f"📊 Ad Analysis Report - {stats.get('totalAds', 0)} ads detected")
        dialog.setMinimumSize(1000, 700)
        dialog.resize(1200, 800)
        
        layout = QVBoxLayout(dialog)
        
        # Header
        header_label = QLabel(f"Advertisement Analysis for: {base_url}")
        header_label.setStyleSheet("font-weight: bold; padding: 10px; background-color: #fff3cd; border-radius: 5px;")
        header_label.setWordWrap(True)
        layout.addWidget(header_label)
        
        # Statistics overview
        stats_group = QGroupBox("📈 Advertisement Statistics")
        stats_grid = QGridLayout(stats_group)
        
        stats_grid.addWidget(QLabel(f"Total Ads Detected: {stats.get('totalAds', 0)}"), 0, 0)
        stats_grid.addWidget(QLabel(f"Tracking Scripts: {stats.get('trackingScripts', 0)}"), 0, 1)
        stats_grid.addWidget(QLabel(f"Suspicious Elements: {stats.get('suspiciousElements', 0)}"), 1, 0)
        
        # Ad networks
        networks = stats.get('adNetworks', [])
        networks_text = ', '.join(networks) if networks else 'None detected'
        networks_label = QLabel(f"Ad Networks: {networks_text}")
        networks_label.setWordWrap(True)
        stats_grid.addWidget(networks_label, 1, 1)
        
        layout.addWidget(stats_group)
        
        # Tab widget for different ad types
        tab_widget = QTabWidget()
        layout.addWidget(tab_widget)
        
        # Scripts tab
        scripts_widget = QWidget()
        scripts_layout = QVBoxLayout(scripts_widget)
        
        scripts_tree = QTreeWidget()
        scripts_tree.setHeaderLabels(['Source', 'Network', 'Type', 'Loading'])
        scripts_tree.header().setSectionResizeMode(0, QHeaderView.Stretch)
        
        for script in detected.get('scripts', []):
            item = QTreeWidgetItem()
            item.setText(0, script.get('src', '')[-60:])  # Last 60 chars
            item.setText(1, script.get('network', 'Unknown'))
            item.setText(2, script.get('type', 'text/javascript'))
            
            loading = []
            if script.get('async'):
                loading.append('async')
            if script.get('defer'):
                loading.append('defer')
            item.setText(3, ', '.join(loading) if loading else 'blocking')
            
            scripts_tree.addTopLevelItem(item)
        
        scripts_layout.addWidget(scripts_tree)
        tab_widget.addTab(scripts_widget, f"📜 Scripts ({len(detected.get('scripts', []))})")
        
        # Iframes tab
        iframes_widget = QWidget()
        iframes_layout = QVBoxLayout(iframes_widget)
        
        iframes_tree = QTreeWidget()
        iframes_tree.setHeaderLabels(['Source', 'Network', 'Dimensions', 'Ad Size'])
        
        for iframe in detected.get('iframes', []):
            item = QTreeWidgetItem()
            item.setText(0, iframe.get('src', '')[-60:])
            item.setText(1, iframe.get('network', 'Unknown'))
            item.setText(2, f"{iframe.get('width', 0)}x{iframe.get('height', 0)}")
            item.setText(3, 'Yes' if iframe.get('isCommonAdSize') else 'No')
            
            if iframe.get('isCommonAdSize'):
                item.setBackground(3, QColor(255, 200, 200))
            
            iframes_tree.addTopLevelItem(item)
        
        iframes_layout.addWidget(iframes_tree)
        tab_widget.addTab(iframes_widget, f"🖼️ Iframes ({len(detected.get('iframes', []))})")
        
        # Images tab
        images_widget = QWidget()
        images_layout = QVBoxLayout(images_widget)
        
        images_tree = QTreeWidget()
        images_tree.setHeaderLabels(['Source', 'Network', 'Dimensions', 'Alt Text'])
        
        for image in detected.get('images', []):
            item = QTreeWidgetItem()
            item.setText(0, image.get('src', '')[-60:])
            item.setText(1, image.get('network', 'Unknown'))
            item.setText(2, f"{image.get('width', 0)}x{image.get('height', 0)}")
            item.setText(3, image.get('alt', '')[:30])
            
            images_tree.addTopLevelItem(item)
        
        images_layout.addWidget(images_tree)
        tab_widget.addTab(images_widget, f"🖼️ Images ({len(detected.get('images', []))})")
        
        # Trackers tab
        trackers_widget = QWidget()
        trackers_layout = QVBoxLayout(trackers_widget)
        
        trackers_tree = QTreeWidget()
        trackers_tree.setHeaderLabels(['Source', 'Type', 'Network'])
        
        for tracker in detected.get('trackers', []):
            item = QTreeWidgetItem()
            item.setText(0, tracker.get('src', '')[-60:])
            item.setText(1, tracker.get('type', 'unknown'))
            item.setText(2, tracker.get('network', 'Unknown'))
            
            # Color code by type
            if tracker.get('type') == 'tracking_pixel':
                item.setBackground(1, QColor(255, 200, 200))
            else:
                item.setBackground(1, QColor(255, 255, 200))
            
            trackers_tree.addTopLevelItem(item)
        
        trackers_layout.addWidget(trackers_tree)
        tab_widget.addTab(trackers_widget, f"🔍 Trackers ({len(detected.get('trackers', []))})")
        
        # Buttons
        button_layout = QHBoxLayout()
        
        remove_ads_button = QPushButton("🚫 Remove Detected Ads")
        export_button = QPushButton("📊 Export Report")
        close_button = QPushButton("❌ Close")
        
        button_layout.addStretch()
        button_layout.addWidget(remove_ads_button)
        button_layout.addWidget(export_button)
        button_layout.addWidget(close_button)
        layout.addLayout(button_layout)
        
        def remove_ads():
            dialog.accept()
            # Run the ad removal tool
            self.scan_and_remove_ads(browser)
        
        def export_report():
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            filename = f"ad_analysis_report_{timestamp}.txt"
            
            file_path, _ = QFileDialog.getSaveFileName(
                dialog,
                "Export Ad Analysis Report",
                filename,
                "Text Files (*.txt);;All Files (*.*)"
            )
            
            if file_path:
                try:
                    report_lines = []
                    report_lines.append("ADVERTISEMENT ANALYSIS REPORT")
                    report_lines.append("=" * 60)
                    report_lines.append(f"URL: {base_url}")
                    report_lines.append(f"Analysis Date: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
                    report_lines.append("")
                    
                    # Statistics
                    report_lines.append("STATISTICS")
                    report_lines.append("-" * 30)
                    report_lines.append(f"Total Ads Detected: {stats.get('totalAds', 0)}")
                    report_lines.append(f"Tracking Scripts: {stats.get('trackingScripts', 0)}")
                    report_lines.append(f"Suspicious Elements: {stats.get('suspiciousElements', 0)}")
                    report_lines.append(f"Ad Networks: {', '.join(stats.get('adNetworks', []))}")
                    report_lines.append("")
                    
                    # Detailed breakdown
                    if detected.get('scripts'):
                        report_lines.append("AD SCRIPTS")
                        report_lines.append("-" * 20)
                        for script in detected['scripts']:
                            report_lines.append(f"- {script.get('src', '')}")
                            report_lines.append(f"  Network: {script.get('network', 'Unknown')}")
                        report_lines.append("")
                    
                    if detected.get('trackers'):
                        report_lines.append("TRACKING ELEMENTS")
                        report_lines.append("-" * 20)
                        for tracker in detected['trackers']:
                            report_lines.append(f"- {tracker.get('src', '')}")
                            report_lines.append(f"  Type: {tracker.get('type', 'unknown')}")
                        report_lines.append("")
                    
                    with open(file_path, 'w', encoding='utf-8') as f:
                        f.write('\n'.join(report_lines))
                    
                    self.main_window.status_info.setText(f"✅ Report exported to: {file_path}")
                    QTimer.singleShot(3000, lambda: self.main_window.status_info.setText(""))
                except Exception as e:
                    self.main_window.status_info.setText(f"❌ Export failed: {str(e)}")
                    QTimer.singleShot(3000, lambda: self.main_window.status_info.setText(""))
        
        # Connect buttons
        remove_ads_button.clicked.connect(remove_ads)
        export_button.clicked.connect(export_report)
        close_button.clicked.connect(dialog.accept)
        
        # Show dialog
        dialog.exec_()
    
    def analyze_seo(self, browser):
        """Analyze SEO factors of the current website"""
        try:
            page = browser.page()
            current_url = browser.url().toString()
            
            # Show initial status
            self.main_window.status_info.setText("🔍 Analyzing SEO factors...")
            
            # JavaScript to extract SEO-related data from the page
            js_code = """
            (function() {
                var seo = {
                    title: document.title || '',
                    metaDescription: '',
                    metaKeywords: '',
                    headings: {
                        h1: [],
                        h2: [],
                        h3: [],
                        h4: [],
                        h5: [],
                        h6: []
                    },
                    images: [],
                    links: {
                        internal: [],
                        external: []
                    },
                    meta: [],
                    openGraph: {},
                    twitterCard: {},
                    schema: [],
                    canonical: '',
                    robots: '',
                    viewport: '',
                    lang: document.documentElement.lang || '',
                    charset: '',
                    performance: {
                        loadTime: performance.timing ? (performance.timing.loadEventEnd - performance.timing.navigationStart) : 0,
                        domContentLoaded: performance.timing ? (performance.timing.domContentLoadedEventEnd - performance.timing.navigationStart) : 0
                    }
                };
                
                // Extract meta tags
                var metaTags = document.getElementsByTagName('meta');
                for (var i = 0; i < metaTags.length; i++) {
                    var meta = metaTags[i];
                    var name = meta.getAttribute('name') || meta.getAttribute('property') || meta.getAttribute('http-equiv');
                    var content = meta.getAttribute('content') || '';
                    
                    if (name) {
                        seo.meta.push({
                            name: name,
                            content: content
                        });
                        
                        // Extract specific meta tags
                        if (name.toLowerCase() === 'description') {
                            seo.metaDescription = content;
                        } else if (name.toLowerCase() === 'keywords') {
                            seo.metaKeywords = content;
                        } else if (name.toLowerCase() === 'robots') {
                            seo.robots = content;
                        } else if (name.toLowerCase() === 'viewport') {
                            seo.viewport = content;
                        } else if (name.startsWith('og:')) {
                            seo.openGraph[name] = content;
                        } else if (name.startsWith('twitter:')) {
                            seo.twitterCard[name] = content;
                        }
                    }
                    
                    // Check for charset
                    if (meta.getAttribute('charset')) {
                        seo.charset = meta.getAttribute('charset');
                    }
                }
                
                // Extract headings
                for (var level = 1; level <= 6; level++) {
                    var headings = document.getElementsByTagName('h' + level);
                    for (var i = 0; i < headings.length; i++) {
                        seo.headings['h' + level].push({
                            text: headings[i].textContent.trim(),
                            id: headings[i].id || '',
                            className: headings[i].className || ''
                        });
                    }
                }
                
                // Extract images
                var images = document.getElementsByTagName('img');
                for (var i = 0; i < images.length; i++) {
                    var img = images[i];
                    seo.images.push({
                        src: img.src || '',
                        alt: img.alt || '',
                        title: img.title || '',
                        width: img.width || 0,
                        height: img.height || 0,
                        loading: img.loading || '',
                        hasAlt: !!img.alt,
                        hasTitle: !!img.title
                    });
                }
                
                // Extract links
                var links = document.getElementsByTagName('a');
                var currentDomain = window.location.hostname;
                
                for (var i = 0; i < links.length; i++) {
                    var link = links[i];
                    var href = link.href || '';
                    var text = link.textContent.trim();
                    
                    if (href) {
                        var linkData = {
                            href: href,
                            text: text,
                            title: link.title || '',
                            rel: link.rel || '',
                            target: link.target || '',
                            hasTitle: !!link.title,
                            hasText: !!text
                        };
                        
                        try {
                            var linkUrl = new URL(href);
                            if (linkUrl.hostname === currentDomain || href.startsWith('/') || href.startsWith('#')) {
                                seo.links.internal.push(linkData);
                            } else {
                                seo.links.external.push(linkData);
                            }
                        } catch (e) {
                            // Invalid URL, treat as internal
                            seo.links.internal.push(linkData);
                        }
                    }
                }
                
                // Extract canonical URL
                var canonicalLink = document.querySelector('link[rel="canonical"]');
                if (canonicalLink) {
                    seo.canonical = canonicalLink.href || '';
                }
                
                // Extract structured data (JSON-LD)
                var scripts = document.querySelectorAll('script[type="application/ld+json"]');
                for (var i = 0; i < scripts.length; i++) {
                    try {
                        var jsonData = JSON.parse(scripts[i].textContent);
                        seo.schema.push(jsonData);
                    } catch (e) {
                        // Invalid JSON, skip
                    }
                }
                
                return seo;
            })();
            """
            
            def process_seo_data(seo_data):
                if not seo_data:
                    self.main_window.status_info.setText("❌ Failed to analyze SEO data")
                    QTimer.singleShot(3000, lambda: self.main_window.status_info.setText(""))
                    return
                
                # Create and show the SEO analyzer dialog
                self.show_seo_analyzer_dialog(seo_data, current_url)
            
            # Execute JavaScript to get SEO data
            page.runJavaScript(js_code, process_seo_data)
            
        except Exception as e:
            self.main_window.status_info.setText(f"❌ SEO analysis error: {str(e)}")
            QTimer.singleShot(3000, lambda: self.main_window.status_info.setText(""))
    
    def show_seo_analyzer_dialog(self, seo_data, base_url):
        """Show dialog with SEO analysis results"""
        from PyQt5.QtWidgets import (QDialog, QVBoxLayout, QHBoxLayout, QLabel, 
                                   QTextEdit, QPushButton, QTabWidget, QWidget,
                                   QTreeWidget, QTreeWidgetItem, QHeaderView, 
                                   QFileDialog, QScrollArea, QFrame, QProgressBar)
        from PyQt5.QtCore import Qt
        from PyQt5.QtGui import QFont, QColor
        from datetime import datetime
        import json
        
        # Create dialog
        dialog = QDialog(self.main_window)
        dialog.setWindowTitle(f"🔍 SEO Analyzer - {seo_data.get('title', 'Untitled')}")
        dialog.setMinimumSize(1000, 800)
        dialog.resize(1400, 900)
        
        layout = QVBoxLayout(dialog)
        
        # Header
        header_label = QLabel(f"SEO Analysis for: {base_url}")
        header_label.setStyleSheet("font-weight: bold; padding: 10px; background-color: #e8f5e8; border-radius: 5px;")
        header_label.setWordWrap(True)
        layout.addWidget(header_label)
        
        # SEO Score calculation
        score, issues, recommendations = self.calculate_seo_score(seo_data)
        
        # Score display
        score_frame = QFrame()
        score_frame.setStyleSheet("background-color: #f8f9fa; border: 1px solid #dee2e6; border-radius: 5px; padding: 10px;")
        score_layout = QHBoxLayout(score_frame)
        
        score_label = QLabel(f"SEO Score: {score}/100")
        score_font = QFont()
        score_font.setPointSize(16)
        score_font.setBold(True)
        score_label.setFont(score_font)
        
        # Color code the score
        if score >= 80:
            score_label.setStyleSheet("color: #28a745;")  # Green
        elif score >= 60:
            score_label.setStyleSheet("color: #ffc107;")  # Yellow
        else:
            score_label.setStyleSheet("color: #dc3545;")  # Red
        
        score_layout.addWidget(score_label)
        
        # Progress bar for score
        score_progress = QProgressBar()
        score_progress.setRange(0, 100)
        score_progress.setValue(score)
        score_progress.setStyleSheet("""
            QProgressBar {
                border: 2px solid grey;
                border-radius: 5px;
                text-align: center;
            }
            QProgressBar::chunk {
                background-color: #28a745;
                width: 20px;
            }
        """)
        score_layout.addWidget(score_progress)
        
        layout.addWidget(score_frame)
        
        # Tab widget for different analysis sections
        tab_widget = QTabWidget()
        layout.addWidget(tab_widget)
        
        # Overview Tab
        overview_widget = self.create_seo_overview_tab(seo_data, score, issues, recommendations)
        tab_widget.addTab(overview_widget, "📊 Overview")
        
        # Meta Tags Tab
        meta_widget = self.create_seo_meta_tab(seo_data)
        tab_widget.addTab(meta_widget, f"🏷️ Meta Tags ({len(seo_data.get('meta', []))})")
        
        # Headings Tab
        headings_widget = self.create_seo_headings_tab(seo_data)
        total_headings = sum(len(headings) for headings in seo_data.get('headings', {}).values())
        tab_widget.addTab(headings_widget, f"📝 Headings ({total_headings})")
        
        # Images Tab
        images_widget = self.create_seo_images_tab(seo_data)
        tab_widget.addTab(images_widget, f"🖼️ Images ({len(seo_data.get('images', []))})")
        
        # Links Tab
        links_widget = self.create_seo_links_tab(seo_data)
        total_links = len(seo_data.get('links', {}).get('internal', [])) + len(seo_data.get('links', {}).get('external', []))
        tab_widget.addTab(links_widget, f"🔗 Links ({total_links})")
        
        # Technical Tab
        technical_widget = self.create_seo_technical_tab(seo_data, base_url)
        tab_widget.addTab(technical_widget, "⚙️ Technical")
        
        # Structured Data Tab
        schema_widget = self.create_seo_schema_tab(seo_data)
        tab_widget.addTab(schema_widget, f"📋 Schema ({len(seo_data.get('schema', []))})")
        
        # Buttons
        button_layout = QHBoxLayout()
        
        export_button = QPushButton("💾 Export Report")
        reanalyze_button = QPushButton("🔄 Re-analyze")
        close_button = QPushButton("❌ Close")
        
        button_layout.addStretch()
        button_layout.addWidget(export_button)
        button_layout.addWidget(reanalyze_button)
        button_layout.addWidget(close_button)
        layout.addLayout(button_layout)
        
        def export_report():
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            filename = f"seo_analysis_{timestamp}.json"
            
            file_path, _ = QFileDialog.getSaveFileName(
                dialog,
                "Export SEO Analysis Report",
                filename,
                "JSON Files (*.json);;Text Files (*.txt);;All Files (*.*)"
            )
            
            if file_path:
                try:
                    export_data = {
                        'url': base_url,
                        'timestamp': datetime.now().isoformat(),
                        'score': score,
                        'issues': issues,
                        'recommendations': recommendations,
                        'seo_data': seo_data
                    }
                    
                    if file_path.endswith('.json'):
                        with open(file_path, 'w', encoding='utf-8') as f:
                            json.dump(export_data, f, indent=2, ensure_ascii=False)
                    else:
                        # Export as text report
                        with open(file_path, 'w', encoding='utf-8') as f:
                            f.write(self.generate_seo_text_report(export_data))
                    
                    self.main_window.status_info.setText(f"✅ SEO report exported to: {file_path}")
                    QTimer.singleShot(3000, lambda: self.main_window.status_info.setText(""))
                except Exception as e:
                    self.main_window.status_info.setText(f"❌ Export failed: {str(e)}")
                    QTimer.singleShot(3000, lambda: self.main_window.status_info.setText(""))
        
        def reanalyze():
            dialog.accept()
            # Re-run the analysis
            browser = self.get_current_browser()
            if browser:
                self.analyze_seo(browser)
        
        # Connect buttons
        export_button.clicked.connect(export_report)
        reanalyze_button.clicked.connect(reanalyze)
        close_button.clicked.connect(dialog.accept)
        
        # Show dialog
        dialog.exec_()
        
        # Update main window status
        self.main_window.status_info.setText(f"🔍 SEO analysis complete - Score: {score}/100")
        QTimer.singleShot(5000, lambda: self.main_window.status_info.setText(""))
    
    def calculate_seo_score(self, seo_data):
        """Calculate SEO score based on various factors"""
        score = 0
        max_score = 100
        issues = []
        recommendations = []
        
        # Title (15 points)
        title = seo_data.get('title', '')
        if title:
            if 30 <= len(title) <= 60:
                score += 15
            elif len(title) > 0:
                score += 10
                if len(title) < 30:
                    issues.append("Title is too short (< 30 characters)")
                    recommendations.append("Expand your title to 30-60 characters for better SEO")
                elif len(title) > 60:
                    issues.append("Title is too long (> 60 characters)")
                    recommendations.append("Shorten your title to 30-60 characters to avoid truncation")
        else:
            issues.append("Missing page title")
            recommendations.append("Add a descriptive title tag to your page")
        
        # Meta Description (15 points)
        meta_desc = seo_data.get('metaDescription', '')
        if meta_desc:
            if 120 <= len(meta_desc) <= 160:
                score += 15
            elif len(meta_desc) > 0:
                score += 10
                if len(meta_desc) < 120:
                    issues.append("Meta description is too short (< 120 characters)")
                    recommendations.append("Expand your meta description to 120-160 characters")
                elif len(meta_desc) > 160:
                    issues.append("Meta description is too long (> 160 characters)")
                    recommendations.append("Shorten your meta description to 120-160 characters")
        else:
            issues.append("Missing meta description")
            recommendations.append("Add a meta description to improve search result snippets")
        
        # Headings Structure (15 points)
        headings = seo_data.get('headings', {})
        h1_count = len(headings.get('h1', []))
        
        if h1_count == 1:
            score += 10
        elif h1_count == 0:
            issues.append("Missing H1 heading")
            recommendations.append("Add exactly one H1 heading to your page")
        elif h1_count > 1:
            issues.append(f"Multiple H1 headings found ({h1_count})")
            recommendations.append("Use only one H1 heading per page")
        
        # Check heading hierarchy
        has_h2 = len(headings.get('h2', [])) > 0
        has_h3 = len(headings.get('h3', [])) > 0
        
        if has_h2:
            score += 3
        if has_h2 and has_h3:
            score += 2
        
        # Images with Alt Text (10 points)
        images = seo_data.get('images', [])
        if images:
            images_with_alt = sum(1 for img in images if img.get('hasAlt'))
            alt_ratio = images_with_alt / len(images)
            score += int(10 * alt_ratio)
            
            if alt_ratio < 1.0:
                missing_alt = len(images) - images_with_alt
                issues.append(f"{missing_alt} images missing alt text")
                recommendations.append("Add descriptive alt text to all images for accessibility and SEO")
        
        # Internal/External Links (10 points)
        links = seo_data.get('links', {})
        internal_links = links.get('internal', [])
        external_links = links.get('external', [])
        
        if len(internal_links) > 0:
            score += 5
        else:
            issues.append("No internal links found")
            recommendations.append("Add internal links to improve site navigation and SEO")
        
        if len(external_links) > 0:
            score += 3
            # Check for nofollow on external links
            external_with_nofollow = sum(1 for link in external_links if 'nofollow' in link.get('rel', ''))
            if external_with_nofollow < len(external_links):
                recommendations.append("Consider adding rel='nofollow' to external links to preserve link equity")
        
        # Check for links without anchor text
        links_without_text = sum(1 for link in internal_links + external_links if not link.get('hasText'))
        if links_without_text > 0:
            issues.append(f"{links_without_text} links without anchor text")
            recommendations.append("Add descriptive anchor text to all links")
        
        score += 2  # Bonus for having links
        
        # Technical SEO (15 points)
        # Canonical URL
        if seo_data.get('canonical'):
            score += 3
        else:
            recommendations.append("Add a canonical URL to prevent duplicate content issues")
        
        # Viewport meta tag
        if seo_data.get('viewport'):
            score += 3
        else:
            issues.append("Missing viewport meta tag")
            recommendations.append("Add viewport meta tag for mobile responsiveness")
        
        # Language attribute
        if seo_data.get('lang'):
            score += 2
        else:
            issues.append("Missing language attribute")
            recommendations.append("Add lang attribute to html element")
        
        # Charset
        if seo_data.get('charset'):
            score += 2
        else:
            issues.append("Missing charset declaration")
            recommendations.append("Add charset meta tag (preferably UTF-8)")
        
        # Robots meta tag
        robots = seo_data.get('robots', '')
        if robots and 'noindex' not in robots.lower():
            score += 2
        elif 'noindex' in robots.lower():
            issues.append("Page is set to noindex")
            recommendations.append("Remove noindex directive if you want this page to be indexed")
        
        # Performance (basic check)
        performance = seo_data.get('performance', {})
        load_time = performance.get('loadTime', 0)
        if load_time > 0:
            if load_time < 3000:  # Less than 3 seconds
                score += 3
            elif load_time < 5000:  # Less than 5 seconds
                score += 1
            else:
                issues.append(f"Slow page load time ({load_time/1000:.1f}s)")
                recommendations.append("Optimize page load time to under 3 seconds")
        
        # Social Media Tags (10 points)
        og_tags = seo_data.get('openGraph', {})
        twitter_tags = seo_data.get('twitterCard', {})
        
        if og_tags:
            score += 5
            if 'og:title' not in og_tags:
                recommendations.append("Add og:title for better social media sharing")
            if 'og:description' not in og_tags:
                recommendations.append("Add og:description for better social media sharing")
            if 'og:image' not in og_tags:
                recommendations.append("Add og:image for better social media sharing")
        else:
            recommendations.append("Add Open Graph tags for better social media sharing")
        
        if twitter_tags:
            score += 3
        else:
            recommendations.append("Add Twitter Card tags for better Twitter sharing")
        
        # Structured Data (10 points)
        schema = seo_data.get('schema', [])
        if schema:
            score += 10
        else:
            recommendations.append("Add structured data (JSON-LD) to help search engines understand your content")
        
        # Ensure score doesn't exceed maximum
        score = min(score, max_score)
        
        return score, issues, recommendations
    
    def create_seo_overview_tab(self, seo_data, score, issues, recommendations):
        """Create the overview tab for SEO analysis"""
        from PyQt5.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QLabel, 
                                   QTextEdit, QFrame, QScrollArea)
        from PyQt5.QtCore import Qt
        from PyQt5.QtGui import QFont
        
        widget = QWidget()
        layout = QVBoxLayout(widget)
        
        # Create scroll area
        scroll = QScrollArea()
        scroll_widget = QWidget()
        scroll_layout = QVBoxLayout(scroll_widget)
        
        # Basic Information
        basic_frame = QFrame()
        basic_frame.setStyleSheet("background-color: #f8f9fa; border: 1px solid #dee2e6; border-radius: 5px; padding: 10px;")
        basic_layout = QVBoxLayout(basic_frame)
        
        basic_title = QLabel("📋 Basic Information")
        basic_title.setFont(QFont("Arial", 12, QFont.Bold))
        basic_layout.addWidget(basic_title)
        
        title = seo_data.get('title', 'No title')
        meta_desc = seo_data.get('metaDescription', 'No meta description')
        
        basic_layout.addWidget(QLabel(f"Title: {title} ({len(title)} chars)"))
        basic_layout.addWidget(QLabel(f"Meta Description: {meta_desc[:100]}{'...' if len(meta_desc) > 100 else ''} ({len(meta_desc)} chars)"))
        basic_layout.addWidget(QLabel(f"Language: {seo_data.get('lang', 'Not specified')}"))
        basic_layout.addWidget(QLabel(f"Charset: {seo_data.get('charset', 'Not specified')}"))
        
        scroll_layout.addWidget(basic_frame)
        
        # Issues Section
        if issues:
            issues_frame = QFrame()
            issues_frame.setStyleSheet("background-color: #f8d7da; border: 1px solid #f5c6cb; border-radius: 5px; padding: 10px;")
            issues_layout = QVBoxLayout(issues_frame)
            
            issues_title = QLabel(f"⚠️ Issues Found ({len(issues)})")
            issues_title.setFont(QFont("Arial", 12, QFont.Bold))
            issues_layout.addWidget(issues_title)
            
            for issue in issues:
                issue_label = QLabel(f"• {issue}")
                issue_label.setWordWrap(True)
                issues_layout.addWidget(issue_label)
            
            scroll_layout.addWidget(issues_frame)
        
        # Recommendations Section
        if recommendations:
            rec_frame = QFrame()
            rec_frame.setStyleSheet("background-color: #d1ecf1; border: 1px solid #bee5eb; border-radius: 5px; padding: 10px;")
            rec_layout = QVBoxLayout(rec_frame)
            
            rec_title = QLabel(f"💡 Recommendations ({len(recommendations)})")
            rec_title.setFont(QFont("Arial", 12, QFont.Bold))
            rec_layout.addWidget(rec_title)
            
            for rec in recommendations:
                rec_label = QLabel(f"• {rec}")
                rec_label.setWordWrap(True)
                rec_layout.addWidget(rec_label)
            
            scroll_layout.addWidget(rec_frame)
        
        # Quick Stats
        stats_frame = QFrame()
        stats_frame.setStyleSheet("background-color: #d4edda; border: 1px solid #c3e6cb; border-radius: 5px; padding: 10px;")
        stats_layout = QVBoxLayout(stats_frame)
        
        stats_title = QLabel("📊 Quick Statistics")
        stats_title.setFont(QFont("Arial", 12, QFont.Bold))
        stats_layout.addWidget(stats_title)
        
        headings = seo_data.get('headings', {})
        images = seo_data.get('images', [])
        links = seo_data.get('links', {})
        
        stats_layout.addWidget(QLabel(f"H1 Headings: {len(headings.get('h1', []))}"))
        stats_layout.addWidget(QLabel(f"Total Headings: {sum(len(h) for h in headings.values())}"))
        stats_layout.addWidget(QLabel(f"Images: {len(images)} (Alt text: {sum(1 for img in images if img.get('hasAlt'))})"))
        stats_layout.addWidget(QLabel(f"Internal Links: {len(links.get('internal', []))}"))
        stats_layout.addWidget(QLabel(f"External Links: {len(links.get('external', []))}"))
        stats_layout.addWidget(QLabel(f"Meta Tags: {len(seo_data.get('meta', []))}"))
        stats_layout.addWidget(QLabel(f"Structured Data: {len(seo_data.get('schema', []))} items"))
        
        scroll_layout.addWidget(stats_frame)
        
        scroll_layout.addStretch()
        scroll.setWidget(scroll_widget)
        scroll.setWidgetResizable(True)
        
        layout.addWidget(scroll)
        
        return widget
    
    def create_seo_meta_tab(self, seo_data):
        """Create the meta tags tab for SEO analysis"""
        from PyQt5.QtWidgets import (QWidget, QVBoxLayout, QTreeWidget, QTreeWidgetItem, 
                                   QHeaderView, QLabel)
        from PyQt5.QtCore import Qt
        from PyQt5.QtGui import QColor
        
        widget = QWidget()
        layout = QVBoxLayout(widget)
        
        # Header
        header = QLabel("🏷️ Meta Tags Analysis")
        header.setStyleSheet("font-weight: bold; font-size: 14px; padding: 5px;")
        layout.addWidget(header)
        
        # Tree widget for meta tags
        tree = QTreeWidget()
        tree.setHeaderLabels(['Name/Property', 'Content', 'Length', 'Status'])
        tree.header().setSectionResizeMode(0, QHeaderView.ResizeToContents)
        tree.header().setSectionResizeMode(1, QHeaderView.Stretch)
        tree.header().setSectionResizeMode(2, QHeaderView.ResizeToContents)
        tree.header().setSectionResizeMode(3, QHeaderView.ResizeToContents)
        
        meta_tags = seo_data.get('meta', [])
        
        # Important meta tags to check
        important_tags = {
            'description': seo_data.get('metaDescription', ''),
            'keywords': seo_data.get('metaKeywords', ''),
            'robots': seo_data.get('robots', ''),
            'viewport': seo_data.get('viewport', ''),
            'charset': seo_data.get('charset', '')
        }
        
        # Add important tags first
        for tag_name, content in important_tags.items():
            item = QTreeWidgetItem()
            item.setText(0, tag_name)
            item.setText(1, content[:100] + ('...' if len(content) > 100 else ''))
            item.setText(2, str(len(content)))
            
            # Status based on content and best practices
            if not content:
                item.setText(3, '❌ Missing')
                item.setBackground(3, QColor(255, 182, 193))  # Light red
            elif tag_name == 'description' and (len(content) < 120 or len(content) > 160):
                item.setText(3, '⚠️ Length issue')
                item.setBackground(3, QColor(255, 255, 0))  # Yellow
            elif tag_name == 'viewport' and 'width=device-width' not in content:
                item.setText(3, '⚠️ Not responsive')
                item.setBackground(3, QColor(255, 255, 0))  # Yellow
            else:
                item.setText(3, '✅ Good')
                item.setBackground(3, QColor(144, 238, 144))  # Light green
            
            tree.addTopLevelItem(item)
        
        # Add separator
        separator = QTreeWidgetItem()
        separator.setText(0, "--- Other Meta Tags ---")
        separator.setBackground(0, QColor(211, 211, 211))  # Light gray
        tree.addTopLevelItem(separator)
        
        # Add other meta tags
        for meta in meta_tags:
            name = meta.get('name', '')
            content = meta.get('content', '')
            
            # Skip if already added above
            if name.lower() in important_tags:
                continue
            
            item = QTreeWidgetItem()
            item.setText(0, name)
            item.setText(1, content[:100] + ('...' if len(content) > 100 else ''))
            item.setText(2, str(len(content)))
            item.setText(3, '✅ Present')
            item.setBackground(3, QColor(144, 238, 144))  # Light green
            
            tree.addTopLevelItem(item)
        
        layout.addWidget(tree)
        
        return widget
    
    def create_seo_headings_tab(self, seo_data):
        """Create the headings tab for SEO analysis"""
        from PyQt5.QtWidgets import (QWidget, QVBoxLayout, QTreeWidget, QTreeWidgetItem, 
                                   QHeaderView, QLabel)
        from PyQt5.QtCore import Qt
        from PyQt5.QtGui import QColor
        
        widget = QWidget()
        layout = QVBoxLayout(widget)
        
        # Header
        header = QLabel("📝 Headings Structure Analysis")
        header.setStyleSheet("font-weight: bold; font-size: 14px; padding: 5px;")
        layout.addWidget(header)
        
        # Tree widget for headings
        tree = QTreeWidget()
        tree.setHeaderLabels(['Level', 'Text', 'ID', 'Class', 'Length'])
        tree.header().setSectionResizeMode(0, QHeaderView.ResizeToContents)
        tree.header().setSectionResizeMode(1, QHeaderView.Stretch)
        tree.header().setSectionResizeMode(2, QHeaderView.ResizeToContents)
        tree.header().setSectionResizeMode(3, QHeaderView.ResizeToContents)
        tree.header().setSectionResizeMode(4, QHeaderView.ResizeToContents)
        
        headings = seo_data.get('headings', {})
        
        # Add headings in hierarchical order
        for level in ['h1', 'h2', 'h3', 'h4', 'h5', 'h6']:
            level_headings = headings.get(level, [])
            
            if level_headings:
                # Add level separator
                level_item = QTreeWidgetItem()
                level_item.setText(0, f"{level.upper()} ({len(level_headings)})")
                level_item.setBackground(0, QColor(211, 211, 211))  # Light gray
                tree.addTopLevelItem(level_item)
                
                for heading in level_headings:
                    item = QTreeWidgetItem()
                    item.setText(0, level.upper())
                    
                    text = heading.get('text', '')
                    item.setText(1, text[:80] + ('...' if len(text) > 80 else ''))
                    item.setText(2, heading.get('id', ''))
                    item.setText(3, heading.get('className', ''))
                    item.setText(4, str(len(text)))
                    
                    # Color code based on level and best practices
                    if level == 'h1':
                        item.setBackground(0, QColor(144, 238, 144) if len(level_headings) == 1 else QColor(255, 182, 193))
                    elif level == 'h2':
                        item.setBackground(0, QColor(173, 255, 173))
                    else:
                        item.setBackground(0, QColor(255, 255, 255))
                    
                    tree.addTopLevelItem(item)
        
        layout.addWidget(tree)
        
        return widget
    
    def create_seo_images_tab(self, seo_data):
        """Create the images tab for SEO analysis"""
        from PyQt5.QtWidgets import (QWidget, QVBoxLayout, QTreeWidget, QTreeWidgetItem, 
                                   QHeaderView, QLabel)
        from PyQt5.QtCore import Qt
        from PyQt5.QtGui import QColor
        
        widget = QWidget()
        layout = QVBoxLayout(widget)
        
        # Header
        header = QLabel("🖼️ Images SEO Analysis")
        header.setStyleSheet("font-weight: bold; font-size: 14px; padding: 5px;")
        layout.addWidget(header)
        
        # Tree widget for images
        tree = QTreeWidget()
        tree.setHeaderLabels(['Source', 'Alt Text', 'Title', 'Dimensions', 'Loading', 'Status'])
        tree.header().setSectionResizeMode(0, QHeaderView.Stretch)
        tree.header().setSectionResizeMode(1, QHeaderView.Stretch)
        tree.header().setSectionResizeMode(2, QHeaderView.ResizeToContents)
        tree.header().setSectionResizeMode(3, QHeaderView.ResizeToContents)
        tree.header().setSectionResizeMode(4, QHeaderView.ResizeToContents)
        tree.header().setSectionResizeMode(5, QHeaderView.ResizeToContents)
        
        images = seo_data.get('images', [])
        
        for img in images:
            item = QTreeWidgetItem()
            
            # Source (truncated)
            src = img.get('src', '')
            item.setText(0, src[-50:] if len(src) > 50 else src)
            
            # Alt text
            alt = img.get('alt', '')
            item.setText(1, alt[:50] + ('...' if len(alt) > 50 else ''))
            
            # Title
            title = img.get('title', '')
            item.setText(2, title[:30] + ('...' if len(title) > 30 else ''))
            
            # Dimensions
            width = img.get('width', 0)
            height = img.get('height', 0)
            if width and height:
                item.setText(3, f"{width}x{height}")
            else:
                item.setText(3, "Unknown")
            
            # Loading attribute
            loading = img.get('loading', '')
            item.setText(4, loading or 'default')
            
            # Status
            if not img.get('hasAlt'):
                item.setText(5, '❌ No Alt')
                item.setBackground(5, QColor(255, 182, 193))  # Light red
            elif len(alt) < 10:
                item.setText(5, '⚠️ Short Alt')
                item.setBackground(5, QColor(255, 255, 0))  # Yellow
            else:
                item.setText(5, '✅ Good')
                item.setBackground(5, QColor(144, 238, 144))  # Light green
            
            tree.addTopLevelItem(item)
        
        layout.addWidget(tree)
        
        return widget
    
    def create_seo_links_tab(self, seo_data):
        """Create the links tab for SEO analysis"""
        from PyQt5.QtWidgets import (QWidget, QVBoxLayout, QTreeWidget, QTreeWidgetItem, 
                                   QHeaderView, QLabel, QTabWidget)
        from PyQt5.QtCore import Qt
        from PyQt5.QtGui import QColor
        
        widget = QWidget()
        layout = QVBoxLayout(widget)
        
        # Header
        header = QLabel("🔗 Links SEO Analysis")
        header.setStyleSheet("font-weight: bold; font-size: 14px; padding: 5px;")
        layout.addWidget(header)
        
        # Sub-tabs for internal and external links
        links_tabs = QTabWidget()
        layout.addWidget(links_tabs)
        
        links = seo_data.get('links', {})
        internal_links = links.get('internal', [])
        external_links = links.get('external', [])
        
        # Internal Links Tab
        internal_widget = QWidget()
        internal_layout = QVBoxLayout(internal_widget)
        
        internal_tree = QTreeWidget()
        internal_tree.setHeaderLabels(['URL', 'Anchor Text', 'Title', 'Target', 'Status'])
        internal_tree.header().setSectionResizeMode(0, QHeaderView.Stretch)
        internal_tree.header().setSectionResizeMode(1, QHeaderView.Stretch)
        internal_tree.header().setSectionResizeMode(2, QHeaderView.ResizeToContents)
        internal_tree.header().setSectionResizeMode(3, QHeaderView.ResizeToContents)
        internal_tree.header().setSectionResizeMode(4, QHeaderView.ResizeToContents)
        
        for link in internal_links:
            item = QTreeWidgetItem()
            
            href = link.get('href', '')
            item.setText(0, href[:60] + ('...' if len(href) > 60 else ''))
            
            text = link.get('text', '')
            item.setText(1, text[:40] + ('...' if len(text) > 40 else ''))
            
            item.setText(2, link.get('title', ''))
            item.setText(3, link.get('target', ''))
            
            # Status
            if not link.get('hasText'):
                item.setText(4, '❌ No Text')
                item.setBackground(4, QColor(255, 182, 193))  # Light red
            elif len(text) < 3:
                item.setText(4, '⚠️ Short Text')
                item.setBackground(4, QColor(255, 255, 0))  # Yellow
            else:
                item.setText(4, '✅ Good')
                item.setBackground(4, QColor(144, 238, 144))  # Light green
            
            internal_tree.addTopLevelItem(item)
        
        internal_layout.addWidget(internal_tree)
        links_tabs.addTab(internal_widget, f"Internal ({len(internal_links)})")
        
        # External Links Tab
        external_widget = QWidget()
        external_layout = QVBoxLayout(external_widget)
        
        external_tree = QTreeWidget()
        external_tree.setHeaderLabels(['URL', 'Anchor Text', 'Rel', 'Target', 'Status'])
        external_tree.header().setSectionResizeMode(0, QHeaderView.Stretch)
        external_tree.header().setSectionResizeMode(1, QHeaderView.Stretch)
        external_tree.header().setSectionResizeMode(2, QHeaderView.ResizeToContents)
        external_tree.header().setSectionResizeMode(3, QHeaderView.ResizeToContents)
        external_tree.header().setSectionResizeMode(4, QHeaderView.ResizeToContents)
        
        for link in external_links:
            item = QTreeWidgetItem()
            
            href = link.get('href', '')
            item.setText(0, href[:60] + ('...' if len(href) > 60 else ''))
            
            text = link.get('text', '')
            item.setText(1, text[:40] + ('...' if len(text) > 40 else ''))
            
            rel = link.get('rel', '')
            item.setText(2, rel)
            item.setText(3, link.get('target', ''))
            
            # Status
            if not link.get('hasText'):
                item.setText(4, '❌ No Text')
                item.setBackground(4, QColor(255, 182, 193))  # Light red
            elif 'nofollow' not in rel:
                item.setText(4, '⚠️ No nofollow')
                item.setBackground(4, QColor(255, 255, 0))  # Yellow
            else:
                item.setText(4, '✅ Good')
                item.setBackground(4, QColor(144, 238, 144))  # Light green
            
            external_tree.addTopLevelItem(item)
        
        external_layout.addWidget(external_tree)
        links_tabs.addTab(external_widget, f"External ({len(external_links)})")
        
        return widget
    
    def create_seo_technical_tab(self, seo_data, base_url):
        """Create the technical SEO tab"""
        from PyQt5.QtWidgets import (QWidget, QVBoxLayout, QLabel, QFrame, QScrollArea)
        from PyQt5.QtCore import Qt
        from PyQt5.QtGui import QFont
        
        widget = QWidget()
        layout = QVBoxLayout(widget)
        
        # Header
        header = QLabel("⚙️ Technical SEO Analysis")
        header.setStyleSheet("font-weight: bold; font-size: 14px; padding: 5px;")
        layout.addWidget(header)
        
        # Create scroll area
        scroll = QScrollArea()
        scroll_widget = QWidget()
        scroll_layout = QVBoxLayout(scroll_widget)
        
        # URL Structure
        url_frame = QFrame()
        url_frame.setStyleSheet("background-color: #f8f9fa; border: 1px solid #dee2e6; border-radius: 5px; padding: 10px;")
        url_layout = QVBoxLayout(url_frame)
        
        url_title = QLabel("🌐 URL Structure")
        url_title.setFont(QFont("Arial", 12, QFont.Bold))
        url_layout.addWidget(url_title)
        
        url_layout.addWidget(QLabel(f"Current URL: {base_url}"))
        url_layout.addWidget(QLabel(f"Canonical: {seo_data.get('canonical', 'Not set')}"))
        
        # URL analysis
        if len(base_url) > 100:
            url_layout.addWidget(QLabel("⚠️ URL is quite long (>100 chars)"))
        if '_' in base_url:
            url_layout.addWidget(QLabel("⚠️ URL contains underscores (hyphens preferred)"))
        if base_url.count('/') > 5:
            url_layout.addWidget(QLabel("⚠️ URL has deep directory structure"))
        
        scroll_layout.addWidget(url_frame)
        
        # Mobile & Responsive
        mobile_frame = QFrame()
        mobile_frame.setStyleSheet("background-color: #e8f4fd; border: 1px solid #bee5eb; border-radius: 5px; padding: 10px;")
        mobile_layout = QVBoxLayout(mobile_frame)
        
        mobile_title = QLabel("📱 Mobile & Responsive")
        mobile_title.setFont(QFont("Arial", 12, QFont.Bold))
        mobile_layout.addWidget(mobile_title)
        
        viewport = seo_data.get('viewport', '')
        if viewport:
            mobile_layout.addWidget(QLabel(f"✅ Viewport: {viewport}"))
            if 'width=device-width' in viewport:
                mobile_layout.addWidget(QLabel("✅ Responsive design detected"))
            else:
                mobile_layout.addWidget(QLabel("⚠️ May not be fully responsive"))
        else:
            mobile_layout.addWidget(QLabel("❌ No viewport meta tag"))
        
        scroll_layout.addWidget(mobile_frame)
        
        # Performance
        perf_frame = QFrame()
        perf_frame.setStyleSheet("background-color: #fff3cd; border: 1px solid #ffeaa7; border-radius: 5px; padding: 10px;")
        perf_layout = QVBoxLayout(perf_frame)
        
        perf_title = QLabel("⚡ Performance")
        perf_title.setFont(QFont("Arial", 12, QFont.Bold))
        perf_layout.addWidget(perf_title)
        
        performance = seo_data.get('performance', {})
        load_time = performance.get('loadTime', 0)
        dom_time = performance.get('domContentLoaded', 0)
        
        if load_time > 0:
            perf_layout.addWidget(QLabel(f"Page Load Time: {load_time/1000:.2f}s"))
            if load_time < 3000:
                perf_layout.addWidget(QLabel("✅ Good load time (<3s)"))
            elif load_time < 5000:
                perf_layout.addWidget(QLabel("⚠️ Moderate load time (3-5s)"))
            else:
                perf_layout.addWidget(QLabel("❌ Slow load time (>5s)"))
        
        if dom_time > 0:
            perf_layout.addWidget(QLabel(f"DOM Content Loaded: {dom_time/1000:.2f}s"))
        
        scroll_layout.addWidget(perf_frame)
        
        # Security & Protocol
        security_frame = QFrame()
        security_frame.setStyleSheet("background-color: #d4edda; border: 1px solid #c3e6cb; border-radius: 5px; padding: 10px;")
        security_layout = QVBoxLayout(security_frame)
        
        security_title = QLabel("🔒 Security & Protocol")
        security_title.setFont(QFont("Arial", 12, QFont.Bold))
        security_layout.addWidget(security_title)
        
        if base_url.startswith('https://'):
            security_layout.addWidget(QLabel("✅ HTTPS enabled"))
        else:
            security_layout.addWidget(QLabel("❌ Not using HTTPS"))
        
        robots = seo_data.get('robots', '')
        if robots:
            security_layout.addWidget(QLabel(f"Robots directive: {robots}"))
        else:
            security_layout.addWidget(QLabel("No robots meta tag"))
        
        scroll_layout.addWidget(security_frame)
        
        scroll_layout.addStretch()
        scroll.setWidget(scroll_widget)
        scroll.setWidgetResizable(True)
        
        layout.addWidget(scroll)
        
        return widget
    
    def create_seo_schema_tab(self, seo_data):
        """Create the structured data/schema tab"""
        from PyQt5.QtWidgets import (QWidget, QVBoxLayout, QTextEdit, QLabel, 
                                   QTreeWidget, QTreeWidgetItem, QTabWidget)
        from PyQt5.QtCore import Qt
        import json
        
        widget = QWidget()
        layout = QVBoxLayout(widget)
        
        # Header
        header = QLabel("📋 Structured Data (Schema.org)")
        header.setStyleSheet("font-weight: bold; font-size: 14px; padding: 5px;")
        layout.addWidget(header)
        
        schema_data = seo_data.get('schema', [])
        
        if not schema_data:
            no_schema_label = QLabel("❌ No structured data found on this page.\n\nStructured data helps search engines understand your content better.\nConsider adding JSON-LD structured data.")
            no_schema_label.setStyleSheet("padding: 20px; background-color: #f8d7da; border-radius: 5px; color: #721c24;")
            no_schema_label.setWordWrap(True)
            layout.addWidget(no_schema_label)
        else:
            # Tabs for each schema item
            schema_tabs = QTabWidget()
            layout.addWidget(schema_tabs)
            
            for i, schema_item in enumerate(schema_data):
                # Create tab for this schema item
                schema_widget = QWidget()
                schema_layout = QVBoxLayout(schema_widget)
                
                # Schema type
                schema_type = schema_item.get('@type', 'Unknown')
                type_label = QLabel(f"Schema Type: {schema_type}")
                type_label.setStyleSheet("font-weight: bold; padding: 5px; background-color: #d4edda; border-radius: 3px;")
                schema_layout.addWidget(type_label)
                
                # JSON view
                json_text = QTextEdit()
                json_text.setReadOnly(True)
                json_text.setStyleSheet("font-family: monospace; background-color: #f8f9fa;")
                
                try:
                    formatted_json = json.dumps(schema_item, indent=2, ensure_ascii=False)
                    json_text.setPlainText(formatted_json)
                except:
                    json_text.setPlainText(str(schema_item))
                
                schema_layout.addWidget(json_text)
                
                tab_name = f"{schema_type} ({i+1})" if len(schema_data) > 1 else schema_type
                schema_tabs.addTab(schema_widget, tab_name)
        
        return widget
    
    def generate_seo_text_report(self, export_data):
        """Generate a text-based SEO report"""
        lines = []
        lines.append("SEO ANALYSIS REPORT")
        lines.append("=" * 50)
        lines.append(f"URL: {export_data['url']}")
        lines.append(f"Analysis Date: {export_data['timestamp']}")
        lines.append(f"SEO Score: {export_data['score']}/100")
        lines.append("")
        
        # Issues
        if export_data['issues']:
            lines.append("ISSUES FOUND:")
            lines.append("-" * 20)
            for issue in export_data['issues']:
                lines.append(f"• {issue}")
            lines.append("")
        
        # Recommendations
        if export_data['recommendations']:
            lines.append("RECOMMENDATIONS:")
            lines.append("-" * 20)
            for rec in export_data['recommendations']:
                lines.append(f"• {rec}")
            lines.append("")
        
        # Detailed data
        seo_data = export_data['seo_data']
        
        lines.append("DETAILED ANALYSIS:")
        lines.append("-" * 20)
        lines.append(f"Title: {seo_data.get('title', 'N/A')} ({len(seo_data.get('title', ''))} chars)")
        lines.append(f"Meta Description: {seo_data.get('metaDescription', 'N/A')} ({len(seo_data.get('metaDescription', ''))} chars)")
        lines.append(f"Language: {seo_data.get('lang', 'Not specified')}")
        lines.append(f"Canonical URL: {seo_data.get('canonical', 'Not set')}")
        lines.append("")
        
        # Headings
        headings = seo_data.get('headings', {})
        lines.append("HEADINGS STRUCTURE:")
        for level in ['h1', 'h2', 'h3', 'h4', 'h5', 'h6']:
            count = len(headings.get(level, []))
            if count > 0:
                lines.append(f"  {level.upper()}: {count}")
        lines.append("")
        
        # Images
        images = seo_data.get('images', [])
        images_with_alt = sum(1 for img in images if img.get('hasAlt'))
        lines.append(f"IMAGES: {len(images)} total, {images_with_alt} with alt text")
        lines.append("")
        
        # Links
        links = seo_data.get('links', {})
        lines.append(f"LINKS: {len(links.get('internal', []))} internal, {len(links.get('external', []))} external")
        lines.append("")
        
        return '\n'.join(lines)
    
    def detect_fonts(self, browser):
        """Detect and analyze fonts used on the current website"""
        try:
            page = browser.page()
            current_url = browser.url().toString()
            
            # Show initial status
            self.main_window.status_info.setText("🔤 Detecting fonts...")
            
            # JavaScript to extract font information from the page
            js_code = """
            (function() {
                var fontData = {
                    elements: [],
                    uniqueFonts: new Set(),
                    fontFaces: [],
                    webFonts: [],
                    systemFonts: [],
                    fontSizes: new Set(),
                    fontWeights: new Set(),
                    fontStyles: new Set()
                };
                
                // Get all elements with text content
                var allElements = document.querySelectorAll('*');
                var textElements = [];
                
                for (var i = 0; i < allElements.length; i++) {
                    var element = allElements[i];
                    var hasDirectText = false;
                    
                    // Check if element has direct text content (not just from children)
                    for (var j = 0; j < element.childNodes.length; j++) {
                        if (element.childNodes[j].nodeType === Node.TEXT_NODE && 
                            element.childNodes[j].textContent.trim().length > 0) {
                            hasDirectText = true;
                            break;
                        }
                    }
                    
                    if (hasDirectText || 
                        ['H1', 'H2', 'H3', 'H4', 'H5', 'H6', 'P', 'SPAN', 'DIV', 'A', 'BUTTON', 'LABEL', 'LI'].includes(element.tagName)) {
                        textElements.push(element);
                    }
                }
                
                // Analyze each text element
                textElements.forEach(function(element, index) {
                    if (index > 200) return; // Limit to first 200 elements for performance
                    
                    var computedStyle = window.getComputedStyle(element);
                    var fontFamily = computedStyle.fontFamily;
                    var fontSize = computedStyle.fontSize;
                    var fontWeight = computedStyle.fontWeight;
                    var fontStyle = computedStyle.fontStyle;
                    var lineHeight = computedStyle.lineHeight;
                    var letterSpacing = computedStyle.letterSpacing;
                    var textTransform = computedStyle.textTransform;
                    var color = computedStyle.color;
                    
                    // Get element text content (truncated)
                    var textContent = element.textContent || element.innerText || '';
                    textContent = textContent.trim().substring(0, 100);
                    
                    if (textContent.length > 0) {
                        var elementData = {
                            tagName: element.tagName.toLowerCase(),
                            className: element.className || '',
                            id: element.id || '',
                            fontFamily: fontFamily,
                            fontSize: fontSize,
                            fontWeight: fontWeight,
                            fontStyle: fontStyle,
                            lineHeight: lineHeight,
                            letterSpacing: letterSpacing,
                            textTransform: textTransform,
                            color: color,
                            textContent: textContent,
                            xpath: getXPath(element)
                        };
                        
                        fontData.elements.push(elementData);
                        
                        // Collect unique values
                        fontData.uniqueFonts.add(fontFamily);
                        fontData.fontSizes.add(fontSize);
                        fontData.fontWeights.add(fontWeight);
                        fontData.fontStyles.add(fontStyle);
                    }
                });
                
                // Convert Sets to Arrays for JSON serialization
                fontData.uniqueFonts = Array.from(fontData.uniqueFonts);
                fontData.fontSizes = Array.from(fontData.fontSizes);
                fontData.fontWeights = Array.from(fontData.fontWeights);
                fontData.fontStyles = Array.from(fontData.fontStyles);
                
                // Detect web fonts vs system fonts
                fontData.uniqueFonts.forEach(function(fontFamily) {
                    var fonts = fontFamily.split(',').map(f => f.trim().replace(/['"]/g, ''));
                    
                    fonts.forEach(function(font) {
                        var isSystemFont = [
                            'serif', 'sans-serif', 'monospace', 'cursive', 'fantasy',
                            'Arial', 'Helvetica', 'Times', 'Times New Roman', 'Courier',
                            'Courier New', 'Verdana', 'Georgia', 'Palatino', 'Garamond',
                            'Bookman', 'Comic Sans MS', 'Trebuchet MS', 'Arial Black',
                            'Impact', 'Lucida Console', 'Tahoma', 'Geneva', 'Lucida Sans',
                            'system-ui', '-apple-system', 'BlinkMacSystemFont', 'Segoe UI',
                            'Roboto', 'Oxygen', 'Ubuntu', 'Cantarell', 'Fira Sans',
                            'Droid Sans', 'Helvetica Neue'
                        ].some(sysFont => font.toLowerCase().includes(sysFont.toLowerCase()));
                        
                        if (isSystemFont) {
                            if (!fontData.systemFonts.includes(font)) {
                                fontData.systemFonts.push(font);
                            }
                        } else {
                            if (!fontData.webFonts.includes(font)) {
                                fontData.webFonts.push(font);
                            }
                        }
                    });
                });
                
                // Detect @font-face declarations
                try {
                    var styleSheets = document.styleSheets;
                    for (var i = 0; i < styleSheets.length; i++) {
                        try {
                            var rules = styleSheets[i].cssRules || styleSheets[i].rules;
                            if (rules) {
                                for (var j = 0; j < rules.length; j++) {
                                    if (rules[j].type === CSSRule.FONT_FACE_RULE) {
                                        var fontFace = {
                                            fontFamily: rules[j].style.fontFamily || '',
                                            src: rules[j].style.src || '',
                                            fontWeight: rules[j].style.fontWeight || '',
                                            fontStyle: rules[j].style.fontStyle || '',
                                            fontDisplay: rules[j].style.fontDisplay || ''
                                        };
                                        fontData.fontFaces.push(fontFace);
                                    }
                                }
                            }
                        } catch (e) {
                            // Cross-origin stylesheet, skip
                        }
                    }
                } catch (e) {
                    // Error accessing stylesheets
                }
                
                // Helper function to get XPath
                function getXPath(element) {
                    if (element.id !== '') {
                        return '//*[@id="' + element.id + '"]';
                    }
                    if (element === document.body) {
                        return '/html/body';
                    }
                    
                    var ix = 0;
                    var siblings = element.parentNode.childNodes;
                    for (var i = 0; i < siblings.length; i++) {
                        var sibling = siblings[i];
                        if (sibling === element) {
                            return getXPath(element.parentNode) + '/' + element.tagName.toLowerCase() + '[' + (ix + 1) + ']';
                        }
                        if (sibling.nodeType === 1 && sibling.tagName === element.tagName) {
                            ix++;
                        }
                    }
                }
                
                return fontData;
            })();
            """
            
            def process_font_data(font_data):
                if not font_data:
                    self.main_window.status_info.setText("❌ Failed to detect fonts")
                    QTimer.singleShot(3000, lambda: self.main_window.status_info.setText(""))
                    return
                
                # Create and show the font detector dialog
                self.show_font_detector_dialog(font_data, current_url)
            
            # Execute JavaScript to get font data
            page.runJavaScript(js_code, process_font_data)
            
        except Exception as e:
            self.main_window.status_info.setText(f"❌ Font detection error: {str(e)}")
            QTimer.singleShot(3000, lambda: self.main_window.status_info.setText(""))
    
    def show_font_detector_dialog(self, font_data, base_url):
        """Show dialog with font detection results"""
        from PyQt5.QtWidgets import (QDialog, QVBoxLayout, QHBoxLayout, QLabel, 
                                   QTextEdit, QPushButton, QTabWidget, QWidget,
                                   QTreeWidget, QTreeWidgetItem, QHeaderView, 
                                   QFileDialog, QScrollArea, QFrame, QComboBox,
                                   QCheckBox, QSpinBox, QColorDialog)
        from PyQt5.QtCore import Qt, QTimer
        from PyQt5.QtGui import QFont, QColor, QPalette
        from datetime import datetime
        import json
        
        # Create dialog
        dialog = QDialog(self.main_window)
        dialog.setWindowTitle(f"🔤 Font Detector - {len(font_data.get('uniqueFonts', []))} fonts found")
        dialog.setMinimumSize(1200, 800)
        dialog.resize(1400, 900)
        
        layout = QVBoxLayout(dialog)
        
        # Header
        header_label = QLabel(f"Font Analysis for: {base_url}")
        header_label.setStyleSheet("font-weight: bold; padding: 10px; background-color: #e8f4fd; border-radius: 5px;")
        header_label.setWordWrap(True)
        layout.addWidget(header_label)
        
        # Summary
        unique_fonts = font_data.get('uniqueFonts', [])
        web_fonts = font_data.get('webFonts', [])
        system_fonts = font_data.get('systemFonts', [])
        font_faces = font_data.get('fontFaces', [])
        
        summary_label = QLabel(f"📊 Summary: {len(unique_fonts)} font families, {len(web_fonts)} web fonts, {len(system_fonts)} system fonts, {len(font_faces)} @font-face rules")
        summary_label.setStyleSheet("padding: 5px; background-color: #f0f8ff; border-radius: 3px;")
        summary_label.setWordWrap(True)
        layout.addWidget(summary_label)
        
        # Tab widget for different views
        tab_widget = QTabWidget()
        layout.addWidget(tab_widget)
        
        # Overview Tab
        overview_widget = self.create_font_overview_tab(font_data)
        tab_widget.addTab(overview_widget, "📊 Overview")
        
        # Font Families Tab
        families_widget = self.create_font_families_tab(font_data)
        tab_widget.addTab(families_widget, f"🔤 Font Families ({len(unique_fonts)})")
        
        # Elements Tab
        elements_widget = self.create_font_elements_tab(font_data)
        tab_widget.addTab(elements_widget, f"📝 Elements ({len(font_data.get('elements', []))})")
        
        # @font-face Tab
        fontface_widget = self.create_fontface_tab(font_data)
        tab_widget.addTab(fontface_widget, f"⚙️ @font-face ({len(font_faces)})")
        
        # Font Tester Tab
        tester_widget = self.create_font_tester_tab(font_data)
        tab_widget.addTab(tester_widget, "🧪 Font Tester")
        
        # Typography Analysis Tab
        typography_widget = self.create_typography_analysis_tab(font_data)
        tab_widget.addTab(typography_widget, "📐 Typography Analysis")
        
        # Buttons
        button_layout = QHBoxLayout()
        
        export_button = QPushButton("💾 Export Report")
        copy_css_button = QPushButton("📋 Copy CSS")
        refresh_button = QPushButton("🔄 Refresh")
        close_button = QPushButton("❌ Close")
        
        button_layout.addStretch()
        button_layout.addWidget(export_button)
        button_layout.addWidget(copy_css_button)
        button_layout.addWidget(refresh_button)
        button_layout.addWidget(close_button)
        layout.addLayout(button_layout)
        
        def export_report():
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            filename = f"font_analysis_{timestamp}.json"
            
            file_path, _ = QFileDialog.getSaveFileName(
                dialog,
                "Export Font Analysis Report",
                filename,
                "JSON Files (*.json);;Text Files (*.txt);;CSS Files (*.css);;All Files (*.*)"
            )
            
            if file_path:
                try:
                    export_data = {
                        'url': base_url,
                        'timestamp': datetime.now().isoformat(),
                        'font_data': font_data
                    }
                    
                    if file_path.endswith('.json'):
                        with open(file_path, 'w', encoding='utf-8') as f:
                            json.dump(export_data, f, indent=2, ensure_ascii=False)
                    elif file_path.endswith('.css'):
                        with open(file_path, 'w', encoding='utf-8') as f:
                            f.write(self.generate_font_css(font_data))
                    else:
                        # Export as text report
                        with open(file_path, 'w', encoding='utf-8') as f:
                            f.write(self.generate_font_text_report(export_data))
                    
                    self.main_window.status_info.setText(f"✅ Font report exported to: {file_path}")
                    QTimer.singleShot(3000, lambda: self.main_window.status_info.setText(""))
                except Exception as e:
                    self.main_window.status_info.setText(f"❌ Export failed: {str(e)}")
                    QTimer.singleShot(3000, lambda: self.main_window.status_info.setText(""))
        
        def copy_css():
            css_content = self.generate_font_css(font_data)
            from PyQt5.QtWidgets import QApplication
            clipboard = QApplication.clipboard()
            clipboard.setText(css_content)
            self.main_window.status_info.setText("📋 Font CSS copied to clipboard")
            QTimer.singleShot(3000, lambda: self.main_window.status_info.setText(""))
        
        def refresh_fonts():
            dialog.accept()
            # Re-run the font detection
            browser = self.get_current_browser()
            if browser:
                self.detect_fonts(browser)
        
        # Connect buttons
        export_button.clicked.connect(export_report)
        copy_css_button.clicked.connect(copy_css)
        refresh_button.clicked.connect(refresh_fonts)
        close_button.clicked.connect(dialog.accept)
        
        # Show dialog
        dialog.exec_()
        
        # Update main window status
        self.main_window.status_info.setText(f"🔤 Font detection complete - {len(unique_fonts)} fonts found")
        QTimer.singleShot(5000, lambda: self.main_window.status_info.setText(""))
    
    def create_font_overview_tab(self, font_data):
        """Create the overview tab for font analysis"""
        from PyQt5.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QLabel, 
                                   QFrame, QScrollArea)
        from PyQt5.QtCore import Qt
        from PyQt5.QtGui import QFont
        
        widget = QWidget()
        layout = QVBoxLayout(widget)
        
        # Create scroll area
        scroll = QScrollArea()
        scroll_widget = QWidget()
        scroll_layout = QVBoxLayout(scroll_widget)
        
        # Font Families Summary
        families_frame = QFrame()
        families_frame.setStyleSheet("background-color: #f8f9fa; border: 1px solid #dee2e6; border-radius: 5px; padding: 10px;")
        families_layout = QVBoxLayout(families_frame)
        
        families_title = QLabel("🔤 Font Families")
        families_title.setFont(QFont("Arial", 12, QFont.Bold))
        families_layout.addWidget(families_title)
        
        unique_fonts = font_data.get('uniqueFonts', [])
        for font_family in unique_fonts[:10]:  # Show first 10
            font_label = QLabel(f"• {font_family}")
            font_label.setWordWrap(True)
            families_layout.addWidget(font_label)
        
        if len(unique_fonts) > 10:
            more_label = QLabel(f"... and {len(unique_fonts) - 10} more")
            more_label.setStyleSheet("font-style: italic; color: #666;")
            families_layout.addWidget(more_label)
        
        scroll_layout.addWidget(families_frame)
        
        # Web Fonts vs System Fonts
        types_frame = QFrame()
        types_frame.setStyleSheet("background-color: #e8f4fd; border: 1px solid #bee5eb; border-radius: 5px; padding: 10px;")
        types_layout = QVBoxLayout(types_frame)
        
        types_title = QLabel("📊 Font Types")
        types_title.setFont(QFont("Arial", 12, QFont.Bold))
        types_layout.addWidget(types_title)
        
        web_fonts = font_data.get('webFonts', [])
        system_fonts = font_data.get('systemFonts', [])
        
        types_layout.addWidget(QLabel(f"🌐 Web Fonts: {len(web_fonts)}"))
        for font in web_fonts[:5]:
            types_layout.addWidget(QLabel(f"  • {font}"))
        
        types_layout.addWidget(QLabel(f"💻 System Fonts: {len(system_fonts)}"))
        for font in system_fonts[:5]:
            types_layout.addWidget(QLabel(f"  • {font}"))
        
        scroll_layout.addWidget(types_frame)
        
        # Typography Stats
        stats_frame = QFrame()
        stats_frame.setStyleSheet("background-color: #d4edda; border: 1px solid #c3e6cb; border-radius: 5px; padding: 10px;")
        stats_layout = QVBoxLayout(stats_frame)
        
        stats_title = QLabel("📐 Typography Statistics")
        stats_title.setFont(QFont("Arial", 12, QFont.Bold))
        stats_layout.addWidget(stats_title)
        
        font_sizes = font_data.get('fontSizes', [])
        font_weights = font_data.get('fontWeights', [])
        font_styles = font_data.get('fontStyles', [])
        
        stats_layout.addWidget(QLabel(f"Font Sizes: {len(font_sizes)} unique ({', '.join(font_sizes[:5])})"))
        stats_layout.addWidget(QLabel(f"Font Weights: {len(font_weights)} unique ({', '.join(font_weights[:5])})"))
        stats_layout.addWidget(QLabel(f"Font Styles: {len(font_styles)} unique ({', '.join(font_styles)})"))
        
        scroll_layout.addWidget(stats_frame)
        
        # @font-face Rules
        fontface_count = len(font_data.get('fontFaces', []))
        if fontface_count > 0:
            fontface_frame = QFrame()
            fontface_frame.setStyleSheet("background-color: #fff3cd; border: 1px solid #ffeaa7; border-radius: 5px; padding: 10px;")
            fontface_layout = QVBoxLayout(fontface_frame)
            
            fontface_title = QLabel("⚙️ @font-face Declarations")
            fontface_title.setFont(QFont("Arial", 12, QFont.Bold))
            fontface_layout.addWidget(fontface_title)
            
            fontface_layout.addWidget(QLabel(f"Found {fontface_count} @font-face rules"))
            
            for fontface in font_data.get('fontFaces', [])[:3]:
                family = fontface.get('fontFamily', '').replace('"', '').replace("'", '')
                fontface_layout.addWidget(QLabel(f"• {family}"))
            
            scroll_layout.addWidget(fontface_frame)
        
        scroll_layout.addStretch()
        scroll.setWidget(scroll_widget)
        scroll.setWidgetResizable(True)
        
        layout.addWidget(scroll)
        
        return widget
    
    def create_font_families_tab(self, font_data):
        """Create the font families tab"""
        from PyQt5.QtWidgets import (QWidget, QVBoxLayout, QTreeWidget, QTreeWidgetItem, 
                                   QHeaderView, QLabel)
        from PyQt5.QtCore import Qt
        from PyQt5.QtGui import QFont
        
        widget = QWidget()
        layout = QVBoxLayout(widget)
        
        # Header
        header = QLabel("🔤 Font Families Analysis")
        header.setStyleSheet("font-weight: bold; font-size: 14px; padding: 5px;")
        layout.addWidget(header)
        
        # Tree widget for font families
        tree = QTreeWidget()
        tree.setHeaderLabels(['Font Family', 'Type', 'Usage Count', 'Sample Text'])
        tree.header().setSectionResizeMode(0, QHeaderView.Stretch)
        tree.header().setSectionResizeMode(1, QHeaderView.ResizeToContents)
        tree.header().setSectionResizeMode(2, QHeaderView.ResizeToContents)
        tree.header().setSectionResizeMode(3, QHeaderView.Stretch)
        
        unique_fonts = font_data.get('uniqueFonts', [])
        web_fonts = font_data.get('webFonts', [])
        system_fonts = font_data.get('systemFonts', [])
        elements = font_data.get('elements', [])
        
        # Count usage for each font family
        font_usage = {}
        for element in elements:
            font_family = element.get('fontFamily', '')
            if font_family in font_usage:
                font_usage[font_family] += 1
            else:
                font_usage[font_family] = 1
        
        for font_family in unique_fonts:
            item = QTreeWidgetItem()
            item.setText(0, font_family)
            
            # Determine font type
            is_web_font = any(web_font in font_family for web_font in web_fonts)
            is_system_font = any(sys_font in font_family for sys_font in system_fonts)
            
            if is_web_font:
                item.setText(1, "🌐 Web Font")
            elif is_system_font:
                item.setText(1, "💻 System Font")
            else:
                item.setText(1, "❓ Unknown")
            
            # Usage count
            usage_count = font_usage.get(font_family, 0)
            item.setText(2, str(usage_count))
            
            # Sample text
            sample_element = next((el for el in elements if el.get('fontFamily') == font_family), None)
            if sample_element:
                sample_text = sample_element.get('textContent', '')[:50]
                item.setText(3, sample_text + ('...' if len(sample_text) == 50 else ''))
            
            tree.addTopLevelItem(item)
        
        layout.addWidget(tree)
        
        return widget
    
    def create_font_elements_tab(self, font_data):
        """Create the elements tab showing font usage per element"""
        from PyQt5.QtWidgets import (QWidget, QVBoxLayout, QTreeWidget, QTreeWidgetItem, 
                                   QHeaderView, QLabel)
        from PyQt5.QtCore import Qt
        
        widget = QWidget()
        layout = QVBoxLayout(widget)
        
        # Header
        header = QLabel("📝 Elements Font Usage")
        header.setStyleSheet("font-weight: bold; font-size: 14px; padding: 5px;")
        layout.addWidget(header)
        
        # Tree widget for elements
        tree = QTreeWidget()
        tree.setHeaderLabels(['Element', 'Font Family', 'Size', 'Weight', 'Style', 'Color', 'Text Preview'])
        tree.header().setSectionResizeMode(0, QHeaderView.ResizeToContents)
        tree.header().setSectionResizeMode(1, QHeaderView.Stretch)
        tree.header().setSectionResizeMode(2, QHeaderView.ResizeToContents)
        tree.header().setSectionResizeMode(3, QHeaderView.ResizeToContents)
        tree.header().setSectionResizeMode(4, QHeaderView.ResizeToContents)
        tree.header().setSectionResizeMode(5, QHeaderView.ResizeToContents)
        tree.header().setSectionResizeMode(6, QHeaderView.Stretch)
        
        elements = font_data.get('elements', [])
        
        for element in elements[:100]:  # Limit to first 100 for performance
            item = QTreeWidgetItem()
            
            # Element info
            tag_name = element.get('tagName', '')
            class_name = element.get('className', '')
            element_id = element.get('id', '')
            
            element_desc = tag_name
            if element_id:
                element_desc += f"#{element_id}"
            if class_name:
                element_desc += f".{class_name[:20]}"
            
            item.setText(0, element_desc)
            item.setText(1, element.get('fontFamily', ''))
            item.setText(2, element.get('fontSize', ''))
            item.setText(3, element.get('fontWeight', ''))
            item.setText(4, element.get('fontStyle', ''))
            item.setText(5, element.get('color', ''))
            
            # Text preview
            text_content = element.get('textContent', '')
            item.setText(6, text_content[:60] + ('...' if len(text_content) > 60 else ''))
            
            tree.addTopLevelItem(item)
        
        if len(elements) > 100:
            info_label = QLabel(f"Showing first 100 elements out of {len(elements)} total")
            info_label.setStyleSheet("font-style: italic; color: #666; padding: 5px;")
            layout.addWidget(info_label)
        
        layout.addWidget(tree)
        
        return widget
    
    def create_fontface_tab(self, font_data):
        """Create the @font-face tab"""
        from PyQt5.QtWidgets import (QWidget, QVBoxLayout, QTextEdit, QLabel, 
                                   QTreeWidget, QTreeWidgetItem, QHeaderView)
        from PyQt5.QtCore import Qt
        
        widget = QWidget()
        layout = QVBoxLayout(widget)
        
        # Header
        header = QLabel("⚙️ @font-face Declarations")
        header.setStyleSheet("font-weight: bold; font-size: 14px; padding: 5px;")
        layout.addWidget(header)
        
        font_faces = font_data.get('fontFaces', [])
        
        if not font_faces:
            no_fontface_label = QLabel("❌ No @font-face declarations found.\n\nThis page is using system fonts or web fonts loaded via external services.")
            no_fontface_label.setStyleSheet("padding: 20px; background-color: #f8d7da; border-radius: 5px; color: #721c24;")
            no_fontface_label.setWordWrap(True)
            layout.addWidget(no_fontface_label)
        else:
            # Tree widget for @font-face rules
            tree = QTreeWidget()
            tree.setHeaderLabels(['Font Family', 'Source', 'Weight', 'Style', 'Display'])
            tree.header().setSectionResizeMode(0, QHeaderView.ResizeToContents)
            tree.header().setSectionResizeMode(1, QHeaderView.Stretch)
            tree.header().setSectionResizeMode(2, QHeaderView.ResizeToContents)
            tree.header().setSectionResizeMode(3, QHeaderView.ResizeToContents)
            tree.header().setSectionResizeMode(4, QHeaderView.ResizeToContents)
            
            for fontface in font_faces:
                item = QTreeWidgetItem()
                
                family = fontface.get('fontFamily', '').replace('"', '').replace("'", '')
                item.setText(0, family)
                
                src = fontface.get('src', '')
                # Extract URL from src if present
                if 'url(' in src:
                    import re
                    urls = re.findall(r'url\(["\']?([^"\']+)["\']?\)', src)
                    if urls:
                        src = urls[0]
                        if len(src) > 50:
                            src = '...' + src[-47:]
                
                item.setText(1, src)
                item.setText(2, fontface.get('fontWeight', ''))
                item.setText(3, fontface.get('fontStyle', ''))
                item.setText(4, fontface.get('fontDisplay', ''))
                
                tree.addTopLevelItem(item)
            
            layout.addWidget(tree)
            
            # CSS Preview
            css_label = QLabel("📋 Generated CSS:")
            css_label.setStyleSheet("font-weight: bold; margin-top: 10px;")
            layout.addWidget(css_label)
            
            css_text = QTextEdit()
            css_text.setReadOnly(True)
            css_text.setMaximumHeight(150)
            css_text.setStyleSheet("font-family: monospace; background-color: #f8f9fa;")
            
            css_content = self.generate_fontface_css(font_faces)
            css_text.setPlainText(css_content)
            
            layout.addWidget(css_text)
        
        return widget
    
    def create_font_tester_tab(self, font_data):
        """Create the font tester tab"""
        from PyQt5.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QLabel, 
                                   QComboBox, QSpinBox, QTextEdit, QCheckBox,
                                   QPushButton, QColorDialog, QFrame)
        from PyQt5.QtCore import Qt
        from PyQt5.QtGui import QFont, QColor
        
        widget = QWidget()
        layout = QVBoxLayout(widget)
        
        # Header
        header = QLabel("🧪 Font Tester")
        header.setStyleSheet("font-weight: bold; font-size: 14px; padding: 5px;")
        layout.addWidget(header)
        
        # Controls frame
        controls_frame = QFrame()
        controls_frame.setStyleSheet("background-color: #f8f9fa; border: 1px solid #dee2e6; border-radius: 5px; padding: 10px;")
        controls_layout = QVBoxLayout(controls_frame)
        
        # Font family selector
        font_row = QHBoxLayout()
        font_row.addWidget(QLabel("Font Family:"))
        
        font_combo = QComboBox()
        font_combo.setEditable(True)
        unique_fonts = font_data.get('uniqueFonts', [])
        for font_family in unique_fonts:
            font_combo.addItem(font_family)
        font_row.addWidget(font_combo)
        
        controls_layout.addLayout(font_row)
        
        # Size and weight controls
        size_weight_row = QHBoxLayout()
        
        size_weight_row.addWidget(QLabel("Size:"))
        size_spin = QSpinBox()
        size_spin.setRange(8, 72)
        size_spin.setValue(16)
        size_weight_row.addWidget(size_spin)
        
        size_weight_row.addWidget(QLabel("Weight:"))
        weight_combo = QComboBox()
        weights = ['normal', 'bold', '100', '200', '300', '400', '500', '600', '700', '800', '900']
        weight_combo.addItems(weights)
        size_weight_row.addWidget(weight_combo)
        
        controls_layout.addLayout(size_weight_row)
        
        # Style controls
        style_row = QHBoxLayout()
        
        italic_cb = QCheckBox("Italic")
        underline_cb = QCheckBox("Underline")
        
        color_btn = QPushButton("Text Color")
        color_btn.setStyleSheet("background-color: #000000; color: white;")
        
        style_row.addWidget(italic_cb)
        style_row.addWidget(underline_cb)
        style_row.addWidget(color_btn)
        style_row.addStretch()
        
        controls_layout.addLayout(style_row)
        
        layout.addWidget(controls_frame)
        
        # Preview text area
        preview_label = QLabel("Preview:")
        preview_label.setStyleSheet("font-weight: bold; margin-top: 10px;")
        layout.addWidget(preview_label)
        
        preview_text = QTextEdit()
        preview_text.setPlainText("The quick brown fox jumps over the lazy dog.\nABCDEFGHIJKLMNOPQRSTUVWXYZ\nabcdefghijklmnopqrstuvwxyz\n0123456789")
        preview_text.setMinimumHeight(200)
        layout.addWidget(preview_text)
        
        # Current color for color picker
        current_color = QColor(0, 0, 0)
        
        def update_preview():
            font_family = font_combo.currentText()
            font_size = size_spin.value()
            font_weight = weight_combo.currentText()
            is_italic = italic_cb.isChecked()
            is_underline = underline_cb.isChecked()
            
            # Create font
            font = QFont()
            font.setFamily(font_family)
            font.setPointSize(font_size)
            
            if font_weight == 'bold':
                font.setBold(True)
            elif font_weight.isdigit():
                font.setWeight(int(font_weight) // 10)
            
            font.setItalic(is_italic)
            font.setUnderline(is_underline)
            
            preview_text.setFont(font)
            
            # Set text color
            palette = preview_text.palette()
            palette.setColor(palette.Text, current_color)
            preview_text.setPalette(palette)
        
        def choose_color():
            nonlocal current_color
            color = QColorDialog.getColor(current_color, widget)
            if color.isValid():
                current_color = color
                color_btn.setStyleSheet(f"background-color: {color.name()}; color: {'white' if color.lightness() < 128 else 'black'};")
                update_preview()
        
        # Connect controls
        font_combo.currentTextChanged.connect(update_preview)
        size_spin.valueChanged.connect(update_preview)
        weight_combo.currentTextChanged.connect(update_preview)
        italic_cb.toggled.connect(update_preview)
        underline_cb.toggled.connect(update_preview)
        color_btn.clicked.connect(choose_color)
        
        # Initial preview update
        update_preview()
        
        return widget
    
    def create_typography_analysis_tab(self, font_data):
        """Create the typography analysis tab"""
        from PyQt5.QtWidgets import (QWidget, QVBoxLayout, QLabel, QFrame, QScrollArea)
        from PyQt5.QtCore import Qt
        from PyQt5.QtGui import QFont
        
        widget = QWidget()
        layout = QVBoxLayout(widget)
        
        # Header
        header = QLabel("📐 Typography Analysis")
        header.setStyleSheet("font-weight: bold; font-size: 14px; padding: 5px;")
        layout.addWidget(header)
        
        # Create scroll area
        scroll = QScrollArea()
        scroll_widget = QWidget()
        scroll_layout = QVBoxLayout(scroll_widget)
        
        # Font Size Analysis
        sizes_frame = QFrame()
        sizes_frame.setStyleSheet("background-color: #f8f9fa; border: 1px solid #dee2e6; border-radius: 5px; padding: 10px;")
        sizes_layout = QVBoxLayout(sizes_frame)
        
        sizes_title = QLabel("📏 Font Size Analysis")
        sizes_title.setFont(QFont("Arial", 12, QFont.Bold))
        sizes_layout.addWidget(sizes_title)
        
        font_sizes = font_data.get('fontSizes', [])
        elements = font_data.get('elements', [])
        
        # Parse and analyze font sizes
        size_usage = {}
        for element in elements:
            size = element.get('fontSize', '')
            if size in size_usage:
                size_usage[size] += 1
            else:
                size_usage[size] = 1
        
        # Sort by usage
        sorted_sizes = sorted(size_usage.items(), key=lambda x: x[1], reverse=True)
        
        sizes_layout.addWidget(QLabel(f"Total unique font sizes: {len(font_sizes)}"))
        sizes_layout.addWidget(QLabel("Most used sizes:"))
        
        for size, count in sorted_sizes[:10]:
            sizes_layout.addWidget(QLabel(f"  • {size}: {count} elements"))
        
        scroll_layout.addWidget(sizes_frame)
        
        # Font Weight Analysis
        weights_frame = QFrame()
        weights_frame.setStyleSheet("background-color: #e8f4fd; border: 1px solid #bee5eb; border-radius: 5px; padding: 10px;")
        weights_layout = QVBoxLayout(weights_frame)
        
        weights_title = QLabel("⚖️ Font Weight Analysis")
        weights_title.setFont(QFont("Arial", 12, QFont.Bold))
        weights_layout.addWidget(weights_title)
        
        font_weights = font_data.get('fontWeights', [])
        
        # Analyze font weights
        weight_usage = {}
        for element in elements:
            weight = element.get('fontWeight', '')
            if weight in weight_usage:
                weight_usage[weight] += 1
            else:
                weight_usage[weight] = 1
        
        sorted_weights = sorted(weight_usage.items(), key=lambda x: x[1], reverse=True)
        
        weights_layout.addWidget(QLabel(f"Total unique font weights: {len(font_weights)}"))
        weights_layout.addWidget(QLabel("Weight distribution:"))
        
        for weight, count in sorted_weights:
            weights_layout.addWidget(QLabel(f"  • {weight}: {count} elements"))
        
        scroll_layout.addWidget(weights_frame)
        
        # Typography Recommendations
        recommendations_frame = QFrame()
        recommendations_frame.setStyleSheet("background-color: #d1ecf1; border: 1px solid #bee5eb; border-radius: 5px; padding: 10px;")
        recommendations_layout = QVBoxLayout(recommendations_frame)
        
        recommendations_title = QLabel("💡 Typography Recommendations")
        recommendations_title.setFont(QFont("Arial", 12, QFont.Bold))
        recommendations_layout.addWidget(recommendations_title)
        
        # Generate recommendations
        recommendations = []
        
        if len(font_data.get('uniqueFonts', [])) > 5:
            recommendations.append("Consider reducing the number of font families for better consistency")
        
        if len(font_sizes) > 8:
            recommendations.append("Too many font sizes detected - consider using a typographic scale")
        
        web_fonts = font_data.get('webFonts', [])
        if len(web_fonts) > 3:
            recommendations.append("Multiple web fonts may impact page load performance")
        
        if not font_data.get('fontFaces'):
            recommendations.append("Consider using @font-face for better font loading control")
        
        if not recommendations:
            recommendations.append("Typography looks well-organized!")
        
        for rec in recommendations:
            rec_label = QLabel(f"• {rec}")
            rec_label.setWordWrap(True)
            recommendations_layout.addWidget(rec_label)
        
        scroll_layout.addWidget(recommendations_frame)
        
        scroll_layout.addStretch()
        scroll.setWidget(scroll_widget)
        scroll.setWidgetResizable(True)
        
        layout.addWidget(scroll)
        
        return widget
    
    def generate_font_css(self, font_data):
        """Generate CSS based on detected fonts"""
        css_lines = []
        css_lines.append("/* Generated CSS from Font Detector */")
        css_lines.append("")
        
        # @font-face rules
        font_faces = font_data.get('fontFaces', [])
        if font_faces:
            css_lines.append("/* @font-face declarations */")
            for fontface in font_faces:
                css_lines.append("@font-face {")
                if fontface.get('fontFamily'):
                    css_lines.append(f"  font-family: {fontface['fontFamily']};")
                if fontface.get('src'):
                    css_lines.append(f"  src: {fontface['src']};")
                if fontface.get('fontWeight'):
                    css_lines.append(f"  font-weight: {fontface['fontWeight']};")
                if fontface.get('fontStyle'):
                    css_lines.append(f"  font-style: {fontface['fontStyle']};")
                if fontface.get('fontDisplay'):
                    css_lines.append(f"  font-display: {fontface['fontDisplay']};")
                css_lines.append("}")
                css_lines.append("")
        
        # Font family variables
        unique_fonts = font_data.get('uniqueFonts', [])
        if unique_fonts:
            css_lines.append("/* CSS Custom Properties for Font Families */")
            css_lines.append(":root {")
            for i, font_family in enumerate(unique_fonts[:5]):  # Limit to first 5
                var_name = f"--font-family-{i+1}"
                css_lines.append(f"  {var_name}: {font_family};")
            css_lines.append("}")
            css_lines.append("")
        
        return '\n'.join(css_lines)
    
    def generate_fontface_css(self, font_faces):
        """Generate CSS for @font-face rules"""
        css_lines = []
        
        for fontface in font_faces:
            css_lines.append("@font-face {")
            if fontface.get('fontFamily'):
                css_lines.append(f"  font-family: {fontface['fontFamily']};")
            if fontface.get('src'):
                css_lines.append(f"  src: {fontface['src']};")
            if fontface.get('fontWeight'):
                css_lines.append(f"  font-weight: {fontface['fontWeight']};")
            if fontface.get('fontStyle'):
                css_lines.append(f"  font-style: {fontface['fontStyle']};")
            if fontface.get('fontDisplay'):
                css_lines.append(f"  font-display: {fontface['fontDisplay']};")
            css_lines.append("}")
            css_lines.append("")
        
        return '\n'.join(css_lines)
    
    def generate_font_text_report(self, export_data):
        """Generate a text-based font report"""
        lines = []
        lines.append("FONT ANALYSIS REPORT")
        lines.append("=" * 50)
        lines.append(f"URL: {export_data['url']}")
        lines.append(f"Analysis Date: {export_data['timestamp']}")
        lines.append("")
        
        font_data = export_data['font_data']
        
        # Summary
        unique_fonts = font_data.get('uniqueFonts', [])
        web_fonts = font_data.get('webFonts', [])
        system_fonts = font_data.get('systemFonts', [])
        font_faces = font_data.get('fontFaces', [])
        
        lines.append("SUMMARY:")
        lines.append("-" * 20)
        lines.append(f"Total Font Families: {len(unique_fonts)}")
        lines.append(f"Web Fonts: {len(web_fonts)}")
        lines.append(f"System Fonts: {len(system_fonts)}")
        lines.append(f"@font-face Rules: {len(font_faces)}")
        lines.append("")
        
        # Font families
        if unique_fonts:
            lines.append("FONT FAMILIES:")
            lines.append("-" * 20)
            for font_family in unique_fonts:
                lines.append(f"• {font_family}")
            lines.append("")
        
        # Web fonts
        if web_fonts:
            lines.append("WEB FONTS:")
            lines.append("-" * 20)
            for font in web_fonts:
                lines.append(f"• {font}")
            lines.append("")
        
        # Typography stats
        font_sizes = font_data.get('fontSizes', [])
        font_weights = font_data.get('fontWeights', [])
        
        lines.append("TYPOGRAPHY STATISTICS:")
        lines.append("-" * 20)
        lines.append(f"Font Sizes: {len(font_sizes)} unique")
        lines.append(f"Font Weights: {len(font_weights)} unique")
        lines.append("")
        
        return '\n'.join(lines)
    
    def detect_technologies(self, browser):
        """Detect technologies used on the current website"""
        try:
            page = browser.page()
            current_url = browser.url().toString()
            
            # Show initial status
            self.main_window.status_info.setText("🔧 Detecting technologies...")
            
            # JavaScript to detect technologies
            js_code = """
            (function() {
                var techData = {
                    url: window.location.href,
                    title: document.title,
                    frameworks: [],
                    libraries: [],
                    cms: [],
                    analytics: [],
                    advertising: [],
                    cdn: [],
                    webServer: [],
                    programming: [],
                    databases: [],
                    security: [],
                    performance: [],
                    ui: [],
                    fonts: [],
                    meta: {
                        viewport: '',
                        charset: '',
                        generator: '',
                        description: '',
                        keywords: ''
                    },
                    scripts: [],
                    stylesheets: [],
                    images: [],
                    technologies: {},
                    headers: {},
                    cookies: []
                };
                
                // Detect meta information
                var metaTags = document.getElementsByTagName('meta');
                for (var i = 0; i < metaTags.length; i++) {
                    var meta = metaTags[i];
                    var name = meta.getAttribute('name') || meta.getAttribute('property') || meta.getAttribute('http-equiv');
                    var content = meta.getAttribute('content') || '';
                    
                    if (name) {
                        switch(name.toLowerCase()) {
                            case 'viewport':
                                techData.meta.viewport = content;
                                break;
                            case 'generator':
                                techData.meta.generator = content;
                                break;
                            case 'description':
                                techData.meta.description = content;
                                break;
                            case 'keywords':
                                techData.meta.keywords = content;
                                break;
                        }
                    }
                    
                    if (meta.getAttribute('charset')) {
                        techData.meta.charset = meta.getAttribute('charset');
                    }
                }
                
                // Detect scripts
                var scripts = document.getElementsByTagName('script');
                for (var i = 0; i < scripts.length; i++) {
                    var script = scripts[i];
                    var src = script.src || '';
                    var content = script.textContent || script.innerHTML || '';
                    
                    if (src) {
                        techData.scripts.push({
                            type: 'external',
                            src: src,
                            async: script.async || false,
                            defer: script.defer || false
                        });
                    } else if (content.trim()) {
                        techData.scripts.push({
                            type: 'inline',
                            content: content.substring(0, 200) + (content.length > 200 ? '...' : ''),
                            size: content.length
                        });
                    }
                }
                
                // Detect stylesheets
                var links = document.getElementsByTagName('link');
                for (var i = 0; i < links.length; i++) {
                    var link = links[i];
                    if (link.rel === 'stylesheet') {
                        techData.stylesheets.push({
                            href: link.href || '',
                            media: link.media || 'all'
                        });
                    }
                }
                
                // Detect images
                var images = document.getElementsByTagName('img');
                var imageFormats = {};
                for (var i = 0; i < images.length; i++) {
                    var img = images[i];
                    var src = img.src || '';
                    if (src) {
                        var ext = src.split('.').pop().split('?')[0].toLowerCase();
                        imageFormats[ext] = (imageFormats[ext] || 0) + 1;
                    }
                }
                techData.images = imageFormats;
                
                // Technology detection patterns
                var detectionPatterns = {
                    // JavaScript Frameworks
                    'React': function() {
                        return !!(window.React || window.ReactDOM || document.querySelector('[data-reactroot]') || 
                                document.querySelector('script[src*="react"]'));
                    },
                    'Vue.js': function() {
                        return !!(window.Vue || document.querySelector('[data-v-]') || 
                                document.querySelector('script[src*="vue"]'));
                    },
                    'Angular': function() {
                        return !!(window.angular || window.ng || document.querySelector('[ng-app]') || 
                                document.querySelector('script[src*="angular"]'));
                    },
                    'AngularJS': function() {
                        return !!(window.angular && !window.ng);
                    },
                    'Svelte': function() {
                        return !!(document.querySelector('script[src*="svelte"]') || 
                                document.querySelector('[class*="svelte-"]'));
                    },
                    'Next.js': function() {
                        return !!(window.__NEXT_DATA__ || document.querySelector('script[src*="next"]'));
                    },
                    'Nuxt.js': function() {
                        return !!(window.$nuxt || document.querySelector('script[src*="nuxt"]'));
                    },
                    
                    // JavaScript Libraries
                    'jQuery': function() {
                        return !!(window.jQuery || window.$);
                    },
                    'Lodash': function() {
                        return !!(window._ && window._.VERSION);
                    },
                    'Moment.js': function() {
                        return !!(window.moment);
                    },
                    'D3.js': function() {
                        return !!(window.d3);
                    },
                    'Three.js': function() {
                        return !!(window.THREE);
                    },
                    'Chart.js': function() {
                        return !!(window.Chart);
                    },
                    'Axios': function() {
                        return !!(window.axios);
                    },
                    
                    // CSS Frameworks
                    'Bootstrap': function() {
                        return !!(document.querySelector('link[href*="bootstrap"]') || 
                                document.querySelector('.container, .row, .col-') ||
                                document.querySelector('script[src*="bootstrap"]'));
                    },
                    'Tailwind CSS': function() {
                        return !!(document.querySelector('link[href*="tailwind"]') || 
                                document.querySelector('[class*="tw-"], [class*="bg-"], [class*="text-"]'));
                    },
                    'Bulma': function() {
                        return !!(document.querySelector('link[href*="bulma"]') || 
                                document.querySelector('.column, .columns'));
                    },
                    'Foundation': function() {
                        return !!(document.querySelector('link[href*="foundation"]') || 
                                document.querySelector('.foundation-'));
                    },
                    'Materialize': function() {
                        return !!(document.querySelector('link[href*="materialize"]') || 
                                document.querySelector('.material-'));
                    },
                    
                    // Content Management Systems
                    'WordPress': function() {
                        return !!(document.querySelector('link[href*="wp-content"]') || 
                                document.querySelector('script[src*="wp-"]') ||
                                techData.meta.generator.toLowerCase().includes('wordpress'));
                    },
                    'Drupal': function() {
                        return !!(document.querySelector('script[src*="drupal"]') || 
                                techData.meta.generator.toLowerCase().includes('drupal'));
                    },
                    'Joomla': function() {
                        return !!(document.querySelector('script[src*="joomla"]') || 
                                techData.meta.generator.toLowerCase().includes('joomla'));
                    },
                    'Shopify': function() {
                        return !!(window.Shopify || document.querySelector('script[src*="shopify"]'));
                    },
                    'Magento': function() {
                        return !!(window.Magento || document.querySelector('script[src*="magento"]'));
                    },
                    
                    // Analytics & Tracking
                    'Google Analytics': function() {
                        return !!(window.gtag || window.ga || window.GoogleAnalyticsObject || 
                                document.querySelector('script[src*="google-analytics"]') ||
                                document.querySelector('script[src*="gtag"]'));
                    },
                    'Google Tag Manager': function() {
                        return !!(window.dataLayer || document.querySelector('script[src*="googletagmanager"]'));
                    },
                    'Facebook Pixel': function() {
                        return !!(window.fbq || document.querySelector('script[src*="facebook"]'));
                    },
                    'Hotjar': function() {
                        return !!(window.hj || document.querySelector('script[src*="hotjar"]'));
                    },
                    'Mixpanel': function() {
                        return !!(window.mixpanel);
                    },
                    
                    // CDNs
                    'Cloudflare': function() {
                        return !!(document.querySelector('script[src*="cloudflare"]') || 
                                document.querySelector('link[href*="cloudflare"]'));
                    },
                    'jsDelivr': function() {
                        return !!(document.querySelector('script[src*="jsdelivr"]') || 
                                document.querySelector('link[href*="jsdelivr"]'));
                    },
                    'unpkg': function() {
                        return !!(document.querySelector('script[src*="unpkg"]') || 
                                document.querySelector('link[href*="unpkg"]'));
                    },
                    'cdnjs': function() {
                        return !!(document.querySelector('script[src*="cdnjs"]') || 
                                document.querySelector('link[href*="cdnjs"]'));
                    },
                    
                    // Fonts
                    'Google Fonts': function() {
                        return !!(document.querySelector('link[href*="fonts.googleapis"]') || 
                                document.querySelector('link[href*="fonts.gstatic"]'));
                    },
                    'Adobe Fonts': function() {
                        return !!(document.querySelector('script[src*="typekit"]') || 
                                document.querySelector('link[href*="typekit"]'));
                    },
                    'Font Awesome': function() {
                        return !!(document.querySelector('link[href*="font-awesome"]') || 
                                document.querySelector('script[src*="font-awesome"]') ||
                                document.querySelector('[class*="fa-"]'));
                    },
                    
                    // Build Tools & Bundlers (detectable traces)
                    'Webpack': function() {
                        return !!(window.webpackJsonp || document.querySelector('script[src*="webpack"]'));
                    },
                    'Vite': function() {
                        return !!(document.querySelector('script[src*="vite"]') || 
                                document.querySelector('script[type="module"][src*="@vite"]'));
                    },
                    'Parcel': function() {
                        return !!(document.querySelector('script[src*="parcel"]'));
                    },
                    
                    // Payment Systems
                    'Stripe': function() {
                        return !!(window.Stripe || document.querySelector('script[src*="stripe"]'));
                    },
                    'PayPal': function() {
                        return !!(window.paypal || document.querySelector('script[src*="paypal"]'));
                    },
                    
                    // Maps
                    'Google Maps': function() {
                        return !!(window.google && window.google.maps || 
                                document.querySelector('script[src*="maps.googleapis"]'));
                    },
                    'Mapbox': function() {
                        return !!(window.mapboxgl || document.querySelector('script[src*="mapbox"]'));
                    },
                    
                    // Social Media
                    'Twitter Widgets': function() {
                        return !!(window.twttr || document.querySelector('script[src*="twitter"]'));
                    },
                    'Facebook SDK': function() {
                        return !!(window.FB || document.querySelector('script[src*="facebook"]'));
                    },
                    
                    // Security
                    'reCAPTCHA': function() {
                        return !!(window.grecaptcha || document.querySelector('script[src*="recaptcha"]'));
                    },
                    
                    // Performance
                    'Service Worker': function() {
                        return !!('serviceWorker' in navigator && navigator.serviceWorker.controller);
                    },
                    'Web Workers': function() {
                        return !!(window.Worker);
                    },
                    'WebAssembly': function() {
                        return !!(window.WebAssembly);
                    }
                };
                
                // Run detection
                for (var tech in detectionPatterns) {
                    try {
                        if (detectionPatterns[tech]()) {
                            techData.technologies[tech] = {
                                detected: true,
                                confidence: 'high'
                            };
                        }
                    } catch (e) {
                        // Ignore detection errors
                    }
                }
                
                // Analyze script sources for additional technologies
                techData.scripts.forEach(function(script) {
                    if (script.type === 'external' && script.src) {
                        var src = script.src.toLowerCase();
                        
                        // Additional detections based on script URLs
                        if (src.includes('jquery')) techData.technologies['jQuery'] = {detected: true, confidence: 'high'};
                        if (src.includes('bootstrap')) techData.technologies['Bootstrap'] = {detected: true, confidence: 'high'};
                        if (src.includes('react')) techData.technologies['React'] = {detected: true, confidence: 'high'};
                        if (src.includes('vue')) techData.technologies['Vue.js'] = {detected: true, confidence: 'high'};
                        if (src.includes('angular')) techData.technologies['Angular'] = {detected: true, confidence: 'high'};
                        if (src.includes('lodash')) techData.technologies['Lodash'] = {detected: true, confidence: 'high'};
                        if (src.includes('moment')) techData.technologies['Moment.js'] = {detected: true, confidence: 'high'};
                        if (src.includes('d3')) techData.technologies['D3.js'] = {detected: true, confidence: 'high'};
                        if (src.includes('three')) techData.technologies['Three.js'] = {detected: true, confidence: 'high'};
                        if (src.includes('chart')) techData.technologies['Chart.js'] = {detected: true, confidence: 'high'};
                    }
                });
                
                // Analyze stylesheets
                techData.stylesheets.forEach(function(stylesheet) {
                    if (stylesheet.href) {
                        var href = stylesheet.href.toLowerCase();
                        
                        if (href.includes('bootstrap')) techData.technologies['Bootstrap'] = {detected: true, confidence: 'high'};
                        if (href.includes('tailwind')) techData.technologies['Tailwind CSS'] = {detected: true, confidence: 'high'};
                        if (href.includes('bulma')) techData.technologies['Bulma'] = {detected: true, confidence: 'high'};
                        if (href.includes('foundation')) techData.technologies['Foundation'] = {detected: true, confidence: 'high'};
                        if (href.includes('materialize')) techData.technologies['Materialize'] = {detected: true, confidence: 'high'};
                        if (href.includes('font-awesome')) techData.technologies['Font Awesome'] = {detected: true, confidence: 'high'};
                    }
                });
                
                // Get cookies
                if (document.cookie) {
                    var cookies = document.cookie.split(';');
                    cookies.forEach(function(cookie) {
                        var parts = cookie.trim().split('=');
                        if (parts.length >= 2) {
                            techData.cookies.push({
                                name: parts[0],
                                value: parts[1].substring(0, 50) + (parts[1].length > 50 ? '...' : '')
                            });
                        }
                    });
                }
                
                // Categorize technologies
                var categories = {
                    'JavaScript Frameworks': ['React', 'Vue.js', 'Angular', 'AngularJS', 'Svelte', 'Next.js', 'Nuxt.js'],
                    'JavaScript Libraries': ['jQuery', 'Lodash', 'Moment.js', 'D3.js', 'Three.js', 'Chart.js', 'Axios'],
                    'CSS Frameworks': ['Bootstrap', 'Tailwind CSS', 'Bulma', 'Foundation', 'Materialize'],
                    'Content Management': ['WordPress', 'Drupal', 'Joomla', 'Shopify', 'Magento'],
                    'Analytics & Tracking': ['Google Analytics', 'Google Tag Manager', 'Facebook Pixel', 'Hotjar', 'Mixpanel'],
                    'CDN & Hosting': ['Cloudflare', 'jsDelivr', 'unpkg', 'cdnjs'],
                    'Fonts & Icons': ['Google Fonts', 'Adobe Fonts', 'Font Awesome'],
                    'Build Tools': ['Webpack', 'Vite', 'Parcel'],
                    'Payment Systems': ['Stripe', 'PayPal'],
                    'Maps & Location': ['Google Maps', 'Mapbox'],
                    'Social Media': ['Twitter Widgets', 'Facebook SDK'],
                    'Security': ['reCAPTCHA'],
                    'Performance': ['Service Worker', 'Web Workers', 'WebAssembly']
                };
                
                techData.categories = {};
                for (var category in categories) {
                    techData.categories[category] = [];
                    categories[category].forEach(function(tech) {
                        if (techData.technologies[tech] && techData.technologies[tech].detected) {
                            techData.categories[category].push(tech);
                        }
                    });
                }
                
                return techData;
            })();
            """
            
            def process_tech_data(tech_data):
                if not tech_data:
                    self.main_window.status_info.setText("❌ Failed to detect technologies")
                    QTimer.singleShot(3000, lambda: self.main_window.status_info.setText(""))
                    return
                
                # Create and show the technology detector dialog
                self.show_technology_detector_dialog(tech_data, current_url)
            
            # Execute JavaScript to get technology data
            page.runJavaScript(js_code, process_tech_data)
            
        except Exception as e:
            self.main_window.status_info.setText(f"❌ Technology detection error: {str(e)}")
            QTimer.singleShot(3000, lambda: self.main_window.status_info.setText(""))
    
    def show_technology_detector_dialog(self, tech_data, base_url):
        """Show dialog with technology detection results"""
        from PyQt5.QtWidgets import (QDialog, QVBoxLayout, QHBoxLayout, QLabel, 
                                   QTextEdit, QPushButton, QTabWidget, QWidget,
                                   QTreeWidget, QTreeWidgetItem, QHeaderView, 
                                   QFileDialog, QScrollArea, QFrame, QProgressBar)
        from PyQt5.QtCore import Qt, QTimer
        from PyQt5.QtGui import QFont, QColor
        from datetime import datetime
        import json
        
        # Count detected technologies
        detected_count = len([tech for tech, data in tech_data.get('technologies', {}).items() if data.get('detected')])
        
        # Create dialog
        dialog = QDialog(self.main_window)
        dialog.setWindowTitle(f"🔧 Technology Detector - {detected_count} technologies found")
        dialog.setMinimumSize(900, 700)
        dialog.resize(1200, 800)
        
        layout = QVBoxLayout(dialog)
        
        # Header
        header_label = QLabel(f"Technology Analysis for: {base_url}")
        header_label.setStyleSheet("font-weight: bold; padding: 10px; background-color: #e8f4fd; border-radius: 5px;")
        header_label.setWordWrap(True)
        layout.addWidget(header_label)
        
        # Summary
        scripts_count = len(tech_data.get('scripts', []))
        stylesheets_count = len(tech_data.get('stylesheets', []))
        cookies_count = len(tech_data.get('cookies', []))
        
        summary_label = QLabel(f"📊 Summary: {detected_count} technologies, {scripts_count} scripts, {stylesheets_count} stylesheets, {cookies_count} cookies")
        summary_label.setStyleSheet("padding: 5px; background-color: #f0f8ff; border-radius: 3px;")
        summary_label.setWordWrap(True)
        layout.addWidget(summary_label)
        
        # Tab widget for different views
        tab_widget = QTabWidget()
        layout.addWidget(tab_widget)
        
        # Overview Tab
        overview_widget = self.create_tech_overview_tab(tech_data)
        tab_widget.addTab(overview_widget, "📊 Overview")
        
        # Technologies Tab
        technologies_widget = self.create_technologies_tab(tech_data)
        tab_widget.addTab(technologies_widget, f"🔧 Technologies ({detected_count})")
        
        # Buttons
        button_layout = QHBoxLayout()
        
        export_button = QPushButton("💾 Export Report")
        copy_button = QPushButton("📋 Copy Summary")
        refresh_button = QPushButton("🔄 Re-analyze")
        close_button = QPushButton("❌ Close")
        
        button_layout.addStretch()
        button_layout.addWidget(export_button)
        button_layout.addWidget(copy_button)
        button_layout.addWidget(refresh_button)
        button_layout.addWidget(close_button)
        layout.addLayout(button_layout)
        
        def export_report():
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            filename = f"tech_analysis_{timestamp}.json"
            
            file_path, _ = QFileDialog.getSaveFileName(
                dialog,
                "Export Technology Analysis Report",
                filename,
                "JSON Files (*.json);;Text Files (*.txt);;All Files (*.*)"
            )
            
            if file_path:
                try:
                    export_data = {
                        'url': base_url,
                        'timestamp': datetime.now().isoformat(),
                        'tech_data': tech_data
                    }
                    
                    if file_path.endswith('.json'):
                        with open(file_path, 'w', encoding='utf-8') as f:
                            json.dump(export_data, f, indent=2, ensure_ascii=False)
                    else:
                        # Export as text report
                        with open(file_path, 'w', encoding='utf-8') as f:
                            f.write(self.generate_tech_text_report(export_data))
                    
                    self.main_window.status_info.setText(f"✅ Technology report exported to: {file_path}")
                    QTimer.singleShot(3000, lambda: self.main_window.status_info.setText(""))
                except Exception as e:
                    self.main_window.status_info.setText(f"❌ Export failed: {str(e)}")
                    QTimer.singleShot(3000, lambda: self.main_window.status_info.setText(""))
        
        def copy_summary():
            summary_text = self.generate_tech_summary(tech_data, base_url)
            from PyQt5.QtWidgets import QApplication
            clipboard = QApplication.clipboard()
            clipboard.setText(summary_text)
            self.main_window.status_info.setText("📋 Technology summary copied to clipboard")
            QTimer.singleShot(3000, lambda: self.main_window.status_info.setText(""))
        
        def refresh_analysis():
            dialog.accept()
            # Re-run the analysis
            browser = self.get_current_browser()
            if browser:
                self.detect_technologies(browser)
        
        # Connect buttons
        export_button.clicked.connect(export_report)
        copy_button.clicked.connect(copy_summary)
        refresh_button.clicked.connect(refresh_analysis)
        close_button.clicked.connect(dialog.accept)
        
        # Show dialog
        dialog.exec_()
        
        # Update main window status
        self.main_window.status_info.setText(f"🔧 Technology detection complete - {detected_count} technologies found")
        QTimer.singleShot(5000, lambda: self.main_window.status_info.setText(""))
    
    def create_tech_overview_tab(self, tech_data):
        """Create the overview tab for technology analysis"""
        from PyQt5.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QLabel, 
                                   QFrame, QScrollArea)
        from PyQt5.QtCore import Qt
        from PyQt5.QtGui import QFont
        
        widget = QWidget()
        layout = QVBoxLayout(widget)
        
        # Create scroll area
        scroll = QScrollArea()
        scroll_widget = QWidget()
        scroll_layout = QVBoxLayout(scroll_widget)
        
        # Basic Information
        basic_frame = QFrame()
        basic_frame.setStyleSheet("background-color: #f8f9fa; border: 1px solid #dee2e6; border-radius: 5px; padding: 15px;")
        basic_layout = QVBoxLayout(basic_frame)
        
        basic_title = QLabel("📋 Website Information")
        basic_title.setFont(QFont("Arial", 12, QFont.Bold))
        basic_layout.addWidget(basic_title)
        
        meta = tech_data.get('meta', {})
        basic_layout.addWidget(QLabel(f"Title: {tech_data.get('title', 'No title')}"))
        basic_layout.addWidget(QLabel(f"Generator: {meta.get('generator', 'Not specified')}"))
        basic_layout.addWidget(QLabel(f"Charset: {meta.get('charset', 'Not specified')}"))
        basic_layout.addWidget(QLabel(f"Viewport: {meta.get('viewport', 'Not specified')}"))
        
        # Security info
        url = tech_data.get('url', '')
        if url.startswith('https://'):
            basic_layout.addWidget(QLabel("🔒 HTTPS: Enabled"))
        else:
            basic_layout.addWidget(QLabel("⚠️ HTTPS: Not enabled"))
        
        scroll_layout.addWidget(basic_frame)
        
        # Resource Summary
        resources_frame = QFrame()
        resources_frame.setStyleSheet("background-color: #e8f4fd; border: 1px solid #bee5eb; border-radius: 5px; padding: 15px;")
        resources_layout = QVBoxLayout(resources_frame)
        
        resources_title = QLabel("📊 Resource Summary")
        resources_title.setFont(QFont("Arial", 12, QFont.Bold))
        resources_layout.addWidget(resources_title)
        
        scripts = tech_data.get('scripts', [])
        stylesheets = tech_data.get('stylesheets', [])
        images = tech_data.get('images', {})
        cookies = tech_data.get('cookies', [])
        
        external_scripts = len([s for s in scripts if s.get('type') == 'external'])
        inline_scripts = len([s for s in scripts if s.get('type') == 'inline'])
        
        resources_layout.addWidget(QLabel(f"📜 External Scripts: {external_scripts}"))
        resources_layout.addWidget(QLabel(f"📝 Inline Scripts: {inline_scripts}"))
        resources_layout.addWidget(QLabel(f"🎨 Stylesheets: {len(stylesheets)}"))
        resources_layout.addWidget(QLabel(f"🖼️ Image Formats: {len(images)} types"))
        resources_layout.addWidget(QLabel(f"🍪 Cookies: {len(cookies)}"))
        
        scroll_layout.addWidget(resources_frame)
        
        # Technology Categories (Enhanced)
        categories = tech_data.get('categories', {})
        for category, technologies in categories.items():
            if technologies:  # Only show categories with detected technologies
                cat_frame = QFrame()
                cat_frame.setStyleSheet("background-color: #d4edda; border: 1px solid #c3e6cb; border-radius: 5px; padding: 15px;")
                cat_layout = QVBoxLayout(cat_frame)
                
                cat_title = QLabel(f"🔧 {category} ({len(technologies)})")
                cat_title.setFont(QFont("Arial", 11, QFont.Bold))
                cat_layout.addWidget(cat_title)
                
                # Create a grid layout for technologies
                tech_text = ", ".join(technologies)
                tech_label = QLabel(tech_text)
                tech_label.setWordWrap(True)
                tech_label.setStyleSheet("color: #155724; margin-left: 10px; font-weight: 500;")
                cat_layout.addWidget(tech_label)
                
                scroll_layout.addWidget(cat_frame)
        
        # Quick Performance & Security Assessment
        assessment_frame = QFrame()
        assessment_frame.setStyleSheet("background-color: #fff3cd; border: 1px solid #ffeaa7; border-radius: 5px; padding: 15px;")
        assessment_layout = QVBoxLayout(assessment_frame)
        
        assessment_title = QLabel("⚡ Quick Assessment")
        assessment_title.setFont(QFont("Arial", 12, QFont.Bold))
        assessment_layout.addWidget(assessment_title)
        
        # Performance indicators
        technologies = tech_data.get('technologies', {})
        
        if external_scripts > 10:
            assessment_layout.addWidget(QLabel("⚠️ Many external scripts may impact loading speed"))
        elif external_scripts <= 5:
            assessment_layout.addWidget(QLabel("✅ Good number of external scripts"))
        
        if 'Service Worker' in technologies:
            assessment_layout.addWidget(QLabel("✅ Service Worker detected - Offline capability"))
        
        if any(cdn in str(s.get('src', '')) for s in scripts for cdn in ['cdn', 'jsdelivr', 'unpkg', 'cdnjs']):
            assessment_layout.addWidget(QLabel("✅ CDN usage detected - Good for performance"))
        
        if 'reCAPTCHA' in technologies:
            assessment_layout.addWidget(QLabel("✅ reCAPTCHA detected - Bot protection enabled"))
        
        if url.startswith('https://'):
            assessment_layout.addWidget(QLabel("✅ HTTPS enabled - Secure connection"))
        else:
            assessment_layout.addWidget(QLabel("⚠️ HTTP connection - Consider enabling HTTPS"))
        
        scroll_layout.addWidget(assessment_frame)
        
        # Top Technologies Summary
        detected_techs = [tech for tech, data in technologies.items() if data.get('detected')]
        if detected_techs:
            top_frame = QFrame()
            top_frame.setStyleSheet("background-color: #f0f8ff; border: 1px solid #b8daff; border-radius: 5px; padding: 15px;")
            top_layout = QVBoxLayout(top_frame)
            
            top_title = QLabel(f"🏆 Key Technologies ({len(detected_techs)})")
            top_title.setFont(QFont("Arial", 12, QFont.Bold))
            top_layout.addWidget(top_title)
            
            # Show top technologies in a more compact format
            top_techs = detected_techs[:8]  # Show first 8
            tech_grid_text = " • ".join(top_techs)
            if len(detected_techs) > 8:
                tech_grid_text += f" • and {len(detected_techs) - 8} more..."
            
            tech_summary = QLabel(tech_grid_text)
            tech_summary.setWordWrap(True)
            tech_summary.setStyleSheet("color: #004085; font-weight: 500;")
            top_layout.addWidget(tech_summary)
            
            scroll_layout.addWidget(top_frame)
        
        scroll_layout.addStretch()
        scroll.setWidget(scroll_widget)
        scroll.setWidgetResizable(True)
        
        layout.addWidget(scroll)
        
        return widget
    
    def create_technologies_tab(self, tech_data):
        """Create the technologies tab"""
        from PyQt5.QtWidgets import (QWidget, QVBoxLayout, QTreeWidget, QTreeWidgetItem, 
                                   QHeaderView, QLabel, QHBoxLayout, QFrame)
        from PyQt5.QtCore import Qt
        from PyQt5.QtGui import QColor, QFont
        
        widget = QWidget()
        layout = QVBoxLayout(widget)
        
        # Header with summary
        header_frame = QFrame()
        header_frame.setStyleSheet("background-color: #f8f9fa; border: 1px solid #dee2e6; border-radius: 5px; padding: 10px;")
        header_layout = QHBoxLayout(header_frame)
        
        technologies = tech_data.get('technologies', {})
        detected_count = len([tech for tech, data in technologies.items() if data.get('detected')])
        
        header_label = QLabel(f"🔧 Detected Technologies ({detected_count})")
        header_label.setFont(QFont("Arial", 14, QFont.Bold))
        header_layout.addWidget(header_label)
        
        # Add confidence legend
        legend_layout = QVBoxLayout()
        legend_layout.addWidget(QLabel("Confidence Levels:"))
        
        high_label = QLabel("🟢 High")
        high_label.setStyleSheet("color: #28a745; font-size: 11px;")
        legend_layout.addWidget(high_label)
        
        medium_label = QLabel("🟡 Medium") 
        medium_label.setStyleSheet("color: #ffc107; font-size: 11px;")
        legend_layout.addWidget(medium_label)
        
        low_label = QLabel("🔴 Low")
        low_label.setStyleSheet("color: #dc3545; font-size: 11px;")
        legend_layout.addWidget(low_label)
        
        header_layout.addStretch()
        header_layout.addLayout(legend_layout)
        
        layout.addWidget(header_frame)
        
        # Tree widget for technologies
        tree = QTreeWidget()
        tree.setHeaderLabels(['Technology', 'Category', 'Confidence', 'Description', 'Details'])
        tree.header().setSectionResizeMode(0, QHeaderView.ResizeToContents)
        tree.header().setSectionResizeMode(1, QHeaderView.ResizeToContents)
        tree.header().setSectionResizeMode(2, QHeaderView.ResizeToContents)
        tree.header().setSectionResizeMode(3, QHeaderView.Stretch)
        tree.header().setSectionResizeMode(4, QHeaderView.ResizeToContents)
        
        categories = tech_data.get('categories', {})
        
        # Enhanced technology descriptions
        tech_descriptions = {
            'React': 'JavaScript library for building user interfaces with component-based architecture',
            'Vue.js': 'Progressive JavaScript framework for building user interfaces',
            'Angular': 'Platform and framework for building single-page client applications',
            'AngularJS': 'Legacy JavaScript MVW framework (predecessor to Angular)',
            'Svelte': 'Compile-time JavaScript framework for building web applications',
            'Next.js': 'React framework for production with server-side rendering',
            'Nuxt.js': 'Vue.js framework for universal applications',
            'jQuery': 'Fast, small, and feature-rich JavaScript library for DOM manipulation',
            'Lodash': 'Modern JavaScript utility library delivering modularity and performance',
            'Moment.js': 'JavaScript library for parsing, validating, and formatting dates',
            'D3.js': 'JavaScript library for producing dynamic, interactive data visualizations',
            'Three.js': 'JavaScript 3D library for creating and displaying 3D computer graphics',
            'Chart.js': 'Simple yet flexible JavaScript charting library',
            'Axios': 'Promise-based HTTP client for JavaScript',
            'Bootstrap': 'CSS framework for responsive, mobile-first front-end development',
            'Tailwind CSS': 'Utility-first CSS framework for rapidly building custom designs',
            'Bulma': 'Modern CSS framework based on Flexbox',
            'Foundation': 'Responsive front-end framework for web development',
            'Materialize': 'CSS framework based on Material Design principles',
            'WordPress': 'Content management system (CMS) powering 40% of the web',
            'Drupal': 'Open-source content management framework',
            'Joomla': 'Content management system for publishing web content',
            'Shopify': 'E-commerce platform for online stores and retail point-of-sale systems',
            'Magento': 'Open-source e-commerce platform written in PHP',
            'Google Analytics': 'Web analytics service for tracking and reporting website traffic',
            'Google Tag Manager': 'Tag management system for marketing and analytics tags',
            'Facebook Pixel': 'Analytics tool for tracking conversions from Facebook ads',
            'Hotjar': 'Behavior analytics and user feedback service',
            'Mixpanel': 'Business analytics service for tracking user interactions',
            'Font Awesome': 'Icon library and toolkit with scalable vector icons',
            'Cloudflare': 'Content delivery network and DDoS mitigation service',
            'jsDelivr': 'Free CDN for open source projects',
            'unpkg': 'Fast, global content delivery network for npm packages',
            'cdnjs': 'Free and open-source CDN service',
            'Google Fonts': 'Library of free licensed font families',
            'Adobe Fonts': 'Subscription-based font service (formerly Typekit)',
            'Stripe': 'Payment processing platform for internet businesses',
            'PayPal': 'Online payment system supporting money transfers',
            'Google Maps': 'Web mapping service with satellite imagery and street maps',
            'Mapbox': 'Location data platform providing maps and location services',
            'reCAPTCHA': 'CAPTCHA service to protect websites from spam and abuse',
            'Service Worker': 'Script for background sync, push notifications, and offline functionality',
            'Web Workers': 'JavaScript API for running scripts in background threads',
            'WebAssembly': 'Binary instruction format for stack-based virtual machine',
            'Webpack': 'Static module bundler for modern JavaScript applications',
            'Vite': 'Build tool for modern web development with fast HMR',
            'Parcel': 'Zero-configuration build tool for web applications'
        }
        
        # Technology details (version info, usage notes, etc.)
        tech_details = {
            'React': 'Component-based',
            'Vue.js': 'Progressive',
            'Angular': 'Full framework',
            'jQuery': 'DOM library',
            'Bootstrap': 'CSS framework',
            'Google Analytics': 'Web analytics',
            'Font Awesome': 'Icon library',
            'Cloudflare': 'CDN + Security',
            'Service Worker': 'PWA feature',
            'WebAssembly': 'High performance'
        }
        
        # Find category for each technology
        tech_to_category = {}
        for category, techs in categories.items():
            for tech in techs:
                tech_to_category[tech] = category
        
        # Sort technologies by category and name
        sorted_technologies = sorted(
            [(tech_name, tech_info) for tech_name, tech_info in technologies.items() if tech_info.get('detected')],
            key=lambda x: (tech_to_category.get(x[0], 'Other'), x[0])
        )
        
        for tech_name, tech_info in sorted_technologies:
            item = QTreeWidgetItem()
            item.setText(0, tech_name)
            item.setText(1, tech_to_category.get(tech_name, 'Other'))
            
            confidence = tech_info.get('confidence', 'medium')
            item.setText(2, confidence.title())
            
            # Color code confidence with emojis
            if confidence == 'high':
                item.setText(2, "🟢 High")
                item.setBackground(2, QColor(144, 238, 144))  # Light green
            elif confidence == 'medium':
                item.setText(2, "🟡 Medium")
                item.setBackground(2, QColor(255, 255, 0))    # Yellow
            else:
                item.setText(2, "🔴 Low")
                item.setBackground(2, QColor(255, 182, 193))  # Light red
            
            # Enhanced description
            description = tech_descriptions.get(tech_name, f'{tech_name} technology detected on this website')
            item.setText(3, description)
            
            # Additional details
            details = tech_details.get(tech_name, 'Detected')
            item.setText(4, details)
            
            # Color code by category
            category = tech_to_category.get(tech_name, 'Other')
            if 'JavaScript' in category:
                item.setBackground(0, QColor(255, 248, 220))  # Light yellow
            elif 'CSS' in category:
                item.setBackground(0, QColor(230, 247, 255))  # Light blue
            elif 'Analytics' in category:
                item.setBackground(0, QColor(240, 255, 240))  # Light green
            elif 'CDN' in category:
                item.setBackground(0, QColor(255, 240, 245))  # Light pink
            
            tree.addTopLevelItem(item)
        
        layout.addWidget(tree)
        
        # Summary footer
        if detected_count > 0:
            footer_frame = QFrame()
            footer_frame.setStyleSheet("background-color: #d1ecf1; border: 1px solid #bee5eb; border-radius: 5px; padding: 10px; margin-top: 10px;")
            footer_layout = QVBoxLayout(footer_frame)
            
            # Category breakdown
            category_summary = []
            for category, techs in categories.items():
                if techs:
                    category_summary.append(f"{category}: {len(techs)}")
            
            if category_summary:
                summary_text = " | ".join(category_summary)
                summary_label = QLabel(f"📊 Category Breakdown: {summary_text}")
                summary_label.setStyleSheet("font-weight: 500; color: #0c5460;")
                footer_layout.addWidget(summary_label)
            
            layout.addWidget(footer_frame)
        
        return widget
    
    def create_scripts_tab(self, tech_data):
        """Create the scripts tab"""
        from PyQt5.QtWidgets import (QWidget, QVBoxLayout, QTreeWidget, QTreeWidgetItem, 
                                   QHeaderView, QLabel)
        from PyQt5.QtCore import Qt
        
        widget = QWidget()
        layout = QVBoxLayout(widget)
        
        # Header
        header = QLabel("📜 JavaScript Files & Scripts")
        header.setStyleSheet("font-weight: bold; font-size: 14px; padding: 5px;")
        layout.addWidget(header)
        
        # Tree widget for scripts
        tree = QTreeWidget()
        tree.setHeaderLabels(['Type', 'Source/Content', 'Attributes', 'Size/Info'])
        tree.header().setSectionResizeMode(0, QHeaderView.ResizeToContents)
        tree.header().setSectionResizeMode(1, QHeaderView.Stretch)
        tree.header().setSectionResizeMode(2, QHeaderView.ResizeToContents)
        tree.header().setSectionResizeMode(3, QHeaderView.ResizeToContents)
        
        scripts = tech_data.get('scripts', [])
        
        for script in scripts:
            item = QTreeWidgetItem()
            
            script_type = script.get('type', 'unknown')
            item.setText(0, script_type.title())
            
            if script_type == 'external':
                src = script.get('src', '')
                item.setText(1, src)
                
                # Attributes
                attrs = []
                if script.get('async'):
                    attrs.append('async')
                if script.get('defer'):
                    attrs.append('defer')
                item.setText(2, ', '.join(attrs) if attrs else 'none')
                
                # Try to determine file size or type from URL
                if 'min.js' in src:
                    item.setText(3, 'Minified')
                elif any(cdn in src for cdn in ['cdn', 'jsdelivr', 'unpkg', 'cdnjs']):
                    item.setText(3, 'CDN')
                else:
                    item.setText(3, 'Local')
                    
            else:  # inline
                content = script.get('content', '')
                item.setText(1, content[:100] + ('...' if len(content) > 100 else ''))
                item.setText(2, 'inline')
                
                size = script.get('size', 0)
                if size > 1024:
                    item.setText(3, f"{size // 1024}KB")
                else:
                    item.setText(3, f"{size}B")
            
            tree.addTopLevelItem(item)
        
        layout.addWidget(tree)
        
        return widget
    
    def create_stylesheets_tab(self, tech_data):
        """Create the stylesheets tab"""
        from PyQt5.QtWidgets import (QWidget, QVBoxLayout, QTreeWidget, QTreeWidgetItem, 
                                   QHeaderView, QLabel)
        from PyQt5.QtCore import Qt
        
        widget = QWidget()
        layout = QVBoxLayout(widget)
        
        # Header
        header = QLabel("🎨 CSS Stylesheets")
        header.setStyleSheet("font-weight: bold; font-size: 14px; padding: 5px;")
        layout.addWidget(header)
        
        # Tree widget for stylesheets
        tree = QTreeWidget()
        tree.setHeaderLabels(['Source', 'Media', 'Type'])
        tree.header().setSectionResizeMode(0, QHeaderView.Stretch)
        tree.header().setSectionResizeMode(1, QHeaderView.ResizeToContents)
        tree.header().setSectionResizeMode(2, QHeaderView.ResizeToContents)
        
        stylesheets = tech_data.get('stylesheets', [])
        
        for stylesheet in stylesheets:
            item = QTreeWidgetItem()
            
            href = stylesheet.get('href', '')
            item.setText(0, href)
            item.setText(1, stylesheet.get('media', 'all'))
            
            # Determine type
            if any(cdn in href for cdn in ['cdn', 'googleapis', 'jsdelivr', 'unpkg', 'cdnjs']):
                item.setText(2, 'CDN')
            elif 'min.css' in href:
                item.setText(2, 'Minified')
            else:
                item.setText(2, 'Local')
            
            tree.addTopLevelItem(item)
        
        # Image formats section
        images = tech_data.get('images', {})
        if images:
            layout.addWidget(QLabel(""))  # Spacer
            
            images_header = QLabel("🖼️ Image Formats")
            images_header.setStyleSheet("font-weight: bold; font-size: 14px; padding: 5px;")
            layout.addWidget(images_header)
            
            images_tree = QTreeWidget()
            images_tree.setHeaderLabels(['Format', 'Count'])
            images_tree.header().setSectionResizeMode(0, QHeaderView.Stretch)
            images_tree.header().setSectionResizeMode(1, QHeaderView.ResizeToContents)
            
            for format_ext, count in images.items():
                item = QTreeWidgetItem()
                item.setText(0, format_ext.upper())
                item.setText(1, str(count))
                images_tree.addTopLevelItem(item)
            
            layout.addWidget(images_tree)
        else:
            layout.addWidget(tree)
        
        return widget
    
    def create_meta_tab(self, tech_data):
        """Create the meta information tab"""
        from PyQt5.QtWidgets import (QWidget, QVBoxLayout, QTextEdit, QLabel, QTabWidget)
        from PyQt5.QtCore import Qt
        
        widget = QWidget()
        layout = QVBoxLayout(widget)
        
        # Sub-tabs for different meta information
        meta_tabs = QTabWidget()
        layout.addWidget(meta_tabs)
        
        # Meta Tags Tab
        meta_widget = QWidget()
        meta_layout = QVBoxLayout(meta_widget)
        
        meta_text = QTextEdit()
        meta_text.setReadOnly(True)
        meta_text.setStyleSheet("font-family: monospace; background-color: #f8f9fa;")
        
        meta_info = tech_data.get('meta', {})
        meta_content = []
        meta_content.append("META INFORMATION:")
        meta_content.append("=" * 30)
        
        for key, value in meta_info.items():
            if value:
                meta_content.append(f"{key.title()}: {value}")
        
        meta_text.setPlainText('\n'.join(meta_content))
        meta_layout.addWidget(meta_text)
        
        meta_tabs.addTab(meta_widget, "📋 Meta Tags")
        
        # Cookies Tab
        cookies_widget = QWidget()
        cookies_layout = QVBoxLayout(cookies_widget)
        
        cookies_text = QTextEdit()
        cookies_text.setReadOnly(True)
        cookies_text.setStyleSheet("font-family: monospace; background-color: #f8f9fa;")
        
        cookies = tech_data.get('cookies', [])
        cookies_content = []
        cookies_content.append("COOKIES:")
        cookies_content.append("=" * 30)
        
        if cookies:
            for cookie in cookies:
                cookies_content.append(f"Name: {cookie.get('name', '')}")
                cookies_content.append(f"Value: {cookie.get('value', '')}")
                cookies_content.append("-" * 20)
        else:
            cookies_content.append("No cookies found")
        
        cookies_text.setPlainText('\n'.join(cookies_content))
        cookies_layout.addWidget(cookies_text)
        
        meta_tabs.addTab(cookies_widget, f"🍪 Cookies ({len(cookies)})")
        
        return widget
    
    def create_security_performance_tab(self, tech_data):
        """Create the security and performance tab"""
        from PyQt5.QtWidgets import (QWidget, QVBoxLayout, QLabel, QFrame, QScrollArea)
        from PyQt5.QtCore import Qt
        from PyQt5.QtGui import QFont
        
        widget = QWidget()
        layout = QVBoxLayout(widget)
        
        # Create scroll area
        scroll = QScrollArea()
        scroll_widget = QWidget()
        scroll_layout = QVBoxLayout(scroll_widget)
        
        # Security Analysis
        security_frame = QFrame()
        security_frame.setStyleSheet("background-color: #f8d7da; border: 1px solid #f5c6cb; border-radius: 5px; padding: 10px;")
        security_layout = QVBoxLayout(security_frame)
        
        security_title = QLabel("🛡️ Security Analysis")
        security_title.setFont(QFont("Arial", 12, QFont.Bold))
        security_layout.addWidget(security_title)
        
        technologies = tech_data.get('technologies', {})
        
        # Check for security-related technologies
        security_techs = []
        if 'reCAPTCHA' in technologies:
            security_techs.append("✅ reCAPTCHA detected - Bot protection enabled")
        
        # Check for HTTPS
        url = tech_data.get('url', '')
        if url.startswith('https://'):
            security_techs.append("✅ HTTPS enabled - Secure connection")
        else:
            security_techs.append("⚠️ HTTP connection - Not secure")
        
        # Check for security headers (basic analysis)
        meta = tech_data.get('meta', {})
        if any('security' in str(v).lower() for v in meta.values()):
            security_techs.append("✅ Security-related meta tags found")
        
        if not security_techs:
            security_techs.append("ℹ️ No obvious security measures detected")
        
        for tech in security_techs:
            security_layout.addWidget(QLabel(tech))
        
        scroll_layout.addWidget(security_frame)
        
        # Performance Analysis
        performance_frame = QFrame()
        performance_frame.setStyleSheet("background-color: #d1ecf1; border: 1px solid #bee5eb; border-radius: 5px; padding: 10px;")
        performance_layout = QVBoxLayout(performance_frame)
        
        performance_title = QLabel("⚡ Performance Analysis")
        performance_title.setFont(QFont("Arial", 12, QFont.Bold))
        performance_layout.addWidget(performance_title)
        
        performance_items = []
        
        # Check for performance technologies
        if 'Service Worker' in technologies:
            performance_items.append("✅ Service Worker detected - Offline capability")
        if 'WebAssembly' in technologies:
            performance_items.append("✅ WebAssembly detected - High performance computing")
        if 'Cloudflare' in technologies:
            performance_items.append("✅ Cloudflare CDN detected - Global content delivery")
        
        # Analyze scripts
        scripts = tech_data.get('scripts', [])
        external_scripts = len([s for s in scripts if s.get('type') == 'external'])
        inline_scripts = len([s for s in scripts if s.get('type') == 'inline'])
        
        if external_scripts > 10:
            performance_items.append(f"⚠️ Many external scripts ({external_scripts}) - May impact loading speed")
        elif external_scripts > 5:
            performance_items.append(f"ℹ️ Moderate number of external scripts ({external_scripts})")
        else:
            performance_items.append(f"✅ Few external scripts ({external_scripts}) - Good for performance")
        
        if inline_scripts > 5:
            performance_items.append(f"ℹ️ Several inline scripts ({inline_scripts}) - Consider bundling")
        
        # Check for minified resources
        minified_scripts = len([s for s in scripts if s.get('type') == 'external' and 'min.js' in s.get('src', '')])
        if minified_scripts > 0:
            performance_items.append(f"✅ {minified_scripts} minified scripts detected - Good for performance")
        
        if not performance_items:
            performance_items.append("ℹ️ Basic performance analysis - no major issues detected")
        
        for item in performance_items:
            performance_layout.addWidget(QLabel(item))
        
        scroll_layout.addWidget(performance_frame)
        
        # Recommendations
        recommendations_frame = QFrame()
        recommendations_frame.setStyleSheet("background-color: #fff3cd; border: 1px solid #ffeaa7; border-radius: 5px; padding: 10px;")
        recommendations_layout = QVBoxLayout(recommendations_frame)
        
        recommendations_title = QLabel("💡 Recommendations")
        recommendations_title.setFont(QFont("Arial", 12, QFont.Bold))
        recommendations_layout.addWidget(recommendations_title)
        
        recommendations = []
        
        # Security recommendations
        if not url.startswith('https://'):
            recommendations.append("🔒 Enable HTTPS for secure connections")
        if 'reCAPTCHA' not in technologies:
            recommendations.append("🛡️ Consider adding reCAPTCHA for form protection")
        
        # Performance recommendations
        if external_scripts > 10:
            recommendations.append("⚡ Consider bundling or reducing external scripts")
        if len(tech_data.get('stylesheets', [])) > 5:
            recommendations.append("🎨 Consider combining CSS files to reduce requests")
        
        # Modern web recommendations
        if 'Service Worker' not in technologies:
            recommendations.append("📱 Consider implementing Service Worker for offline functionality")
        if not any('CDN' in str(s) for s in scripts):
            recommendations.append("🌐 Consider using a CDN for better global performance")
        
        if not recommendations:
            recommendations.append("✅ Website appears to follow good practices")
        
        for rec in recommendations:
            rec_label = QLabel(rec)
            rec_label.setWordWrap(True)
            recommendations_layout.addWidget(rec_label)
        
        scroll_layout.addWidget(recommendations_frame)
        
        scroll_layout.addStretch()
        scroll.setWidget(scroll_widget)
        scroll.setWidgetResizable(True)
        
        layout.addWidget(scroll)
        
        return widget
    
    def generate_tech_summary(self, tech_data, base_url):
        """Generate a summary of detected technologies"""
        lines = []
        lines.append(f"TECHNOLOGY SUMMARY FOR: {base_url}")
        lines.append("=" * 60)
        lines.append("")
        
        # Detected technologies by category
        categories = tech_data.get('categories', {})
        for category, technologies in categories.items():
            if technologies:
                lines.append(f"{category.upper()}:")
                for tech in technologies:
                    lines.append(f"  • {tech}")
                lines.append("")
        
        # Resource summary
        scripts = tech_data.get('scripts', [])
        stylesheets = tech_data.get('stylesheets', [])
        cookies = tech_data.get('cookies', [])
        
        lines.append("RESOURCE SUMMARY:")
        lines.append(f"  Scripts: {len(scripts)} ({len([s for s in scripts if s.get('type') == 'external'])} external, {len([s for s in scripts if s.get('type') == 'inline'])} inline)")
        lines.append(f"  Stylesheets: {len(stylesheets)}")
        lines.append(f"  Cookies: {len(cookies)}")
        lines.append("")
        
        return '\n'.join(lines)
    
    def generate_tech_text_report(self, export_data):
        """Generate a detailed text report"""
        lines = []
        lines.append("TECHNOLOGY ANALYSIS REPORT")
        lines.append("=" * 50)
        lines.append(f"URL: {export_data['url']}")
        lines.append(f"Analysis Date: {export_data['timestamp']}")
        lines.append("")
        
        tech_data = export_data['tech_data']
        
        # Basic information
        lines.append("BASIC INFORMATION:")
        lines.append("-" * 20)
        lines.append(f"Title: {tech_data.get('title', 'N/A')}")
        
        meta = tech_data.get('meta', {})
        for key, value in meta.items():
            if value:
                lines.append(f"{key.title()}: {value}")
        lines.append("")
        
        # Technologies by category
        categories = tech_data.get('categories', {})
        for category, technologies in categories.items():
            if technologies:
                lines.append(f"{category.upper()}:")
                for tech in technologies:
                    lines.append(f"  • {tech}")
                lines.append("")
        
        # Scripts
        scripts = tech_data.get('scripts', [])
        if scripts:
            lines.append("SCRIPTS:")
            lines.append("-" * 20)
            for script in scripts[:10]:  # Limit to first 10
                if script.get('type') == 'external':
                    lines.append(f"External: {script.get('src', '')}")
                else:
                    lines.append(f"Inline: {len(script.get('content', ''))} characters")
            if len(scripts) > 10:
                lines.append(f"... and {len(scripts) - 10} more scripts")
            lines.append("")
        
        # Stylesheets
        stylesheets = tech_data.get('stylesheets', [])
        if stylesheets:
            lines.append("STYLESHEETS:")
            lines.append("-" * 20)
            for stylesheet in stylesheets[:10]:  # Limit to first 10
                lines.append(f"  • {stylesheet.get('href', '')}")
            if len(stylesheets) > 10:
                lines.append(f"... and {len(stylesheets) - 10} more stylesheets")
            lines.append("")
        
        return '\n'.join(lines)
    
    def test_csrf_cors(self, browser):
        """Test CSRF and CORS policies on the current website"""
        try:
            page = browser.page()
            current_url = browser.url().toString()
            
            # Show initial status
            self.main_window.status_info.setText("🛡️ Testing CSRF/CORS policies...")
            
            # JavaScript to test CSRF/CORS
            js_code = """
            (function() {
                var testResults = {
                    url: window.location.href,
                    origin: window.location.origin,
                    protocol: window.location.protocol,
                    host: window.location.host,
                    timestamp: new Date().toISOString(),
                    csrf: {
                        tokens: [],
                        forms: [],
                        metaTags: [],
                        headers: {},
                        protection: 'unknown'
                    },
                    cors: {
                        headers: {},
                        preflight: {},
                        credentials: 'unknown',
                        origins: [],
                        methods: [],
                        allowedHeaders: []
                    },
                    security: {
                        https: window.location.protocol === 'https:',
                        mixedContent: false,
                        csp: null,
                        xFrameOptions: null,
                        referrerPolicy: null
                    },
                    tests: {
                        corsSimpleRequest: null,
                        corsPreflightRequest: null,
                        csrfTokenPresence: null,
                        sameOriginPolicy: null
                    }
                };
                
                // CSRF Token Detection
                function detectCSRFTokens() {
                    var tokens = [];
                    
                    // Check meta tags for CSRF tokens
                    var metaTags = document.querySelectorAll('meta[name*="csrf"], meta[name*="token"], meta[name*="_token"]');
                    metaTags.forEach(function(meta) {
                        tokens.push({
                            type: 'meta',
                            name: meta.getAttribute('name'),
                            content: meta.getAttribute('content') ? meta.getAttribute('content').substring(0, 20) + '...' : '',
                            element: meta.outerHTML
                        });
                        testResults.csrf.metaTags.push({
                            name: meta.getAttribute('name'),
                            content: meta.getAttribute('content') || ''
                        });
                    });
                    
                    // Check forms for CSRF tokens
                    var forms = document.querySelectorAll('form');
                    forms.forEach(function(form, index) {
                        var csrfInputs = form.querySelectorAll('input[name*="csrf"], input[name*="token"], input[name*="_token"]');
                        var formData = {
                            index: index,
                            action: form.action || 'current page',
                            method: form.method || 'GET',
                            csrfTokens: []
                        };
                        
                        csrfInputs.forEach(function(input) {
                            var tokenData = {
                                type: 'form_input',
                                name: input.name,
                                value: input.value ? input.value.substring(0, 20) + '...' : '',
                                inputType: input.type
                            };
                            tokens.push(tokenData);
                            formData.csrfTokens.push(tokenData);
                        });
                        
                        testResults.csrf.forms.push(formData);
                    });
                    
                    testResults.csrf.tokens = tokens;
                    testResults.csrf.protection = tokens.length > 0 ? 'detected' : 'not_detected';
                }
                
                // CORS Headers Detection (from response headers if available)
                function detectCORSHeaders() {
                    // We'll try to make a test request to detect CORS headers
                    // Note: This is limited by browser security, but we can detect some things
                    
                    // Check if we can access certain properties that indicate CORS setup
                    try {
                        // Test for CORS by attempting a cross-origin request simulation
                        var testOrigins = [
                            'https://example.com',
                            'http://localhost:3000',
                            'https://test.com'
                        ];
                        
                        testResults.cors.origins = testOrigins;
                        testResults.cors.methods = ['GET', 'POST', 'PUT', 'DELETE', 'OPTIONS'];
                        testResults.cors.allowedHeaders = ['Content-Type', 'Authorization', 'X-Requested-With'];
                    } catch (e) {
                        console.log('CORS detection limited by browser security');
                    }
                }
                
                // Security Headers Detection
                function detectSecurityHeaders() {
                    // Check for Content Security Policy
                    var cspMeta = document.querySelector('meta[http-equiv="Content-Security-Policy"]');
                    if (cspMeta) {
                        testResults.security.csp = cspMeta.getAttribute('content');
                    }
                    
                    // Check for X-Frame-Options
                    var xFrameMeta = document.querySelector('meta[http-equiv="X-Frame-Options"]');
                    if (xFrameMeta) {
                        testResults.security.xFrameOptions = xFrameMeta.getAttribute('content');
                    }
                    
                    // Check for Referrer Policy
                    var referrerMeta = document.querySelector('meta[name="referrer"]');
                    if (referrerMeta) {
                        testResults.security.referrerPolicy = referrerMeta.getAttribute('content');
                    }
                    
                    // Check for mixed content
                    var httpResources = document.querySelectorAll('script[src^="http:"], link[href^="http:"], img[src^="http:"]');
                    if (httpResources.length > 0 && window.location.protocol === 'https:') {
                        testResults.security.mixedContent = true;
                    }
                }
                
                // Perform CORS Tests
                function performCORSTests() {
                    return new Promise(function(resolve) {
                        var testsPending = 0;
                        var testsCompleted = 0;
                        
                        function testComplete() {
                            testsCompleted++;
                            if (testsCompleted >= testsPending) {
                                resolve();
                            }
                        }
                        
                        // Test 1: Simple CORS request
                        testsPending++;
                        var img = new Image();
                        img.onload = function() {
                            testResults.tests.corsSimpleRequest = {
                                status: 'allowed',
                                message: 'Simple CORS requests appear to be allowed'
                            };
                            testComplete();
                        };
                        img.onerror = function() {
                            testResults.tests.corsSimpleRequest = {
                                status: 'blocked',
                                message: 'Simple CORS requests may be blocked'
                            };
                            testComplete();
                        };
                        img.src = window.location.origin + '/favicon.ico?' + Date.now();
                        
                        // Test 2: Fetch API test (if available)
                        if (typeof fetch !== 'undefined') {
                            testsPending++;
                            fetch(window.location.origin + '/robots.txt', {
                                method: 'GET',
                                mode: 'cors'
                            }).then(function(response) {
                                testResults.tests.corsPreflightRequest = {
                                    status: 'success',
                                    message: 'CORS fetch request successful',
                                    headers: response.headers ? 'available' : 'not_available'
                                };
                                testComplete();
                            }).catch(function(error) {
                                testResults.tests.corsPreflightRequest = {
                                    status: 'error',
                                    message: 'CORS fetch request failed: ' + error.message
                                };
                                testComplete();
                            });
                        }
                        
                        // Test 3: Same-origin policy test
                        testsPending++;
                        try {
                            var testFrame = document.createElement('iframe');
                            testFrame.style.display = 'none';
                            testFrame.src = window.location.origin + '/';
                            testFrame.onload = function() {
                                try {
                                    var frameDoc = testFrame.contentDocument;
                                    testResults.tests.sameOriginPolicy = {
                                        status: 'accessible',
                                        message: 'Same-origin content is accessible'
                                    };
                                } catch (e) {
                                    testResults.tests.sameOriginPolicy = {
                                        status: 'blocked',
                                        message: 'Same-origin policy enforced: ' + e.message
                                    };
                                }
                                document.body.removeChild(testFrame);
                                testComplete();
                            };
                            testFrame.onerror = function() {
                                testResults.tests.sameOriginPolicy = {
                                    status: 'error',
                                    message: 'Frame loading failed'
                                };
                                document.body.removeChild(testFrame);
                                testComplete();
                            };
                            document.body.appendChild(testFrame);
                        } catch (e) {
                            testResults.tests.sameOriginPolicy = {
                                status: 'error',
                                message: 'Frame test failed: ' + e.message
                            };
                            testComplete();
                        }
                        
                        // Fallback timeout
                        setTimeout(function() {
                            if (testsCompleted < testsPending) {
                                console.log('Some CORS tests timed out');
                                resolve();
                            }
                        }, 5000);
                    });
                }
                
                // Run all detection functions
                detectCSRFTokens();
                detectCORSHeaders();
                detectSecurityHeaders();
                
                // Perform async tests and return results
                performCORSTests().then(function() {
                    // Additional analysis
                    testResults.analysis = {
                        csrfProtectionLevel: testResults.csrf.tokens.length > 0 ? 'good' : 'poor',
                        securityScore: 0,
                        recommendations: []
                    };
                    
                    // Calculate security score
                    var score = 0;
                    if (testResults.security.https) score += 20;
                    if (testResults.csrf.tokens.length > 0) score += 25;
                    if (testResults.security.csp) score += 15;
                    if (testResults.security.xFrameOptions) score += 10;
                    if (!testResults.security.mixedContent) score += 10;
                    if (testResults.security.referrerPolicy) score += 5;
                    
                    testResults.analysis.securityScore = Math.min(score, 100);
                    
                    // Generate recommendations
                    if (!testResults.security.https) {
                        testResults.analysis.recommendations.push('Enable HTTPS for secure communication');
                    }
                    if (testResults.csrf.tokens.length === 0) {
                        testResults.analysis.recommendations.push('Implement CSRF protection tokens in forms');
                    }
                    if (!testResults.security.csp) {
                        testResults.analysis.recommendations.push('Add Content Security Policy headers');
                    }
                    if (!testResults.security.xFrameOptions) {
                        testResults.analysis.recommendations.push('Add X-Frame-Options header to prevent clickjacking');
                    }
                    if (testResults.security.mixedContent) {
                        testResults.analysis.recommendations.push('Fix mixed content issues (HTTP resources on HTTPS page)');
                    }
                    
                    // Store results for retrieval
                    window.csrfCorsTestResults = testResults;
                });
                
                return 'CSRF/CORS testing initiated...';
            })();
            """
            
            def process_initial_response(response):
                # Start polling for test results
                self.start_csrf_cors_polling(page, current_url)
            
            # Execute the JavaScript
            page.runJavaScript(js_code, process_initial_response)
            
        except Exception as e:
            self.main_window.status_info.setText(f"❌ CSRF/CORS test error: {str(e)}")
            QTimer.singleShot(3000, lambda: self.main_window.status_info.setText(""))
    
    def start_csrf_cors_polling(self, page, current_url):
        """Start polling for CSRF/CORS test results"""
        self.csrf_cors_poll_timer = QTimer()
        self.csrf_cors_poll_timer.timeout.connect(lambda: self.check_csrf_cors_results(page, current_url))
        self.csrf_cors_poll_timer.start(1000)  # Check every second
        
        # Stop polling after 10 seconds
        QTimer.singleShot(10000, lambda: self.stop_csrf_cors_polling())
    
    def check_csrf_cors_results(self, page, current_url):
        """Check if CSRF/CORS test results are ready"""
        js_check = """
        (function() {
            if (window.csrfCorsTestResults) {
                var results = window.csrfCorsTestResults;
                delete window.csrfCorsTestResults;  // Clear it
                return results;
            }
            return null;
        })();
        """
        
        def handle_results(results):
            if results:
                self.stop_csrf_cors_polling()
                self.show_csrf_cors_dialog(results, current_url)
        
        page.runJavaScript(js_check, handle_results)
    
    def stop_csrf_cors_polling(self):
        """Stop polling for CSRF/CORS results"""
        if hasattr(self, 'csrf_cors_poll_timer'):
            self.csrf_cors_poll_timer.stop()
    
    def show_csrf_cors_dialog(self, test_results, base_url):
        """Show dialog with CSRF/CORS test results"""
        from PyQt5.QtWidgets import (QDialog, QVBoxLayout, QHBoxLayout, QLabel, 
                                   QTextEdit, QPushButton, QTabWidget, QWidget,
                                   QTreeWidget, QTreeWidgetItem, QHeaderView, 
                                   QFileDialog, QScrollArea, QFrame, QProgressBar)
        from PyQt5.QtCore import Qt, QTimer
        from PyQt5.QtGui import QFont, QColor
        from datetime import datetime
        import json
        
        # Create dialog
        dialog = QDialog(self.main_window)
        security_score = test_results.get('analysis', {}).get('securityScore', 0)
        dialog.setWindowTitle(f"🛡️ CSRF/CORS Visual Tester - Security Score: {security_score}/100")
        dialog.setMinimumSize(900, 700)
        dialog.resize(1200, 800)
        
        layout = QVBoxLayout(dialog)
        
        # Header
        header_label = QLabel(f"CSRF/CORS Security Analysis for: {base_url}")
        header_label.setStyleSheet("font-weight: bold; padding: 10px; background-color: #e8f4fd; border-radius: 5px;")
        header_label.setWordWrap(True)
        layout.addWidget(header_label)
        
        # Security Score Display
        score_frame = QFrame()
        score_frame.setStyleSheet("background-color: #f8f9fa; border: 1px solid #dee2e6; border-radius: 5px; padding: 10px;")
        score_layout = QHBoxLayout(score_frame)
        
        score_label = QLabel(f"Security Score: {security_score}/100")
        score_font = QFont()
        score_font.setPointSize(16)
        score_font.setBold(True)
        score_label.setFont(score_font)
        
        # Color code the score
        if security_score >= 80:
            score_label.setStyleSheet("color: #28a745;")  # Green
        elif security_score >= 60:
            score_label.setStyleSheet("color: #ffc107;")  # Yellow
        else:
            score_label.setStyleSheet("color: #dc3545;")  # Red
        
        score_layout.addWidget(score_label)
        
        # Progress bar for score
        score_progress = QProgressBar()
        score_progress.setRange(0, 100)
        score_progress.setValue(security_score)
        score_progress.setStyleSheet("""
            QProgressBar {
                border: 2px solid grey;
                border-radius: 5px;
                text-align: center;
            }
            QProgressBar::chunk {
                background-color: #28a745;
                width: 20px;
            }
        """)
        score_layout.addWidget(score_progress)
        
        layout.addWidget(score_frame)
        
        # Tab widget
        tab_widget = QTabWidget()
        layout.addWidget(tab_widget)
        
        # Overview Tab
        overview_widget = self.create_csrf_cors_overview_tab(test_results)
        tab_widget.addTab(overview_widget, "📊 Overview")
        
        # CSRF Analysis Tab
        csrf_widget = self.create_csrf_analysis_tab(test_results)
        tab_widget.addTab(csrf_widget, "🛡️ CSRF Analysis")
        
        # CORS Analysis Tab
        cors_widget = self.create_cors_analysis_tab(test_results)
        tab_widget.addTab(cors_widget, "🌐 CORS Analysis")
        
        # Security Headers Tab
        security_widget = self.create_security_headers_tab(test_results)
        tab_widget.addTab(security_widget, "🔒 Security Headers")
        
        # Test Results Tab
        tests_widget = self.create_test_results_tab(test_results)
        tab_widget.addTab(tests_widget, "🧪 Test Results")
        
        # Buttons
        button_layout = QHBoxLayout()
        
        export_button = QPushButton("💾 Export Report")
        retest_button = QPushButton("🔄 Re-test")
        close_button = QPushButton("❌ Close")
        
        button_layout.addStretch()
        button_layout.addWidget(export_button)
        button_layout.addWidget(retest_button)
        button_layout.addWidget(close_button)
        layout.addLayout(button_layout)
        
        def export_report():
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            filename = f"csrf_cors_analysis_{timestamp}.json"
            
            file_path, _ = QFileDialog.getSaveFileName(
                dialog,
                "Export CSRF/CORS Analysis Report",
                filename,
                "JSON Files (*.json);;Text Files (*.txt);;All Files (*.*)"
            )
            
            if file_path:
                try:
                    export_data = {
                        'url': base_url,
                        'timestamp': datetime.now().isoformat(),
                        'test_results': test_results
                    }
                    
                    if file_path.endswith('.json'):
                        with open(file_path, 'w', encoding='utf-8') as f:
                            json.dump(export_data, f, indent=2, ensure_ascii=False)
                    else:
                        # Export as text report
                        with open(file_path, 'w', encoding='utf-8') as f:
                            f.write(self.generate_csrf_cors_text_report(export_data))
                    
                    self.main_window.status_info.setText(f"✅ CSRF/CORS report exported to: {file_path}")
                    QTimer.singleShot(3000, lambda: self.main_window.status_info.setText(""))
                except Exception as e:
                    self.main_window.status_info.setText(f"❌ Export failed: {str(e)}")
                    QTimer.singleShot(3000, lambda: self.main_window.status_info.setText(""))
        
        def retest():
            dialog.accept()
            # Re-run the test
            browser = self.get_current_browser()
            if browser:
                self.test_csrf_cors(browser)
        
        # Connect buttons
        export_button.clicked.connect(export_report)
        retest_button.clicked.connect(retest)
        close_button.clicked.connect(dialog.accept)
        
        # Show dialog
        dialog.exec_()
        
        # Update main window status
        self.main_window.status_info.setText(f"🛡️ CSRF/CORS analysis complete - Security Score: {security_score}/100")
        QTimer.singleShot(5000, lambda: self.main_window.status_info.setText(""))
    
    def create_csrf_cors_overview_tab(self, test_results):
        """Create the overview tab for CSRF/CORS analysis"""
        from PyQt5.QtWidgets import (QWidget, QVBoxLayout, QLabel, QFrame, QScrollArea)
        from PyQt5.QtCore import Qt
        from PyQt5.QtGui import QFont
        
        widget = QWidget()
        layout = QVBoxLayout(widget)
        
        # Create scroll area
        scroll = QScrollArea()
        scroll_widget = QWidget()
        scroll_layout = QVBoxLayout(scroll_widget)
        
        # Basic Information
        basic_frame = QFrame()
        basic_frame.setStyleSheet("background-color: #f8f9fa; border: 1px solid #dee2e6; border-radius: 5px; padding: 15px;")
        basic_layout = QVBoxLayout(basic_frame)
        
        basic_title = QLabel("📋 Website Security Overview")
        basic_title.setFont(QFont("Arial", 12, QFont.Bold))
        basic_layout.addWidget(basic_title)
        
        basic_layout.addWidget(QLabel(f"URL: {test_results.get('url', 'N/A')}"))
        basic_layout.addWidget(QLabel(f"Origin: {test_results.get('origin', 'N/A')}"))
        basic_layout.addWidget(QLabel(f"Protocol: {test_results.get('protocol', 'N/A')}"))
        basic_layout.addWidget(QLabel(f"Host: {test_results.get('host', 'N/A')}"))
        
        security = test_results.get('security', {})
        https_status = "✅ Enabled" if security.get('https') else "❌ Disabled"
        basic_layout.addWidget(QLabel(f"HTTPS: {https_status}"))
        
        scroll_layout.addWidget(basic_frame)
        
        # Security Score Breakdown
        analysis = test_results.get('analysis', {})
        score_frame = QFrame()
        score_frame.setStyleSheet("background-color: #e8f4fd; border: 1px solid #bee5eb; border-radius: 5px; padding: 15px;")
        score_layout = QVBoxLayout(score_frame)
        
        score_title = QLabel("📊 Security Score Breakdown")
        score_title.setFont(QFont("Arial", 12, QFont.Bold))
        score_layout.addWidget(score_title)
        
        security_score = analysis.get('securityScore', 0)
        score_layout.addWidget(QLabel(f"Overall Score: {security_score}/100"))
        
        # Score components
        if security.get('https'):
            score_layout.addWidget(QLabel("✅ HTTPS: +20 points"))
        else:
            score_layout.addWidget(QLabel("❌ HTTPS: 0 points"))
        
        csrf_tokens = len(test_results.get('csrf', {}).get('tokens', []))
        if csrf_tokens > 0:
            score_layout.addWidget(QLabel(f"✅ CSRF Protection: +25 points ({csrf_tokens} tokens found)"))
        else:
            score_layout.addWidget(QLabel("❌ CSRF Protection: 0 points"))
        
        if security.get('csp'):
            score_layout.addWidget(QLabel("✅ Content Security Policy: +15 points"))
        else:
            score_layout.addWidget(QLabel("❌ Content Security Policy: 0 points"))
        
        if security.get('xFrameOptions'):
            score_layout.addWidget(QLabel("✅ X-Frame-Options: +10 points"))
        else:
            score_layout.addWidget(QLabel("❌ X-Frame-Options: 0 points"))
        
        scroll_layout.addWidget(score_frame)
        
        # Quick Status
        status_frame = QFrame()
        status_frame.setStyleSheet("background-color: #d4edda; border: 1px solid #c3e6cb; border-radius: 5px; padding: 15px;")
        status_layout = QVBoxLayout(status_frame)
        
        status_title = QLabel("🚦 Quick Status")
        status_title.setFont(QFont("Arial", 12, QFont.Bold))
        status_layout.addWidget(status_title)
        
        csrf_protection = test_results.get('csrf', {}).get('protection', 'unknown')
        if csrf_protection == 'detected':
            status_layout.addWidget(QLabel("✅ CSRF Protection: Detected"))
        else:
            status_layout.addWidget(QLabel("❌ CSRF Protection: Not detected"))
        
        mixed_content = security.get('mixedContent', False)
        if mixed_content:
            status_layout.addWidget(QLabel("⚠️ Mixed Content: Issues detected"))
        else:
            status_layout.addWidget(QLabel("✅ Mixed Content: No issues"))
        
        scroll_layout.addWidget(status_frame)
        
        # Recommendations
        recommendations = analysis.get('recommendations', [])
        if recommendations:
            rec_frame = QFrame()
            rec_frame.setStyleSheet("background-color: #fff3cd; border: 1px solid #ffeaa7; border-radius: 5px; padding: 15px;")
            rec_layout = QVBoxLayout(rec_frame)
            
            rec_title = QLabel(f"💡 Recommendations ({len(recommendations)})")
            rec_title.setFont(QFont("Arial", 12, QFont.Bold))
            rec_layout.addWidget(rec_title)
            
            for rec in recommendations:
                rec_label = QLabel(f"• {rec}")
                rec_label.setWordWrap(True)
                rec_layout.addWidget(rec_label)
            
            scroll_layout.addWidget(rec_frame)
        
        scroll_layout.addStretch()
        scroll.setWidget(scroll_widget)
        scroll.setWidgetResizable(True)
        
        layout.addWidget(scroll)
        
        return widget
    
    def create_csrf_analysis_tab(self, test_results):
        """Create the CSRF analysis tab"""
        from PyQt5.QtWidgets import (QWidget, QVBoxLayout, QTreeWidget, QTreeWidgetItem, 
                                   QHeaderView, QLabel, QTextEdit)
        from PyQt5.QtCore import Qt
        
        widget = QWidget()
        layout = QVBoxLayout(widget)
        
        # Header
        csrf_data = test_results.get('csrf', {})
        tokens_count = len(csrf_data.get('tokens', []))
        forms_count = len(csrf_data.get('forms', []))
        
        header = QLabel(f"🛡️ CSRF Protection Analysis - {tokens_count} tokens, {forms_count} forms")
        header.setStyleSheet("font-weight: bold; font-size: 14px; padding: 5px;")
        layout.addWidget(header)
        
        # CSRF Tokens Tree
        if tokens_count > 0:
            tokens_label = QLabel("🔑 CSRF Tokens Found:")
            tokens_label.setStyleSheet("font-weight: bold; margin-top: 10px;")
            layout.addWidget(tokens_label)
            
            tokens_tree = QTreeWidget()
            tokens_tree.setHeaderLabels(['Type', 'Name', 'Value Preview', 'Location'])
            tokens_tree.header().setSectionResizeMode(0, QHeaderView.ResizeToContents)
            tokens_tree.header().setSectionResizeMode(1, QHeaderView.ResizeToContents)
            tokens_tree.header().setSectionResizeMode(2, QHeaderView.Stretch)
            tokens_tree.header().setSectionResizeMode(3, QHeaderView.ResizeToContents)
            
            for token in csrf_data.get('tokens', []):
                item = QTreeWidgetItem()
                item.setText(0, token.get('type', 'unknown').replace('_', ' ').title())
                item.setText(1, token.get('name', ''))
                item.setText(2, token.get('value', token.get('content', '')))
                
                if token.get('type') == 'meta':
                    item.setText(3, 'HTML Head')
                elif token.get('type') == 'form_input':
                    item.setText(3, 'Form Input')
                else:
                    item.setText(3, 'Other')
                
                # Color code by type
                if token.get('type') == 'meta':
                    item.setBackground(0, QColor(173, 255, 173))  # Light green
                elif token.get('type') == 'form_input':
                    item.setBackground(0, QColor(255, 248, 220))  # Light yellow
                
                tokens_tree.addTopLevelItem(item)
            
            layout.addWidget(tokens_tree)
        
        # Forms Analysis
        if forms_count > 0:
            forms_label = QLabel("📝 Forms Analysis:")
            forms_label.setStyleSheet("font-weight: bold; margin-top: 10px;")
            layout.addWidget(forms_label)
            
            forms_tree = QTreeWidget()
            forms_tree.setHeaderLabels(['Form #', 'Action', 'Method', 'CSRF Tokens', 'Protection Status'])
            forms_tree.header().setSectionResizeMode(0, QHeaderView.ResizeToContents)
            forms_tree.header().setSectionResizeMode(1, QHeaderView.Stretch)
            forms_tree.header().setSectionResizeMode(2, QHeaderView.ResizeToContents)
            forms_tree.header().setSectionResizeMode(3, QHeaderView.ResizeToContents)
            forms_tree.header().setSectionResizeMode(4, QHeaderView.ResizeToContents)
            
            for form in csrf_data.get('forms', []):
                item = QTreeWidgetItem()
                item.setText(0, str(form.get('index', 0) + 1))
                item.setText(1, form.get('action', 'current page'))
                item.setText(2, form.get('method', 'GET'))
                
                csrf_tokens = form.get('csrfTokens', [])
                item.setText(3, str(len(csrf_tokens)))
                
                if len(csrf_tokens) > 0:
                    item.setText(4, '✅ Protected')
                    item.setBackground(4, QColor(144, 238, 144))  # Light green
                else:
                    item.setText(4, '❌ Vulnerable')
                    item.setBackground(4, QColor(255, 182, 193))  # Light red
                
                forms_tree.addTopLevelItem(item)
            
            layout.addWidget(forms_tree)
        
        # No CSRF protection found
        if tokens_count == 0:
            no_csrf_label = QLabel("❌ No CSRF protection detected on this page.\n\nCSRF (Cross-Site Request Forgery) protection is important for preventing unauthorized actions.\nConsider implementing CSRF tokens in your forms.")
            no_csrf_label.setStyleSheet("padding: 20px; background-color: #f8d7da; border-radius: 5px; color: #721c24;")
            no_csrf_label.setWordWrap(True)
            layout.addWidget(no_csrf_label)
        
        return widget
    
    def create_cors_analysis_tab(self, test_results):
        """Create the CORS analysis tab"""
        from PyQt5.QtWidgets import (QWidget, QVBoxLayout, QLabel, QTextEdit, QFrame)
        from PyQt5.QtCore import Qt
        from PyQt5.QtGui import QFont
        
        widget = QWidget()
        layout = QVBoxLayout(widget)
        
        # Header
        header = QLabel("🌐 CORS (Cross-Origin Resource Sharing) Analysis")
        header.setStyleSheet("font-weight: bold; font-size: 14px; padding: 5px;")
        layout.addWidget(header)
        
        cors_data = test_results.get('cors', {})
        
        # CORS Information
        cors_frame = QFrame()
        cors_frame.setStyleSheet("background-color: #f8f9fa; border: 1px solid #dee2e6; border-radius: 5px; padding: 15px;")
        cors_layout = QVBoxLayout(cors_frame)
        
        cors_title = QLabel("📋 CORS Configuration")
        cors_title.setFont(QFont("Arial", 12, QFont.Bold))
        cors_layout.addWidget(cors_title)
        
        # Note about CORS detection limitations
        cors_note = QLabel("ℹ️ Note: CORS headers are typically set by the server and may not be fully detectable from client-side JavaScript due to browser security restrictions.")
        cors_note.setStyleSheet("color: #6c757d; font-style: italic; margin-bottom: 10px;")
        cors_note.setWordWrap(True)
        cors_layout.addWidget(cors_note)
        
        # Test origins
        origins = cors_data.get('origins', [])
        if origins:
            cors_layout.addWidget(QLabel(f"Test Origins: {', '.join(origins)}"))
        
        # Allowed methods
        methods = cors_data.get('methods', [])
        if methods:
            cors_layout.addWidget(QLabel(f"Common Methods: {', '.join(methods)}"))
        
        # Allowed headers
        headers = cors_data.get('allowedHeaders', [])
        if headers:
            cors_layout.addWidget(QLabel(f"Common Headers: {', '.join(headers)}"))
        
        layout.addWidget(cors_frame)
        
        # CORS Explanation
        explanation_frame = QFrame()
        explanation_frame.setStyleSheet("background-color: #e8f4fd; border: 1px solid #bee5eb; border-radius: 5px; padding: 15px;")
        explanation_layout = QVBoxLayout(explanation_frame)
        
        explanation_title = QLabel("📚 CORS Explanation")
        explanation_title.setFont(QFont("Arial", 12, QFont.Bold))
        explanation_layout.addWidget(explanation_title)
        
        explanation_text = QTextEdit()
        explanation_text.setReadOnly(True)
        explanation_text.setMaximumHeight(200)
        explanation_text.setStyleSheet("background-color: white; border: 1px solid #ccc;")
        
        explanation_content = """CORS (Cross-Origin Resource Sharing) is a security feature implemented by web browsers to restrict web pages from making requests to a different domain than the one serving the web page.

Key CORS Headers:
• Access-Control-Allow-Origin: Specifies which origins can access the resource
• Access-Control-Allow-Methods: Specifies which HTTP methods are allowed
• Access-Control-Allow-Headers: Specifies which headers can be used
• Access-Control-Allow-Credentials: Indicates whether credentials can be included

CORS is enforced by browsers and configured by servers. Proper CORS configuration is essential for:
- API security
- Cross-domain requests
- Web application functionality"""
        
        explanation_text.setPlainText(explanation_content)
        explanation_layout.addWidget(explanation_text)
        
        layout.addWidget(explanation_frame)
        
        return widget
    
    def create_security_headers_tab(self, test_results):
        """Create the security headers tab"""
        from PyQt5.QtWidgets import (QWidget, QVBoxLayout, QTreeWidget, QTreeWidgetItem, 
                                   QHeaderView, QLabel)
        from PyQt5.QtCore import Qt
        from PyQt5.QtGui import QColor
        
        widget = QWidget()
        layout = QVBoxLayout(widget)
        
        # Header
        header = QLabel("🔒 Security Headers Analysis")
        header.setStyleSheet("font-weight: bold; font-size: 14px; padding: 5px;")
        layout.addWidget(header)
        
        # Security headers tree
        headers_tree = QTreeWidget()
        headers_tree.setHeaderLabels(['Security Header', 'Status', 'Value', 'Description'])
        headers_tree.header().setSectionResizeMode(0, QHeaderView.ResizeToContents)
        headers_tree.header().setSectionResizeMode(1, QHeaderView.ResizeToContents)
        headers_tree.header().setSectionResizeMode(2, QHeaderView.Stretch)
        headers_tree.header().setSectionResizeMode(3, QHeaderView.Stretch)
        
        security = test_results.get('security', {})
        
        # Security headers to check
        security_headers = [
            {
                'name': 'HTTPS',
                'value': 'Enabled' if security.get('https') else 'Disabled',
                'status': 'present' if security.get('https') else 'missing',
                'description': 'Encrypts data in transit between client and server'
            },
            {
                'name': 'Content-Security-Policy',
                'value': security.get('csp', 'Not set'),
                'status': 'present' if security.get('csp') else 'missing',
                'description': 'Prevents XSS attacks by controlling resource loading'
            },
            {
                'name': 'X-Frame-Options',
                'value': security.get('xFrameOptions', 'Not set'),
                'status': 'present' if security.get('xFrameOptions') else 'missing',
                'description': 'Prevents clickjacking attacks by controlling frame embedding'
            },
            {
                'name': 'Referrer-Policy',
                'value': security.get('referrerPolicy', 'Not set'),
                'status': 'present' if security.get('referrerPolicy') else 'missing',
                'description': 'Controls how much referrer information is sent with requests'
            },
            {
                'name': 'Mixed Content',
                'value': 'Issues detected' if security.get('mixedContent') else 'No issues',
                'status': 'warning' if security.get('mixedContent') else 'good',
                'description': 'HTTP resources on HTTPS pages can compromise security'
            }
        ]
        
        for header_info in security_headers:
            item = QTreeWidgetItem()
            item.setText(0, header_info['name'])
            
            status = header_info['status']
            if status == 'present' or status == 'good':
                item.setText(1, '✅ Present')
                item.setBackground(1, QColor(144, 238, 144))  # Light green
            elif status == 'warning':
                item.setText(1, '⚠️ Warning')
                item.setBackground(1, QColor(255, 255, 0))    # Yellow
            else:
                item.setText(1, '❌ Missing')
                item.setBackground(1, QColor(255, 182, 193))  # Light red
            
            item.setText(2, header_info['value'])
            item.setText(3, header_info['description'])
            
            headers_tree.addTopLevelItem(item)
        
        layout.addWidget(headers_tree)
        
        return widget
    
    def create_test_results_tab(self, test_results):
        """Create the test results tab"""
        from PyQt5.QtWidgets import (QWidget, QVBoxLayout, QTreeWidget, QTreeWidgetItem, 
                                   QHeaderView, QLabel, QTextEdit)
        from PyQt5.QtCore import Qt
        from PyQt5.QtGui import QColor
        
        widget = QWidget()
        layout = QVBoxLayout(widget)
        
        # Header
        header = QLabel("🧪 Automated Test Results")
        header.setStyleSheet("font-weight: bold; font-size: 14px; padding: 5px;")
        layout.addWidget(header)
        
        # Test results tree
        tests_tree = QTreeWidget()
        tests_tree.setHeaderLabels(['Test Name', 'Status', 'Result', 'Details'])
        tests_tree.header().setSectionResizeMode(0, QHeaderView.ResizeToContents)
        tests_tree.header().setSectionResizeMode(1, QHeaderView.ResizeToContents)
        tests_tree.header().setSectionResizeMode(2, QHeaderView.ResizeToContents)
        tests_tree.header().setSectionResizeMode(3, QHeaderView.Stretch)
        
        tests = test_results.get('tests', {})
        
        for test_name, test_result in tests.items():
            if test_result:  # Only show tests that have results
                item = QTreeWidgetItem()
                
                # Format test name
                formatted_name = test_name.replace('cors', 'CORS').replace('csrf', 'CSRF').replace('sameOrigin', 'Same-Origin')
                item.setText(0, formatted_name)
                
                status = test_result.get('status', 'unknown')
                message = test_result.get('message', 'No details available')
                
                # Status with icon
                if status in ['success', 'allowed', 'accessible']:
                    item.setText(1, '✅ Pass')
                    item.setBackground(1, QColor(144, 238, 144))  # Light green
                    item.setText(2, 'Success')
                elif status in ['blocked', 'error']:
                    item.setText(1, '❌ Fail')
                    item.setBackground(1, QColor(255, 182, 193))  # Light red
                    item.setText(2, 'Failed')
                else:
                    item.setText(1, '⚠️ Warning')
                    item.setBackground(1, QColor(255, 255, 0))    # Yellow
                    item.setText(2, 'Unknown')
                
                item.setText(3, message)
                
                tests_tree.addTopLevelItem(item)
        
        layout.addWidget(tests_tree)
        
        # Raw test data (for debugging)
        raw_data_label = QLabel("📋 Raw Test Data:")
        raw_data_label.setStyleSheet("font-weight: bold; margin-top: 15px;")
        layout.addWidget(raw_data_label)
        
        raw_data_text = QTextEdit()
        raw_data_text.setReadOnly(True)
        raw_data_text.setMaximumHeight(150)
        raw_data_text.setStyleSheet("font-family: monospace; background-color: #f8f9fa;")
        
        import json
        raw_data_text.setPlainText(json.dumps(test_results, indent=2))
        layout.addWidget(raw_data_text)
        
        return widget
    
    def generate_csrf_cors_text_report(self, export_data):
        """Generate a text-based CSRF/CORS report"""
        lines = []
        lines.append("CSRF/CORS SECURITY ANALYSIS REPORT")
        lines.append("=" * 50)
        lines.append(f"URL: {export_data['url']}")
        lines.append(f"Analysis Date: {export_data['timestamp']}")
        lines.append("")
        
        test_results = export_data['test_results']
        analysis = test_results.get('analysis', {})
        
        # Security Score
        security_score = analysis.get('securityScore', 0)
        lines.append(f"SECURITY SCORE: {security_score}/100")
        lines.append("")
        
        # CSRF Analysis
        csrf_data = test_results.get('csrf', {})
        lines.append("CSRF PROTECTION ANALYSIS:")
        lines.append("-" * 30)
        lines.append(f"Protection Status: {csrf_data.get('protection', 'unknown')}")
        lines.append(f"CSRF Tokens Found: {len(csrf_data.get('tokens', []))}")
        lines.append(f"Forms Analyzed: {len(csrf_data.get('forms', []))}")
        lines.append("")
        
        # Security Headers
        security = test_results.get('security', {})
        lines.append("SECURITY HEADERS:")
        lines.append("-" * 20)
        lines.append(f"HTTPS: {'Enabled' if security.get('https') else 'Disabled'}")
        lines.append(f"Content Security Policy: {'Present' if security.get('csp') else 'Missing'}")
        lines.append(f"X-Frame-Options: {'Present' if security.get('xFrameOptions') else 'Missing'}")
        lines.append(f"Mixed Content Issues: {'Yes' if security.get('mixedContent') else 'No'}")
        lines.append("")
        
        # Recommendations
        recommendations = analysis.get('recommendations', [])
        if recommendations:
            lines.append("RECOMMENDATIONS:")
            lines.append("-" * 20)
            for rec in recommendations:
                lines.append(f"• {rec}")
            lines.append("")
        
        return '\n'.join(lines)
    
    def manage_storage(self, browser):
        """Comprehensive storage management for localStorage, sessionStorage, cookies, etc."""
        try:
            page = browser.page()
            current_url = browser.url().toString()
            
            # Show initial status
            self.main_window.status_info.setText("💾 Analyzing browser storage...")
            
            # JavaScript to extract all storage data from the page
            js_code = """
            (function() {
                var storageData = {
                    localStorage: {},
                    sessionStorage: {},
                    cookies: [],
                    phpSessions: [],
                    indexedDB: [],
                    webSQL: [],
                    cacheStorage: [],
                    serviceWorkerRegistrations: [],
                    permissions: {},
                    quota: {},
                    storageEstimate: null,
                    url: window.location.href,
                    domain: window.location.hostname,
                    protocol: window.location.protocol
                };
                
                // Extract localStorage
                try {
                    if (typeof Storage !== 'undefined' && localStorage) {
                        for (var i = 0; i < localStorage.length; i++) {
                            var key = localStorage.key(i);
                            var value = localStorage.getItem(key);
                            storageData.localStorage[key] = {
                                value: value,
                                size: new Blob([value]).size,
                                type: typeof value
                            };
                        }
                    }
                } catch (e) {
                    storageData.localStorage = { error: e.message };
                }
                
                // Extract sessionStorage
                try {
                    if (typeof Storage !== 'undefined' && sessionStorage) {
                        for (var i = 0; i < sessionStorage.length; i++) {
                            var key = sessionStorage.key(i);
                            var value = sessionStorage.getItem(key);
                            storageData.sessionStorage[key] = {
                                value: value,
                                size: new Blob([value]).size,
                                type: typeof value
                            };
                        }
                    }
                } catch (e) {
                    storageData.sessionStorage = { error: e.message };
                }
                
                // Extract cookies
                try {
                    if (document.cookie) {
                        var cookies = document.cookie.split(';');
                        cookies.forEach(function(cookie) {
                            var parts = cookie.trim().split('=');
                            if (parts.length >= 2) {
                                var name = parts[0].trim();
                                var value = parts.slice(1).join('=').trim();
                                
                                var cookieData = {
                                    name: name,
                                    value: value,
                                    size: new Blob([name + value]).size,
                                    domain: window.location.hostname,
                                    path: '/',
                                    secure: false, // Can't determine from document.cookie
                                    httpOnly: false, // Can't determine from document.cookie
                                    sameSite: 'unknown',
                                    isPHPSession: false
                                };
                                
                                // Detect PHP session cookies
                                if (name.toLowerCase() === 'phpsessid' || 
                                    name.toLowerCase().includes('sess') ||
                                    name.toLowerCase().includes('session') ||
                                    /^[A-Z0-9]{26,40}$/i.test(value)) { // Common PHP session ID pattern
                                    cookieData.isPHPSession = true;
                                    storageData.phpSessions.push({
                                        sessionId: value,
                                        cookieName: name,
                                        domain: window.location.hostname,
                                        detected: 'cookie-based',
                                        size: cookieData.size,
                                        pattern: 'standard'
                                    });
                                }
                                
                                storageData.cookies.push(cookieData);
                            }
                        });
                    }
                } catch (e) {
                    storageData.cookies = [{ error: e.message }];
                }
                
                // Additional PHP session detection methods
                try {
                    // Check for common PHP session indicators in the page
                    var scripts = document.getElementsByTagName('script');
                    var hasPhpSessionVars = false;
                    
                    for (var i = 0; i < scripts.length; i++) {
                        var scriptContent = scripts[i].textContent || scripts[i].innerText || '';
                        
                        // Look for PHP session variables in JavaScript
                        if (scriptContent.includes('$_SESSION') || 
                            scriptContent.includes('session_id') ||
                            scriptContent.includes('PHPSESSID') ||
                            scriptContent.includes('session_start')) {
                            hasPhpSessionVars = true;
                            break;
                        }
                    }
                    
                    // Check for PHP session in URL parameters
                    var urlParams = new URLSearchParams(window.location.search);
                    var sessionInUrl = false;
                    
                    urlParams.forEach(function(value, key) {
                        if (key.toLowerCase().includes('sess') || 
                            key.toLowerCase() === 'phpsessid' ||
                            /^[A-Z0-9]{26,40}$/i.test(value)) {
                            sessionInUrl = true;
                            storageData.phpSessions.push({
                                sessionId: value,
                                paramName: key,
                                domain: window.location.hostname,
                                detected: 'url-parameter',
                                size: new Blob([key + value]).size,
                                pattern: 'url-based'
                            });
                        }
                    });
                    
                    // Check for PHP session indicators in meta tags
                    var metaTags = document.getElementsByTagName('meta');
                    for (var i = 0; i < metaTags.length; i++) {
                        var name = metaTags[i].getAttribute('name') || '';
                        var content = metaTags[i].getAttribute('content') || '';
                        
                        if (name.toLowerCase().includes('session') || 
                            content.includes('PHPSESSID') ||
                            content.includes('session_id')) {
                            storageData.phpSessions.push({
                                sessionId: content,
                                metaName: name,
                                domain: window.location.hostname,
                                detected: 'meta-tag',
                                size: new Blob([name + content]).size,
                                pattern: 'meta-based'
                            });
                        }
                    }
                    
                    // Check for server-side session indicators
                    if (hasPhpSessionVars && storageData.phpSessions.length === 0) {
                        storageData.phpSessions.push({
                            sessionId: 'detected-in-scripts',
                            domain: window.location.hostname,
                            detected: 'server-side-variables',
                            size: 0,
                            pattern: 'script-based',
                            note: 'PHP session variables detected in page scripts'
                        });
                    }
                    
                    // Check for common PHP frameworks session patterns
                    var frameworks = [
                        { name: 'Laravel', pattern: /laravel_session/i },
                        { name: 'Symfony', pattern: /REMEMBERME|sf2s/i },
                        { name: 'CodeIgniter', pattern: /ci_session/i },
                        { name: 'CakePHP', pattern: /CAKEPHP/i },
                        { name: 'Zend', pattern: /ZFSESSION/i },
                        { name: 'WordPress', pattern: /wordpress_logged_in|wp-settings/i },
                        { name: 'Drupal', pattern: /SESS[a-f0-9]{32}/i },
                        { name: 'Joomla', pattern: /[a-f0-9]{32}/i }
                    ];
                    
                    storageData.cookies.forEach(function(cookie) {
                        frameworks.forEach(function(framework) {
                            if (framework.pattern.test(cookie.name) || framework.pattern.test(cookie.value)) {
                                var existingSession = storageData.phpSessions.find(function(session) {
                                    return session.framework === framework.name;
                                });
                                
                                if (!existingSession) {
                                    storageData.phpSessions.push({
                                        sessionId: cookie.value,
                                        cookieName: cookie.name,
                                        domain: window.location.hostname,
                                        detected: 'framework-cookie',
                                        size: cookie.size,
                                        pattern: 'framework-based',
                                        framework: framework.name
                                    });
                                }
                            }
                        });
                    });
                    
                } catch (e) {
                    // Error in PHP session detection
                    console.log('PHP session detection error:', e.message);
                }
                
                // Check IndexedDB
                try {
                    if ('indexedDB' in window) {
                        // We can't easily enumerate all databases without knowing their names
                        // So we'll just indicate IndexedDB is available
                        storageData.indexedDB.push({
                            available: true,
                            note: 'IndexedDB is available but requires specific database names to enumerate'
                        });
                    }
                } catch (e) {
                    storageData.indexedDB = [{ error: e.message }];
                }
                
                // Check WebSQL (deprecated but might still exist)
                try {
                    if ('openDatabase' in window) {
                        storageData.webSQL.push({
                            available: true,
                            note: 'WebSQL is deprecated but still available'
                        });
                    }
                } catch (e) {
                    storageData.webSQL = [{ error: e.message }];
                }
                
                // Check Cache Storage
                try {
                    if ('caches' in window) {
                        // We'll indicate it's available but can't enumerate without async
                        storageData.cacheStorage.push({
                            available: true,
                            note: 'Cache Storage API is available'
                        });
                    }
                } catch (e) {
                    storageData.cacheStorage = [{ error: e.message }];
                }
                
                // Check Service Worker registrations
                try {
                    if ('serviceWorker' in navigator) {
                        storageData.serviceWorkerRegistrations.push({
                            available: true,
                            note: 'Service Worker API is available'
                        });
                    }
                } catch (e) {
                    storageData.serviceWorkerRegistrations = [{ error: e.message }];
                }
                
                // Check Storage Quota API
                try {
                    if ('storage' in navigator && 'estimate' in navigator.storage) {
                        // We'll mark it as available but can't get estimate synchronously
                        storageData.quota = {
                            available: true,
                            note: 'Storage Quota API is available'
                        };
                    }
                } catch (e) {
                    storageData.quota = { error: e.message };
                }
                
                // Check Permissions API
                try {
                    if ('permissions' in navigator) {
                        storageData.permissions = {
                            available: true,
                            note: 'Permissions API is available'
                        };
                    }
                } catch (e) {
                    storageData.permissions = { error: e.message };
                }
                
                // Calculate total storage usage
                var totalSize = 0;
                
                // Add localStorage size
                Object.keys(storageData.localStorage).forEach(function(key) {
                    if (storageData.localStorage[key].size) {
                        totalSize += storageData.localStorage[key].size;
                    }
                });
                
                // Add sessionStorage size
                Object.keys(storageData.sessionStorage).forEach(function(key) {
                    if (storageData.sessionStorage[key].size) {
                        totalSize += storageData.sessionStorage[key].size;
                    }
                });
                
                // Add cookies size
                storageData.cookies.forEach(function(cookie) {
                    if (cookie.size) {
                        totalSize += cookie.size;
                    }
                });
                
                storageData.totalSize = totalSize;
                
                // Storage summary
                storageData.summary = {
                    localStorageItems: Object.keys(storageData.localStorage).length,
                    sessionStorageItems: Object.keys(storageData.sessionStorage).length,
                    cookiesCount: storageData.cookies.length,
                    phpSessionsCount: storageData.phpSessions.length,
                    totalSize: totalSize,
                    hasIndexedDB: storageData.indexedDB.length > 0 && storageData.indexedDB[0].available,
                    hasWebSQL: storageData.webSQL.length > 0 && storageData.webSQL[0].available,
                    hasCacheStorage: storageData.cacheStorage.length > 0 && storageData.cacheStorage[0].available,
                    hasServiceWorker: storageData.serviceWorkerRegistrations.length > 0 && storageData.serviceWorkerRegistrations[0].available,
                    hasPHPSessions: storageData.phpSessions.length > 0
                };
                
                return storageData;
            })();
            """
            
            def process_storage_data(storage_data):
                if not storage_data:
                    self.main_window.status_info.setText("❌ Failed to analyze storage")
                    QTimer.singleShot(3000, lambda: self.main_window.status_info.setText(""))
                    return
                
                # Create and show the storage management dialog
                self.show_storage_management_dialog(storage_data, current_url)
            
            # Execute JavaScript to get storage data
            page.runJavaScript(js_code, process_storage_data)
            
        except Exception as e:
            self.main_window.status_info.setText(f"❌ Storage analysis error: {str(e)}")
            QTimer.singleShot(3000, lambda: self.main_window.status_info.setText(""))
    
    def show_storage_management_dialog(self, storage_data, base_url):
        """Show dialog with storage management interface"""
        from PyQt5.QtWidgets import (QDialog, QVBoxLayout, QHBoxLayout, QLabel, 
                                   QTextEdit, QPushButton, QTabWidget, QWidget,
                                   QTreeWidget, QTreeWidgetItem, QHeaderView, 
                                   QFileDialog, QScrollArea, QFrame, QMessageBox,
                                   QCheckBox, QSpinBox, QComboBox, QLineEdit)
        from PyQt5.QtCore import Qt, QTimer
        from PyQt5.QtGui import QFont, QColor
        from datetime import datetime
        import json
        
        # Create dialog
        dialog = QDialog(self.main_window)
        summary = storage_data.get('summary', {})
        total_items = summary.get('localStorageItems', 0) + summary.get('sessionStorageItems', 0) + summary.get('cookiesCount', 0)
        dialog.setWindowTitle(f"💾 Store Management - {total_items} items found")
        dialog.setMinimumSize(1200, 800)
        dialog.resize(1400, 900)
        
        layout = QVBoxLayout(dialog)
        
        # Header
        header_label = QLabel(f"Storage Analysis for: {base_url}")
        header_label.setStyleSheet("font-weight: bold; padding: 10px; background-color: #e8f4fd; border-radius: 5px;")
        header_label.setWordWrap(True)
        layout.addWidget(header_label)
        
        # Summary
        total_size = storage_data.get('totalSize', 0)
        size_text = self.format_storage_size(total_size)
        php_sessions_count = len(storage_data.get('phpSessions', []))
        
        summary_label = QLabel(f"📊 Summary: {summary.get('localStorageItems', 0)} localStorage, {summary.get('sessionStorageItems', 0)} sessionStorage, {summary.get('cookiesCount', 0)} cookies, {php_sessions_count} PHP sessions | Total size: {size_text}")
        summary_label.setStyleSheet("padding: 5px; background-color: #f0f8ff; border-radius: 3px;")
        summary_label.setWordWrap(True)
        layout.addWidget(summary_label)
        
        # Tab widget for different storage types
        tab_widget = QTabWidget()
        layout.addWidget(tab_widget)
        
        # Overview Tab
        overview_widget = self.create_storage_overview_tab(storage_data)
        tab_widget.addTab(overview_widget, "📊 Overview")
        
        # localStorage Tab
        local_storage_widget = self.create_local_storage_tab(storage_data)
        local_count = len(storage_data.get('localStorage', {}))
        tab_widget.addTab(local_storage_widget, f"🏠 localStorage ({local_count})")
        
        # sessionStorage Tab
        session_storage_widget = self.create_session_storage_tab(storage_data)
        session_count = len(storage_data.get('sessionStorage', {}))
        tab_widget.addTab(session_storage_widget, f"⏱️ sessionStorage ({session_count})")
        
        # Cookies Tab
        cookies_widget = self.create_cookies_tab(storage_data)
        cookies_count = len(storage_data.get('cookies', []))
        tab_widget.addTab(cookies_widget, f"🍪 Cookies ({cookies_count})")
        
        # PHP Sessions Tab
        php_sessions_widget = self.create_php_sessions_tab(storage_data)
        php_sessions_count = len(storage_data.get('phpSessions', []))
        tab_widget.addTab(php_sessions_widget, f"🐘 PHP Sessions ({php_sessions_count})")
        
        # Advanced Storage Tab
        advanced_widget = self.create_advanced_storage_tab(storage_data)
        tab_widget.addTab(advanced_widget, "🔧 Advanced Storage")
        
        # Storage Tools Tab
        tools_widget = self.create_storage_tools_tab(storage_data)
        tab_widget.addTab(tools_widget, "🛠️ Storage Tools")
        
        # Buttons
        button_layout = QHBoxLayout()
        
        export_button = QPushButton("💾 Export Data")
        clear_all_button = QPushButton("🗑️ Clear All Storage")
        refresh_button = QPushButton("🔄 Refresh")
        close_button = QPushButton("❌ Close")
        
        button_layout.addStretch()
        button_layout.addWidget(export_button)
        button_layout.addWidget(clear_all_button)
        button_layout.addWidget(refresh_button)
        button_layout.addWidget(close_button)
        layout.addLayout(button_layout)
        
        def export_data():
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            filename = f"storage_data_{timestamp}.json"
            
            file_path, _ = QFileDialog.getSaveFileName(
                dialog,
                "Export Storage Data",
                filename,
                "JSON Files (*.json);;Text Files (*.txt);;All Files (*.*)"
            )
            
            if file_path:
                try:
                    export_data = {
                        'url': base_url,
                        'timestamp': datetime.now().isoformat(),
                        'storage_data': storage_data
                    }
                    
                    if file_path.endswith('.json'):
                        with open(file_path, 'w', encoding='utf-8') as f:
                            json.dump(export_data, f, indent=2, ensure_ascii=False)
                    else:
                        # Export as text report
                        with open(file_path, 'w', encoding='utf-8') as f:
                            f.write(self.generate_storage_text_report(export_data))
                    
                    self.main_window.status_info.setText(f"✅ Storage data exported to: {file_path}")
                    QTimer.singleShot(3000, lambda: self.main_window.status_info.setText(""))
                except Exception as e:
                    self.main_window.status_info.setText(f"❌ Export failed: {str(e)}")
                    QTimer.singleShot(3000, lambda: self.main_window.status_info.setText(""))
        
        def clear_all_storage():
            reply = QMessageBox.question(
                dialog,
                "Clear All Storage",
                "Are you sure you want to clear ALL storage data?\n\nThis will remove:\n• All localStorage items\n• All sessionStorage items\n• All cookies\n\nThis action cannot be undone!",
                QMessageBox.Yes | QMessageBox.No,
                QMessageBox.No
            )
            
            if reply == QMessageBox.Yes:
                self.clear_all_browser_storage()
                dialog.accept()
                # Re-run the storage analysis
                browser = self.get_current_browser()
                if browser:
                    self.manage_storage(browser)
        
        def refresh_storage():
            dialog.accept()
            # Re-run the storage analysis
            browser = self.get_current_browser()
            if browser:
                self.manage_storage(browser)
        
        # Connect buttons
        export_button.clicked.connect(export_data)
        clear_all_button.clicked.connect(clear_all_storage)
        refresh_button.clicked.connect(refresh_storage)
        close_button.clicked.connect(dialog.accept)
        
        # Show dialog
        dialog.exec_()
        
        # Update main window status
        self.main_window.status_info.setText(f"💾 Storage analysis complete - {total_items} items found")
        QTimer.singleShot(5000, lambda: self.main_window.status_info.setText(""))
    
    def create_storage_overview_tab(self, storage_data):
        """Create the overview tab for storage analysis"""
        from PyQt5.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QLabel, 
                                   QFrame, QScrollArea, QProgressBar)
        from PyQt5.QtCore import Qt
        from PyQt5.QtGui import QFont
        
        widget = QWidget()
        layout = QVBoxLayout(widget)
        
        # Create scroll area
        scroll = QScrollArea()
        scroll_widget = QWidget()
        scroll_layout = QVBoxLayout(scroll_widget)
        
        # Storage Summary
        summary_frame = QFrame()
        summary_frame.setStyleSheet("background-color: #f8f9fa; border: 1px solid #dee2e6; border-radius: 5px; padding: 15px;")
        summary_layout = QVBoxLayout(summary_frame)
        
        summary_title = QLabel("📊 Storage Summary")
        summary_title.setFont(QFont("Arial", 12, QFont.Bold))
        summary_layout.addWidget(summary_title)
        
        summary = storage_data.get('summary', {})
        total_size = storage_data.get('totalSize', 0)
        
        # Storage type breakdown
        local_items = summary.get('localStorageItems', 0)
        session_items = summary.get('sessionStorageItems', 0)
        cookies_count = summary.get('cookiesCount', 0)
        
        summary_layout.addWidget(QLabel(f"🏠 localStorage: {local_items} items"))
        summary_layout.addWidget(QLabel(f"⏱️ sessionStorage: {session_items} items"))
        summary_layout.addWidget(QLabel(f"🍪 Cookies: {cookies_count} items"))
        summary_layout.addWidget(QLabel(f"� PHPa Sessions: {summary.get('phpSessionsCount', 0)} detected"))
        summary_layout.addWidget(QLabel(f"📏 Total Size: {self.format_storage_size(total_size)}"))
        
        scroll_layout.addWidget(summary_frame)
        
        # Storage Types Available
        types_frame = QFrame()
        types_frame.setStyleSheet("background-color: #e8f4fd; border: 1px solid #bee5eb; border-radius: 5px; padding: 15px;")
        types_layout = QVBoxLayout(types_frame)
        
        types_title = QLabel("🔧 Available Storage APIs")
        types_title.setFont(QFont("Arial", 12, QFont.Bold))
        types_layout.addWidget(types_title)
        
        # Check which storage APIs are available
        if summary.get('hasIndexedDB'):
            types_layout.addWidget(QLabel("✅ IndexedDB - Available for complex data storage"))
        else:
            types_layout.addWidget(QLabel("❌ IndexedDB - Not available"))
        
        if summary.get('hasWebSQL'):
            types_layout.addWidget(QLabel("⚠️ WebSQL - Available but deprecated"))
        else:
            types_layout.addWidget(QLabel("❌ WebSQL - Not available (deprecated)"))
        
        if summary.get('hasCacheStorage'):
            types_layout.addWidget(QLabel("✅ Cache Storage - Available for offline caching"))
        else:
            types_layout.addWidget(QLabel("❌ Cache Storage - Not available"))
        
        if summary.get('hasServiceWorker'):
            types_layout.addWidget(QLabel("✅ Service Worker - Available for background processing"))
        else:
            types_layout.addWidget(QLabel("❌ Service Worker - Not available"))
        
        if summary.get('hasPHPSessions'):
            types_layout.addWidget(QLabel("✅ PHP Sessions - Detected on this website"))
        else:
            types_layout.addWidget(QLabel("❌ PHP Sessions - Not detected"))
        
        scroll_layout.addWidget(types_frame)
        
        # Storage Usage Visualization
        if total_size > 0:
            usage_frame = QFrame()
            usage_frame.setStyleSheet("background-color: #d4edda; border: 1px solid #c3e6cb; border-radius: 5px; padding: 15px;")
            usage_layout = QVBoxLayout(usage_frame)
            
            usage_title = QLabel("📈 Storage Usage Breakdown")
            usage_title.setFont(QFont("Arial", 12, QFont.Bold))
            usage_layout.addWidget(usage_title)
            
            # Calculate sizes for each storage type
            local_storage = storage_data.get('localStorage', {})
            session_storage = storage_data.get('sessionStorage', {})
            cookies = storage_data.get('cookies', [])
            
            local_size = sum(item.get('size', 0) for item in local_storage.values() if isinstance(item, dict))
            session_size = sum(item.get('size', 0) for item in session_storage.values() if isinstance(item, dict))
            cookies_size = sum(cookie.get('size', 0) for cookie in cookies if isinstance(cookie, dict))
            
            # Progress bars for visual representation
            if local_size > 0:
                local_progress = QProgressBar()
                local_progress.setRange(0, total_size)
                local_progress.setValue(local_size)
                local_progress.setFormat(f"localStorage: {self.format_storage_size(local_size)} ({local_size*100//total_size}%)")
                usage_layout.addWidget(local_progress)
            
            if session_size > 0:
                session_progress = QProgressBar()
                session_progress.setRange(0, total_size)
                session_progress.setValue(session_size)
                session_progress.setFormat(f"sessionStorage: {self.format_storage_size(session_size)} ({session_size*100//total_size}%)")
                usage_layout.addWidget(session_progress)
            
            if cookies_size > 0:
                cookies_progress = QProgressBar()
                cookies_progress.setRange(0, total_size)
                cookies_progress.setValue(cookies_size)
                cookies_progress.setFormat(f"Cookies: {self.format_storage_size(cookies_size)} ({cookies_size*100//total_size}%)")
                usage_layout.addWidget(cookies_progress)
            
            scroll_layout.addWidget(usage_frame)
        
        # Domain and Security Info
        security_frame = QFrame()
        security_frame.setStyleSheet("background-color: #fff3cd; border: 1px solid #ffeaa7; border-radius: 5px; padding: 15px;")
        security_layout = QVBoxLayout(security_frame)
        
        security_title = QLabel("🔒 Domain & Security Information")
        security_title.setFont(QFont("Arial", 12, QFont.Bold))
        security_layout.addWidget(security_title)
        
        domain = storage_data.get('domain', 'Unknown')
        protocol = storage_data.get('protocol', 'Unknown')
        
        security_layout.addWidget(QLabel(f"Domain: {domain}"))
        security_layout.addWidget(QLabel(f"Protocol: {protocol}"))
        
        if protocol == 'https:':
            security_layout.addWidget(QLabel("✅ Secure connection (HTTPS)"))
        else:
            security_layout.addWidget(QLabel("⚠️ Insecure connection (HTTP)"))
        
        scroll_layout.addWidget(security_frame)
        
        scroll_layout.addStretch()
        scroll.setWidget(scroll_widget)
        scroll.setWidgetResizable(True)
        
        layout.addWidget(scroll)
        
        return widget
    
    def create_local_storage_tab(self, storage_data):
        """Create the localStorage tab"""
        from PyQt5.QtWidgets import (QWidget, QVBoxLayout, QTreeWidget, QTreeWidgetItem, 
                                   QHeaderView, QLabel, QHBoxLayout, QPushButton, QMessageBox)
        from PyQt5.QtCore import Qt
        from PyQt5.QtGui import QColor
        
        widget = QWidget()
        layout = QVBoxLayout(widget)
        
        # Header with controls
        header_layout = QHBoxLayout()
        
        header = QLabel("🏠 localStorage Items")
        header.setStyleSheet("font-weight: bold; font-size: 14px; padding: 5px;")
        header_layout.addWidget(header)
        
        header_layout.addStretch()
        
        clear_local_btn = QPushButton("🗑️ Clear localStorage")
        clear_local_btn.clicked.connect(lambda: self.clear_storage_type('localStorage'))
        header_layout.addWidget(clear_local_btn)
        
        layout.addLayout(header_layout)
        
        # Tree widget for localStorage items
        tree = QTreeWidget()
        tree.setHeaderLabels(['Key', 'Value Preview', 'Size', 'Type', 'Actions'])
        tree.header().setSectionResizeMode(0, QHeaderView.ResizeToContents)
        tree.header().setSectionResizeMode(1, QHeaderView.Stretch)
        tree.header().setSectionResizeMode(2, QHeaderView.ResizeToContents)
        tree.header().setSectionResizeMode(3, QHeaderView.ResizeToContents)
        tree.header().setSectionResizeMode(4, QHeaderView.ResizeToContents)
        
        local_storage = storage_data.get('localStorage', {})
        
        if not local_storage or (len(local_storage) == 1 and 'error' in local_storage):
            no_data_label = QLabel("❌ No localStorage data found or access denied.")
            no_data_label.setStyleSheet("padding: 20px; background-color: #f8d7da; border-radius: 5px; color: #721c24;")
            no_data_label.setWordWrap(True)
            layout.addWidget(no_data_label)
        else:
            for key, item_data in local_storage.items():
                if isinstance(item_data, dict) and 'value' in item_data:
                    item = QTreeWidgetItem()
                    item.setText(0, key)
                    
                    # Value preview (truncated)
                    value = str(item_data.get('value', ''))
                    preview = value[:100] + ('...' if len(value) > 100 else '')
                    item.setText(1, preview)
                    
                    # Size
                    size = item_data.get('size', 0)
                    item.setText(2, self.format_storage_size(size))
                    
                    # Type detection
                    try:
                        import json
                        json.loads(value)
                        item.setText(3, "JSON")
                        item.setBackground(3, QColor(173, 255, 173))  # Light green
                    except:
                        if value.startswith('data:'):
                            item.setText(3, "Data URL")
                            item.setBackground(3, QColor(255, 255, 173))  # Light yellow
                        elif len(value) > 1000:
                            item.setText(3, "Large Text")
                            item.setBackground(3, QColor(255, 182, 193))  # Light red
                        else:
                            item.setText(3, "String")
                    
                    item.setText(4, "🗑️ Delete")
                    
                    tree.addTopLevelItem(item)
            
            # Handle item clicks for actions
            def on_item_clicked(item, column):
                if column == 4:  # Actions column
                    key = item.text(0)
                    reply = QMessageBox.question(
                        widget,
                        "Delete localStorage Item",
                        f"Are you sure you want to delete the localStorage item '{key}'?",
                        QMessageBox.Yes | QMessageBox.No,
                        QMessageBox.No
                    )
                    if reply == QMessageBox.Yes:
                        self.delete_storage_item('localStorage', key)
            
            tree.itemClicked.connect(on_item_clicked)
            layout.addWidget(tree)
        
        return widget
    
    def create_session_storage_tab(self, storage_data):
        """Create the sessionStorage tab"""
        from PyQt5.QtWidgets import (QWidget, QVBoxLayout, QTreeWidget, QTreeWidgetItem, 
                                   QHeaderView, QLabel, QHBoxLayout, QPushButton, QMessageBox)
        from PyQt5.QtCore import Qt
        from PyQt5.QtGui import QColor
        
        widget = QWidget()
        layout = QVBoxLayout(widget)
        
        # Header with controls
        header_layout = QHBoxLayout()
        
        header = QLabel("⏱️ sessionStorage Items")
        header.setStyleSheet("font-weight: bold; font-size: 14px; padding: 5px;")
        header_layout.addWidget(header)
        
        header_layout.addStretch()
        
        clear_session_btn = QPushButton("🗑️ Clear sessionStorage")
        clear_session_btn.clicked.connect(lambda: self.clear_storage_type('sessionStorage'))
        header_layout.addWidget(clear_session_btn)
        
        layout.addLayout(header_layout)
        
        # Tree widget for sessionStorage items
        tree = QTreeWidget()
        tree.setHeaderLabels(['Key', 'Value Preview', 'Size', 'Type', 'Actions'])
        tree.header().setSectionResizeMode(0, QHeaderView.ResizeToContents)
        tree.header().setSectionResizeMode(1, QHeaderView.Stretch)
        tree.header().setSectionResizeMode(2, QHeaderView.ResizeToContents)
        tree.header().setSectionResizeMode(3, QHeaderView.ResizeToContents)
        tree.header().setSectionResizeMode(4, QHeaderView.ResizeToContents)
        
        session_storage = storage_data.get('sessionStorage', {})
        
        if not session_storage or (len(session_storage) == 1 and 'error' in session_storage):
            no_data_label = QLabel("❌ No sessionStorage data found or access denied.")
            no_data_label.setStyleSheet("padding: 20px; background-color: #f8d7da; border-radius: 5px; color: #721c24;")
            no_data_label.setWordWrap(True)
            layout.addWidget(no_data_label)
        else:
            for key, item_data in session_storage.items():
                if isinstance(item_data, dict) and 'value' in item_data:
                    item = QTreeWidgetItem()
                    item.setText(0, key)
                    
                    # Value preview (truncated)
                    value = str(item_data.get('value', ''))
                    preview = value[:100] + ('...' if len(value) > 100 else '')
                    item.setText(1, preview)
                    
                    # Size
                    size = item_data.get('size', 0)
                    item.setText(2, self.format_storage_size(size))
                    
                    # Type detection
                    try:
                        import json
                        json.loads(value)
                        item.setText(3, "JSON")
                        item.setBackground(3, QColor(173, 255, 173))  # Light green
                    except:
                        if value.startswith('data:'):
                            item.setText(3, "Data URL")
                            item.setBackground(3, QColor(255, 255, 173))  # Light yellow
                        elif len(value) > 1000:
                            item.setText(3, "Large Text")
                            item.setBackground(3, QColor(255, 182, 193))  # Light red
                        else:
                            item.setText(3, "String")
                    
                    item.setText(4, "🗑️ Delete")
                    
                    tree.addTopLevelItem(item)
            
            # Handle item clicks for actions
            def on_item_clicked(item, column):
                if column == 4:  # Actions column
                    key = item.text(0)
                    reply = QMessageBox.question(
                        widget,
                        "Delete sessionStorage Item",
                        f"Are you sure you want to delete the sessionStorage item '{key}'?",
                        QMessageBox.Yes | QMessageBox.No,
                        QMessageBox.No
                    )
                    if reply == QMessageBox.Yes:
                        self.delete_storage_item('sessionStorage', key)
            
            tree.itemClicked.connect(on_item_clicked)
            layout.addWidget(tree)
        
        return widget
    
    def create_cookies_tab(self, storage_data):
        """Create the cookies tab"""
        from PyQt5.QtWidgets import (QWidget, QVBoxLayout, QTreeWidget, QTreeWidgetItem, 
                                   QHeaderView, QLabel, QHBoxLayout, QPushButton, QMessageBox)
        from PyQt5.QtCore import Qt
        from PyQt5.QtGui import QColor
        
        widget = QWidget()
        layout = QVBoxLayout(widget)
        
        # Header with controls
        header_layout = QHBoxLayout()
        
        header = QLabel("🍪 Cookies")
        header.setStyleSheet("font-weight: bold; font-size: 14px; padding: 5px;")
        header_layout.addWidget(header)
        
        header_layout.addStretch()
        
        clear_cookies_btn = QPushButton("🗑️ Clear All Cookies")
        clear_cookies_btn.clicked.connect(lambda: self.clear_storage_type('cookies'))
        header_layout.addWidget(clear_cookies_btn)
        
        layout.addLayout(header_layout)
        
        # Tree widget for cookies
        tree = QTreeWidget()
        tree.setHeaderLabels(['Name', 'Value Preview', 'Size', 'Domain', 'Path', 'Security', 'Actions'])
        tree.header().setSectionResizeMode(0, QHeaderView.ResizeToContents)
        tree.header().setSectionResizeMode(1, QHeaderView.Stretch)
        tree.header().setSectionResizeMode(2, QHeaderView.ResizeToContents)
        tree.header().setSectionResizeMode(3, QHeaderView.ResizeToContents)
        tree.header().setSectionResizeMode(4, QHeaderView.ResizeToContents)
        tree.header().setSectionResizeMode(5, QHeaderView.ResizeToContents)
        tree.header().setSectionResizeMode(6, QHeaderView.ResizeToContents)
        
        cookies = storage_data.get('cookies', [])
        
        if not cookies or (len(cookies) == 1 and 'error' in cookies[0]):
            no_data_label = QLabel("❌ No cookies found or access denied.")
            no_data_label.setStyleSheet("padding: 20px; background-color: #f8d7da; border-radius: 5px; color: #721c24;")
            no_data_label.setWordWrap(True)
            layout.addWidget(no_data_label)
        else:
            for cookie in cookies:
                if isinstance(cookie, dict) and 'name' in cookie:
                    item = QTreeWidgetItem()
                    
                    name = cookie.get('name', '')
                    value = cookie.get('value', '')
                    
                    item.setText(0, name)
                    
                    # Value preview (truncated)
                    preview = value[:50] + ('...' if len(value) > 50 else '')
                    item.setText(1, preview)
                    
                    # Size
                    size = cookie.get('size', 0)
                    item.setText(2, self.format_storage_size(size))
                    
                    # Domain and Path
                    item.setText(3, cookie.get('domain', ''))
                    item.setText(4, cookie.get('path', '/'))
                    
                    # Security attributes
                    security_attrs = []
                    if cookie.get('secure'):
                        security_attrs.append('Secure')
                    if cookie.get('httpOnly'):
                        security_attrs.append('HttpOnly')
                    if cookie.get('sameSite') and cookie.get('sameSite') != 'unknown':
                        security_attrs.append(f"SameSite={cookie.get('sameSite')}")
                    
                    security_text = ', '.join(security_attrs) if security_attrs else 'None'
                    item.setText(5, security_text)
                    
                    # Color code based on security
                    if security_attrs:
                        item.setBackground(5, QColor(144, 238, 144))  # Light green
                    else:
                        item.setBackground(5, QColor(255, 182, 193))  # Light red
                    
                    item.setText(6, "🗑️ Delete")
                    
                    tree.addTopLevelItem(item)
            
            # Handle item clicks for actions
            def on_item_clicked(item, column):
                if column == 6:  # Actions column
                    name = item.text(0)
                    reply = QMessageBox.question(
                        widget,
                        "Delete Cookie",
                        f"Are you sure you want to delete the cookie '{name}'?",
                        QMessageBox.Yes | QMessageBox.No,
                        QMessageBox.No
                    )
                    if reply == QMessageBox.Yes:
                        self.delete_storage_item('cookies', name)
            
            tree.itemClicked.connect(on_item_clicked)
            layout.addWidget(tree)
        
        return widget
    
    def create_php_sessions_tab(self, storage_data):
        """Create the PHP sessions tab"""
        from PyQt5.QtWidgets import (QWidget, QVBoxLayout, QTreeWidget, QTreeWidgetItem, 
                                   QHeaderView, QLabel, QHBoxLayout, QPushButton, QMessageBox,
                                   QTextEdit, QFrame)
        from PyQt5.QtCore import Qt
        from PyQt5.QtGui import QColor, QFont
        
        widget = QWidget()
        layout = QVBoxLayout(widget)
        
        # Header with info
        header_frame = QFrame()
        header_frame.setStyleSheet("background-color: #f0f8ff; border: 1px solid #b8daff; border-radius: 5px; padding: 10px;")
        header_layout = QVBoxLayout(header_frame)
        
        header = QLabel("🐘 PHP Sessions Analysis")
        header.setStyleSheet("font-weight: bold; font-size: 14px;")
        header_layout.addWidget(header)
        
        info_label = QLabel("PHP sessions are server-side storage mechanisms. Detection is based on cookies, URL parameters, and page analysis.")
        info_label.setStyleSheet("font-size: 11px; color: #666; font-style: italic;")
        info_label.setWordWrap(True)
        header_layout.addWidget(info_label)
        
        layout.addWidget(header_frame)
        
        php_sessions = storage_data.get('phpSessions', [])
        
        if not php_sessions:
            no_data_frame = QFrame()
            no_data_frame.setStyleSheet("background-color: #fff3cd; border: 1px solid #ffeaa7; border-radius: 5px; padding: 20px;")
            no_data_layout = QVBoxLayout(no_data_frame)
            
            no_data_title = QLabel("❌ No PHP Sessions Detected")
            no_data_title.setFont(QFont("Arial", 12, QFont.Bold))
            no_data_layout.addWidget(no_data_title)
            
            no_data_text = QLabel("""
This could mean:
• The website doesn't use PHP sessions
• Sessions are managed server-side without client-side indicators
• Session cookies are HttpOnly (more secure but not detectable via JavaScript)
• Custom session management is being used

Common PHP session indicators we look for:
• PHPSESSID cookie
• Session-related cookies (names containing 'sess', 'session')
• Framework-specific session cookies (Laravel, Symfony, etc.)
• Session IDs in URL parameters
• PHP session variables in page scripts
            """)
            no_data_text.setWordWrap(True)
            no_data_text.setStyleSheet("color: #856404;")
            no_data_layout.addWidget(no_data_text)
            
            layout.addWidget(no_data_frame)
        else:
            # Tree widget for PHP sessions
            tree = QTreeWidget()
            tree.setHeaderLabels(['Session ID', 'Detection Method', 'Framework/Type', 'Size', 'Domain', 'Pattern', 'Details'])
            tree.header().setSectionResizeMode(0, QHeaderView.Stretch)
            tree.header().setSectionResizeMode(1, QHeaderView.ResizeToContents)
            tree.header().setSectionResizeMode(2, QHeaderView.ResizeToContents)
            tree.header().setSectionResizeMode(3, QHeaderView.ResizeToContents)
            tree.header().setSectionResizeMode(4, QHeaderView.ResizeToContents)
            tree.header().setSectionResizeMode(5, QHeaderView.ResizeToContents)
            tree.header().setSectionResizeMode(6, QHeaderView.Stretch)
            
            for session in php_sessions:
                item = QTreeWidgetItem()
                
                # Session ID (truncated for display)
                session_id = session.get('sessionId', '')
                if len(session_id) > 20:
                    display_id = session_id[:10] + '...' + session_id[-10:]
                else:
                    display_id = session_id
                item.setText(0, display_id)
                
                # Detection method
                detection_method = session.get('detected', 'unknown')
                method_display = {
                    'cookie-based': '🍪 Cookie',
                    'url-parameter': '🔗 URL Parameter',
                    'meta-tag': '📋 Meta Tag',
                    'server-side-variables': '⚙️ Server Variables',
                    'framework-cookie': '🏗️ Framework Cookie'
                }.get(detection_method, detection_method)
                item.setText(1, method_display)
                
                # Framework/Type
                framework = session.get('framework', '')
                if framework:
                    item.setText(2, framework)
                    # Color code by framework
                    framework_colors = {
                        'Laravel': QColor(255, 182, 193),    # Light red
                        'Symfony': QColor(173, 255, 173),    # Light green
                        'CodeIgniter': QColor(255, 255, 173), # Light yellow
                        'WordPress': QColor(173, 216, 230),   # Light blue
                        'Drupal': QColor(221, 160, 221),     # Light purple
                        'CakePHP': QColor(255, 218, 185),    # Light orange
                    }
                    if framework in framework_colors:
                        item.setBackground(2, framework_colors[framework])
                else:
                    item.setText(2, 'Standard PHP')
                
                # Size
                size = session.get('size', 0)
                item.setText(3, self.format_storage_size(size))
                
                # Domain
                item.setText(4, session.get('domain', ''))
                
                # Pattern
                pattern = session.get('pattern', '')
                pattern_display = {
                    'standard': '📝 Standard',
                    'url-based': '🔗 URL-based',
                    'meta-based': '📋 Meta-based',
                    'script-based': '📜 Script-based',
                    'framework-based': '🏗️ Framework-based'
                }.get(pattern, pattern)
                item.setText(5, pattern_display)
                
                # Details
                details = []
                if session.get('cookieName'):
                    details.append(f"Cookie: {session.get('cookieName')}")
                if session.get('paramName'):
                    details.append(f"Parameter: {session.get('paramName')}")
                if session.get('metaName'):
                    details.append(f"Meta: {session.get('metaName')}")
                if session.get('note'):
                    details.append(session.get('note'))
                
                item.setText(6, ' | '.join(details))
                
                # Color code by detection confidence
                if detection_method in ['cookie-based', 'framework-cookie']:
                    item.setBackground(0, QColor(144, 238, 144))  # Light green - high confidence
                elif detection_method in ['url-parameter', 'meta-tag']:
                    item.setBackground(0, QColor(255, 255, 0))    # Yellow - medium confidence
                else:
                    item.setBackground(0, QColor(255, 182, 193))  # Light red - low confidence
                
                tree.addTopLevelItem(item)
            
            layout.addWidget(tree)
            
            # PHP Session Information
            info_frame = QFrame()
            info_frame.setStyleSheet("background-color: #d4edda; border: 1px solid #c3e6cb; border-radius: 5px; padding: 15px; margin-top: 10px;")
            info_layout = QVBoxLayout(info_frame)
            
            info_title = QLabel("ℹ️ PHP Session Information")
            info_title.setFont(QFont("Arial", 12, QFont.Bold))
            info_layout.addWidget(info_title)
            
            info_text = QTextEdit()
            info_text.setReadOnly(True)
            info_text.setMaximumHeight(120)
            info_text.setStyleSheet("font-family: monospace; background-color: #f8f9fa; border: 1px solid #dee2e6;")
            
            info_content = []
            info_content.append("PHP SESSION ANALYSIS:")
            info_content.append("-" * 25)
            info_content.append(f"Total sessions detected: {len(php_sessions)}")
            
            # Group by detection method
            methods = {}
            frameworks = set()
            for session in php_sessions:
                method = session.get('detected', 'unknown')
                methods[method] = methods.get(method, 0) + 1
                if session.get('framework'):
                    frameworks.add(session.get('framework'))
            
            info_content.append("\nDetection methods:")
            for method, count in methods.items():
                info_content.append(f"  {method}: {count}")
            
            if frameworks:
                info_content.append(f"\nFrameworks detected: {', '.join(frameworks)}")
            
            info_content.append("\nSecurity Notes:")
            info_content.append("• HttpOnly cookies are more secure but not detectable via JavaScript")
            info_content.append("• URL-based sessions are less secure than cookie-based")
            info_content.append("• Server-side session storage is not directly accessible from client")
            
            info_text.setPlainText('\n'.join(info_content))
            info_layout.addWidget(info_text)
            
            layout.addWidget(info_frame)
        
        return widget
    
    def create_advanced_storage_tab(self, storage_data):
        """Create the advanced storage tab for IndexedDB, WebSQL, etc."""
        from PyQt5.QtWidgets import (QWidget, QVBoxLayout, QLabel, QFrame, QScrollArea, QTextEdit)
        from PyQt5.QtCore import Qt
        from PyQt5.QtGui import QFont
        
        widget = QWidget()
        layout = QVBoxLayout(widget)
        
        # Header
        header = QLabel("🔧 Advanced Storage APIs")
        header.setStyleSheet("font-weight: bold; font-size: 14px; padding: 5px;")
        layout.addWidget(header)
        
        # Create scroll area
        scroll = QScrollArea()
        scroll_widget = QWidget()
        scroll_layout = QVBoxLayout(scroll_widget)
        
        # IndexedDB
        indexeddb_frame = QFrame()
        indexeddb_frame.setStyleSheet("background-color: #f8f9fa; border: 1px solid #dee2e6; border-radius: 5px; padding: 15px;")
        indexeddb_layout = QVBoxLayout(indexeddb_frame)
        
        indexeddb_title = QLabel("🗄️ IndexedDB")
        indexeddb_title.setFont(QFont("Arial", 12, QFont.Bold))
        indexeddb_layout.addWidget(indexeddb_title)
        
        indexeddb_data = storage_data.get('indexedDB', [])
        if indexeddb_data and indexeddb_data[0].get('available'):
            indexeddb_layout.addWidget(QLabel("✅ IndexedDB API is available"))
            indexeddb_layout.addWidget(QLabel("ℹ️ IndexedDB databases require specific names to enumerate"))
            indexeddb_layout.addWidget(QLabel("💡 Use browser DevTools → Application → Storage → IndexedDB for detailed inspection"))
        else:
            indexeddb_layout.addWidget(QLabel("❌ IndexedDB is not available"))
        
        scroll_layout.addWidget(indexeddb_frame)
        
        # WebSQL
        websql_frame = QFrame()
        websql_frame.setStyleSheet("background-color: #fff3cd; border: 1px solid #ffeaa7; border-radius: 5px; padding: 15px;")
        websql_layout = QVBoxLayout(websql_frame)
        
        websql_title = QLabel("🗃️ WebSQL (Deprecated)")
        websql_title.setFont(QFont("Arial", 12, QFont.Bold))
        websql_layout.addWidget(websql_title)
        
        websql_data = storage_data.get('webSQL', [])
        if websql_data and websql_data[0].get('available'):
            websql_layout.addWidget(QLabel("⚠️ WebSQL is available but deprecated"))
            websql_layout.addWidget(QLabel("🚫 WebSQL support has been removed from modern browsers"))
            websql_layout.addWidget(QLabel("💡 Consider migrating to IndexedDB"))
        else:
            websql_layout.addWidget(QLabel("❌ WebSQL is not available (expected in modern browsers)"))
        
        scroll_layout.addWidget(websql_frame)
        
        # Cache Storage
        cache_frame = QFrame()
        cache_frame.setStyleSheet("background-color: #e8f4fd; border: 1px solid #bee5eb; border-radius: 5px; padding: 15px;")
        cache_layout = QVBoxLayout(cache_frame)
        
        cache_title = QLabel("📦 Cache Storage")
        cache_title.setFont(QFont("Arial", 12, QFont.Bold))
        cache_layout.addWidget(cache_title)
        
        cache_data = storage_data.get('cacheStorage', [])
        if cache_data and cache_data[0].get('available'):
            cache_layout.addWidget(QLabel("✅ Cache Storage API is available"))
            cache_layout.addWidget(QLabel("🌐 Used by Service Workers for offline functionality"))
            cache_layout.addWidget(QLabel("💡 Use browser DevTools → Application → Storage → Cache Storage for inspection"))
        else:
            cache_layout.addWidget(QLabel("❌ Cache Storage is not available"))
        
        scroll_layout.addWidget(cache_frame)
        
        # Service Worker
        sw_frame = QFrame()
        sw_frame.setStyleSheet("background-color: #d4edda; border: 1px solid #c3e6cb; border-radius: 5px; padding: 15px;")
        sw_layout = QVBoxLayout(sw_frame)
        
        sw_title = QLabel("⚙️ Service Worker")
        sw_title.setFont(QFont("Arial", 12, QFont.Bold))
        sw_layout.addWidget(sw_title)
        
        sw_data = storage_data.get('serviceWorkerRegistrations', [])
        if sw_data and sw_data[0].get('available'):
            sw_layout.addWidget(QLabel("✅ Service Worker API is available"))
            sw_layout.addWidget(QLabel("🔄 Enables background sync, push notifications, and offline functionality"))
            sw_layout.addWidget(QLabel("💡 Use browser DevTools → Application → Service Workers for management"))
        else:
            sw_layout.addWidget(QLabel("❌ Service Worker is not available"))
        
        scroll_layout.addWidget(sw_frame)
        
        # Storage Quota
        quota_frame = QFrame()
        quota_frame.setStyleSheet("background-color: #f0f8ff; border: 1px solid #b8daff; border-radius: 5px; padding: 15px;")
        quota_layout = QVBoxLayout(quota_frame)
        
        quota_title = QLabel("📊 Storage Quota")
        quota_title.setFont(QFont("Arial", 12, QFont.Bold))
        quota_layout.addWidget(quota_title)
        
        quota_data = storage_data.get('quota', {})
        if quota_data.get('available'):
            quota_layout.addWidget(QLabel("✅ Storage Quota API is available"))
            quota_layout.addWidget(QLabel("📏 Provides information about storage usage and quota"))
            quota_layout.addWidget(QLabel("💡 Use navigator.storage.estimate() in console for details"))
        else:
            quota_layout.addWidget(QLabel("❌ Storage Quota API is not available"))
        
        scroll_layout.addWidget(quota_frame)
        
        # Permissions API
        permissions_frame = QFrame()
        permissions_frame.setStyleSheet("background-color: #fff5f5; border: 1px solid #ffcccc; border-radius: 5px; padding: 15px;")
        permissions_layout = QVBoxLayout(permissions_frame)
        
        permissions_title = QLabel("🔐 Permissions API")
        permissions_title.setFont(QFont("Arial", 12, QFont.Bold))
        permissions_layout.addWidget(permissions_title)
        
        permissions_data = storage_data.get('permissions', {})
        if permissions_data.get('available'):
            permissions_layout.addWidget(QLabel("✅ Permissions API is available"))
            permissions_layout.addWidget(QLabel("🔒 Manages permissions for various browser features"))
            permissions_layout.addWidget(QLabel("💡 Use navigator.permissions.query() in console"))
        else:
            permissions_layout.addWidget(QLabel("❌ Permissions API is not available"))
        
        scroll_layout.addWidget(permissions_frame)
        
        scroll_layout.addStretch()
        scroll.setWidget(scroll_widget)
        scroll.setWidgetResizable(True)
        
        layout.addWidget(scroll)
        
        return widget
    
    def create_storage_tools_tab(self, storage_data):
        """Create the storage tools tab with utilities"""
        from PyQt5.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QLabel, 
                                   QFrame, QPushButton, QTextEdit, QLineEdit,
                                   QComboBox, QSpinBox, QCheckBox, QMessageBox)
        from PyQt5.QtCore import Qt
        from PyQt5.QtGui import QFont
        
        widget = QWidget()
        layout = QVBoxLayout(widget)
        
        # Header
        header = QLabel("🛠️ Storage Management Tools")
        header.setStyleSheet("font-weight: bold; font-size: 14px; padding: 5px;")
        layout.addWidget(header)
        
        # Storage Cleaner
        cleaner_frame = QFrame()
        cleaner_frame.setStyleSheet("background-color: #f8d7da; border: 1px solid #f5c6cb; border-radius: 5px; padding: 15px;")
        cleaner_layout = QVBoxLayout(cleaner_frame)
        
        cleaner_title = QLabel("🧹 Storage Cleaner")
        cleaner_title.setFont(QFont("Arial", 12, QFont.Bold))
        cleaner_layout.addWidget(cleaner_title)
        
        # Selective clearing options
        clear_options_layout = QHBoxLayout()
        
        clear_local_btn = QPushButton("🗑️ Clear localStorage")
        clear_local_btn.clicked.connect(lambda: self.clear_storage_type('localStorage'))
        clear_options_layout.addWidget(clear_local_btn)
        
        clear_session_btn = QPushButton("🗑️ Clear sessionStorage")
        clear_session_btn.clicked.connect(lambda: self.clear_storage_type('sessionStorage'))
        clear_options_layout.addWidget(clear_session_btn)
        
        clear_cookies_btn = QPushButton("🗑️ Clear Cookies")
        clear_cookies_btn.clicked.connect(lambda: self.clear_storage_type('cookies'))
        clear_options_layout.addWidget(clear_cookies_btn)
        
        cleaner_layout.addLayout(clear_options_layout)
        
        # Clear all button
        clear_all_btn = QPushButton("🗑️ Clear ALL Storage")
        clear_all_btn.setStyleSheet("background-color: #dc3545; color: white; font-weight: bold; padding: 8px;")
        clear_all_btn.clicked.connect(self.clear_all_browser_storage)
        cleaner_layout.addWidget(clear_all_btn)
        
        layout.addWidget(cleaner_frame)
        
        # Storage Inspector
        inspector_frame = QFrame()
        inspector_frame.setStyleSheet("background-color: #d1ecf1; border: 1px solid #bee5eb; border-radius: 5px; padding: 15px;")
        inspector_layout = QVBoxLayout(inspector_frame)
        
        inspector_title = QLabel("🔍 Storage Inspector")
        inspector_title.setFont(QFont("Arial", 12, QFont.Bold))
        inspector_layout.addWidget(inspector_title)
        
        # Search functionality
        search_layout = QHBoxLayout()
        search_layout.addWidget(QLabel("Search:"))
        
        search_input = QLineEdit()
        search_input.setPlaceholderText("Search keys/values...")
        search_layout.addWidget(search_input)
        
        search_btn = QPushButton("🔍 Search")
        search_layout.addWidget(search_btn)
        
        inspector_layout.addLayout(search_layout)
        
        # Search results
        search_results = QTextEdit()
        search_results.setReadOnly(True)
        search_results.setMaximumHeight(150)
        search_results.setStyleSheet("font-family: monospace; background-color: #f8f9fa;")
        search_results.setPlainText("Enter a search term to find matching keys or values in storage...")
        
        def perform_search():
            query = search_input.text().lower()
            if not query:
                search_results.setPlainText("Please enter a search term.")
                return
            
            results = []
            results.append(f"Search results for: '{query}'")
            results.append("=" * 40)
            
            # Search localStorage
            local_storage = storage_data.get('localStorage', {})
            for key, item_data in local_storage.items():
                if isinstance(item_data, dict):
                    value = str(item_data.get('value', ''))
                    if query in key.lower() or query in value.lower():
                        results.append(f"localStorage[{key}]: {value[:100]}...")
            
            # Search sessionStorage
            session_storage = storage_data.get('sessionStorage', {})
            for key, item_data in session_storage.items():
                if isinstance(item_data, dict):
                    value = str(item_data.get('value', ''))
                    if query in key.lower() or query in value.lower():
                        results.append(f"sessionStorage[{key}]: {value[:100]}...")
            
            # Search cookies
            cookies = storage_data.get('cookies', [])
            for cookie in cookies:
                if isinstance(cookie, dict):
                    name = cookie.get('name', '')
                    value = cookie.get('value', '')
                    if query in name.lower() or query in value.lower():
                        results.append(f"Cookie[{name}]: {value[:100]}...")
            
            if len(results) == 2:  # Only header
                results.append("No matches found.")
            
            search_results.setPlainText('\n'.join(results))
        
        search_btn.clicked.connect(perform_search)
        search_input.returnPressed.connect(perform_search)
        
        inspector_layout.addWidget(search_results)
        
        layout.addWidget(inspector_frame)
        
        # Storage Statistics
        stats_frame = QFrame()
        stats_frame.setStyleSheet("background-color: #d4edda; border: 1px solid #c3e6cb; border-radius: 5px; padding: 15px;")
        stats_layout = QVBoxLayout(stats_frame)
        
        stats_title = QLabel("📊 Storage Statistics")
        stats_title.setFont(QFont("Arial", 12, QFont.Bold))
        stats_layout.addWidget(stats_title)
        
        # Calculate and display statistics
        summary = storage_data.get('summary', {})
        total_size = storage_data.get('totalSize', 0)
        
        stats_text = QTextEdit()
        stats_text.setReadOnly(True)
        stats_text.setMaximumHeight(120)
        stats_text.setStyleSheet("font-family: monospace; background-color: #f8f9fa;")
        
        stats_content = []
        stats_content.append("STORAGE STATISTICS:")
        stats_content.append("-" * 20)
        stats_content.append(f"localStorage items: {summary.get('localStorageItems', 0)}")
        stats_content.append(f"sessionStorage items: {summary.get('sessionStorageItems', 0)}")
        stats_content.append(f"Cookies: {summary.get('cookiesCount', 0)}")
        stats_content.append(f"PHP Sessions: {summary.get('phpSessionsCount', 0)}")
        stats_content.append(f"Total size: {self.format_storage_size(total_size)}")
        stats_content.append(f"Domain: {storage_data.get('domain', 'Unknown')}")
        stats_content.append(f"Protocol: {storage_data.get('protocol', 'Unknown')}")
        
        stats_text.setPlainText('\n'.join(stats_content))
        stats_layout.addWidget(stats_text)
        
        layout.addWidget(stats_frame)
        
        layout.addStretch()
        
        return widget
    
    def format_storage_size(self, size_bytes):
        """Format storage size in human-readable format"""
        if size_bytes == 0:
            return "0 B"
        
        units = ['B', 'KB', 'MB', 'GB']
        size = float(size_bytes)
        unit_index = 0
        
        while size >= 1024 and unit_index < len(units) - 1:
            size /= 1024
            unit_index += 1
        
        if unit_index == 0:
            return f"{int(size)} {units[unit_index]}"
        else:
            return f"{size:.1f} {units[unit_index]}"
    
    def clear_storage_type(self, storage_type):
        """Clear specific storage type"""
        from PyQt5.QtWidgets import QMessageBox
        
        reply = QMessageBox.question(
            self.main_window,
            f"Clear {storage_type}",
            f"Are you sure you want to clear all {storage_type} data?\n\nThis action cannot be undone!",
            QMessageBox.Yes | QMessageBox.No,
            QMessageBox.No
        )
        
        if reply == QMessageBox.Yes:
            browser = self.get_current_browser()
            if browser:
                page = browser.page()
                
                if storage_type == 'localStorage':
                    js_code = "localStorage.clear(); 'localStorage cleared';"
                elif storage_type == 'sessionStorage':
                    js_code = "sessionStorage.clear(); 'sessionStorage cleared';"
                elif storage_type == 'cookies':
                    js_code = """
                    document.cookie.split(";").forEach(function(c) { 
                        document.cookie = c.replace(/^ +/, "").replace(/=.*/, "=;expires=" + new Date().toUTCString() + ";path=/"); 
                    }); 
                    'Cookies cleared';
                    """
                else:
                    return
                
                def on_cleared(result):
                    self.main_window.status_info.setText(f"✅ {storage_type} cleared successfully")
                    QTimer.singleShot(3000, lambda: self.main_window.status_info.setText(""))
                
                page.runJavaScript(js_code, on_cleared)
    
    def clear_all_browser_storage(self):
        """Clear all browser storage"""
        from PyQt5.QtWidgets import QMessageBox
        
        reply = QMessageBox.question(
            self.main_window,
            "Clear All Storage",
            "Are you sure you want to clear ALL storage data?\n\nThis will remove:\n• All localStorage items\n• All sessionStorage items\n• All cookies\n\nThis action cannot be undone!",
            QMessageBox.Yes | QMessageBox.No,
            QMessageBox.No
        )
        
        if reply == QMessageBox.Yes:
            browser = self.get_current_browser()
            if browser:
                page = browser.page()
                
                js_code = """
                // Clear localStorage
                localStorage.clear();
                
                // Clear sessionStorage
                sessionStorage.clear();
                
                // Clear cookies
                document.cookie.split(";").forEach(function(c) { 
                    document.cookie = c.replace(/^ +/, "").replace(/=.*/, "=;expires=" + new Date().toUTCString() + ";path=/"); 
                });
                
                'All storage cleared';
                """
                
                def on_cleared(result):
                    self.main_window.status_info.setText("✅ All storage cleared successfully")
                    QTimer.singleShot(3000, lambda: self.main_window.status_info.setText(""))
                
                page.runJavaScript(js_code, on_cleared)
    
    def delete_storage_item(self, storage_type, key):
        """Delete specific storage item"""
        browser = self.get_current_browser()
        if browser:
            page = browser.page()
            
            if storage_type == 'localStorage':
                js_code = f"localStorage.removeItem('{key}'); 'Item removed from localStorage';"
            elif storage_type == 'sessionStorage':
                js_code = f"sessionStorage.removeItem('{key}'); 'Item removed from sessionStorage';"
            elif storage_type == 'cookies':
                js_code = f"document.cookie = '{key}=;expires=Thu, 01 Jan 1970 00:00:00 UTC;path=/;'; 'Cookie removed';"
            else:
                return
            
            def on_deleted(result):
                self.main_window.status_info.setText(f"✅ {key} deleted from {storage_type}")
                QTimer.singleShot(3000, lambda: self.main_window.status_info.setText(""))
            
            page.runJavaScript(js_code, on_deleted)
    
    def generate_storage_text_report(self, export_data):
        """Generate a text-based storage report"""
        lines = []
        lines.append("BROWSER STORAGE ANALYSIS REPORT")
        lines.append("=" * 50)
        lines.append(f"URL: {export_data['url']}")
        lines.append(f"Analysis Date: {export_data['timestamp']}")
        lines.append("")
        
        storage_data = export_data['storage_data']
        summary = storage_data.get('summary', {})
        
        # Summary
        lines.append("STORAGE SUMMARY:")
        lines.append("-" * 20)
        lines.append(f"localStorage items: {summary.get('localStorageItems', 0)}")
        lines.append(f"sessionStorage items: {summary.get('sessionStorageItems', 0)}")
        lines.append(f"Cookies: {summary.get('cookiesCount', 0)}")
        lines.append(f"PHP Sessions: {summary.get('phpSessionsCount', 0)}")
        lines.append(f"Total size: {self.format_storage_size(storage_data.get('totalSize', 0))}")
        lines.append(f"Domain: {storage_data.get('domain', 'Unknown')}")
        lines.append(f"Protocol: {storage_data.get('protocol', 'Unknown')}")
        lines.append("")
        
        # localStorage details
        local_storage = storage_data.get('localStorage', {})
        if local_storage and not ('error' in local_storage):
            lines.append("LOCALSTORAGE ITEMS:")
            lines.append("-" * 20)
            for key, item_data in local_storage.items():
                if isinstance(item_data, dict):
                    value = str(item_data.get('value', ''))
                    size = item_data.get('size', 0)
                    lines.append(f"Key: {key}")
                    lines.append(f"Size: {self.format_storage_size(size)}")
                    lines.append(f"Value: {value[:200]}{'...' if len(value) > 200 else ''}")
                    lines.append("-" * 10)
            lines.append("")
        
        # sessionStorage details
        session_storage = storage_data.get('sessionStorage', {})
        if session_storage and not ('error' in session_storage):
            lines.append("SESSIONSTORAGE ITEMS:")
            lines.append("-" * 20)
            for key, item_data in session_storage.items():
                if isinstance(item_data, dict):
                    value = str(item_data.get('value', ''))
                    size = item_data.get('size', 0)
                    lines.append(f"Key: {key}")
                    lines.append(f"Size: {self.format_storage_size(size)}")
                    lines.append(f"Value: {value[:200]}{'...' if len(value) > 200 else ''}")
                    lines.append("-" * 10)
            lines.append("")
        
        # Cookies details
        cookies = storage_data.get('cookies', [])
        if cookies and not ('error' in cookies[0] if cookies else False):
            lines.append("COOKIES:")
            lines.append("-" * 20)
            for cookie in cookies:
                if isinstance(cookie, dict):
                    lines.append(f"Name: {cookie.get('name', '')}")
                    lines.append(f"Value: {cookie.get('value', '')}")
                    lines.append(f"Domain: {cookie.get('domain', '')}")
                    lines.append(f"Path: {cookie.get('path', '')}")
                    lines.append(f"Size: {self.format_storage_size(cookie.get('size', 0))}")
                    lines.append("-" * 10)
            lines.append("")
        
        # PHP Sessions details
        php_sessions = storage_data.get('phpSessions', [])
        if php_sessions:
            lines.append("PHP SESSIONS:")
            lines.append("-" * 20)
            for session in php_sessions:
                session_id = session.get('sessionId', '')
                if len(session_id) > 40:
                    session_id = session_id[:20] + '...' + session_id[-20:]
                lines.append(f"Session ID: {session_id}")
                lines.append(f"Detection: {session.get('detected', 'unknown')}")
                lines.append(f"Framework: {session.get('framework', 'Standard PHP')}")
                lines.append(f"Pattern: {session.get('pattern', 'unknown')}")
                lines.append(f"Size: {self.format_storage_size(session.get('size', 0))}")
                if session.get('cookieName'):
                    lines.append(f"Cookie Name: {session.get('cookieName')}")
                if session.get('note'):
                    lines.append(f"Note: {session.get('note')}")
                lines.append("-" * 10)
            lines.append("")
        
        # Advanced storage APIs
        lines.append("ADVANCED STORAGE APIS:")
        lines.append("-" * 20)
        lines.append(f"IndexedDB: {'Available' if summary.get('hasIndexedDB') else 'Not available'}")
        lines.append(f"WebSQL: {'Available (deprecated)' if summary.get('hasWebSQL') else 'Not available'}")
        lines.append(f"Cache Storage: {'Available' if summary.get('hasCacheStorage') else 'Not available'}")
        lines.append(f"Service Worker: {'Available' if summary.get('hasServiceWorker') else 'Not available'}")
        lines.append(f"PHP Sessions: {'Detected' if summary.get('hasPHPSessions') else 'Not detected'}")
        
        return '\n'.join(lines)