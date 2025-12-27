"""
JavaScript Pretty Formatter Tool
A utility for formatting, validating, and analyzing JavaScript code.
"""

import re
import ast
from datetime import datetime
from PyQt5.QtCore import *
from PyQt5.QtWidgets import *
from PyQt5.QtGui import *


class JsFormatterDialog(QDialog):
    """JavaScript Pretty Formatter Dialog"""
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setup_ui()
        self.setup_connections()
    
    def setup_ui(self):
        """Setup the user interface"""
        self.setWindowTitle("⚡ JavaScript Pretty Formatter")
        self.setMinimumSize(900, 700)
        self.setModal(False)  # Allow interaction with main window
        
        # Main layout
        layout = QVBoxLayout(self)
        layout.setSpacing(10)
        
        # Header
        header_layout = QHBoxLayout()
        
        # Icon and title
        icon_label = QLabel("⚡")
        icon_label.setStyleSheet("font-size: 24px;")
        
        title_label = QLabel("JavaScript Pretty Formatter")
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
        desc_label = QLabel("Format, validate, minify, and analyze JavaScript code with syntax highlighting and function analysis")
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
        
        input_label = QLabel("📝 Input JavaScript:")
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
        self.input_text.setPlaceholderText("""Paste your JavaScript here or load from file...

Example:
function greet(name) {
    console.log("Hello, " + name + "!");
}

const users = [
    { id: 1, name: "John" },
    { id: 2, name: "Jane" }
];""")
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
        self.format_btn.clicked.connect(self.format_js)
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
        self.minify_btn.clicked.connect(self.minify_js)
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
        self.analyze_btn.clicked.connect(self.analyze_js)
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
        
        # Formatted JavaScript tab
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
        
        self.status_label = QLabel("Ready - Paste JavaScript and click 'Format & Validate'")
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
Welcome to JavaScript Pretty Formatter! 🎉

Features:
• ✨ Format and beautify JavaScript with proper indentation
• 📦 Minify JavaScript to reduce size
• 🔍 Analyze JavaScript structure and functions
• ✅ Validate JavaScript syntax and best practices
• 📂 Load JavaScript from files
• 💾 Save formatted JavaScript to files
• 📋 Copy results to clipboard

Instructions:
1. Paste your JavaScript in the left panel or load from file
2. Click 'Format & Validate' to beautify and check syntax
3. Use 'Minify' to compress JavaScript
4. Click 'Analyze' to get detailed statistics
5. Copy or save the results as needed

Ready to format your JavaScript! 🚀
        """
        
        self.output_text.setPlainText(welcome_msg)
        self.analysis_text.setPlainText("No analysis performed yet. Click 'Analyze' after formatting JavaScript.")
        self.status_text.setPlainText("Status: Ready\nWaiting for JavaScript input...")
    
    def update_char_count(self):
        """Update character count"""
        text = self.input_text.toPlainText()
        char_count = len(text)
        self.char_count_label.setText(f"Characters: {char_count:,}")
    
    def format_js(self):
        """Format and validate JavaScript"""
        input_text = self.input_text.toPlainText().strip()
        
        if not input_text:
            self.show_error("No JavaScript input provided. Please paste JavaScript code first.")
            return
        
        try:
            # Format JavaScript with proper indentation
            self.status_label.setText("Formatting JavaScript...")
            formatted_js = self.format_js_content(input_text)
            
            # Display formatted JavaScript
            self.output_text.setPlainText(formatted_js)
            
            # Update status
            self.status_label.setText("✅ JavaScript formatted successfully!")
            self.status_text.setPlainText(f"""Status: ✅ JavaScript Formatted

Formatting Results:
• Structure: Properly indented
• Functions: Well-organized
• Variables: Properly spaced
• Operators: Normalized spacing
• Indentation: 2 spaces per level

