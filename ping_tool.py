"""
Ping tool for testing domain/IP connectivity.
Provides ping functionality with results display.
"""

import subprocess
import platform
import re
import threading
import time
import os
from datetime import datetime
from PyQt5.QtCore import QObject, pyqtSignal, QTimer, Qt
from PyQt5.QtWidgets import *
from PyQt5.QtGui import *


class PingWorker(QObject):
    """Worker thread for ping operations"""
    
    ping_result = pyqtSignal(str, bool)  # result, success
    ping_progress = pyqtSignal(str)  # progress update
    ping_finished = pyqtSignal()
    
    def __init__(self, target, count=4):
        super().__init__()
        self.target = target
        self.count = count
        self.is_running = False
    
    def start_ping(self):
        """Start ping operation"""
        self.is_running = True
        threading.Thread(target=self._ping_target, daemon=True).start()
    
    def stop_ping(self):
        """Stop ping operation"""
        self.is_running = False
    
    def _ping_target(self):
        """Execute ping command"""
        try:
            # Determine ping command based on OS
            system = platform.system().lower()
            if system == "windows":
                cmd = ["ping", "-n", str(self.count), self.target]
            else:
                cmd = ["ping", "-c", str(self.count), self.target]
            
            self.ping_progress.emit(f"Pinging {self.target}...")
            
            # Execute ping command
            process = subprocess.Popen(
                cmd,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                text=True,
                creationflags=subprocess.CREATE_NO_WINDOW if system == "windows" else 0
            )
            
            output, error = process.communicate()
            
            if not self.is_running:
                return
            
            if process.returncode == 0:
                # Parse ping results
                parsed_result = self._parse_ping_output(output)
                self.ping_result.emit(parsed_result, True)
            else:
                error_msg = f"Ping failed: {error.strip() if error else 'Unknown error'}"
                self.ping_result.emit(error_msg, False)
                
        except Exception as e:
            if self.is_running:
                self.ping_result.emit(f"Error: {str(e)}", False)
        finally:
            if self.is_running:
                self.ping_finished.emit()
    
    def _parse_ping_output(self, output):
        """Parse ping command output"""
        lines = output.strip().split('\n')
        result = []
        
        # Add header
        result.append(f"Ping results for {self.target}:")
        result.append("-" * 50)
        
        # Parse individual ping responses
        ping_times = []
        packets_sent = 0
        packets_received = 0
        
        for line in lines:
            line = line.strip()
            
            # Windows ping response pattern
            if "Reply from" in line:
                packets_received += 1
                time_match = re.search(r'time[<=](\d+)ms', line)
                if time_match:
                    ping_time = int(time_match.group(1))
                    ping_times.append(ping_time)
                    result.append(f"✅ {line}")
                else:
                    result.append(f"✅ {line}")
            
            # Linux/Mac ping response pattern
            elif "bytes from" in line:
                packets_received += 1
                time_match = re.search(r'time=(\d+\.?\d*).*ms', line)
                if time_match:
                    ping_time = float(time_match.group(1))
                    ping_times.append(ping_time)
                    result.append(f"✅ {line}")
                else:
                    result.append(f"✅ {line}")
            
            # Timeout or error responses
            elif "Request timed out" in line or "Destination host unreachable" in line:
                packets_sent += 1
                result.append(f"❌ {line}")
            
            # Statistics section
            elif "Packets:" in line or "packet loss" in line:
                result.append("")
                result.append("📊 Statistics:")
                result.append(line)
        
        # Calculate statistics if we have ping times
        if ping_times:
            result.append("")
            result.append("📈 Timing Statistics:")
            result.append(f"   Minimum: {min(ping_times):.1f}ms")
            result.append(f"   Maximum: {max(ping_times):.1f}ms")
            result.append(f"   Average: {sum(ping_times)/len(ping_times):.1f}ms")
            
            # Determine connection quality
            avg_time = sum(ping_times) / len(ping_times)
            if avg_time < 50:
                quality = "Excellent 🟢"
            elif avg_time < 100:
                quality = "Good 🟡"
            elif avg_time < 200:
                quality = "Fair 🟠"
            else:
                quality = "Poor 🔴"
            
            result.append(f"   Quality: {quality}")
        
        return "\n".join(result)


