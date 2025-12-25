"""
Network Speed Test Tool
A simple network speed test dialog for testing download/upload speeds.
"""

import sys
import time
import threading
import requests
from PyQt5.QtCore import *
from PyQt5.QtWidgets import *
from PyQt5.QtGui import *


class SpeedTestWorker(QObject):
    """Worker thread for running speed tests"""
    
    progress_updated = pyqtSignal(str)  # Status message
    download_progress = pyqtSignal(float)  # Download speed in Mbps
    upload_progress = pyqtSignal(float)  # Upload speed in Mbps
    test_completed = pyqtSignal(dict)  # Final results
    error_occurred = pyqtSignal(str)  # Error message
    
    def __init__(self):
        super().__init__()
        self.is_running = False
        
    def run_speed_test(self):
        """Run the complete speed test"""
        self.is_running = True
        results = {
            'download_speed': 0,
            'upload_speed': 0,
            'ping': 0,
            'server': 'Unknown'
        }
        
        try:
            # Test ping first
            self.progress_updated.emit("Testing ping...")
            results['ping'] = self.test_ping()
            
            if not self.is_running:
                return
                
            # Test download speed
            self.progress_updated.emit("Testing download speed...")
            results['download_speed'] = self.test_download_speed()
            
            if not self.is_running:
                return
                
            # Test upload speed
            self.progress_updated.emit("Testing upload speed...")
            results['upload_speed'] = self.test_upload_speed()
            
            self.progress_updated.emit("Speed test completed!")
            self.test_completed.emit(results)
            
        except Exception as e:
            self.error_occurred.emit(f"Speed test failed: {str(e)}")
        finally:
            self.is_running = False
    
    def test_ping(self):
        """Test ping to a reliable server"""
        try:
            start_time = time.time()
            response = requests.get('https://www.google.com', timeout=10)
            end_time = time.time()
            
            if response.status_code == 200:
                ping_ms = (end_time - start_time) * 1000
                return round(ping_ms, 2)
            else:
                return 0
        except:
            return 0
    
    def test_download_speed(self):
        """Test download speed using a test file"""
        try:
            # Use a test file (10MB from httpbin or similar service)
            test_urls = [
                'https://httpbin.org/bytes/10485760',  # 10MB
                'https://www.google.com',  # Fallback
            ]
            
            best_speed = 0
            
            for url in test_urls:
                if not self.is_running:
                    break
                    
                try:
                    start_time = time.time()
                    response = requests.get(url, timeout=30, stream=True)
                    
                    if response.status_code == 200:
                        total_size = 0
                        chunk_size = 8192
                        
                        for chunk in response.iter_content(chunk_size=chunk_size):
                            if not self.is_running:
                                break
                            if chunk:
                                total_size += len(chunk)
                        
                        end_time = time.time()
                        duration = end_time - start_time
                        
                        if duration > 0:
                            # Calculate speed in Mbps
                            speed_bps = (total_size * 8) / duration
                            speed_mbps = speed_bps / (1024 * 1024)
                            
                            if speed_mbps > best_speed:
                                best_speed = speed_mbps
                            
                            self.download_progress.emit(speed_mbps)
                            break  # Use first successful test
                            
                except requests.RequestException:
                    continue
            
            return round(best_speed, 2)
            
        except Exception as e:
            print(f"Download test error: {e}")
            return 0
    
    def test_upload_speed(self):
        """Test upload speed by posting data"""
        try:
            # Create test data (1MB)
            test_data = b'0' * (1024 * 1024)
            
            start_time = time.time()
            response = requests.post(
                'https://httpbin.org/post',
                data=test_data,
                timeout=30,
                headers={'Content-Type': 'application/octet-stream'}
            )
            end_time = time.time()
            
            if response.status_code == 200:
                duration = end_time - start_time
                if duration > 0:
                    # Calculate speed in Mbps
                    speed_bps = (len(test_data) * 8) / duration
                    speed_mbps = speed_bps / (1024 * 1024)
                    self.upload_progress.emit(speed_mbps)
                    return round(speed_mbps, 2)
            
            return 0
            
        except Exception as e:
            print(f"Upload test error: {e}")
            return 0
    
    def stop_test(self):
        """Stop the running test"""
        self.is_running = False