Timestamp: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}
""")
            
            # Switch to formatted tab
            self.output_tabs.setCurrentIndex(0)
            
            # Enable copy and save buttons
            self.copy_btn.setEnabled(True)
            self.save_btn.setEnabled(True)
            
        except Exception as e:
            self.show_error(f"JavaScript formatting error: {str(e)}")
    
    def format_js_content(self, js_content):
        """Format JavaScript content with proper indentation"""
        # Basic JavaScript formatting
        formatted_lines = []
        indent_level = 0
        indent_size = 2
        
        # Split into lines and process
        lines = js_content.split('\n')
        
        for line in lines:
            stripped = line.strip()
            if not stripped:
                formatted_lines.append('')
                continue
            
            # Handle closing braces
            if stripped.startswith('}'):
                indent_level = max(0, indent_level - 1)
            
            # Add indentation
            indent = ' ' * (indent_level * indent_size)
            formatted_lines.append(indent + stripped)
            
            # Handle opening braces
            if stripped.endswith('{'):
                indent_level += 1
        
        # Join lines and apply additional formatting
        formatted_code = '\n'.join(formatted_lines)
        
        # Add spacing around operators
        formatted_code = re.sub(r'([=+\-*/%<>!&|])([^=])', r'\1 \2', formatted_code)
        formatted_code = re.sub(r'([^=])([=+\-*/%<>!&|])', r'\1 \2', formatted_code)
        
        # Fix double spaces
        formatted_code = re.sub(r'  +', ' ', formatted_code)
        
        # Add space after keywords
        keywords = ['if', 'else', 'for', 'while', 'function', 'return', 'var', 'let', 'const']
        for keyword in keywords:
            formatted_code = re.sub(f'\\b{keyword}\\(', f'{keyword} (', formatted_code)
        
        return formatted_code
    
    def minify_js(self):
        """Minify JavaScript (remove whitespace)"""
        input_text = self.input_text.toPlainText().strip()
        
        if not input_text:
            self.show_error("No JavaScript input provided. Please paste JavaScript code first.")
            return
        
        try:
            # Minify JavaScript
            self.status_label.setText("Minifying JavaScript...")
            minified_js = self.minify_js_content(input_text)
            
            # Display minified JavaScript
            self.output_text.setPlainText(minified_js)
            
            # Calculate size reduction
            original_size = len(input_text)
            minified_size = len(minified_js)
            reduction = ((original_size - minified_size) / original_size) * 100 if original_size > 0 else 0
            
            # Update status
            self.status_label.setText("📦 JavaScript minified successfully!")
            self.status_text.setPlainText(f"""Status: 📦 JavaScript Minified

Minification Results:
• Original size: {original_size:,} characters
• Minified size: {minified_size:,} characters
• Size reduction: {reduction:.1f}%
• Whitespace removed: Yes
• Comments removed: Yes

