"""
Web Tracker Detection Tool
Detects and analyzes tracking attempts on websites including cookies, scripts, pixels, and fingerprinting.
"""

from PyQt5.QtCore import *
from PyQt5.QtWidgets import *
from PyQt5.QtGui import *
from PyQt5.QtWebEngineWidgets import *
import json
import re
import urllib.parse
from datetime import datetime
import os


class TrackerDetector(QObject):
    """Detects various types of web tracking"""
    
    # Signal emitted when trackers are detected
    trackers_detected = pyqtSignal(dict)
    
    def __init__(self, parent=None):
        super().__init__(parent)
        
        # Known tracking domains and patterns
        self.tracking_domains = {
            # Analytics
            'google-analytics.com': {'type': 'Analytics', 'company': 'Google', 'risk': 'Medium'},
            'googletagmanager.com': {'type': 'Analytics', 'company': 'Google', 'risk': 'Medium'},
            'analytics.google.com': {'type': 'Analytics', 'company': 'Google', 'risk': 'Medium'},
            'facebook.com/tr': {'type': 'Analytics', 'company': 'Facebook/Meta', 'risk': 'High'},
            'connect.facebook.net': {'type': 'Analytics', 'company': 'Facebook/Meta', 'risk': 'High'},
            
            # Advertising
            'doubleclick.net': {'type': 'Advertising', 'company': 'Google', 'risk': 'High'},
            'googlesyndication.com': {'type': 'Advertising', 'company': 'Google', 'risk': 'High'},
            'googleadservices.com': {'type': 'Advertising', 'company': 'Google', 'risk': 'High'},
            'amazon-adsystem.com': {'type': 'Advertising', 'company': 'Amazon', 'risk': 'High'},
            'adsystem.amazon.com': {'type': 'Advertising', 'company': 'Amazon', 'risk': 'High'},
            
            # Social Media
            'facebook.com/plugins': {'type': 'Social', 'company': 'Facebook/Meta', 'risk': 'Medium'},
            'twitter.com/widgets': {'type': 'Social', 'company': 'Twitter/X', 'risk': 'Medium'},
            'linkedin.com/analytics': {'type': 'Social', 'company': 'LinkedIn', 'risk': 'Medium'},
            
            # Data Brokers
            'scorecardresearch.com': {'type': 'Data Broker', 'company': 'Comscore', 'risk': 'High'},
            'quantserve.com': {'type': 'Data Broker', 'company': 'Quantcast', 'risk': 'High'},
            'addthis.com': {'type': 'Data Broker', 'company': 'Oracle', 'risk': 'High'},
            'outbrain.com': {'type': 'Content', 'company': 'Outbrain', 'risk': 'Medium'},
            
            # CDNs that track
            'jsdelivr.net': {'type': 'CDN/Analytics', 'company': 'JSDelivr', 'risk': 'Low'},
            'unpkg.com': {'type': 'CDN', 'company': 'Unpkg', 'risk': 'Low'},
            
            # Other trackers
            'hotjar.com': {'type': 'Heatmap', 'company': 'Hotjar', 'risk': 'Medium'},
            'crazyegg.com': {'type': 'Heatmap', 'company': 'Crazy Egg', 'risk': 'Medium'},
            'mixpanel.com': {'type': 'Analytics', 'company': 'Mixpanel', 'risk': 'Medium'},
            'segment.com': {'type': 'Analytics', 'company': 'Twilio Segment', 'risk': 'Medium'},
        }
        
        # Tracking script patterns
        self.tracking_patterns = [
            r'gtag\(',  # Google Analytics
            r'ga\(',    # Google Analytics
            r'fbq\(',   # Facebook Pixel
            r'_gaq',    # Google Analytics (old)
            r'__utm',   # UTM tracking
            r'_trackEvent',  # Event tracking
            r'mixpanel',     # Mixpanel
            r'amplitude',    # Amplitude
            r'hotjar',       # Hotjar
        ]
        
        # Cookie tracking patterns
        self.tracking_cookies = [
            '_ga', '_gid', '_gat',  # Google Analytics
            '_fbp', '_fbc',         # Facebook
            '__utma', '__utmb', '__utmc', '__utmz',  # Google Analytics (old)
            '_hjid', '_hjIncludedInSample',  # Hotjar
            'mp_', 'mixpanel',      # Mixpanel
            '_pk_id', '_pk_ses',    # Piwik/Matomo
        ]
    
    def detect_trackers_on_page(self, web_page):
        """Detect trackers on the current web page"""
        if not web_page:
            return
        
        # Get page URL
        page_url = web_page.url().toString()
        
        # Initialize tracking data
        tracking_data = {
            'url': page_url,
            'timestamp': datetime.now().isoformat(),
            'trackers': [],
            'cookies': [],
            'scripts': [],
            'pixels': [],
            'fingerprinting': [],
            'summary': {
                'total_trackers': 0,
                'risk_level': 'Low',
                'companies': set(),
                'types': set()
            }
        }
        
        # Inject JavaScript to detect trackers
        js_code = self._get_tracker_detection_js()
        
        def process_tracking_results(results):
            if results:
                self._process_tracking_data(results, tracking_data)
                self.trackers_detected.emit(tracking_data)
        
        web_page.runJavaScript(js_code, process_tracking_results)
    
    def _get_tracker_detection_js(self):
        """JavaScript code to detect various tracking methods"""
        return """
        (function() {
            var trackingData = {
                scripts: [],
                cookies: [],
                localStorage: [],
                sessionStorage: [],
                pixels: [],
                fingerprinting: [],
                networkRequests: []
            };
            
            // Detect tracking scripts
            var scripts = document.getElementsByTagName('script');
            for (var i = 0; i < scripts.length; i++) {
                var script = scripts[i];
                if (script.src) {
                    trackingData.scripts.push({
                        src: script.src,
                        type: 'external'
                    });
                } else if (script.innerHTML) {
                    // Check for tracking patterns in inline scripts
                    var content = script.innerHTML.toLowerCase();
                    if (content.includes('gtag') || content.includes('analytics') || 
                        content.includes('fbq') || content.includes('mixpanel') ||
                        content.includes('hotjar') || content.includes('_gaq')) {
                        trackingData.scripts.push({
                            content: content.substring(0, 200) + '...',
                            type: 'inline_tracking'
                        });
                    }
                }
            }
            
            // Detect cookies
            if (document.cookie) {
                var cookies = document.cookie.split(';');
                for (var j = 0; j < cookies.length; j++) {
                    var cookie = cookies[j].trim();
                    if (cookie) {
                        var parts = cookie.split('=');
                        trackingData.cookies.push({
                            name: parts[0],
                            value: parts[1] ? parts[1].substring(0, 50) + '...' : '',
                            domain: document.domain
                        });
                    }
                }
            }
            
            // Detect localStorage tracking
            try {
                for (var key in localStorage) {
                    if (localStorage.hasOwnProperty(key)) {
                        trackingData.localStorage.push({
                            key: key,
                            value: localStorage[key].substring(0, 100) + '...'
                        });
                    }
                }
            } catch (e) {
                // localStorage not accessible
            }
            
            // Detect sessionStorage tracking
            try {
                for (var sKey in sessionStorage) {
                    if (sessionStorage.hasOwnProperty(sKey)) {
                        trackingData.sessionStorage.push({
                            key: sKey,
                            value: sessionStorage[sKey].substring(0, 100) + '...'
                        });
                    }
                }
            } catch (e) {
                // sessionStorage not accessible
            }
            
            // Detect tracking pixels (1x1 images)
            var images = document.getElementsByTagName('img');
            for (var k = 0; k < images.length; k++) {
                var img = images[k];
                if ((img.width === 1 && img.height === 1) || 
                    (img.naturalWidth === 1 && img.naturalHeight === 1)) {
                    trackingData.pixels.push({
                        src: img.src,
                        width: img.width,
                        height: img.height
                    });
                }
            }
            
            // Detect fingerprinting attempts
            var fingerprintingMethods = [];
            
            // Canvas fingerprinting
            if (typeof CanvasRenderingContext2D !== 'undefined') {
                fingerprintingMethods.push('Canvas API');
            }
            
            // WebGL fingerprinting
            if (typeof WebGLRenderingContext !== 'undefined') {
                fingerprintingMethods.push('WebGL');
            }
            
            // Audio fingerprinting
            if (typeof AudioContext !== 'undefined' || typeof webkitAudioContext !== 'undefined') {
                fingerprintingMethods.push('Audio API');
            }
            
            // Font detection
            if (document.fonts && document.fonts.check) {
                fingerprintingMethods.push('Font Detection');
            }
            
            // Screen/device info
            if (screen.width && screen.height) {
                fingerprintingMethods.push('Screen Info');
            }
            
            trackingData.fingerprinting = fingerprintingMethods;
            
            // Detect global tracking objects
            var globalTrackers = [];
            if (typeof gtag !== 'undefined') globalTrackers.push('Google Analytics (gtag)');
            if (typeof ga !== 'undefined') globalTrackers.push('Google Analytics (ga)');
            if (typeof _gaq !== 'undefined') globalTrackers.push('Google Analytics (legacy)');
            if (typeof fbq !== 'undefined') globalTrackers.push('Facebook Pixel');
            if (typeof mixpanel !== 'undefined') globalTrackers.push('Mixpanel');
            if (typeof amplitude !== 'undefined') globalTrackers.push('Amplitude');
            if (typeof hj !== 'undefined') globalTrackers.push('Hotjar');
            
            trackingData.globalTrackers = globalTrackers;
            
            return trackingData;
        })();
        """
    
    def _process_tracking_data(self, js_results, tracking_data):
        """Process the JavaScript results and categorize trackers"""
        
        # Process scripts
        for script in js_results.get('scripts', []):
            tracker_info = self._analyze_script(script)
            if tracker_info:
                tracking_data['trackers'].append(tracker_info)
        
        # Process cookies
        for cookie in js_results.get('cookies', []):
            tracker_info = self._analyze_cookie(cookie)
            if tracker_info:
                tracking_data['cookies'].append(tracker_info)
        
        # Process pixels
        for pixel in js_results.get('pixels', []):
            tracker_info = self._analyze_pixel(pixel)
            if tracker_info:
                tracking_data['pixels'].append(tracker_info)
        
        # Process fingerprinting
        if js_results.get('fingerprinting'):
            tracking_data['fingerprinting'] = js_results['fingerprinting']
        
        # Process global trackers
        if js_results.get('globalTrackers'):
            for tracker in js_results['globalTrackers']:
                tracking_data['trackers'].append({
                    'name': tracker,
                    'type': 'JavaScript API',
                    'company': self._get_company_from_tracker(tracker),
                    'risk': 'Medium',
                    'method': 'Global Object'
                })
        
        # Calculate summary
        self._calculate_summary(tracking_data)
    
    def _analyze_script(self, script):
        """Analyze a script for tracking behavior"""
        src = script.get('src', '')
        
        # Check against known tracking domains
        for domain, info in self.tracking_domains.items():
            if domain in src:
                return {
                    'name': domain,
                    'type': info['type'],
                    'company': info['company'],
                    'risk': info['risk'],
                    'method': 'External Script',
                    'url': src
                }
        
        # Check inline scripts for tracking patterns
        if script.get('type') == 'inline_tracking':
            return {
                'name': 'Inline Tracking Script',
                'type': 'Analytics',
                'company': 'Unknown',
                'risk': 'Medium',
                'method': 'Inline Script',
                'content': script.get('content', '')
            }
        
        return None
    
    def _analyze_cookie(self, cookie):
        """Analyze a cookie for tracking behavior"""
        name = cookie.get('name', '')
        
        # Check against known tracking cookies
        for pattern in self.tracking_cookies:
            if pattern in name:
                return {
                    'name': name,
                    'type': 'Cookie Tracking',
                    'company': self._get_company_from_cookie(name),
                    'risk': 'Medium',
                    'method': 'HTTP Cookie',
                    'domain': cookie.get('domain', ''),
                    'value': cookie.get('value', '')
                }
        
        return None
    
    def _analyze_pixel(self, pixel):
        """Analyze a tracking pixel"""
        src = pixel.get('src', '')
        
        # Check against known tracking domains
        for domain, info in self.tracking_domains.items():
            if domain in src:
                return {
                    'name': f"Tracking Pixel ({domain})",
                    'type': 'Tracking Pixel',
                    'company': info['company'],
                    'risk': info['risk'],
                    'method': '1x1 Image',
                    'url': src
                }
        
        # Generic tracking pixel
        if src:
            return {
                'name': 'Unknown Tracking Pixel',
                'type': 'Tracking Pixel',
                'company': 'Unknown',
                'risk': 'Medium',
                'method': '1x1 Image',
                'url': src
            }
        
        return None
    
    def _get_company_from_tracker(self, tracker_name):
        """Get company name from tracker"""
        tracker_lower = tracker_name.lower()
        if 'google' in tracker_lower or 'gtag' in tracker_lower or 'ga' in tracker_lower:
            return 'Google'
        elif 'facebook' in tracker_lower or 'fbq' in tracker_lower:
            return 'Facebook/Meta'
        elif 'mixpanel' in tracker_lower:
            return 'Mixpanel'
        elif 'amplitude' in tracker_lower:
            return 'Amplitude'
        elif 'hotjar' in tracker_lower:
            return 'Hotjar'
        else:
            return 'Unknown'
    
    def _get_company_from_cookie(self, cookie_name):
        """Get company name from cookie"""
        if cookie_name.startswith('_ga') or cookie_name.startswith('_gid') or cookie_name.startswith('__utm'):
            return 'Google'
        elif cookie_name.startswith('_fb'):
            return 'Facebook/Meta'
        elif cookie_name.startswith('_hj'):
            return 'Hotjar'
        elif 'mixpanel' in cookie_name or cookie_name.startswith('mp_'):
            return 'Mixpanel'
        else:
            return 'Unknown'
    
    def _calculate_summary(self, tracking_data):
        """Calculate summary statistics"""
        all_trackers = (tracking_data['trackers'] + tracking_data['cookies'] + 
                       tracking_data['pixels'])
        
        tracking_data['summary']['total_trackers'] = len(all_trackers)
        
        # Collect companies and types
        companies = set()
        types = set()
        risk_levels = []
        
        for tracker in all_trackers:
            if tracker.get('company'):
                companies.add(tracker['company'])
            if tracker.get('type'):
                types.add(tracker['type'])
            if tracker.get('risk'):
                risk_levels.append(tracker['risk'])
        
        tracking_data['summary']['companies'] = list(companies)
        tracking_data['summary']['types'] = list(types)
        
        # Calculate overall risk level
        if 'High' in risk_levels:
            tracking_data['summary']['risk_level'] = 'High'
        elif 'Medium' in risk_levels:
            tracking_data['summary']['risk_level'] = 'Medium'
        else:
            tracking_data['summary']['risk_level'] = 'Low'
        
        # Add fingerprinting to summary
        if tracking_data['fingerprinting']:
            tracking_data['summary']['fingerprinting_methods'] = len(tracking_data['fingerprinting'])
        else:
            tracking_data['summary']['fingerprinting_methods'] = 0


