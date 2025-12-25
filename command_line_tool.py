"""
Command line tool for executing system commands.
Provides a terminal-like interface within the browser.
"""

import subprocess
import platform
import os
import threading
import time
from datetime import datetime
from PyQt5.QtCore import QObject, pyqtSignal, QTimer, Qt
from PyQt5.QtWidgets import *
from PyQt5.QtGui import *


class CommandWorker(QObject):
    """Worker thread for command execution"""
    
    command_output = pyqtSignal(str, bool)  # output, is_error
    command_finished = pyqtSignal(int)  # exit_code
    
    def __init__(self, command, working_dir=None):
        super().__init__()
        self.command = command
        self.working_dir = working_dir or os.getcwd()
        self.process = None
        self.is_running = False
    
    def start_command(self):
        """Start command execution"""
        self.is_running = True
        threading.Thread(target=self._execute_command, daemon=True).start()
    
    def stop_command(self):
        """Stop command execution"""
        self.is_running = False
        if self.process:
            try:
                self.process.terminate()
            except:
                pass
    
    def _execute_command(self):
        """Execute the command"""
        try:
            # Determine shell based on OS
            system = platform.system().lower()
            if system == "windows":
                shell_cmd = ["cmd", "/c", self.command]
            else:
                shell_cmd = ["bash", "-c", self.command]
            
            # Execute command
            self.process = subprocess.Popen(
                shell_cmd,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                text=True,
                encoding='utf-8',
                errors='replace',
                cwd=self.working_dir,
                creationflags=subprocess.CREATE_NO_WINDOW if system == "windows" else 0
            )
            
            # Read output in real-time
            while self.is_running and self.process.poll() is None:
                # Read stdout
                if self.process.stdout:
                    line = self.process.stdout.readline()
                    if line:
                        self.command_output.emit(line.rstrip(), False)
                
                # Read stderr
                if self.process.stderr:
                    line = self.process.stderr.readline()
                    if line:
                        self.command_output.emit(line.rstrip(), True)
                
                time.sleep(0.01)  # Small delay to prevent high CPU usage
            
            # Get remaining output
            if self.process and self.is_running:
                stdout, stderr = self.process.communicate()
                if stdout:
                    for line in stdout.split('\n'):
                        if line.strip():
                            self.command_output.emit(line, False)
                if stderr:
                    for line in stderr.split('\n'):
                        if line.strip():
                            self.command_output.emit(line, True)
                
                exit_code = self.process.returncode
            else:
                exit_code = -1
                
        except Exception as e:
            if self.is_running:
                self.command_output.emit(f"Error: {str(e)}", True)
                exit_code = -1
        finally:
            if self.is_running:
                self.command_finished.emit(exit_code)