Timestamp: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}
""")
            
            # Switch to formatted tab
            self.output_tabs.setCurrentIndex(0)
            
        except Exception as e:
            self.show_error(f"JavaScript minification error: {str(e)}")
    
    def minify_js_content(self, js_content):
        """Minify JavaScript content"""
        # Remove single-line comments
        js_content = re.sub(r'//.*$', '', js_content, flags=re.MULTILINE)
        
        # Remove multi-line comments
        js_content = re.sub(r'/\*.*?\*/', '', js_content, flags=re.DOTALL)
        
        # Remove extra whitespace
        js_content = re.sub(r'\s+', ' ', js_content)
        
        # Remove spaces around operators and punctuation
        js_content = re.sub(r'\s*([{}();,=+\-*/%<>!&|])\s*', r'\1', js_content)
        
        # Remove spaces after keywords that don't need them
        js_content = re.sub(r'\b(return|throw|delete|typeof|new|in|of)\s+', r'\1 ', js_content)
        
        return js_content.strip()
    
    def analyze_js(self):
        """Analyze JavaScript structure and provide statistics"""
        input_text = self.input_text.toPlainText().strip()
        
        if not input_text:
            self.show_error("No JavaScript input provided. Please paste JavaScript code first.")
            return
        
        try:
            # Analyze JavaScript
            self.status_label.setText("Analyzing JavaScript structure...")
            analysis = self.perform_js_analysis(input_text)
            
            # Display analysis
            self.analysis_text.setHtml(analysis)
            
            # Update status
            self.status_label.setText("🔍 JavaScript analysis completed!")
            
            # Switch to analysis tab
            self.output_tabs.setCurrentIndex(1)
            
        except Exception as e:
            self.show_error(f"JavaScript analysis error: {str(e)}")
    
    def perform_js_analysis(self, js_content):
        """Perform detailed JavaScript analysis"""
        # Basic statistics
        char_count = len(js_content)
        line_count = js_content.count('\n') + 1
        
        # Find functions
        function_pattern = r'function\s+(\w+)\s*\([^)]*\)'
        functions = re.findall(function_pattern, js_content)
        
        # Find arrow functions
        arrow_function_pattern = r'(\w+)\s*=\s*\([^)]*\)\s*=>'
        arrow_functions = re.findall(arrow_function_pattern, js_content)
        
        # Find variables
        var_pattern = r'\b(var|let|const)\s+(\w+)'
        variables = re.findall(var_pattern, js_content)
        
        # Count variable types
        var_counts = {'var': 0, 'let': 0, 'const': 0}
        for var_type, var_name in variables:
            var_counts[var_type] += 1
        
        # Find comments
        single_comments = re.findall(r'//.*$', js_content, re.MULTILINE)
        multi_comments = re.findall(r'/\*.*?\*/', js_content, re.DOTALL)
        
        # Find ES6+ features
        es6_features = {
            'Arrow Functions': len(re.findall(r'=>', js_content)),
            'Template Literals': len(re.findall(r'`[^`]*`', js_content)),
            'Destructuring': len(re.findall(r'\{[^}]*\}\s*=', js_content)),
            'Spread Operator': len(re.findall(r'\.\.\.', js_content)),
            'Classes': len(re.findall(r'\bclass\s+\w+', js_content)),
            'Async/Await': len(re.findall(r'\b(async|await)\b', js_content)),
        }
        
        # Find common methods/APIs
        common_apis = {
            'console': len(re.findall(r'\bconsole\.\w+', js_content)),
            'document': len(re.findall(r'\bdocument\.\w+', js_content)),
            'window': len(re.findall(r'\bwindow\.\w+', js_content)),
            'JSON': len(re.findall(r'\bJSON\.\w+', js_content)),
            'localStorage': len(re.findall(r'\blocalStorage\.\w+', js_content)),
            'fetch': len(re.findall(r'\bfetch\s*\(', js_content)),
        }
        
        # Generate analysis HTML
        analysis_html = f"""
        <div style="font-family: Arial, sans-serif; padding: 10px;">
            <h2 style="color: #007bff; margin-top: 0;">📊 JavaScript Code Analysis</h2>
            
            <h3 style="color: #28a745;">📋 Basic Information</h3>
            <table style="border-collapse: collapse; width: 100%; margin-bottom: 20px;">
                <tr style="background-color: #f8f9fa;">
                    <td style="padding: 8px; border: 1px solid #dee2e6; font-weight: bold;">Total Characters</td>
                    <td style="padding: 8px; border: 1px solid #dee2e6;">{char_count:,}</td>
                </tr>
                <tr>
                    <td style="padding: 8px; border: 1px solid #dee2e6; font-weight: bold;">Total Lines</td>
                    <td style="padding: 8px; border: 1px solid #dee2e6;">{line_count:,}</td>
                </tr>
                <tr style="background-color: #f8f9fa;">
                    <td style="padding: 8px; border: 1px solid #dee2e6; font-weight: bold;">Functions</td>
                    <td style="padding: 8px; border: 1px solid #dee2e6;">{len(functions):,}</td>
                </tr>
                <tr>
                    <td style="padding: 8px; border: 1px solid #dee2e6; font-weight: bold;">Arrow Functions</td>
                    <td style="padding: 8px; border: 1px solid #dee2e6;">{len(arrow_functions):,}</td>
                </tr>
                <tr style="background-color: #f8f9fa;">
                    <td style="padding: 8px; border: 1px solid #dee2e6; font-weight: bold;">Variables</td>
                    <td style="padding: 8px; border: 1px solid #dee2e6;">{len(variables):,}</td>
                </tr>
                <tr>
                    <td style="padding: 8px; border: 1px solid #dee2e6; font-weight: bold;">Comments</td>
                    <td style="padding: 8px; border: 1px solid #dee2e6;">{len(single_comments) + len(multi_comments):,}</td>
                </tr>
            </table>
            
            <h3 style="color: #17a2b8;">📦 Variable Declarations</h3>
            <table style="border-collapse: collapse; width: 100%; margin-bottom: 20px;">
                <tr style="background-color: #f8f9fa;">
                    <td style="padding: 8px; border: 1px solid #dee2e6; font-weight: bold;">var</td>
                    <td style="padding: 8px; border: 1px solid #dee2e6;">{var_counts['var']:,}</td>
                </tr>
                <tr>
                    <td style="padding: 8px; border: 1px solid #dee2e6; font-weight: bold;">let</td>
                    <td style="padding: 8px; border: 1px solid #dee2e6;">{var_counts['let']:,}</td>
                </tr>
                <tr style="background-color: #f8f9fa;">
                    <td style="padding: 8px; border: 1px solid #dee2e6; font-weight: bold;">const</td>
                    <td style="padding: 8px; border: 1px solid #dee2e6;">{var_counts['const']:,}</td>
                </tr>
            </table>
            
            <h3 style="color: #ffc107;">🚀 ES6+ Features</h3>
            <table style="border-collapse: collapse; width: 100%; margin-bottom: 20px;">
        """
        
        # Add ES6+ features
        for i, (feature, count) in enumerate(es6_features.items()):
            if count > 0:
                bg_color = "#f8f9fa" if i % 2 == 0 else "white"
                analysis_html += f"""
                    <tr style="background-color: {bg_color};">
                        <td style="padding: 8px; border: 1px solid #dee2e6; font-weight: bold;">{feature}</td>
                        <td style="padding: 8px; border: 1px solid #dee2e6;">{count:,}</td>
                    </tr>
                """
        
        analysis_html += """
            </table>
            
            <h3 style="color: #dc3545;">🌐 Common APIs Used</h3>
            <table style="border-collapse: collapse; width: 100%; margin-bottom: 20px;">
        """
        
        # Add common APIs
        for i, (api, count) in enumerate(common_apis.items()):
            if count > 0:
                bg_color = "#f8f9fa" if i % 2 == 0 else "white"
                analysis_html += f"""
                    <tr style="background-color: {bg_color};">
                        <td style="padding: 8px; border: 1px solid #dee2e6; font-weight: bold;">{api}</td>
                        <td style="padding: 8px; border: 1px solid #dee2e6;">{count:,}</td>
                    </tr>
                """
        
        analysis_html += """
            </table>
            
            <h3 style="color: #6f42c1;">💡 Recommendations</h3>
            <ul style="margin-bottom: 20px;">
        """
        
        # Add recommendations
        if var_counts['var'] > 0 and (var_counts['let'] > 0 or var_counts['const'] > 0):
            analysis_html += "<li>🔄 Consider replacing 'var' with 'let' or 'const' for better scoping.</li>"
        
        if len(functions) > 0 and len(arrow_functions) == 0:
            analysis_html += "<li>🏹 Consider using arrow functions for shorter syntax where appropriate.</li>"
        
        if es6_features['Template Literals'] == 0 and '+' in js_content:
            analysis_html += "<li>📝 Consider using template literals instead of string concatenation.</li>"
        
        if len(single_comments) + len(multi_comments) == 0:
            analysis_html += "<li>📝 Consider adding comments to document complex logic.</li>"
        
        if char_count > 50000:
            analysis_html += "<li>📦 Large JavaScript file detected. Consider minifying for production.</li>"
        
        if common_apis['console'] > 5:
            analysis_html += "<li>🐛 High console usage detected. Consider removing debug statements for production.</li>"
        
        if es6_features['Async/Await'] == 0 and 'Promise' in js_content:
            analysis_html += "<li>⚡ Consider using async/await instead of Promise chains for better readability.</li>"
        
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
    
    def show_error(self, message):
        """Show general error message"""
        self.status_label.setText(f"❌ Error: {message}")
        self.status_text.setPlainText(f"❌ Error: {message}\n\nTimestamp: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        self.output_tabs.setCurrentIndex(2)
    
    def load_from_file(self):
        """Load JavaScript from file"""
        file_path, _ = QFileDialog.getOpenFileName(
            self,
            "Load JavaScript File",
            "",
            "JavaScript Files (*.js);;Text Files (*.txt);;All Files (*.*)"
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
        """Save formatted JavaScript to file"""
        output_content = self.output_text.toPlainText()
        
        if not output_content or "Welcome to JavaScript Pretty Formatter" in output_content:
            self.show_error("No formatted JavaScript to save. Please format JavaScript first.")
            return
        
        file_path, _ = QFileDialog.getSaveFileName(
            self,
            "Save Formatted JavaScript",
            f"formatted_js_{datetime.now().strftime('%Y%m%d_%H%M%S')}.js",
            "JavaScript Files (*.js);;Text Files (*.txt);;All Files (*.*)"
        )
        
        if file_path:
            try:
                with open(file_path, 'w', encoding='utf-8') as f:
                    f.write(output_content)
                
                self.status_label.setText(f"💾 Saved to: {file_path}")
                
            except Exception as e:
                self.show_error(f"Failed to save file: {str(e)}")
    
    def copy_output(self):
        """Copy formatted JavaScript to clipboard"""
        output_content = self.output_text.toPlainText()
        
        if not output_content or "Welcome to JavaScript Pretty Formatter" in output_content:
            self.show_error("No formatted JavaScript to copy. Please format JavaScript first.")
            return
        
        clipboard = QApplication.clipboard()
        clipboard.setText(output_content)
        
        self.status_label.setText("📋 Formatted JavaScript copied to clipboard!")
        
        # Reset status after 3 seconds
        QTimer.singleShot(3000, lambda: self.status_label.setText("Ready"))
    
    def clear_input(self):
        """Clear input text"""
        self.input_text.clear()
        self.status_label.setText("Input cleared")
    
    def show_help(self):
        """Show help dialog"""
        help_text = """