class PingDialog(QDialog):
    """Dialog for ping tool interface"""
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.ping_worker = None
        self.setup_ui()
    
    def setup_ui(self):
        """Setup the ping dialog UI"""
        self.setWindowTitle("🏓 Ping Tool")
        self.setModal(False)
        self.resize(600, 500)
        
        layout = QVBoxLayout(self)
        
        # Input section
        input_group = QGroupBox("Target Configuration")
        input_layout = QGridLayout(input_group)
        
        # Target input
        input_layout.addWidget(QLabel("Target (Domain/IP):"), 0, 0)
        self.target_input = QLineEdit()
        self.target_input.setPlaceholderText("e.g., google.com, 8.8.8.8")
        self.target_input.returnPressed.connect(self.start_ping)
        input_layout.addWidget(self.target_input, 0, 1)
        
        # Count input
        input_layout.addWidget(QLabel("Packet Count:"), 1, 0)
        self.count_spin = QSpinBox()
        self.count_spin.setRange(1, 100)
        self.count_spin.setValue(4)
        input_layout.addWidget(self.count_spin, 1, 1)
        
        layout.addWidget(input_group)
        
        # Control buttons
        button_layout = QHBoxLayout()
        
        self.ping_btn = QPushButton("🏓 Start Ping")
        self.ping_btn.clicked.connect(self.start_ping)
        self.ping_btn.setDefault(True)
        self.ping_btn.setToolTip("Start ping test (Ctrl+Return)")
        button_layout.addWidget(self.ping_btn)
        
        self.stop_btn = QPushButton("⏹️ Stop")
        self.stop_btn.clicked.connect(self.stop_ping)
        self.stop_btn.setEnabled(False)
        self.stop_btn.setToolTip("Stop current ping test")
        button_layout.addWidget(self.stop_btn)
        
        self.clear_btn = QPushButton("🗑️ Clear")
        self.clear_btn.clicked.connect(self.clear_results)
        self.clear_btn.setToolTip("Clear results (Ctrl+L)")
        button_layout.addWidget(self.clear_btn)
        
        self.capture_btn = QPushButton("📸 Capture")
        self.capture_btn.clicked.connect(self.capture_results)
        self.capture_btn.setStatusTip("Save ping results as image")
        self.capture_btn.setToolTip("Save results as image (Ctrl+S)")
        button_layout.addWidget(self.capture_btn)
        
        button_layout.addStretch()
        
        # Quick targets
        quick_layout = QHBoxLayout()
        quick_layout.addWidget(QLabel("Quick targets:"))
        
        quick_targets = [
            ("Google DNS", "8.8.8.8"),
            ("Cloudflare", "1.1.1.1"),
            ("Google", "google.com"),
            ("GitHub", "github.com")
        ]
        
        for name, target in quick_targets:
            btn = QPushButton(name)
            btn.clicked.connect(lambda checked, t=target: self.set_target(t))
            btn.setMaximumWidth(80)
            quick_layout.addWidget(btn)
        
        button_layout.addLayout(quick_layout)
        layout.addLayout(button_layout)
        
        # Results area
        results_group = QGroupBox("Ping Results")
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
        self.status_label = QLabel("Ready to ping")
        self.status_label.setStyleSheet("QLabel { color: #666; padding: 4px; }")
        layout.addWidget(self.status_label)
        
        # Set focus to target input
        self.target_input.setFocus()
        
        # Add keyboard shortcuts
        self.setup_shortcuts()
    
    def setup_shortcuts(self):
        """Setup keyboard shortcuts"""
        # Capture shortcut (Ctrl+S)
        capture_shortcut = QShortcut(QKeySequence("Ctrl+S"), self)
        capture_shortcut.activated.connect(self.capture_results)
        
        # Start ping shortcut (Enter/Return when not in input field)
        start_shortcut = QShortcut(QKeySequence("Ctrl+Return"), self)
        start_shortcut.activated.connect(self.start_ping)
        
        # Clear shortcut (Ctrl+L)
        clear_shortcut = QShortcut(QKeySequence("Ctrl+L"), self)
        clear_shortcut.activated.connect(self.clear_results)
    
    def set_target(self, target):
        """Set target in input field and focus"""
        self.target_input.setText(target)
        self.target_input.setFocus()
        self.target_input.selectAll()
    
    def start_ping(self):
        """Start ping operation"""
        target = self.target_input.text().strip()
        if not target:
            QMessageBox.warning(self, "Invalid Target", "Please enter a domain or IP address.")
            return
        
        count = self.count_spin.value()
        
        # Create and setup worker
        self.ping_worker = PingWorker(target, count)
        self.ping_worker.ping_result.connect(self.on_ping_result)
        self.ping_worker.ping_progress.connect(self.on_ping_progress)
        self.ping_worker.ping_finished.connect(self.on_ping_finished)
        
        # Update UI
        self.ping_btn.setEnabled(False)
        self.stop_btn.setEnabled(True)
        self.target_input.setEnabled(False)
        self.count_spin.setEnabled(False)
        
        # Add timestamp to results
        timestamp = time.strftime("%Y-%m-%d %H:%M:%S")
        self.results_text.append(f"\n[{timestamp}] Starting ping to {target}...")
        
        # Start ping
        self.ping_worker.start_ping()
    
    def stop_ping(self):
        """Stop ping operation"""
        if self.ping_worker:
            self.ping_worker.stop_ping()
        self.on_ping_finished()
    
    def on_ping_result(self, result, success):
        """Handle ping result"""
        self.results_text.append(result)
        
        if success:
            self.status_label.setText("✅ Ping completed successfully")
        else:
            self.status_label.setText("❌ Ping failed")
    
    def on_ping_progress(self, message):
        """Handle ping progress update"""
        self.status_label.setText(message)
    
    def on_ping_finished(self):
        """Handle ping completion"""
        # Reset UI
        self.ping_btn.setEnabled(True)
        self.stop_btn.setEnabled(False)
        self.target_input.setEnabled(True)
        self.count_spin.setEnabled(True)
        
        if "completed" not in self.status_label.text() and "failed" not in self.status_label.text():
            self.status_label.setText("Ready to ping")
        
        # Clean up worker
        if self.ping_worker:
            self.ping_worker = None
    
    def clear_results(self):
        """Clear ping results"""
        self.results_text.clear()
        self.status_label.setText("Results cleared - Ready to ping")
    
    def capture_results(self):
        """Capture ping results as image"""
        if not self.results_text.toPlainText().strip():
            QMessageBox.information(self, "No Results", "No ping results to capture. Please run a ping test first.")
            return
        
        # Get save location
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        default_filename = f"ping_results_{timestamp}.png"
        
        filename, _ = QFileDialog.getSaveFileName(
            self,
            "Save Ping Results Image",
            default_filename,
            "PNG Images (*.png);;JPEG Images (*.jpg);;All Files (*.*)"
        )
        
        if not filename:
            return
        
        try:
            # Create a widget to render the results
            capture_widget = self.create_capture_widget()
            
            # Render widget to pixmap
            pixmap = capture_widget.grab()
            
            # Save the image
            if pixmap.save(filename):
                self.status_label.setText(f"📸 Results saved to: {os.path.basename(filename)}")
                
                # Ask if user wants to open the image
                reply = QMessageBox.question(
                    self,
                    "Image Saved",
                    f"Ping results saved successfully!\n\nFile: {os.path.basename(filename)}\n\nWould you like to open the image?",
                    QMessageBox.Yes | QMessageBox.No,
                    QMessageBox.No
                )
                
                if reply == QMessageBox.Yes:
                    self.open_image_file(filename)
            else:
                QMessageBox.warning(self, "Save Error", "Failed to save the image file.")
                self.status_label.setText("❌ Failed to save image")
                
        except Exception as e:
            QMessageBox.critical(self, "Capture Error", f"Error capturing results:\n{str(e)}")
            self.status_label.setText("❌ Capture failed")
    
    def create_capture_widget(self):
        """Create a widget for capturing ping results - content only"""
        # Get results content
        results_content = self.results_text.toPlainText()
        
        if not results_content.strip():
            # Create empty widget if no content
            capture_widget = QWidget()
            capture_widget.setFixedSize(600, 300)
            return capture_widget
        
        # Create a text widget for the results only
        results_display = QTextEdit()
        results_display.setPlainText(results_content)
        results_display.setReadOnly(True)
        results_display.setStyleSheet("""
            QTextEdit {
                background-color: #1e1e1e;
                color: #d4d4d4;
                border: none;
                padding: 20px;
                font-family: 'Consolas', 'Monaco', 'Courier New', monospace;
                font-size: 16px;
                line-height: 1.6;
                font-weight: normal;
            }
        """)
        
        # Calculate size based on content
        doc = results_display.document()
        doc.setPlainText(results_content)
        
        # Calculate width based on longest line
        lines = results_content.split('\n')
        max_line_length = max(len(line) for line in lines) if lines else 50
        
        # Estimate width (approximately 12 pixels per character for larger font)
        width = min(max(max_line_length * 12 + 40, 600), 1600)
        
        # Calculate height based on number of lines (larger line height)
        line_count = len(lines)
        height = min(max(line_count * 28 + 40, 300), 1200)
        
        # Set the size
        results_display.setFixedSize(width, height)
        
        # Create container widget
        capture_widget = QWidget()
        capture_widget.setFixedSize(width, height)
        capture_widget.setStyleSheet("""
            QWidget {
                background-color: #1e1e1e;
            }
        """)
        
        # Layout to hold the text widget
        layout = QVBoxLayout(capture_widget)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.addWidget(results_display)
        
        return capture_widget
    
    def open_image_file(self, filename):
        """Open the saved image file with default system application"""
        try:
            import os
            import platform
            
            system = platform.system()
            if system == "Windows":
                os.startfile(filename)
            elif system == "Darwin":  # macOS
                os.system(f"open '{filename}'")
            else:  # Linux and others
                os.system(f"xdg-open '{filename}'")
                
        except Exception as e:
            QMessageBox.information(
                self, 
                "Open Image", 
                f"Image saved successfully, but couldn't open it automatically.\n\nFile location: {filename}\n\nError: {str(e)}"
            )
    
    def closeEvent(self, event):
        """Handle dialog close"""
        if self.ping_worker:
            self.ping_worker.stop_ping()
        event.accept()