class TrackerDetectionDialog(QDialog):
    """Dialog to display tracker detection results"""
    
    def __init__(self, tracking_data, parent=None):
        super().__init__(parent)
        self.tracking_data = tracking_data
        self.setup_ui()
        self.populate_data()
    
    def setup_ui(self):
        """Setup the dialog UI"""
        self.setWindowTitle("🔍 Web Tracker Detection Results")
        self.setMinimumSize(800, 600)
        self.resize(1000, 700)
        
        layout = QVBoxLayout(self)
        
        # Header
        header_layout = QHBoxLayout()
        
        icon_label = QLabel("🔍")
        icon_label.setStyleSheet("font-size: 24px;")
        header_layout.addWidget(icon_label)
        
        title_label = QLabel("Web Tracker Detection Results")
        title_label.setStyleSheet("font-size: 18px; font-weight: bold; color: #2c3e50;")
        header_layout.addWidget(title_label)
        
        header_layout.addStretch()
        
        # Risk level indicator
        self.risk_label = QLabel()
        self.risk_label.setStyleSheet("padding: 5px 10px; border-radius: 3px; font-weight: bold;")
        header_layout.addWidget(self.risk_label)
        
        layout.addLayout(header_layout)
        
        # Summary section
        summary_group = QGroupBox("📊 Summary")
        summary_layout = QGridLayout(summary_group)
        
        self.total_trackers_label = QLabel()
        self.companies_label = QLabel()
        self.types_label = QLabel()
        self.fingerprinting_label = QLabel()
        
        summary_layout.addWidget(QLabel("Total Trackers:"), 0, 0)
        summary_layout.addWidget(self.total_trackers_label, 0, 1)
        summary_layout.addWidget(QLabel("Companies:"), 1, 0)
        summary_layout.addWidget(self.companies_label, 1, 1)
        summary_layout.addWidget(QLabel("Tracking Types:"), 2, 0)
        summary_layout.addWidget(self.types_label, 2, 1)
        summary_layout.addWidget(QLabel("Fingerprinting:"), 3, 0)
        summary_layout.addWidget(self.fingerprinting_label, 3, 1)
        
        layout.addWidget(summary_group)
        
        # Tabs for different tracker types
        self.tab_widget = QTabWidget()
        
        # Trackers tab
        self.trackers_tab = self.create_trackers_tab()
        self.tab_widget.addTab(self.trackers_tab, "🎯 Trackers")
        
        # Cookies tab
        self.cookies_tab = self.create_cookies_tab()
        self.tab_widget.addTab(self.cookies_tab, "🍪 Cookies")
        
        # Pixels tab
        self.pixels_tab = self.create_pixels_tab()
        self.tab_widget.addTab(self.pixels_tab, "📷 Pixels")
        
        # Fingerprinting tab
        self.fingerprinting_tab = self.create_fingerprinting_tab()
        self.tab_widget.addTab(self.fingerprinting_tab, "👆 Fingerprinting")
        
        layout.addWidget(self.tab_widget)
        
        # Buttons
        button_layout = QHBoxLayout()
        
        export_btn = QPushButton("📄 Export Report")
        export_btn.clicked.connect(self.export_report)
        button_layout.addWidget(export_btn)
        
        block_btn = QPushButton("🚫 Block Trackers")
        block_btn.clicked.connect(self.block_trackers)
        button_layout.addWidget(block_btn)
        
        button_layout.addStretch()
        
        close_btn = QPushButton("✖️ Close")
        close_btn.clicked.connect(self.accept)
        button_layout.addWidget(close_btn)
        
        layout.addLayout(button_layout)
    
    def create_trackers_tab(self):
        """Create the trackers tab"""
        widget = QWidget()
        layout = QVBoxLayout(widget)
        
        self.trackers_tree = QTreeWidget()
        self.trackers_tree.setHeaderLabels(["Tracker", "Company", "Type", "Risk", "Method"])
        self.trackers_tree.setAlternatingRowColors(True)
        
        layout.addWidget(self.trackers_tree)
        return widget
    
    def create_cookies_tab(self):
        """Create the cookies tab"""
        widget = QWidget()
        layout = QVBoxLayout(widget)
        
        self.cookies_tree = QTreeWidget()
        self.cookies_tree.setHeaderLabels(["Cookie Name", "Company", "Domain", "Value"])
        self.cookies_tree.setAlternatingRowColors(True)
        
        layout.addWidget(self.cookies_tree)
        return widget
    
    def create_pixels_tab(self):
        """Create the pixels tab"""
        widget = QWidget()
        layout = QVBoxLayout(widget)
        
        self.pixels_tree = QTreeWidget()
        self.pixels_tree.setHeaderLabels(["Pixel", "Company", "URL", "Risk"])
        self.pixels_tree.setAlternatingRowColors(True)
        
        layout.addWidget(self.pixels_tree)
        return widget
    
    def create_fingerprinting_tab(self):
        """Create the fingerprinting tab"""
        widget = QWidget()
        layout = QVBoxLayout(widget)
        
        info_label = QLabel("Fingerprinting methods detected on this page:")
        info_label.setStyleSheet("font-weight: bold; margin-bottom: 10px;")
        layout.addWidget(info_label)
        
        self.fingerprinting_list = QListWidget()
        layout.addWidget(self.fingerprinting_list)
        
        return widget
    
    def populate_data(self):
        """Populate the dialog with tracking data"""
        summary = self.tracking_data.get('summary', {})
        
        # Update summary
        self.total_trackers_label.setText(str(summary.get('total_trackers', 0)))
        self.companies_label.setText(', '.join(summary.get('companies', [])))
        self.types_label.setText(', '.join(summary.get('types', [])))
        self.fingerprinting_label.setText(f"{summary.get('fingerprinting_methods', 0)} methods detected")
        
        # Update risk level
        risk_level = summary.get('risk_level', 'Low')
        if risk_level == 'High':
            self.risk_label.setText("🔴 High Risk")
            self.risk_label.setStyleSheet("background-color: #e74c3c; color: white; padding: 5px 10px; border-radius: 3px; font-weight: bold;")
        elif risk_level == 'Medium':
            self.risk_label.setText("🟡 Medium Risk")
            self.risk_label.setStyleSheet("background-color: #f39c12; color: white; padding: 5px 10px; border-radius: 3px; font-weight: bold;")
        else:
            self.risk_label.setText("🟢 Low Risk")
            self.risk_label.setStyleSheet("background-color: #27ae60; color: white; padding: 5px 10px; border-radius: 3px; font-weight: bold;")
        
        # Populate trackers
        for tracker in self.tracking_data.get('trackers', []):
            item = QTreeWidgetItem([
                tracker.get('name', ''),
                tracker.get('company', ''),
                tracker.get('type', ''),
                tracker.get('risk', ''),
                tracker.get('method', '')
            ])
            
            # Color code by risk level
            if tracker.get('risk') == 'High':
                item.setBackground(0, QColor(231, 76, 60, 50))
            elif tracker.get('risk') == 'Medium':
                item.setBackground(0, QColor(243, 156, 18, 50))
            
            self.trackers_tree.addTopLevelItem(item)
        
        # Populate cookies
        for cookie in self.tracking_data.get('cookies', []):
            item = QTreeWidgetItem([
                cookie.get('name', ''),
                cookie.get('company', ''),
                cookie.get('domain', ''),
                cookie.get('value', '')[:50] + '...' if len(cookie.get('value', '')) > 50 else cookie.get('value', '')
            ])
            self.cookies_tree.addTopLevelItem(item)
        
        # Populate pixels
        for pixel in self.tracking_data.get('pixels', []):
            item = QTreeWidgetItem([
                pixel.get('name', ''),
                pixel.get('company', ''),
                pixel.get('url', ''),
                pixel.get('risk', '')
            ])
            
            if pixel.get('risk') == 'High':
                item.setBackground(0, QColor(231, 76, 60, 50))
            elif pixel.get('risk') == 'Medium':
                item.setBackground(0, QColor(243, 156, 18, 50))
            
            self.pixels_tree.addTopLevelItem(item)
        
        # Populate fingerprinting
        for method in self.tracking_data.get('fingerprinting', []):
            self.fingerprinting_list.addItem(f"🔍 {method}")
        
        # Resize columns
        for tree in [self.trackers_tree, self.cookies_tree, self.pixels_tree]:
            for i in range(tree.columnCount()):
                tree.resizeColumnToContents(i)
    
    def export_report(self):
        """Export tracking report to file"""
        filename, _ = QFileDialog.getSaveFileName(
            self, 
            "Export Tracker Report", 
            f"tracker_report_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json",
            "JSON Files (*.json);;Text Files (*.txt)"
        )
        
        if filename:
            try:
                with open(filename, 'w') as f:
                    json.dump(self.tracking_data, f, indent=2, default=str)
                
                QMessageBox.information(self, "Export Successful", f"Report exported to:\n{filename}")
            except Exception as e:
                QMessageBox.warning(self, "Export Failed", f"Failed to export report:\n{str(e)}")
    
    def block_trackers(self):
        """Show options to block detected trackers"""
        QMessageBox.information(
            self, 
            "Block Trackers", 
            "Tracker blocking functionality would be integrated with the browser's ad blocker.\n\n"
            "This would add the detected tracking domains to the block list."
        )


def show_tracker_detection_dialog(tracking_data, parent=None):
    """Show the tracker detection dialog"""
    dialog = TrackerDetectionDialog(tracking_data, parent)
    return dialog


if __name__ == "__main__":
    import sys
    from PyQt5.QtWidgets import QApplication
    
    app = QApplication(sys.argv)
    
    # Sample tracking data for testing
    sample_data = {
        'url': 'https://example.com',
        'timestamp': datetime.now().isoformat(),
        'trackers': [
            {
                'name': 'google-analytics.com',
                'type': 'Analytics',
                'company': 'Google',
                'risk': 'Medium',
                'method': 'External Script'
            }
        ],
        'cookies': [
            {
                'name': '_ga',
                'company': 'Google',
                'domain': 'example.com',
                'value': 'GA1.2.123456789.1234567890'
            }
        ],
        'pixels': [],
        'fingerprinting': ['Canvas API', 'WebGL', 'Screen Info'],
        'summary': {
            'total_trackers': 2,
            'risk_level': 'Medium',
            'companies': ['Google'],
            'types': ['Analytics'],
            'fingerprinting_methods': 3
        }
    }
    
    dialog = show_tracker_detection_dialog(sample_data)
    dialog.show()
    
    sys.exit(app.exec_())