class SpeedTestDialog(QDialog):
    """Network Speed Test Dialog"""
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Network Speed Test")
        self.setFixedSize(450, 580)
        self.setWindowIcon(QIcon())
        
        # Worker thread
        self.worker = None
        self.worker_thread = None
        
        self.setup_ui()
        self.setup_connections()
    
    def setup_ui(self):
        """Setup the user interface"""
        layout = QVBoxLayout(self)
        layout.setSpacing(15)
        layout.setContentsMargins(20, 20, 20, 20)
        
        # Title
        title = QLabel("Network Speed Test")
        title.setAlignment(Qt.AlignCenter)
        title.setStyleSheet("""
            QLabel {
                font-size: 18px;
                font-weight: bold;
                color: #2c3e50;
                margin-bottom: 10px;
            }
        """)
        layout.addWidget(title)
        
        # Status label (subtitle)
        self.status_label = QLabel("Click 'Start Test' to begin")
        self.status_label.setAlignment(Qt.AlignCenter)
        self.status_label.setStyleSheet("""
            QLabel {
                font-size: 12px;
                color: #7f8c8d;
                margin-bottom: 15px;
            }
        """)
        layout.addWidget(self.status_label)
        
        # Buttons (moved under subtitle)
        button_layout = QHBoxLayout()
        
        self.start_button = QPushButton("🚀 Start Test")
        self.start_button.setMinimumHeight(35)
        self.start_button.setStyleSheet("""
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
            QPushButton:pressed {
                background-color: #1e7e34;
            }
            QPushButton:disabled {
                background-color: #6c757d;
            }
        """)
        button_layout.addWidget(self.start_button)
        
        self.stop_button = QPushButton("⏹️ Stop Test")
        self.stop_button.setMinimumHeight(35)
        self.stop_button.setEnabled(False)
        self.stop_button.setStyleSheet("""
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
            QPushButton:pressed {
                background-color: #bd2130;
            }
            QPushButton:disabled {
                background-color: #6c757d;
            }
        """)
        button_layout.addWidget(self.stop_button)
        
        self.close_button = QPushButton("❌ Close")
        self.close_button.setMinimumHeight(35)
        self.close_button.setStyleSheet("""
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
            QPushButton:pressed {
                background-color: #545b62;
            }
        """)
        button_layout.addWidget(self.close_button)
        
        layout.addLayout(button_layout)
        
        # Results frame
        results_frame = QFrame()
        results_frame.setFrameStyle(QFrame.StyledPanel)
        results_frame.setStyleSheet("""
            QFrame {
                background-color: #f8f9fa;
                border: 1px solid #dee2e6;
                border-radius: 8px;
                padding: 15px;
            }
        """)
        results_layout = QGridLayout(results_frame)
        
        # Ping result
        ping_label = QLabel("Ping:")
        ping_label.setStyleSheet("font-weight: bold; color: #495057;")
        self.ping_result = QLabel("-- ms")
        self.ping_result.setStyleSheet("color: #28a745; font-weight: bold;")
        results_layout.addWidget(ping_label, 0, 0)
        results_layout.addWidget(self.ping_result, 0, 1)
        
        # Download speed result
        download_label = QLabel("Download:")
        download_label.setStyleSheet("font-weight: bold; color: #495057;")
        self.download_result = QLabel("-- Mbps")
        self.download_result.setStyleSheet("color: #007bff; font-weight: bold;")
        results_layout.addWidget(download_label, 1, 0)
        results_layout.addWidget(self.download_result, 1, 1)
        
        # Upload speed result
        upload_label = QLabel("Upload:")
        upload_label.setStyleSheet("font-weight: bold; color: #495057;")
        self.upload_result = QLabel("-- Mbps")
        self.upload_result.setStyleSheet("color: #fd7e14; font-weight: bold;")
        results_layout.addWidget(upload_label, 2, 0)
        results_layout.addWidget(self.upload_result, 2, 1)
        
        layout.addWidget(results_frame)
        
        # Progress bar (moved under results box)
        self.progress_bar = QProgressBar()
        self.progress_bar.setRange(0, 0)  # Indeterminate progress
        self.progress_bar.setVisible(False)
        self.progress_bar.setStyleSheet("""
            QProgressBar {
                border: 1px solid #ced4da;
                border-radius: 4px;
                text-align: center;
                background-color: #e9ecef;
            }
            QProgressBar::chunk {
                background-color: #007bff;
                border-radius: 3px;
            }
        """)
        layout.addWidget(self.progress_bar)
        
        # Analysis text area
        self.analysis_label = QLabel("")
        self.analysis_label.setAlignment(Qt.AlignCenter)
        self.analysis_label.setWordWrap(True)
        self.analysis_label.setStyleSheet("""
            QLabel {
                background-color: #e8f4fd;
                border: 1px solid #bee5eb;
                border-radius: 6px;
                padding: 12px;
                font-size: 13px;
                font-weight: bold;
                color: #0c5460;
                margin: 5px 0;
            }
        """)
        self.analysis_label.setVisible(False)
        layout.addWidget(self.analysis_label)
        
        # Add stretch to push everything up
        layout.addStretch()
    
    def setup_connections(self):
        """Setup signal connections"""
        self.start_button.clicked.connect(self.start_speed_test)
        self.stop_button.clicked.connect(self.stop_speed_test)
        self.close_button.clicked.connect(self.close)
    
    def start_speed_test(self):
        """Start the speed test"""
        # Reset results
        self.ping_result.setText("-- ms")
        self.download_result.setText("-- Mbps")
        self.upload_result.setText("-- Mbps")
        
        # Hide analysis from previous test
        self.analysis_label.setVisible(False)
        
        # Update UI
        self.start_button.setEnabled(False)
        self.stop_button.setEnabled(True)
        self.progress_bar.setVisible(True)
        self.status_label.setText("Initializing speed test...")
        
        # Create worker thread
        self.worker_thread = QThread()
        self.worker = SpeedTestWorker()
        self.worker.moveToThread(self.worker_thread)
        
        # Connect signals
        self.worker.progress_updated.connect(self.update_status)
        self.worker.download_progress.connect(self.update_download_speed)
        self.worker.upload_progress.connect(self.update_upload_speed)
        self.worker.test_completed.connect(self.on_test_completed)
        self.worker.error_occurred.connect(self.on_error)
        
        self.worker_thread.started.connect(self.worker.run_speed_test)
        self.worker_thread.finished.connect(self.worker_thread.deleteLater)
        
        # Start the thread
        self.worker_thread.start()
    
    def stop_speed_test(self):
        """Stop the speed test"""
        if self.worker:
            self.worker.stop_test()
        
        # Hide analysis when test is stopped
        self.analysis_label.setVisible(False)
        
        self.cleanup_thread()
        self.status_label.setText("Speed test stopped")
    
    def update_status(self, message):
        """Update status label"""
        self.status_label.setText(message)
    
    def update_download_speed(self, speed):
        """Update download speed display"""
        self.download_result.setText(f"{speed:.2f} Mbps")
    
    def update_upload_speed(self, speed):
        """Update upload speed display"""
        self.upload_result.setText(f"{speed:.2f} Mbps")
    
    def analyze_network_performance(self, results):
        """Analyze network performance and return descriptive text"""
        ping = results['ping']
        download = results['download_speed']
        upload = results['upload_speed']
        
        # Analyze ping
        if ping == 0:
            ping_status = "Unable to measure"
            ping_quality = "unknown"
        elif ping < 20:
            ping_status = "Excellent"
            ping_quality = "excellent"
        elif ping < 50:
            ping_status = "Good"
            ping_quality = "good"
        elif ping < 100:
            ping_status = "Fair"
            ping_quality = "fair"
        else:
            ping_status = "Poor"
            ping_quality = "poor"
        
        # Analyze download speed
        if download == 0:
            download_status = "Unable to measure"
            download_quality = "unknown"
        elif download >= 100:
            download_status = "Excellent"
            download_quality = "excellent"
        elif download >= 25:
            download_status = "Good"
            download_quality = "good"
        elif download >= 10:
            download_status = "Fair"
            download_quality = "fair"
        elif download >= 1:
            download_status = "Poor"
            download_quality = "poor"
        else:
            download_status = "Very Poor"
            download_quality = "very poor"
        
        # Analyze upload speed
        if upload == 0:
            upload_status = "Unable to measure"
            upload_quality = "unknown"
        elif upload >= 50:
            upload_status = "Excellent"
            upload_quality = "excellent"
        elif upload >= 10:
            upload_status = "Good"
            upload_quality = "good"
        elif upload >= 3:
            upload_status = "Fair"
            upload_quality = "fair"
        elif upload >= 1:
            upload_status = "Poor"
            upload_quality = "poor"
        else:
            upload_status = "Very Poor"
            upload_quality = "very poor"
        
        # Overall assessment
        qualities = [ping_quality, download_quality, upload_quality]
        
        if "unknown" in qualities:
            overall = "Unable to fully assess your network"
            emoji = "❓"
            color_class = "warning"
        elif "excellent" in qualities and "poor" not in qualities and "very poor" not in qualities:
            overall = "Your network is excellent"
            emoji = "🚀"
            color_class = "excellent"
        elif download_quality in ["good", "excellent"] and upload_quality in ["good", "excellent"] and ping_quality in ["good", "excellent"]:
            overall = "Your network is good"
            emoji = "✅"
            color_class = "good"
        elif download_quality == "fair" or upload_quality == "fair" or ping_quality == "fair":
            overall = "Your network is fair"
            emoji = "⚠️"
            color_class = "fair"
        else:
            overall = "Your network needs improvement"
            emoji = "❌"
            color_class = "poor"
        
        # Create detailed analysis text
        analysis_text = f"{emoji} {overall}\n\n"
        analysis_text += f"📡 Ping: {ping_status} ({ping:.1f}ms)\n"
        analysis_text += f"⬇️ Download: {download_status} ({download:.1f} Mbps)\n"
        analysis_text += f"⬆️ Upload: {upload_status} ({upload:.1f} Mbps)"
        
        # Add recommendations
        if download_quality in ["poor", "very poor"]:
            analysis_text += "\n\n💡 Tip: Slow download speeds may affect streaming and browsing"
        elif upload_quality in ["poor", "very poor"]:
            analysis_text += "\n\n💡 Tip: Slow upload speeds may affect video calls and file sharing"
        elif ping_quality in ["poor", "very poor"]:
            analysis_text += "\n\n💡 Tip: High ping may cause lag in online games and video calls"
        elif overall == "Your network is excellent":
            analysis_text += "\n\n🎉 Perfect for streaming, gaming, and video conferencing!"
        elif overall == "Your network is good":
            analysis_text += "\n\n👍 Great for most online activities!"
        
        return analysis_text, color_class
    
    def update_analysis_style(self, color_class):
        """Update analysis label style based on performance"""
        styles = {
            "excellent": """
                QLabel {
                    background-color: #d4edda;
                    border: 1px solid #c3e6cb;
                    color: #155724;
                }
            """,
            "good": """
                QLabel {
                    background-color: #e8f4fd;
                    border: 1px solid #bee5eb;
                    color: #0c5460;
                }
            """,
            "fair": """
                QLabel {
                    background-color: #fff3cd;
                    border: 1px solid #ffeaa7;
                    color: #856404;
                }
            """,
            "poor": """
                QLabel {
                    background-color: #f8d7da;
                    border: 1px solid #f5c6cb;
                    color: #721c24;
                }
            """,
            "warning": """
                QLabel {
                    background-color: #e2e3e5;
                    border: 1px solid #d6d8db;
                    color: #383d41;
                }
            """
        }
        
        base_style = """
            QLabel {
                border-radius: 6px;
                padding: 12px;
                font-size: 13px;
                font-weight: bold;
                margin: 5px 0;
            }
        """
        
        self.analysis_label.setStyleSheet(base_style + styles.get(color_class, styles["good"]))
    
    def on_test_completed(self, results):
        """Handle test completion"""
        self.ping_result.setText(f"{results['ping']:.2f} ms")
        self.download_result.setText(f"{results['download_speed']:.2f} Mbps")
        self.upload_result.setText(f"{results['upload_speed']:.2f} Mbps")
        
        # Show analysis
        analysis_text, color_class = self.analyze_network_performance(results)
        self.analysis_label.setText(analysis_text)
        self.update_analysis_style(color_class)
        self.analysis_label.setVisible(True)
        
        self.cleanup_thread()
        self.status_label.setText("Speed test completed successfully!")
    
    def on_error(self, error_message):
        """Handle test error"""
        self.cleanup_thread()
        self.status_label.setText(f"Error: {error_message}")
        
        # Show error dialog
        QMessageBox.warning(self, "Speed Test Error", error_message)
    
    def cleanup_thread(self):
        """Clean up worker thread"""
        self.start_button.setEnabled(True)
        self.stop_button.setEnabled(False)
        self.progress_bar.setVisible(False)
        
        if hasattr(self, 'worker_thread') and self.worker_thread and self.worker_thread.isRunning():
            self.worker_thread.quit()
            self.worker_thread.wait()
            self.worker_thread = None
        
        if hasattr(self, 'worker'):
            self.worker = None
    
    def closeEvent(self, event):
        """Handle dialog close event"""
        if hasattr(self, 'worker') and self.worker:
            self.worker.stop_test()
        
        if hasattr(self, 'worker_thread') and self.worker_thread and self.worker_thread.isRunning():
            self.worker_thread.quit()
            self.worker_thread.wait()
        
        event.accept()


if __name__ == "__main__":
    app = QApplication(sys.argv)
    dialog = SpeedTestDialog()
    dialog.show()
    sys.exit(app.exec_())