class CommandLineWidget(QWidget):
    """Command line interface widget"""
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.command_worker = None
        self.command_history = []
        self.history_index = -1
        self.current_directory = os.getcwd()
        self.setup_ui()
    
    def setup_ui(self):
        """Setup the command line UI"""
        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        
        # Header with current directory and controls
        header_layout = QHBoxLayout()
        
        self.dir_label = QLabel(f"📁 {self.current_directory}")
        self.current_font_size = 16  # Default font size
        self.update_dir_label_style()
        header_layout.addWidget(self.dir_label)
        
        # Change directory button
        cd_btn = QPushButton("📂 Change Dir")
        cd_btn.clicked.connect(self.change_directory)
        cd_btn.setMaximumWidth(100)
        cd_btn.setStyleSheet("""
            QPushButton {
                background-color: #34495e;
                color: #ecf0f1;
                border: 1px solid #5d6d7e;
                padding: 6px 12px;
                font-size: 11px;
            }
            QPushButton:hover {
                background-color: #5d6d7e;
            }
        """)
        header_layout.addWidget(cd_btn)
        
        # Font size controls
        font_layout = QHBoxLayout()
        
        font_label = QLabel("Font:")
        font_label.setStyleSheet("""
            QLabel {
                color: #ecf0f1;
                font-size: 11px;
                padding: 6px 4px;
            }
        """)
        font_layout.addWidget(font_label)
        
        # Font size decrease button
        font_minus_btn = QPushButton("➖")
        font_minus_btn.clicked.connect(self.decrease_font_size)
        font_minus_btn.setMaximumWidth(30)
        font_minus_btn.setToolTip("Decrease font size")
        font_minus_btn.setStyleSheet("""
            QPushButton {
                background-color: #34495e;
                color: #ecf0f1;
                border: 1px solid #5d6d7e;
                padding: 4px;
                font-size: 10px;
            }
            QPushButton:hover {
                background-color: #5d6d7e;
            }
        """)
        font_layout.addWidget(font_minus_btn)
        
        # Font size display
        self.font_size_label = QLabel(str(self.current_font_size))
        self.font_size_label.setMinimumWidth(25)
        self.font_size_label.setAlignment(Qt.AlignCenter)
        self.font_size_label.setStyleSheet("""
            QLabel {
                background-color: #2c3e50;
                color: #ecf0f1;
                border: 1px solid #5d6d7e;
                padding: 4px;
                font-size: 11px;
                font-weight: bold;
            }
        """)
        font_layout.addWidget(self.font_size_label)
        
        # Font size increase button
        font_plus_btn = QPushButton("➕")
        font_plus_btn.clicked.connect(self.increase_font_size)
        font_plus_btn.setMaximumWidth(30)
        font_plus_btn.setToolTip("Increase font size")
        font_plus_btn.setStyleSheet("""
            QPushButton {
                background-color: #34495e;
                color: #ecf0f1;
                border: 1px solid #5d6d7e;
                padding: 4px;
                font-size: 10px;
            }
            QPushButton:hover {
                background-color: #5d6d7e;
            }
        """)
        font_layout.addWidget(font_plus_btn)
        
        header_layout.addLayout(font_layout)
        
        layout.addLayout(header_layout)
        
        # Terminal output area
        self.output_text = QTextEdit()
        self.output_text.setReadOnly(True)
        self.update_output_font()
        layout.addWidget(self.output_text)
        
        # Command input area
        input_layout = QHBoxLayout()
        
        # Prompt label
        self.prompt_label = QLabel(self.get_prompt())
        self.update_prompt_font()
        input_layout.addWidget(self.prompt_label)
        
        # Command input
        self.command_input = QLineEdit()
        self.command_input.setPlaceholderText("Enter command...")
        self.command_input.returnPressed.connect(self.execute_command)
        self.update_input_font()
        
        # Install event filter for history navigation
        self.command_input.installEventFilter(self)
        input_layout.addWidget(self.command_input)
        
        # Execute button
        self.execute_btn = QPushButton("▶️")
        self.execute_btn.clicked.connect(self.execute_command)
        self.execute_btn.setMaximumWidth(40)
        self.execute_btn.setStyleSheet("""
            QPushButton {
                background-color: #27ae60;
                color: white;
                border: none;
                padding: 8px;
                font-size: 14px;
                border-top: 1px solid #34495e;
            }
            QPushButton:hover {
                background-color: #2ecc71;
            }
            QPushButton:disabled {
                background-color: #7f8c8d;
            }
        """)
        input_layout.addWidget(self.execute_btn)
        
        # Stop button
        self.stop_btn = QPushButton("⏹️")
        self.stop_btn.clicked.connect(self.stop_command)
        self.stop_btn.setEnabled(False)
        self.stop_btn.setMaximumWidth(40)
        self.stop_btn.setStyleSheet("""
            QPushButton {
                background-color: #e74c3c;
                color: white;
                border: none;
                padding: 8px;
                font-size: 14px;
                border-top: 1px solid #34495e;
            }
            QPushButton:hover {
                background-color: #c0392b;
            }
            QPushButton:disabled {
                background-color: #7f8c8d;
            }
        """)
        input_layout.addWidget(self.stop_btn)
        
        layout.addLayout(input_layout)
        
        # Add welcome message
        self.add_welcome_message()
        
        # Focus on command input
        self.command_input.setFocus()
    
    def get_prompt(self):
        """Get command prompt string"""
        system = platform.system()
        if system == "Windows":
            return f"{os.getcwd()}>"
        else:
            return f"{os.getenv('USER', 'user')}@{platform.node()}:{os.getcwd()}$"
    
    def add_welcome_message(self):
        """Add welcome message to terminal"""
        system_info = f"{platform.system()} {platform.release()}"
        python_version = f"Python {platform.python_version()}"
        
        welcome = f"""
💻 MonoGuard Command Line Interface
System: {system_info}
Python: {python_version}
Working Directory: {self.current_directory}

Type 'help' for available commands or enter any system command.
Use Up/Down arrows to navigate command history.
{'='*60}
"""
        self.output_text.append(welcome)
    
    def eventFilter(self, obj, event):
        """Handle key events for command history"""
        if obj == self.command_input and event.type() == event.KeyPress:
            if event.key() == Qt.Key_Up:
                self.navigate_history(-1)
                return True
            elif event.key() == Qt.Key_Down:
                self.navigate_history(1)
                return True
        return super().eventFilter(obj, event)
    
    def navigate_history(self, direction):
        """Navigate through command history"""
        if not self.command_history:
            return
        
        self.history_index += direction
        
        if self.history_index < 0:
            self.history_index = 0
        elif self.history_index >= len(self.command_history):
            self.history_index = len(self.command_history) - 1
        
        if 0 <= self.history_index < len(self.command_history):
            self.command_input.setText(self.command_history[self.history_index])
    
    def change_directory(self):
        """Change working directory"""
        new_dir = QFileDialog.getExistingDirectory(
            self,
            "Select Working Directory",
            self.current_directory
        )
        
        if new_dir:
            self.current_directory = new_dir
            os.chdir(new_dir)
            self.dir_label.setText(f"📁 {self.current_directory}")
            self.prompt_label.setText(self.get_prompt())
            self.output_text.append(f"\n📁 Changed directory to: {new_dir}\n")
    
    def increase_font_size(self):
        """Increase terminal font size"""
        if self.current_font_size < 24:  # Maximum font size
            self.current_font_size += 1
            self.update_fonts()
    
    def decrease_font_size(self):
        """Decrease terminal font size"""
        if self.current_font_size > 8:  # Minimum font size
            self.current_font_size -= 1
            self.update_fonts()
    
    def update_fonts(self):
        """Update all font sizes"""
        self.font_size_label.setText(str(self.current_font_size))
        self.update_dir_label_style()
        self.update_output_font()
        self.update_input_font()
        self.update_prompt_font()
    
    def update_dir_label_style(self):
        """Update directory label font size"""
        self.dir_label.setStyleSheet(f"""
            QLabel {{
                background-color: #2c3e50;
                color: #ecf0f1;
                padding: 8px 12px;
                font-family: 'Consolas', 'Monaco', monospace;
                font-size: {self.current_font_size}px;
                border-bottom: 1px solid #34495e;
            }}
        """)
    
    def update_output_font(self):
        """Update output text font size"""
        self.output_text.setFont(QFont("Consolas", self.current_font_size))
        self.output_text.setStyleSheet(f"""
            QTextEdit {{
                background-color: #1e1e1e;
                color: #d4d4d4;
                border: none;
                padding: 10px;
                font-family: 'Consolas', 'Monaco', 'Courier New', monospace;
                font-size: {self.current_font_size}px;
                line-height: 1.4;
            }}
        """)
    
    def update_input_font(self):
        """Update command input font size"""
        self.command_input.setStyleSheet(f"""
            QLineEdit {{
                background-color: #2c3e50;
                color: #ecf0f1;
                border: none;
                padding: 8px 12px;
                font-family: 'Consolas', 'Monaco', monospace;
                font-size: {self.current_font_size}px;
                border-top: 1px solid #34495e;
            }}
        """)
    
    def update_prompt_font(self):
        """Update prompt label font size"""
        self.prompt_label.setStyleSheet(f"""
            QLabel {{
                background-color: #2c3e50;
                color: #e74c3c;
                padding: 8px 12px;
                font-family: 'Consolas', 'Monaco', monospace;
                font-size: {self.current_font_size}px;
                font-weight: bold;
                border-top: 1px solid #34495e;
            }}
        """)
    
    def execute_command(self):
        """Execute the entered command"""
        command = self.command_input.text().strip()
        if not command:
            return
        
        # Add to history
        if command not in self.command_history:
            self.command_history.append(command)
        self.history_index = len(self.command_history)
        
        # Clear input
        self.command_input.clear()
        
        # Show command in output
        prompt = self.get_prompt()
        self.output_text.append(f"\n{prompt} {command}")
        
        # Handle built-in commands
        if self.handle_builtin_command(command):
            return
        
        # Execute system command
        self.command_worker = CommandWorker(command, self.current_directory)
        self.command_worker.command_output.connect(self.on_command_output)
        self.command_worker.command_finished.connect(self.on_command_finished)
        
        # Update UI
        self.execute_btn.setEnabled(False)
        self.stop_btn.setEnabled(True)
        self.command_input.setEnabled(False)
        
        # Start command
        self.command_worker.start_command()
    
    def handle_builtin_command(self, command):
        """Handle built-in commands"""
        cmd_parts = command.lower().split()
        if not cmd_parts:
            return False
        
        cmd = cmd_parts[0]
        
        if cmd == "help":
            help_text = """
Built-in Commands:
  help          - Show this help message
  clear         - Clear the terminal output
  pwd           - Show current working directory
  ls / dir      - List directory contents
  cd <path>     - Change directory
  exit / quit   - Close command line mode

System Commands:
  Any system command available in your shell (cmd/bash)
  Examples: ping google.com, python --version, git status
"""
            self.output_text.append(help_text)
            return True
        
        elif cmd == "clear":
            self.output_text.clear()
            self.add_welcome_message()
            return True
        
        elif cmd == "pwd":
            self.output_text.append(f"{self.current_directory}")
            return True
        
        elif cmd in ["ls", "dir"]:
            try:
                files = os.listdir(self.current_directory)
                if files:
                    for file in sorted(files):
                        file_path = os.path.join(self.current_directory, file)
                        if os.path.isdir(file_path):
                            self.output_text.append(f"📁 {file}/")
                        else:
                            self.output_text.append(f"📄 {file}")
                else:
                    self.output_text.append("Directory is empty")
            except Exception as e:
                self.output_text.append(f"Error: {e}")
            return True
        
        elif cmd == "cd":
            if len(cmd_parts) > 1:
                new_path = " ".join(cmd_parts[1:])
                try:
                    if new_path == "..":
                        new_path = os.path.dirname(self.current_directory)
                    elif not os.path.isabs(new_path):
                        new_path = os.path.join(self.current_directory, new_path)
                    
                    if os.path.exists(new_path) and os.path.isdir(new_path):
                        self.current_directory = os.path.abspath(new_path)
                        os.chdir(self.current_directory)
                        self.dir_label.setText(f"📁 {self.current_directory}")
                        self.prompt_label.setText(self.get_prompt())
                        self.output_text.append(f"Changed to: {self.current_directory}")
                    else:
                        self.output_text.append(f"Directory not found: {new_path}")
                except Exception as e:
                    self.output_text.append(f"Error: {e}")
            else:
                self.output_text.append(f"Current directory: {self.current_directory}")
            return True
        
        elif cmd in ["exit", "quit"]:
            # Signal to parent to switch back to web mode
            if hasattr(self.parent(), 'switch_to_web_mode'):
                self.parent().switch_to_web_mode()
            return True
        
        return False
    
    def stop_command(self):
        """Stop current command execution"""
        if self.command_worker:
            self.command_worker.stop_command()
        self.on_command_finished(-1)
    
    def on_command_output(self, output, is_error):
        """Handle command output"""
        if is_error:
            # Red color for errors
            self.output_text.append(f'<span style="color: #e74c3c;">{output}</span>')
        else:
            self.output_text.append(output)
        
        # Auto-scroll to bottom
        scrollbar = self.output_text.verticalScrollBar()
        scrollbar.setValue(scrollbar.maximum())
    
    def on_command_finished(self, exit_code):
        """Handle command completion"""
        # Reset UI
        self.execute_btn.setEnabled(True)
        self.stop_btn.setEnabled(False)
        self.command_input.setEnabled(True)
        
        # Show exit code
        if exit_code == 0:
            self.output_text.append(f'<span style="color: #27ae60;">Command completed successfully (exit code: {exit_code})</span>')
        elif exit_code > 0:
            self.output_text.append(f'<span style="color: #e74c3c;">Command failed (exit code: {exit_code})</span>')
        else:
            self.output_text.append(f'<span style="color: #f39c12;">Command interrupted</span>')
        
        # Clean up worker
        if self.command_worker:
            self.command_worker = None
        
        # Focus back to input
        self.command_input.setFocus()
    
    def closeEvent(self, event):
        """Handle widget close"""
        if self.command_worker:
            self.command_worker.stop_command()
        
        # Handle case where event might be None (called programmatically)
        if event is not None:
            event.accept()