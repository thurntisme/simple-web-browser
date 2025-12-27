"""
JSON Pretty Formatter Tool
A utility for formatting, validating, and manipulating JSON data.
"""

import json
import re
from datetime import datetime
from PyQt5.QtCore import *
from PyQt5.QtWidgets import *
from PyQt5.QtGui import *


class JsonFormatterDialog(QDialog):
    """JSON Pretty Formatter Dialog"""
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setup_ui()
        self.setup_connections()
    
    def setup_ui(self):
        """Setup the user interface"""
        self.setWindowTitle("🔧 JSON Pretty Formatter")
        self.setMinimumSize(900, 700)
        self.setModal(False)  # Allow interaction with main window
        
        # Main layout
        layout = QVBoxLayout(self)
        layout.setSpacing(10)
        
        # Header
        header_layout = QHBoxLayout()
        
        # Icon and title
        icon_label = QLabel("🔧")
        icon_label.setStyleSheet("font-size: 24px;")
        
        title_label = QLabel("JSON Pretty Formatter")
        title_label.setStyleSheet("""
            font-size: 18px;
            font-weight: bold;
            color: #2c3e50;
            margin-left: 10px;
        """)
        
        header_layout.addWidget(icon_label)
        header_layout.addWidget(title_label)
        header_layout.addStretch()
        
        # Help button
        help_btn = QPushButton("❓ Help")
        help_btn.setMaximumWidth(80)
        help_btn.clicked.connect(self.show_help)
        help_btn.setStyleSheet("""
            QPushButton {
                background-color: #17a2b8;
                color: white;
                border: none;
                border-radius: 4px;
                padding: 6px 12px;
                font-weight: bold;
            }
            QPushButton:hover {
                background-color: #138496;
            }
        """)
        header_layout.addWidget(help_btn)
        
        layout.addLayout(header_layout)
        
        # Description
        desc_label = QLabel("Format, validate, minify, and analyze JSON data with syntax highlighting and error detection")
        desc_label.setStyleSheet("""
            color: #6c757d;
            font-style: italic;
            margin-left: 34px;
            margin-bottom: 10px;
        """)
        layout.addWidget(desc_label)
        
        # Main content area with splitter
        splitter = QSplitter(Qt.Horizontal)
        
        # Left panel - Input
        left_panel = QWidget()
        left_layout = QVBoxLayout(left_panel)
        left_layout.setContentsMargins(0, 0, 5, 0)
        
        # Input controls
        input_controls = QHBoxLayout()
        
        input_label = QLabel("📝 Input JSON:")
        input_label.setStyleSheet("font-weight: bold; color: #495057;")
        input_controls.addWidget(input_label)
        
        input_controls.addStretch()
        
        # Load from file button
        self.load_btn = QPushButton("📂 Load File")
        self.load_btn.setMaximumWidth(100)
        self.load_btn.clicked.connect(self.load_from_file)
        self.load_btn.setStyleSheet("""
            QPushButton {
                background-color: #6c757d;
                color: white;
                border: none;
                border-radius: 4px;
                padding: 6px 12px;
                font-weight: bold;
            }
            QPushButton:hover {
                background-color: #5a6268;
            }
        """)
        input_controls.addWidget(self.load_btn)
        
        # Clear input button
        self.clear_input_btn = QPushButton("🗑️ Clear")
        self.clear_input_btn.setMaximumWidth(80)
        self.clear_input_btn.clicked.connect(self.clear_input)
        self.clear_input_btn.setStyleSheet("""
            QPushButton {
                background-color: #dc3545;
                color: white;
                border: none;
                border-radius: 4px;
                padding: 6px 12px;
                font-weight: bold;
            }
            QPushButton:hover {
                background-color: #c82333;
            }
        """)
        input_controls.addWidget(self.clear_input_btn)
        
        left_layout.addLayout(input_controls)
        
        # Input text area
        self.input_text = QTextEdit()
        self.input_text.setPlaceholderText("""Paste your JSON here or load from file...

Example:
{"name": "John", "age": 30, "city": "New York", "hobbies": ["reading", "coding"]}""")
        self.input_text.setStyleSheet("""
            QTextEdit {
                border: 2px solid #dee2e6;
                border-radius: 6px;
                padding: 10px;
                font-family: 'Courier New', monospace;
                font-size: 12px;
                background-color: #f8f9fa;
            }
            QTextEdit:focus {
                border-color: #007bff;
                background-color: white;
            }
        """)
        left_layout.addWidget(self.input_text)
        
        # Action buttons
        action_layout = QHBoxLayout()
        
        self.format_btn = QPushButton("✨ Format & Validate")
        self.format_btn.clicked.connect(self.format_json)
        self.format_btn.setStyleSheet("""
            QPushButton {
                background-color: #28a745;
                color: white;
                border: none;
                border-radius: 6px;
                padding: 10px 20px;
                font-size: 14px;
                font-weight: bold;
            }
            QPushButton:hover {
                background-color: #218838;
            }
            QPushButton:pressed {
                background-color: #1e7e34;
            }
        """)
        action_layout.addWidget(self.format_btn)
        
        self.minify_btn = QPushButton("📦 Minify")
        self.minify_btn.clicked.connect(self.minify_json)
        self.minify_btn.setStyleSheet("""
            QPushButton {
                background-color: #ffc107;
                color: #212529;
                border: none;
                border-radius: 6px;
                padding: 10px 20px;
                font-size: 14px;
                font-weight: bold;
            }
            QPushButton:hover {
                background-color: #e0a800;
            }
            QPushButton:pressed {
                background-color: #d39e00;
            }
        """)
        action_layout.addWidget(self.minify_btn)
        
        self.analyze_btn = QPushButton("🔍 Analyze")
        self.analyze_btn.clicked.connect(self.analyze_json)
        self.analyze_btn.setStyleSheet("""
            QPushButton {
                background-color: #17a2b8;
                color: white;
                border: none;
                border-radius: 6px;
                padding: 10px 20px;
                font-size: 14px;
                font-weight: bold;
            }
            QPushButton:hover {
                background-color: #138496;
            }
            QPushButton:pressed {
                background-color: #117a8b;
            }
        """)
        action_layout.addWidget(self.analyze_btn)
        
        left_layout.addLayout(action_layout)
        
        splitter.addWidget(left_panel)
        
        # Right panel - Output and Analysis
        right_panel = QWidget()
        right_layout = QVBoxLayout(right_panel)
        right_layout.setContentsMargins(5, 0, 0, 0)
        
        # Output tabs
        self.output_tabs = QTabWidget()
        self.output_tabs.setStyleSheet("""
            QTabWidget::pane {
                border: 2px solid #dee2e6;
                border-radius: 6px;
                background-color: white;
            }
            QTabBar::tab {
                background-color: #e9ecef;
                padding: 8px 16px;
                margin-right: 2px;
                border-top-left-radius: 6px;
                border-top-right-radius: 6px;
                font-weight: bold;
            }
            QTabBar::tab:selected {
                background-color: #007bff;
                color: white;
            }
            QTabBar::tab:hover:!selected {
                background-color: #f8f9fa;
            }
        """)
        
        # Formatted JSON tab
        self.formatted_tab = QWidget()
        formatted_layout = QVBoxLayout(self.formatted_tab)
        
        # Output controls
        output_controls = QHBoxLayout()
        
        output_label = QLabel("📄 Formatted Output:")
        output_label.setStyleSheet("font-weight: bold; color: #495057;")
        output_controls.addWidget(output_label)
        
        output_controls.addStretch()
        
        # Copy button
        self.copy_btn = QPushButton("📋 Copy")
        self.copy_btn.setMaximumWidth(80)
        self.copy_btn.clicked.connect(self.copy_output)
        self.copy_btn.setStyleSheet("""
            QPushButton {
                background-color: #6f42c1;
                color: white;
                border: none;
                border-radius: 4px;
                padding: 6px 12px;
                font-weight: bold;
            }
            QPushButton:hover {
                background-color: #5a32a3;
            }
        """)
        output_controls.addWidget(self.copy_btn)
        
        # Save button
        self.save_btn = QPushButton("💾 Save")
        self.save_btn.setMaximumWidth(80)
        self.save_btn.clicked.connect(self.save_to_file)
        self.save_btn.setStyleSheet("""
            QPushButton {
                background-color: #fd7e14;
                color: white;
                border: none;
                border-radius: 4px;
                padding: 6px 12px;
                font-weight: bold;
            }
            QPushButton:hover {
                background-color: #e8650e;
            }
        """)
        output_controls.addWidget(self.save_btn)
        
        formatted_layout.addLayout(output_controls)
        
        # Output text area
        self.output_text = QTextEdit()
        self.output_text.setReadOnly(True)
        self.output_text.setStyleSheet("""
            QTextEdit {
                border: 1px solid #dee2e6;
                border-radius: 4px;
                padding: 10px;
                font-family: 'Courier New', monospace;
                font-size: 12px;
                background-color: #f8f9fa;
            }
        """)
        formatted_layout.addWidget(self.output_text)
        
        self.output_tabs.addTab(self.formatted_tab, "📄 Formatted")
        
        # Analysis tab
        self.analysis_tab = QWidget()
        analysis_layout = QVBoxLayout(self.analysis_tab)
        
        self.analysis_text = QTextEdit()
        self.analysis_text.setReadOnly(True)
        self.analysis_text.setStyleSheet("""
            QTextEdit {
                border: 1px solid #dee2e6;
                border-radius: 4px;
                padding: 10px;
                font-family: Arial, sans-serif;
                font-size: 12px;
                background-color: #f8f9fa;
            }
        """)
        analysis_layout.addWidget(self.analysis_text)
        
        self.output_tabs.addTab(self.analysis_tab, "🔍 Analysis")
        
        # Error/Status tab
        self.status_tab = QWidget()
        status_layout = QVBoxLayout(self.status_tab)
        
        self.status_text = QTextEdit()
        self.status_text.setReadOnly(True)
        self.status_text.setStyleSheet("""
            QTextEdit {
                border: 1px solid #dee2e6;
                border-radius: 4px;
                padding: 10px;
                font-family: 'Courier New', monospace;
                font-size: 12px;
                background-color: #f8f9fa;
            }
        """)
        status_layout.addWidget(self.status_text)
        
        self.output_tabs.addTab(self.status_tab, "⚠️ Status")
        
        right_layout.addWidget(self.output_tabs)
        
        splitter.addWidget(right_panel)
        
        # Set splitter proportions
        splitter.setStretchFactor(0, 1)  # Left panel
        splitter.setStretchFactor(1, 1)  # Right panel
        
        layout.addWidget(splitter)
        
        # Status bar
        status_layout = QHBoxLayout()
        
        self.status_label = QLabel("Ready - Paste JSON and click 'Format & Validate'")
        self.status_label.setStyleSheet("""
            color: #6c757d;
            font-weight: bold;
            padding: 5px;
        """)
        status_layout.addWidget(self.status_label)
        
        status_layout.addStretch()
        
        # Character count
        self.char_count_label = QLabel("Characters: 0")
        self.char_count_label.setStyleSheet("color: #6c757d; font-size: 11px;")
        status_layout.addWidget(self.char_count_label)
        
        layout.addLayout(status_layout)
        
        # Initialize with welcome message
        self.show_welcome_message()
    
    def setup_connections(self):
        """Setup signal connections"""
        self.input_text.textChanged.connect(self.update_char_count)
    
    def show_welcome_message(self):
        """Show welcome message in the output"""
        welcome_msg = """
Welcome to JSON Pretty Formatter! 🎉

Features:
• ✨ Format and beautify JSON with proper indentation
• 📦 Minify JSON to reduce size
• 🔍 Analyze JSON structure and statistics
• ✅ Validate JSON syntax with detailed error messages
• 📂 Load JSON from files
• 💾 Save formatted JSON to files
• 📋 Copy results to clipboard

Instructions:
1. Paste your JSON in the left panel or load from file
2. Click 'Format & Validate' to beautify and check syntax
3. Use 'Minify' to compress JSON
4. Click 'Analyze' to get detailed statistics
5. Copy or save the results as needed

Ready to format your JSON! 🚀
        """
        
        self.output_text.setPlainText(welcome_msg)
        self.analysis_text.setPlainText("No analysis performed yet. Click 'Analyze' after formatting JSON.")
        self.status_text.setPlainText("Status: Ready\nWaiting for JSON input...")
    
    def update_char_count(self):
        """Update character count"""
        text = self.input_text.toPlainText()
        char_count = len(text)
        self.char_count_label.setText(f"Characters: {char_count:,}")
    
    def format_json(self):
        """Format and validate JSON"""
        input_text = self.input_text.toPlainText().strip()
        
        if not input_text:
            self.show_error("No JSON input provided. Please paste JSON data first.")
            return
        
        try:
            # Parse JSON
            self.status_label.setText("Parsing JSON...")
            parsed_json = json.loads(input_text)
            
            # Format with indentation
            formatted_json = json.dumps(parsed_json, indent=2, ensure_ascii=False, sort_keys=False)
            
            # Display formatted JSON
            self.output_text.setPlainText(formatted_json)
            
            # Update status
            self.status_label.setText("✅ JSON formatted successfully!")
            self.status_text.setPlainText(f"""Status: ✅ Valid JSON

Validation Results:
• Syntax: Valid
• Parsed successfully: Yes
• Formatted with 2-space indentation
• Key order: Preserved (original order)
• Unicode characters preserved

Timestamp: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}
""")
            
            # Switch to formatted tab
            self.output_tabs.setCurrentIndex(0)
            
            # Enable copy and save buttons
            self.copy_btn.setEnabled(True)
            self.save_btn.setEnabled(True)
            
        except json.JSONDecodeError as e:
            self.show_json_error(e, input_text)
        except Exception as e:
            self.show_error(f"Unexpected error: {str(e)}")
    
    def minify_json(self):
        """Minify JSON (remove whitespace)"""
        input_text = self.input_text.toPlainText().strip()
        
        if not input_text:
            self.show_error("No JSON input provided. Please paste JSON data first.")
            return
        
        try:
            # Parse and minify
            self.status_label.setText("Minifying JSON...")
            parsed_json = json.loads(input_text)
            minified_json = json.dumps(parsed_json, separators=(',', ':'), ensure_ascii=False)
            
            # Display minified JSON
            self.output_text.setPlainText(minified_json)
            
            # Calculate size reduction
            original_size = len(input_text)
            minified_size = len(minified_json)
            reduction = ((original_size - minified_size) / original_size) * 100 if original_size > 0 else 0
            
            # Update status
            self.status_label.setText("📦 JSON minified successfully!")
            self.status_text.setPlainText(f"""Status: 📦 JSON Minified

Minification Results:
• Original size: {original_size:,} characters
• Minified size: {minified_size:,} characters
• Size reduction: {reduction:.1f}%
• Whitespace removed: Yes
• Separators optimized: Yes

Timestamp: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}
""")
            
            # Switch to formatted tab
            self.output_tabs.setCurrentIndex(0)
            
        except json.JSONDecodeError as e:
            self.show_json_error(e, input_text)
        except Exception as e:
            self.show_error(f"Unexpected error: {str(e)}")
    
    def analyze_json(self):
        """Analyze JSON structure and provide statistics"""
        input_text = self.input_text.toPlainText().strip()
        
        if not input_text:
            self.show_error("No JSON input provided. Please paste JSON data first.")
            return
        
        try:
            # Parse JSON
            self.status_label.setText("Analyzing JSON structure...")
            parsed_json = json.loads(input_text)
            
            # Perform analysis
            analysis = self.perform_json_analysis(parsed_json, input_text)
            
            # Display analysis
            self.analysis_text.setHtml(analysis)
            
            # Update status
            self.status_label.setText("🔍 JSON analysis completed!")
            
            # Switch to analysis tab
            self.output_tabs.setCurrentIndex(1)
            
        except json.JSONDecodeError as e:
            self.show_json_error(e, input_text)
        except Exception as e:
            self.show_error(f"Unexpected error during analysis: {str(e)}")
    
    def perform_json_analysis(self, data, original_text):
        """Perform detailed JSON analysis"""
        def count_elements(obj, counts=None):
            if counts is None:
                counts = {'objects': 0, 'arrays': 0, 'strings': 0, 'numbers': 0, 
                         'booleans': 0, 'nulls': 0, 'total_keys': 0, 'max_depth': 0}
            
            def analyze_recursive(item, depth=0):
                counts['max_depth'] = max(counts['max_depth'], depth)
                
                if isinstance(item, dict):
                    counts['objects'] += 1
                    counts['total_keys'] += len(item)
                    for key, value in item.items():
                        analyze_recursive(value, depth + 1)
                elif isinstance(item, list):
                    counts['arrays'] += 1
                    for value in item:
                        analyze_recursive(value, depth + 1)
                elif isinstance(item, str):
                    counts['strings'] += 1
                elif isinstance(item, (int, float)):
                    counts['numbers'] += 1
                elif isinstance(item, bool):
                    counts['booleans'] += 1
                elif item is None:
                    counts['nulls'] += 1
            
            analyze_recursive(obj)
            return counts
        
        # Get statistics
        stats = count_elements(data)
        
        # Character analysis
        char_count = len(original_text)
        line_count = original_text.count('\n') + 1
        
        # Root type
        root_type = type(data).__name__
        if isinstance(data, dict):
            root_type = "Object"
        elif isinstance(data, list):
            root_type = "Array"
        
        # Generate analysis HTML
        analysis_html = f"""
        <div style="font-family: Arial, sans-serif; padding: 10px;">
            <h2 style="color: #007bff; margin-top: 0;">📊 JSON Structure Analysis</h2>
            
            <h3 style="color: #28a745;">📋 Basic Information</h3>
            <table style="border-collapse: collapse; width: 100%; margin-bottom: 20px;">
                <tr style="background-color: #f8f9fa;">
                    <td style="padding: 8px; border: 1px solid #dee2e6; font-weight: bold;">Root Type</td>
                    <td style="padding: 8px; border: 1px solid #dee2e6;">{root_type}</td>
                </tr>
                <tr>
                    <td style="padding: 8px; border: 1px solid #dee2e6; font-weight: bold;">Total Characters</td>
                    <td style="padding: 8px; border: 1px solid #dee2e6;">{char_count:,}</td>
                </tr>
                <tr style="background-color: #f8f9fa;">
                    <td style="padding: 8px; border: 1px solid #dee2e6; font-weight: bold;">Total Lines</td>
                    <td style="padding: 8px; border: 1px solid #dee2e6;">{line_count:,}</td>
                </tr>
                <tr>
                    <td style="padding: 8px; border: 1px solid #dee2e6; font-weight: bold;">Maximum Depth</td>
                    <td style="padding: 8px; border: 1px solid #dee2e6;">{stats['max_depth']}</td>
                </tr>
            </table>
            
            <h3 style="color: #17a2b8;">🔢 Element Count</h3>
            <table style="border-collapse: collapse; width: 100%; margin-bottom: 20px;">
                <tr style="background-color: #f8f9fa;">
                    <td style="padding: 8px; border: 1px solid #dee2e6; font-weight: bold;">Objects</td>
                    <td style="padding: 8px; border: 1px solid #dee2e6;">{stats['objects']:,}</td>
                </tr>
                <tr>
                    <td style="padding: 8px; border: 1px solid #dee2e6; font-weight: bold;">Arrays</td>
                    <td style="padding: 8px; border: 1px solid #dee2e6;">{stats['arrays']:,}</td>
                </tr>
                <tr style="background-color: #f8f9fa;">
                    <td style="padding: 8px; border: 1px solid #dee2e6; font-weight: bold;">Strings</td>
                    <td style="padding: 8px; border: 1px solid #dee2e6;">{stats['strings']:,}</td>
                </tr>
                <tr>
                    <td style="padding: 8px; border: 1px solid #dee2e6; font-weight: bold;">Numbers</td>
                    <td style="padding: 8px; border: 1px solid #dee2e6;">{stats['numbers']:,}</td>
                </tr>
                <tr style="background-color: #f8f9fa;">
                    <td style="padding: 8px; border: 1px solid #dee2e6; font-weight: bold;">Booleans</td>
                    <td style="padding: 8px; border: 1px solid #dee2e6;">{stats['booleans']:,}</td>
                </tr>
                <tr>
                    <td style="padding: 8px; border: 1px solid #dee2e6; font-weight: bold;">Null Values</td>
                    <td style="padding: 8px; border: 1px solid #dee2e6;">{stats['nulls']:,}</td>
                </tr>
                <tr style="background-color: #e9ecef;">
                    <td style="padding: 8px; border: 1px solid #dee2e6; font-weight: bold;">Total Keys</td>
                    <td style="padding: 8px; border: 1px solid #dee2e6; font-weight: bold;">{stats['total_keys']:,}</td>
                </tr>
            </table>
            
            <h3 style="color: #ffc107;">💡 Recommendations</h3>
            <ul style="margin-bottom: 20px;">
        """
        
        # Add recommendations based on analysis
        total_elements = sum([stats['objects'], stats['arrays'], stats['strings'], 
                             stats['numbers'], stats['booleans'], stats['nulls']])
        
        if stats['max_depth'] > 10:
            analysis_html += "<li>⚠️ Deep nesting detected (>10 levels). Consider flattening structure for better performance.</li>"
        
        if char_count > 100000:
            analysis_html += "<li>📦 Large JSON detected. Consider minifying for production use.</li>"
        
        if stats['objects'] > stats['arrays'] * 3:
            analysis_html += "<li>🏗️ Object-heavy structure. Good for key-value data representation.</li>"
        elif stats['arrays'] > stats['objects'] * 3:
            analysis_html += "<li>📋 Array-heavy structure. Good for list-based data.</li>"
        else:
            analysis_html += "<li>⚖️ Balanced object/array structure. Well-organized data.</li>"
        
        if stats['strings'] > total_elements * 0.7:
            analysis_html += "<li>📝 String-heavy data. Consider data type optimization if applicable.</li>"
        
        if stats['nulls'] > total_elements * 0.2:
            analysis_html += "<li>❓ High null value count. Consider removing unnecessary null fields.</li>"
        
        analysis_html += f"""
            </ul>
            
            <div style="background-color: #e9ecef; padding: 10px; border-radius: 4px; margin-top: 20px;">
                <small style="color: #6c757d;">
                    Analysis completed at {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}
                </small>
            </div>
        </div>
        """
        
        return analysis_html
    
    def show_json_error(self, error, input_text):
        """Show detailed JSON error information"""
        error_msg = str(error)
        line_num = getattr(error, 'lineno', 0)
        col_num = getattr(error, 'colno', 0)
        
        # Try to show context around error
        lines = input_text.split('\n')
        context = ""
        
        if line_num > 0 and line_num <= len(lines):
            start_line = max(0, line_num - 3)
            end_line = min(len(lines), line_num + 2)
            
            context = "\nContext around error:\n"
            for i in range(start_line, end_line):
                line_indicator = ">>> " if i == line_num - 1 else "    "
                context += f"{line_indicator}{i+1:3d}: {lines[i]}\n"
                if i == line_num - 1 and col_num > 0:
                    context += f"    {' ' * (col_num + 3)}^\n"
        
        error_details = f"""❌ JSON Syntax Error

Error: {error_msg}
Line: {line_num}
Column: {col_num}

{context}

Common JSON Issues:
• Missing quotes around strings
• Trailing commas in objects/arrays
• Single quotes instead of double quotes
• Unescaped special characters
• Missing closing brackets/braces

Timestamp: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}
"""
        
        self.status_text.setPlainText(error_details)
        self.output_text.setPlainText("❌ Invalid JSON - Check Status tab for details")
        self.status_label.setText("❌ JSON validation failed - Check Status tab")
        
        # Switch to status tab
        self.output_tabs.setCurrentIndex(2)
    
    def show_error(self, message):
        """Show general error message"""
        self.status_label.setText(f"❌ Error: {message}")
        self.status_text.setPlainText(f"❌ Error: {message}\n\nTimestamp: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        self.output_tabs.setCurrentIndex(2)
    
    def load_from_file(self):
        """Load JSON from file"""
        file_path, _ = QFileDialog.getOpenFileName(
            self,
            "Load JSON File",
            "",
            "JSON Files (*.json);;Text Files (*.txt);;All Files (*.*)"
        )
        
        if file_path:
            try:
                with open(file_path, 'r', encoding='utf-8') as f:
                    content = f.read()
                
                self.input_text.setPlainText(content)
                self.status_label.setText(f"📂 Loaded file: {file_path}")
                
            except Exception as e:
                self.show_error(f"Failed to load file: {str(e)}")
    
    def save_to_file(self):
        """Save formatted JSON to file"""
        output_content = self.output_text.toPlainText()
        
        if not output_content or "Welcome to JSON Pretty Formatter" in output_content:
            self.show_error("No formatted JSON to save. Please format JSON first.")
            return
        
        file_path, _ = QFileDialog.getSaveFileName(
            self,
            "Save Formatted JSON",
            f"formatted_json_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json",
            "JSON Files (*.json);;Text Files (*.txt);;All Files (*.*)"
        )
        
        if file_path:
            try:
                with open(file_path, 'w', encoding='utf-8') as f:
                    f.write(output_content)
                
                self.status_label.setText(f"💾 Saved to: {file_path}")
                
            except Exception as e:
                self.show_error(f"Failed to save file: {str(e)}")
    
    def copy_output(self):
        """Copy formatted JSON to clipboard"""
        output_content = self.output_text.toPlainText()
        
        if not output_content or "Welcome to JSON Pretty Formatter" in output_content:
            self.show_error("No formatted JSON to copy. Please format JSON first.")
            return
        
        clipboard = QApplication.clipboard()
        clipboard.setText(output_content)
        
        self.status_label.setText("📋 Formatted JSON copied to clipboard!")
        
        # Reset status after 3 seconds
        QTimer.singleShot(3000, lambda: self.status_label.setText("Ready"))
    
    def clear_input(self):
        """Clear input text"""
        self.input_text.clear()
        self.status_label.setText("Input cleared")
    
    def show_help(self):
        """Show help dialog"""
        help_text = """
JSON Pretty Formatter Help

🔧 FEATURES:
• Format & Validate: Beautify JSON with proper indentation and validate syntax
• Minify: Remove whitespace to reduce file size
• Analyze: Get detailed statistics about JSON structure
• Load/Save: Work with JSON files
• Copy: Copy results to clipboard

📝 USAGE:
1. Paste JSON in the left panel or load from file
2. Click 'Format & Validate' to check and beautify
3. Use 'Minify' to compress JSON
4. Click 'Analyze' for detailed structure information
5. Copy or save results as needed

⚠️ ERROR HANDLING:
• Detailed error messages with line/column numbers
• Context display around syntax errors
• Common error explanations and fixes

🎯 TIPS:
• Use Ctrl+A to select all text
• Large files are supported
• Unicode characters are preserved
• Original key order is maintained in formatted output

📊 ANALYSIS FEATURES:
• Element counting (objects, arrays, strings, etc.)
• Nesting depth analysis
• Size optimization recommendations
• Structure type identification
        """
        
        QMessageBox.information(self, "JSON Formatter Help", help_text)


def show_json_formatter(parent=None):
    """Show JSON formatter dialog"""
    dialog = JsonFormatterDialog(parent)
    dialog.show()
    return dialog


if __name__ == "__main__":
    # Test the JSON formatter
    import sys
    from PyQt5.QtWidgets import QApplication
    
    app = QApplication(sys.argv)
    dialog = JsonFormatterDialog()
    dialog.show()
    sys.exit(app.exec_())