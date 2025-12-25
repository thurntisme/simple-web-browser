"""
Curl tool for making HTTP requests and testing APIs.
Provides curl-like functionality with results display.
"""

import subprocess
import platform
import json
import threading
import time
import os
import re
import shlex
from datetime import datetime
from PyQt5.QtCore import QObject, pyqtSignal, QTimer, Qt
from PyQt5.QtWidgets import *
from PyQt5.QtGui import *


class CurlWorker(QObject):
    """Worker thread for curl operations"""
    
    curl_result = pyqtSignal(str, bool, dict)  # result, success, metadata
    curl_progress = pyqtSignal(str)  # progress update
    curl_finished = pyqtSignal()
    
    def __init__(self, url, method="GET", headers=None, data=None, timeout=30):
        super().__init__()
        self.url = url
        self.method = method.upper()
        self.headers = headers or {}
        self.data = data
        self.timeout = timeout
        self.is_running = False
    
    def start_curl(self):
        """Start curl operation"""
        self.is_running = True
        threading.Thread(target=self._execute_curl, daemon=True).start()
    
    def stop_curl(self):
        """Stop curl operation"""
        self.is_running = False
    
    def _execute_curl(self):
        """Execute curl command"""
        try:
            # Build curl command
            cmd = ["curl", "-i", "-s", "-S"]  # Include headers, silent, show errors
            
            # Add timeout
            cmd.extend(["--max-time", str(self.timeout)])
            
            # Add method
            if self.method != "GET":
                cmd.extend(["-X", self.method])
            
            # Add headers
            for key, value in self.headers.items():
                cmd.extend(["-H", f"{key}: {value}"])
            
            # Add data for POST/PUT requests
            if self.data and self.method in ["POST", "PUT", "PATCH"]:
                cmd.extend(["-d", self.data])
            
            # Add URL
            cmd.append(self.url)
            
            self.curl_progress.emit(f"Executing: {' '.join(cmd[:5])}... {self.url}")
            
            start_time = time.time()
            
            # Execute curl command
            process = subprocess.Popen(
                cmd,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                text=True,
                encoding='utf-8',
                errors='replace',
                creationflags=subprocess.CREATE_NO_WINDOW if platform.system().lower() == "windows" else 0
            )
            
            output, error = process.communicate()
            end_time = time.time()
            
            if not self.is_running:
                return
            
            # Parse response
            metadata = {
                'duration': round((end_time - start_time) * 1000, 2),  # ms
                'command': ' '.join(cmd),
                'return_code': process.returncode
            }
            
            if process.returncode == 0:
                parsed_result = self._parse_curl_output(output, metadata)
                self.curl_result.emit(parsed_result, True, metadata)
            else:
                error_msg = f"Curl failed (exit code {process.returncode}):\n{error.strip() if error else 'Unknown error'}"
                self.curl_result.emit(error_msg, False, metadata)
                
        except FileNotFoundError:
            if self.is_running:
                self.curl_result.emit("Error: curl command not found. Please install curl.", False, {})
        except Exception as e:
            if self.is_running:
                self.curl_result.emit(f"Error: {str(e)}", False, {})
        finally:
            if self.is_running:
                self.curl_finished.emit()
    
    def _parse_curl_output(self, output, metadata):
        """Parse curl command output"""
        lines = output.split('\n')
        result = []
        
        # Add header with request info
        result.append(f"🌐 HTTP Request to {self.url}")
        result.append(f"Method: {self.method} | Duration: {metadata['duration']}ms")
        result.append("=" * 60)
        result.append("")
        
        # Find the split between headers and body
        header_end = -1
        for i, line in enumerate(lines):
            if line.strip() == "" and i > 0:
                header_end = i
                break
        
        if header_end == -1:
            # No clear split, treat all as headers
            header_end = len(lines)
        
        # Parse headers
        headers = lines[:header_end]
        body = lines[header_end + 1:] if header_end < len(lines) else []
        
        # Add response headers
        if headers:
            result.append("📋 Response Headers:")
            result.append("-" * 30)
            for header in headers:
                if header.strip():
                    if header.startswith("HTTP/"):
                        result.append(f"🔗 {header}")
                    else:
                        result.append(f"   {header}")
            result.append("")
        
        # Add response body
        if body and any(line.strip() for line in body):
            result.append("📄 Response Body:")
            result.append("-" * 30)
            
            body_content = '\n'.join(body).strip()
            
            # Try to format JSON
            try:
                if body_content.startswith('{') or body_content.startswith('['):
                    json_obj = json.loads(body_content)
                    formatted_json = json.dumps(json_obj, indent=2, ensure_ascii=False)
                    result.append(formatted_json)
                else:
                    result.append(body_content)
            except json.JSONDecodeError:
                result.append(body_content)
        else:
            result.append("📄 Response Body: (empty)")
        
        return '\n'.join(result)


