"""
DNS/Nameserver Check Tool for the browser.
Provides DNS lookup and nameserver checking functionality.
"""

from PyQt5.QtCore import *
from PyQt5.QtWidgets import *
from PyQt5.QtGui import *
import subprocess
import socket
import threading
import re
import sys
from datetime import datetime


class DNSWorker(QObject):
    """Worker thread for DNS operations"""
    
    # Signals
    result_ready = pyqtSignal(str, str)  # result_type, result_text
    error_occurred = pyqtSignal(str)
    finished = pyqtSignal()
    
    def __init__(self, domain, check_type):
        super().__init__()
        self.domain = domain.strip().lower()
        self.check_type = check_type
        self.is_cancelled = False
    
    def cancel(self):
        """Cancel the DNS operation"""
        self.is_cancelled = True
    
    def run(self):
        """Run DNS checks"""
        try:
            if self.is_cancelled:
                return
            
            if self.check_type == "all":
                self.check_all_records()
            elif self.check_type == "a":
                self.check_a_record()
            elif self.check_type == "aaaa":
                self.check_aaaa_record()
            elif self.check_type == "mx":
                self.check_mx_record()
            elif self.check_type == "ns":
                self.check_ns_record()
            elif self.check_type == "txt":
                self.check_txt_record()
            elif self.check_type == "cname":
                self.check_cname_record()
            elif self.check_type == "soa":
                self.check_soa_record()
            elif self.check_type == "ptr":
                self.check_ptr_record()
            
        except Exception as e:
            self.error_occurred.emit(f"DNS check failed: {str(e)}")
        finally:
            self.finished.emit()
    
    def check_all_records(self):
        """Check all common DNS record types"""
        if self.is_cancelled:
            return
        
        self.result_ready.emit("info", f"🔍 Comprehensive DNS check for: {self.domain}")
        self.result_ready.emit("info", f"⏰ Started at: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        self.result_ready.emit("separator", "=" * 60)
        
        # Check each record type
        record_types = [
            ("A Record (IPv4)", "a"),
            ("AAAA Record (IPv6)", "aaaa"),
            ("MX Record (Mail)", "mx"),
            ("NS Record (Nameservers)", "ns"),
            ("TXT Record (Text)", "txt"),
            ("CNAME Record (Alias)", "cname"),
            ("SOA Record (Authority)", "soa")
        ]
        
        for name, record_type in record_types:
            if self.is_cancelled:
                return
            
            self.result_ready.emit("header", f"\n📋 {name}")
            self.result_ready.emit("separator", "-" * 40)
            
            if record_type == "a":
                self.check_a_record()
            elif record_type == "aaaa":
                self.check_aaaa_record()
            elif record_type == "mx":
                self.check_mx_record()
            elif record_type == "ns":
                self.check_ns_record()
            elif record_type == "txt":
                self.check_txt_record()
            elif record_type == "cname":
                self.check_cname_record()
            elif record_type == "soa":
                self.check_soa_record()
    
    def check_a_record(self):
        """Check A record (IPv4)"""
        try:
            result = socket.getaddrinfo(self.domain, None, socket.AF_INET)
            ips = list(set([r[4][0] for r in result]))
            
            if ips:
                self.result_ready.emit("success", f"✅ A Records found:")
                for ip in sorted(ips):
                    self.result_ready.emit("data", f"   🌐 {ip}")
            else:
                self.result_ready.emit("warning", "⚠️  No A records found")
                
        except socket.gaierror:
            self.result_ready.emit("error", "❌ No A records found or domain not found")
        except Exception as e:
            self.result_ready.emit("error", f"❌ A record check failed: {str(e)}")
    
    def check_aaaa_record(self):
        """Check AAAA record (IPv6)"""
        try:
            result = socket.getaddrinfo(self.domain, None, socket.AF_INET6)
            ips = list(set([r[4][0] for r in result]))
            
            if ips:
                self.result_ready.emit("success", f"✅ AAAA Records found:")
                for ip in sorted(ips):
                    self.result_ready.emit("data", f"   🌐 {ip}")
            else:
                self.result_ready.emit("warning", "⚠️  No AAAA records found")
                
        except socket.gaierror:
            self.result_ready.emit("warning", "⚠️  No AAAA records found")
        except Exception as e:
            self.result_ready.emit("error", f"❌ AAAA record check failed: {str(e)}")
    
    def check_mx_record(self):
        """Check MX record (Mail Exchange)"""
        try:
            result = self.run_nslookup("MX")
            if result and "mail exchanger" in result.lower():
                self.result_ready.emit("success", "✅ MX Records found:")
                lines = result.split('\n')
                for line in lines:
                    if "mail exchanger" in line.lower():
                        self.result_ready.emit("data", f"   📧 {line.strip()}")
            else:
                self.result_ready.emit("warning", "⚠️  No MX records found")
        except Exception as e:
            self.result_ready.emit("error", f"❌ MX record check failed: {str(e)}")
    
    def check_ns_record(self):
        """Check NS record (Nameservers)"""
        try:
            result = self.run_nslookup("NS")
            if result and "nameserver" in result.lower():
                self.result_ready.emit("success", "✅ NS Records found:")
                lines = result.split('\n')
                for line in lines:
                    if "nameserver" in line.lower():
                        self.result_ready.emit("data", f"   🌐 {line.strip()}")
            else:
                self.result_ready.emit("warning", "⚠️  No NS records found")
        except Exception as e:
            self.result_ready.emit("error", f"❌ NS record check failed: {str(e)}")
    
    def check_txt_record(self):
        """Check TXT record"""
        try:
            result = self.run_nslookup("TXT")
            if result and "text" in result.lower():
                self.result_ready.emit("success", "✅ TXT Records found:")
                lines = result.split('\n')
                for line in lines:
                    if "text" in line.lower() and "=" in line:
                        self.result_ready.emit("data", f"   📝 {line.strip()}")
            else:
                self.result_ready.emit("warning", "⚠️  No TXT records found")
        except Exception as e:
            self.result_ready.emit("error", f"❌ TXT record check failed: {str(e)}")
    
    def check_cname_record(self):
        """Check CNAME record"""
        try:
            result = self.run_nslookup("CNAME")
            if result and "canonical name" in result.lower():
                self.result_ready.emit("success", "✅ CNAME Records found:")
                lines = result.split('\n')
                for line in lines:
                    if "canonical name" in line.lower():
                        self.result_ready.emit("data", f"   🔗 {line.strip()}")
            else:
                self.result_ready.emit("warning", "⚠️  No CNAME records found")
        except Exception as e:
            self.result_ready.emit("error", f"❌ CNAME record check failed: {str(e)}")
    
    def check_soa_record(self):
        """Check SOA record (Start of Authority)"""
        try:
            result = self.run_nslookup("SOA")
            if result and ("origin" in result.lower() or "primary" in result.lower()):
                self.result_ready.emit("success", "✅ SOA Record found:")
                lines = result.split('\n')
                for line in lines:
                    if any(keyword in line.lower() for keyword in ["origin", "primary", "serial", "refresh", "retry"]):
                        self.result_ready.emit("data", f"   ⚙️  {line.strip()}")
            else:
                self.result_ready.emit("warning", "⚠️  No SOA records found")
        except Exception as e:
            self.result_ready.emit("error", f"❌ SOA record check failed: {str(e)}")
    
    def check_ptr_record(self):
        """Check PTR record (Reverse DNS)"""
        try:
            # First check if input is an IP address
            if self.is_ip_address(self.domain):
                hostname = socket.gethostbyaddr(self.domain)[0]
                self.result_ready.emit("success", f"✅ PTR Record found:")
                self.result_ready.emit("data", f"   🔄 {self.domain} → {hostname}")
            else:
                self.result_ready.emit("warning", "⚠️  PTR lookup requires an IP address")
        except socket.herror:
            self.result_ready.emit("warning", "⚠️  No PTR record found")
        except Exception as e:
            self.result_ready.emit("error", f"❌ PTR record check failed: {str(e)}")
    
    def run_nslookup(self, record_type):
        """Run nslookup command"""
        try:
            if sys.platform == "win32":
                cmd = ["nslookup", "-type=" + record_type, self.domain]
            else:
                cmd = ["nslookup", "-type=" + record_type, self.domain]
            
            result = subprocess.run(cmd, capture_output=True, text=True, timeout=10)
            return result.stdout
        except subprocess.TimeoutExpired:
            raise Exception("DNS lookup timed out")
        except FileNotFoundError:
            raise Exception("nslookup command not found")
        except Exception as e:
            raise Exception(f"nslookup failed: {str(e)}")
    
    def is_ip_address(self, address):
        """Check if string is a valid IP address"""
        try:
            socket.inet_aton(address)
            return True
        except socket.error:
            try:
                socket.inet_pton(socket.AF_INET6, address)
                return True
            except socket.error:
                return False


class DNSDialog(QDialog):
    """DNS/Nameserver check dialog"""
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("🌐 DNS/Nameserver Check Tool")
        self.setMinimumSize(700, 600)
        self.resize(800, 700)
        
        # Worker thread
        self.worker = None
        self.worker_thread = None
        
        self.setup_ui()
    
    def setup_ui(self):
        """Setup the dialog UI"""
        layout = QVBoxLayout(self)
        
        # Header
        header_label = QLabel("🌐 DNS/Nameserver Check Tool")
        header_label.setAlignment(Qt.AlignCenter)
        header_label.setStyleSheet("font-size: 18px; font-weight: bold; color: #2196F3; padding: 10px;")
        layout.addWidget(header_label)
        
        # Input section
        input_group = QGroupBox("🔍 DNS Lookup")
        input_layout = QGridLayout(input_group)
        
        # Domain input
        input_layout.addWidget(QLabel("Domain/IP:"), 0, 0)
        self.domain_input = QLineEdit()
        self.domain_input.setPlaceholderText("Enter domain name or IP address (e.g., google.com, 8.8.8.8)")
        self.domain_input.returnPressed.connect(self.start_dns_check)
        input_layout.addWidget(self.domain_input, 0, 1)
        
        # Record type selection
        input_layout.addWidget(QLabel("Record Type:"), 1, 0)
        self.record_type_combo = QComboBox()
        self.record_type_combo.addItems([
            "🔍 All Records (Comprehensive)",
            "🌐 A Record (IPv4)",
            "🌐 AAAA Record (IPv6)",
            "📧 MX Record (Mail)",
            "🌐 NS Record (Nameservers)",
            "📝 TXT Record (Text)",
            "🔗 CNAME Record (Alias)",
            "⚙️ SOA Record (Authority)",
            "🔄 PTR Record (Reverse DNS)"
        ])
        input_layout.addWidget(self.record_type_combo, 1, 1)
        
        layout.addWidget(input_group)
        
        # Control buttons
        button_layout = QHBoxLayout()
        
        self.check_btn = QPushButton("🔍 Check DNS")
        self.check_btn.clicked.connect(self.start_dns_check)
        self.check_btn.setStyleSheet("""
            QPushButton {
                background-color: #4CAF50;
                color: white;
                border: none;
                border-radius: 6px;
                padding: 8px 16px;
                font-size: 14px;
                font-weight: bold;
            }
            QPushButton:hover {
                background-color: #45a049;
            }
            QPushButton:disabled {
                background-color: #cccccc;
                color: #666666;
            }
        """)
        button_layout.addWidget(self.check_btn)
        
        self.stop_btn = QPushButton("⏹️ Stop")
        self.stop_btn.clicked.connect(self.stop_dns_check)
        self.stop_btn.setEnabled(False)
        self.stop_btn.setStyleSheet("""
            QPushButton {
                background-color: #f44336;
                color: white;
                border: none;
                border-radius: 6px;
                padding: 8px 16px;
                font-size: 14px;
                font-weight: bold;
            }
            QPushButton:hover {
                background-color: #da190b;
            }
            QPushButton:disabled {
                background-color: #cccccc;
                color: #666666;
            }
        """)
        button_layout.addWidget(self.stop_btn)
        
        self.clear_btn = QPushButton("🗑️ Clear")
        self.clear_btn.clicked.connect(self.clear_results)
        self.clear_btn.setStyleSheet("""
            QPushButton {
                background-color: #ff9800;
                color: white;
                border: none;
                border-radius: 6px;
                padding: 8px 16px;
                font-size: 14px;
                font-weight: bold;
            }
            QPushButton:hover {
                background-color: #f57c00;
            }
        """)
        button_layout.addWidget(self.clear_btn)
        
        button_layout.addStretch()
        
        self.export_btn = QPushButton("💾 Export Results")
        self.export_btn.clicked.connect(self.export_results)
        self.export_btn.setStyleSheet("""
            QPushButton {
                background-color: #2196F3;
                color: white;
                border: none;
                border-radius: 6px;
                padding: 8px 16px;
                font-size: 14px;
                font-weight: bold;
            }
            QPushButton:hover {
                background-color: #1976D2;
            }
        """)
        button_layout.addWidget(self.export_btn)
        
        layout.addLayout(button_layout)
        
        # Results area
        results_group = QGroupBox("📋 DNS Results")
        results_layout = QVBoxLayout(results_group)
        
        self.results_text = QTextEdit()
        self.results_text.setReadOnly(True)
        self.results_text.setFont(QFont("Consolas", 10))
        self.results_text.setStyleSheet("""
            QTextEdit {
                background-color: #f8f9fa;
                border: 1px solid #dee2e6;
                border-radius: 4px;
                padding: 8px;
            }
        """)
        results_layout.addWidget(self.results_text)
        
        layout.addWidget(results_group)
        
        # Status bar
        self.status_label = QLabel("Ready to check DNS records")
        self.status_label.setStyleSheet("color: #666; font-style: italic; padding: 5px;")
        layout.addWidget(self.status_label)
        
        # Progress bar
        self.progress_bar = QProgressBar()
        self.progress_bar.setVisible(False)
        layout.addWidget(self.progress_bar)
    
    def start_dns_check(self):
        """Start DNS check"""
        domain = self.domain_input.text().strip()
        if not domain:
            QMessageBox.warning(self, "Input Required", "Please enter a domain name or IP address.")
            return
        
        # Get selected record type
        record_types = {
            0: "all",
            1: "a",
            2: "aaaa", 
            3: "mx",
            4: "ns",
            5: "txt",
            6: "cname",
            7: "soa",
            8: "ptr"
        }
        
        record_type = record_types.get(self.record_type_combo.currentIndex(), "all")
        
        # Update UI
        self.check_btn.setEnabled(False)
        self.stop_btn.setEnabled(True)
        self.progress_bar.setVisible(True)
        self.progress_bar.setRange(0, 0)  # Indeterminate progress
        self.status_label.setText(f"Checking DNS records for {domain}...")
        
        # Clear previous results
        self.results_text.clear()
        
        # Create worker thread
        self.worker = DNSWorker(domain, record_type)
        self.worker_thread = QThread()
        self.worker.moveToThread(self.worker_thread)
        
        # Connect signals
        self.worker_thread.started.connect(self.worker.run)
        self.worker.result_ready.connect(self.append_result)
        self.worker.error_occurred.connect(self.show_error)
        self.worker.finished.connect(self.dns_check_finished)
        
        # Start thread
        self.worker_thread.start()
    
    def stop_dns_check(self):
        """Stop DNS check"""
        if self.worker:
            self.worker.cancel()
        
        if self.worker_thread and self.worker_thread.isRunning():
            self.worker_thread.quit()
            self.worker_thread.wait(3000)  # Wait up to 3 seconds
        
        self.dns_check_finished()
        self.append_result("warning", "\n⏹️ DNS check stopped by user")
    
    def dns_check_finished(self):
        """Handle DNS check completion"""
        self.check_btn.setEnabled(True)
        self.stop_btn.setEnabled(False)
        self.progress_bar.setVisible(False)
        self.status_label.setText("DNS check completed")
        
        # Clean up thread
        if self.worker_thread:
            self.worker_thread.quit()
            self.worker_thread.wait()
            self.worker_thread = None
        self.worker = None
    
    def append_result(self, result_type, text):
        """Append result to text area with formatting"""
        cursor = self.results_text.textCursor()
        cursor.movePosition(QTextCursor.End)
        
        # Set color based on result type
        if result_type == "success":
            cursor.insertHtml(f'<span style="color: #4CAF50; font-weight: bold;">{text}</span><br>')
        elif result_type == "error":
            cursor.insertHtml(f'<span style="color: #f44336; font-weight: bold;">{text}</span><br>')
        elif result_type == "warning":
            cursor.insertHtml(f'<span style="color: #ff9800; font-weight: bold;">{text}</span><br>')
        elif result_type == "header":
            cursor.insertHtml(f'<span style="color: #2196F3; font-weight: bold; font-size: 14px;">{text}</span><br>')
        elif result_type == "data":
            cursor.insertHtml(f'<span style="color: #333; font-family: monospace;">{text}</span><br>')
        elif result_type == "separator":
            cursor.insertHtml(f'<span style="color: #666;">{text}</span><br>')
        else:  # info
            cursor.insertHtml(f'<span style="color: #666;">{text}</span><br>')
        
        # Auto-scroll to bottom
        self.results_text.setTextCursor(cursor)
        self.results_text.ensureCursorVisible()
    
    def show_error(self, error_message):
        """Show error message"""
        self.append_result("error", f"❌ {error_message}")
    
    def clear_results(self):
        """Clear results"""
        self.results_text.clear()
        self.status_label.setText("Results cleared")
    
    def export_results(self):
        """Export results to file"""
        if not self.results_text.toPlainText().strip():
            QMessageBox.information(self, "No Results", "No results to export.")
            return
        
        filename, _ = QFileDialog.getSaveFileName(
            self, "Export DNS Results", 
            f"dns_check_{datetime.now().strftime('%Y%m%d_%H%M%S')}.txt",
            "Text Files (*.txt);;All Files (*)"
        )
        
        if filename:
            try:
                with open(filename, 'w', encoding='utf-8') as f:
                    f.write(f"DNS Check Results\n")
                    f.write(f"Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
                    f.write("=" * 60 + "\n\n")
                    f.write(self.results_text.toPlainText())
                
                QMessageBox.information(self, "Export Successful", f"Results exported to:\n{filename}")
            except Exception as e:
                QMessageBox.critical(self, "Export Failed", f"Failed to export results:\n{str(e)}")
    
    def closeEvent(self, event):
        """Handle dialog close"""
        if self.worker_thread and self.worker_thread.isRunning():
            self.stop_dns_check()
        event.accept()