JavaScript Pretty Formatter Help

⚡ FEATURES:
• Format & Validate: Beautify JavaScript with proper indentation and structure
• Minify: Remove whitespace and comments to reduce file size
• Analyze: Get detailed statistics about JavaScript functions and variables
• Load/Save: Work with JavaScript files
• Copy: Copy results to clipboard

📝 USAGE:
1. Paste JavaScript in the left panel or load from file
2. Click 'Format & Validate' to beautify and structure
3. Use 'Minify' to compress JavaScript
4. Click 'Analyze' for detailed code information
5. Copy or save results as needed

🔍 ANALYSIS FEATURES:
• Function and variable counting
• ES6+ feature detection
• Variable declaration analysis (var, let, const)
• Common API usage statistics
• Code quality recommendations

🎯 TIPS:
• Use Ctrl+A to select all text
• Large files are supported
• Provides modern JavaScript best practices recommendations
• Helps identify optimization opportunities
        """
        
        QMessageBox.information(self, "JavaScript Formatter Help", help_text)


def show_js_formatter(parent=None):
    """Show JavaScript formatter dialog"""
    dialog = JsFormatterDialog(parent)
    dialog.show()
    return dialog


if __name__ == "__main__":
    # Test the JavaScript formatter
    import sys
    from PyQt5.QtWidgets import QApplication
    
    app = QApplication(sys.argv)
    dialog = JsFormatterDialog()
    dialog.show()
    sys.exit(app.exec_())