class CurlDialog(QDialog):
    """Dialog for curl tool interface"""
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.curl_worker = None
        self.setup_ui()
    
    def setup_ui(self):
        """Setup the curl dialog UI"""
        self.setWindowTitle("🌐 Curl Tool")
        self.setModal(False)
        self.resize(800, 600)
        
        layout = QVBoxLayout(self)
        
        # Curl command import section
        import_group = QGroupBox("Import Curl Command")
        import_layout = QVBoxLayout(import_group)
        
        # Curl command input
        curl_input_layout = QHBoxLayout()
        self.curl_command_input = QTextEdit()
        self.curl_command_input.setMaximumHeight(80)
        self.curl_command_input.setPlaceholderText("Paste your curl command here:\ncurl --location 'https://api.example.com/endpoint' \\\n--header 'Authorization: Bearer token' \\\n--data '{\"key\": \"value\"}'")
        curl_input_layout.addWidget(self.curl_command_input)
        
        # Import buttons
        import_buttons_layout = QVBoxLayout()
        
        import_btn = QPushButton("📥 Import")
        import_btn.clicked.connect(self.import_curl_command)
        import_btn.setMaximumWidth(80)
        import_btn.setToolTip("Parse and import curl command (Ctrl+I)")
        import_buttons_layout.addWidget(import_btn)
        
        clear_import_btn = QPushButton("🗑️ Clear")
        clear_import_btn.clicked.connect(self.curl_command_input.clear)
        clear_import_btn.setMaximumWidth(80)
        clear_import_btn.setToolTip("Clear import field")
        import_buttons_layout.addWidget(clear_import_btn)
        
        curl_input_layout.addLayout(import_buttons_layout)
        
        import_layout.addLayout(curl_input_layout)
        layout.addWidget(import_group)
        
        # Request configuration
        config_group = QGroupBox("Request Configuration")
        config_layout = QGridLayout(config_group)
        
        # URL input
        config_layout.addWidget(QLabel("URL:"), 0, 0)
        self.url_input = QLineEdit()
        self.url_input.setPlaceholderText("https://api.example.com/endpoint")
        self.url_input.returnPressed.connect(self.execute_curl)
        config_layout.addWidget(self.url_input, 0, 1, 1, 2)
        
        # Method selection
        config_layout.addWidget(QLabel("Method:"), 1, 0)
        self.method_combo = QComboBox()
        self.method_combo.addItems(["GET", "POST", "PUT", "DELETE", "PATCH", "HEAD", "OPTIONS"])
        self.method_combo.setCurrentText("GET")
        config_layout.addWidget(self.method_combo, 1, 1)
        
        # Timeout
        config_layout.addWidget(QLabel("Timeout (s):"), 1, 2)
        self.timeout_spin = QSpinBox()
        self.timeout_spin.setRange(1, 300)
        self.timeout_spin.setValue(30)
        config_layout.addWidget(self.timeout_spin, 1, 3)
        
        layout.addWidget(config_group)
        
        # Headers section
        headers_group = QGroupBox("Headers")
        headers_layout = QVBoxLayout(headers_group)
        
        self.headers_text = QTextEdit()
        self.headers_text.setMaximumHeight(100)
        self.headers_text.setPlaceholderText("Content-Type: application/json\nAuthorization: Bearer token\nUser-Agent: MyApp/1.0")
        headers_layout.addWidget(self.headers_text)
        
        layout.addWidget(headers_group)
        
        # Data section
        data_group = QGroupBox("Request Body (for POST/PUT/PATCH)")
        data_layout = QVBoxLayout(data_group)
        
        self.data_text = QTextEdit()
        self.data_text.setMaximumHeight(100)
        self.data_text.setPlaceholderText('{"key": "value", "number": 123}')
        data_layout.addWidget(self.data_text)
        
        layout.addWidget(data_group)
        
        # Control buttons
        button_layout = QHBoxLayout()
        
        self.execute_btn = QPushButton("🌐 Execute Request")
        self.execute_btn.clicked.connect(self.execute_curl)
        self.execute_btn.setDefault(True)
        button_layout.addWidget(self.execute_btn)
        
        self.stop_btn = QPushButton("⏹️ Stop")
        self.stop_btn.clicked.connect(self.stop_curl)
        self.stop_btn.setEnabled(False)
        button_layout.addWidget(self.stop_btn)
        
        self.clear_btn = QPushButton("🗑️ Clear")
        self.clear_btn.clicked.connect(self.clear_results)
        button_layout.addWidget(self.clear_btn)
        
        self.copy_btn = QPushButton("📋 Copy Result")
        self.copy_btn.clicked.connect(self.copy_results)
        self.copy_btn.setToolTip("Copy full result to clipboard (Ctrl+C)")
        button_layout.addWidget(self.copy_btn)
        
        button_layout.addStretch()
        
        # Quick presets
        presets_layout = QHBoxLayout()
        presets_layout.addWidget(QLabel("Quick presets:"))
        
        presets = [
            ("JSON API", "application/json"),
            ("Form Data", "application/x-www-form-urlencoded"),
            ("Plain Text", "text/plain"),
            ("XML", "application/xml")
        ]
        
        for name, content_type in presets:
            btn = QPushButton(name)
            btn.clicked.connect(lambda checked, ct=content_type: self.set_content_type(ct))
            btn.setMaximumWidth(80)
            presets_layout.addWidget(btn)
        
        button_layout.addLayout(presets_layout)
        layout.addLayout(button_layout)
        
        # Results area
        results_group = QGroupBox("Response")
        results_layout = QVBoxLayout(results_group)
        
        self.results_text = QTextEdit()
        self.results_text.setReadOnly(True)
        self.results_text.setFont(QFont("Consolas", 9))
        self.results_text.setStyleSheet("""
            QTextEdit {
                background-color: #1e1e1e;
                color: #d4d4d4;
                border: 1px solid #3e3e3e;
                padding: 8px;
            }
        """)
        results_layout.addWidget(self.results_text)
        
        layout.addWidget(results_group)
        
        # Status bar
        self.status_label = QLabel("Ready to execute HTTP request")
        self.status_label.setStyleSheet("QLabel { color: #666; padding: 4px; }")
        layout.addWidget(self.status_label)
        
        # Setup shortcuts
        self.setup_shortcuts()
        
        # Set focus to URL input
        self.url_input.setFocus()
    
    def setup_shortcuts(self):
        """Setup keyboard shortcuts"""
        # Execute shortcut (Ctrl+Return)
        execute_shortcut = QShortcut(QKeySequence("Ctrl+Return"), self)
        execute_shortcut.activated.connect(self.execute_curl)
        
        # Copy shortcut (Ctrl+C)
        copy_shortcut = QShortcut(QKeySequence("Ctrl+C"), self)
        copy_shortcut.activated.connect(self.copy_results)
        
        # Clear shortcut (Ctrl+L)
        clear_shortcut = QShortcut(QKeySequence("Ctrl+L"), self)
        clear_shortcut.activated.connect(self.clear_results)
        
        # Import shortcut (Ctrl+I)
        import_shortcut = QShortcut(QKeySequence("Ctrl+I"), self)
        import_shortcut.activated.connect(self.import_curl_command)
    
    def import_curl_command(self):
        """Parse and import curl command"""
        curl_command = self.curl_command_input.toPlainText().strip()
        if not curl_command:
            QMessageBox.warning(self, "No Command", "Please paste a curl command to import.")
            return
        
        try:
            # Parse the curl command
            parsed = self.parse_curl_command(curl_command)
            
            # Update UI with parsed values
            if parsed.get('url'):
                self.url_input.setText(parsed['url'])
            
            if parsed.get('method'):
                index = self.method_combo.findText(parsed['method'].upper())
                if index >= 0:
                    self.method_combo.setCurrentIndex(index)
            
            if parsed.get('headers'):
                headers_text = '\n'.join([f"{k}: {v}" for k, v in parsed['headers'].items()])
                self.headers_text.setPlainText(headers_text)
            
            if parsed.get('data'):
                self.data_text.setPlainText(parsed['data'])
            
            # Clear the import field
            self.curl_command_input.clear()
            
            # Show success message
            self.status_label.setText("✅ Curl command imported successfully")
            QTimer.singleShot(3000, lambda: self.status_label.setText("Ready to execute HTTP request"))
            
        except Exception as e:
            QMessageBox.warning(self, "Parse Error", f"Failed to parse curl command:\n{str(e)}")
            self.status_label.setText("❌ Failed to parse curl command")
    
    def parse_curl_command(self, curl_command):
        """Parse curl command string into components"""
        import re
        import shlex
        
        # Clean up the command - remove line breaks and extra spaces
        curl_command = re.sub(r'\\\s*\n\s*', ' ', curl_command)
        curl_command = re.sub(r'\s+', ' ', curl_command).strip()
        
        # Remove 'curl' from the beginning if present
        if curl_command.startswith('curl '):
            curl_command = curl_command[5:]
        
        # Initialize result
        result = {
            'url': '',
            'method': 'GET',
            'headers': {},
            'data': None
        }
        
        # Try to parse using shlex for proper quote handling
        try:
            parts = shlex.split(curl_command)
        except ValueError:
            # Fallback to simple split if shlex fails
            parts = curl_command.split()
        
        i = 0
        while i < len(parts):
            part = parts[i]
            
            # URL (usually the last argument or after specific flags)
            if part.startswith('http://') or part.startswith('https://'):
                result['url'] = part.strip("'\"")
            
            # Method
            elif part in ['-X', '--request']:
                if i + 1 < len(parts):
                    result['method'] = parts[i + 1].upper()
                    i += 1
            
            # Headers
            elif part in ['-H', '--header']:
                if i + 1 < len(parts):
                    header = parts[i + 1].strip("'\"")
                    if ':' in header:
                        key, value = header.split(':', 1)
                        result['headers'][key.strip()] = value.strip()
                    i += 1
            
            # Data
            elif part in ['-d', '--data', '--data-raw']:
                if i + 1 < len(parts):
                    result['data'] = parts[i + 1].strip("'\"")
                    i += 1
            
            # JSON data
            elif part in ['--json']:
                if i + 1 < len(parts):
                    result['data'] = parts[i + 1].strip("'\"")
                    result['headers']['Content-Type'] = 'application/json'
                    i += 1
            
            # Form data
            elif part in ['-F', '--form']:
                if i + 1 < len(parts):
                    # For form data, we'll just put it in the data field
                    # User can adjust Content-Type manually if needed
                    result['data'] = parts[i + 1].strip("'\"")
                    result['headers']['Content-Type'] = 'multipart/form-data'
                    i += 1
            
            i += 1
        
        # If no explicit method but has data, assume POST
        if result['data'] and result['method'] == 'GET':
            result['method'] = 'POST'
        
        return result
    
    def set_content_type(self, content_type):
        """Set Content-Type header"""
        current_headers = self.headers_text.toPlainText()
        
        # Remove existing Content-Type if present
        lines = current_headers.split('\n')
        filtered_lines = [line for line in lines if not line.strip().lower().startswith('content-type:')]
        
        # Add new Content-Type
        filtered_lines.append(f"Content-Type: {content_type}")
        
        self.headers_text.setPlainText('\n'.join(filtered_lines).strip())
    
    def execute_curl(self):
        """Execute curl request"""
        url = self.url_input.text().strip()
        if not url:
            QMessageBox.warning(self, "Invalid URL", "Please enter a URL.")
            return
        
        # Parse headers
        headers = {}
        headers_text = self.headers_text.toPlainText().strip()
        if headers_text:
            for line in headers_text.split('\n'):
                if ':' in line:
                    key, value = line.split(':', 1)
                    headers[key.strip()] = value.strip()
        
        # Get data
        data = self.data_text.toPlainText().strip() if self.data_text.toPlainText().strip() else None
        
        # Get other parameters
        method = self.method_combo.currentText()
        timeout = self.timeout_spin.value()
        
        # Create and setup worker
        self.curl_worker = CurlWorker(url, method, headers, data, timeout)
        self.curl_worker.curl_result.connect(self.on_curl_result)
        self.curl_worker.curl_progress.connect(self.on_curl_progress)
        self.curl_worker.curl_finished.connect(self.on_curl_finished)
        
        # Update UI
        self.execute_btn.setEnabled(False)
        self.stop_btn.setEnabled(True)
        self.url_input.setEnabled(False)
        self.method_combo.setEnabled(False)
        
        # Add timestamp to results
        timestamp = time.strftime("%Y-%m-%d %H:%M:%S")
        self.results_text.append(f"\n[{timestamp}] Executing {method} request to {url}...")
        
        # Start curl
        self.curl_worker.start_curl()
    
    def stop_curl(self):
        """Stop curl operation"""
        if self.curl_worker:
            self.curl_worker.stop_curl()
        self.on_curl_finished()
    
    def on_curl_result(self, result, success, metadata):
        """Handle curl result"""
        self.results_text.append(result)
        
        if success:
            duration = metadata.get('duration', 0)
            self.status_label.setText(f"✅ Request completed in {duration}ms")
        else:
            self.status_label.setText("❌ Request failed")
    
    def on_curl_progress(self, message):
        """Handle curl progress update"""
        self.status_label.setText(message)
    
    def on_curl_finished(self):
        """Handle curl completion"""
        # Reset UI
        self.execute_btn.setEnabled(True)
        self.stop_btn.setEnabled(False)
        self.url_input.setEnabled(True)
        self.method_combo.setEnabled(True)
        
        if "completed" not in self.status_label.text() and "failed" not in self.status_label.text():
            self.status_label.setText("Ready to execute HTTP request")
        
        # Clean up worker
        if self.curl_worker:
            self.curl_worker = None
    
    def clear_results(self):
        """Clear curl results"""
        self.results_text.clear()
        self.status_label.setText("Results cleared - Ready to execute HTTP request")
    
    def copy_results(self):
        """Copy full curl results to clipboard"""
        if not self.results_text.toPlainText().strip():
            QMessageBox.information(self, "No Results", "No curl results to copy. Please execute a request first.")
            return
        
        try:
            # Build full result content including request details
            results_content = self.results_text.toPlainText()
            full_content = self.build_full_result_content(results_content)
            
            # Copy to clipboard
            clipboard = QApplication.clipboard()
            clipboard.setText(full_content)
            
            # Show success message
            self.status_label.setText("📋 Full results copied to clipboard")
            
            # Show notification
            QMessageBox.information(
                self, 
                "Copied to Clipboard", 
                "Full curl results (request + response) have been copied to clipboard.\n\nYou can now paste them into any text editor or document."
            )
            
            # Reset status after 3 seconds
            QTimer.singleShot(3000, lambda: self.status_label.setText("Ready to execute HTTP request"))
                
        except Exception as e:
            QMessageBox.critical(self, "Copy Error", f"Error copying results:\n{str(e)}")
            self.status_label.setText("❌ Copy failed")
    
    def build_full_result_content(self, results_content):
        """Build full result content including request details"""
        full_result = []
        
        # Add header with timestamp
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        full_result.append(f"🌐 Curl Tool - Full Request & Response")
        full_result.append(f"Generated: {timestamp}")
        full_result.append("=" * 80)
        full_result.append("")
        
        # Add request details
        full_result.append("📤 REQUEST DETAILS:")
        full_result.append("-" * 40)
        
        # URL and Method
        url = self.url_input.text().strip()
        method = self.method_combo.currentText()
        full_result.append(f"URL: {url}")
        full_result.append(f"Method: {method}")
        full_result.append(f"Timeout: {self.timeout_spin.value()}s")
        full_result.append("")
        
        # Headers
        headers_text = self.headers_text.toPlainText().strip()
        if headers_text:
            full_result.append("Headers:")
            for line in headers_text.split('\n'):
                if line.strip():
                    full_result.append(f"  {line}")
        else:
            full_result.append("Headers: (none)")
        full_result.append("")
        
        # Request body
        data_text = self.data_text.toPlainText().strip()
        if data_text:
            full_result.append("Request Body:")
            # Try to format JSON if possible
            try:
                if data_text.startswith('{') or data_text.startswith('['):
                    import json
                    json_obj = json.loads(data_text)
                    formatted_json = json.dumps(json_obj, indent=2, ensure_ascii=False)
                    for line in formatted_json.split('\n'):
                        full_result.append(f"  {line}")
                else:
                    full_result.append(f"  {data_text}")
            except json.JSONDecodeError:
                full_result.append(f"  {data_text}")
        else:
            full_result.append("Request Body: (none)")
        
        full_result.append("")
        full_result.append("=" * 80)
        full_result.append("")
        
        # Add response content
        full_result.append("📥 RESPONSE:")
        full_result.append("-" * 40)
        
        # Add the actual response content
        if results_content.strip():
            # Skip the first few lines if they contain our request info (to avoid duplication)
            response_lines = results_content.split('\n')
            start_index = 0
            
            # Find where the actual response starts (after our request header)
            for i, line in enumerate(response_lines):
                if line.startswith('🌐 HTTP Request to') or line.startswith('Method:') or line.startswith('='):
                    continue
                elif line.strip() == "":
                    continue
                else:
                    start_index = i
                    break
            
            # Add response content
            for line in response_lines[start_index:]:
                full_result.append(line)
        else:
            full_result.append("(No response data)")
        
        return '\n'.join(full_result)
    
    def closeEvent(self, event):
        """Handle dialog close"""
        if self.curl_worker:
            self.curl_worker.stop_curl()
        event.accept()