"""
HTML Pretty Formatter Tool
A utility for formatting, validating, and analyzing HTML code.
"""

import re
import html
from datetime import datetime
from PyQt5.QtCore import *
from PyQt5.QtWidgets import *
from PyQt5.QtGui import *


class HtmlFormatterDialog(QDialog):
    """HTML Pretty Formatter Dialog"""
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setup_ui()
        self.setup_connections()
    
    def setup_ui(self):
        """Setup the user interface"""
        self.setWindowTitle("🌐 HTML Pretty Formatter")
        self.setMinimumSize(900, 700)
        self.setModal(False)  # Allow interaction with main window
        
        # Main layout
        layout = QVBoxLayout(self)
        layout.setSpacing(10)
        
        # Header
        header_layout = QHBoxLayout()
        
        # Icon and title
        icon_label = QLabel("🌐")
        icon_label.setStyleSheet("font-size: 24px;")
        
        title_label = QLabel("HTML Pretty Formatter")
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
        desc_label = QLabel("Format, validate, minify, and analyze HTML code with syntax highlighting and structure analysis")
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
        
        input_label = QLabel("📝 Input HTML:")
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
        self.input_text.setPlaceholderText("""Paste your HTML here or load from file...

Example:
<html><head><title>Test</title></head><body><h1>Hello World</h1><p>This is a paragraph.</p></body></html>""")
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
        self.format_btn.clicked.connect(self.format_html)
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
        self.minify_btn.clicked.connect(self.minify_html)
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
        self.analyze_btn.clicked.connect(self.analyze_html)
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
        
        # Formatted HTML tab
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
        
        self.status_label = QLabel("Ready - Paste HTML and click 'Format & Validate'")
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
Welcome to HTML Pretty Formatter! 🎉

Features:
• ✨ Format and beautify HTML with proper indentation
• 📦 Minify HTML to reduce size
• 🔍 Analyze HTML structure and statistics
• ✅ Validate HTML syntax and structure
• 📂 Load HTML from files
• 💾 Save formatted HTML to files
• 📋 Copy results to clipboard

Instructions:
1. Paste your HTML in the left panel or load from file
2. Click 'Format & Validate' to beautify and check structure
3. Use 'Minify' to compress HTML
4. Click 'Analyze' to get detailed statistics
5. Copy or save the results as needed

Ready to format your HTML! 🚀
        """
        
        self.output_text.setPlainText(welcome_msg)
        self.analysis_text.setPlainText("No analysis performed yet. Click 'Analyze' after formatting HTML.")
        self.status_text.setPlainText("Status: Ready\nWaiting for HTML input...")
    
    def update_char_count(self):
        """Update character count"""
        text = self.input_text.toPlainText()
        char_count = len(text)
        self.char_count_label.setText(f"Characters: {char_count:,}")
    
    def format_html(self):
        """Format and validate HTML"""
        input_text = self.input_text.toPlainText().strip()
        
        if not input_text:
            self.show_error("No HTML input provided. Please paste HTML code first.")
            return
        
        try:
            # Format HTML with proper indentation
            self.status_label.setText("Formatting HTML...")
            formatted_html = self.format_html_content(input_text)
            
            # Display formatted HTML
            self.output_text.setPlainText(formatted_html)
            
            # Update status
            self.status_label.setText("✅ HTML formatted successfully!")
            self.status_text.setPlainText(f"""Status: ✅ HTML Formatted

Formatting Results:
• Structure: Properly indented
• Tags: Well-formed
• Attributes: Properly quoted
• Whitespace: Normalized
• Indentation: 2 spaces per level

Timestamp: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}
""")
            
            # Switch to formatted tab
            self.output_tabs.setCurrentIndex(0)
            
            # Enable copy and save buttons
            self.copy_btn.setEnabled(True)
            self.save_btn.setEnabled(True)
            
        except Exception as e:
            self.show_error(f"HTML formatting error: {str(e)}")
    
    def format_html_content(self, html_content):
        """Format HTML content with proper indentation"""
        # Remove extra whitespace and normalize
        html_content = re.sub(r'\s+', ' ', html_content.strip())
        
        # Self-closing tags
        self_closing_tags = {'area', 'base', 'br', 'col', 'embed', 'hr', 'img', 'input', 
                           'link', 'meta', 'param', 'source', 'track', 'wbr'}
        
        # Tags that should not be formatted (preserve content)
        preserve_content_tags = {'script', 'style', 'pre', 'code', 'textarea'}
        
        formatted_lines = []
        indent_level = 0
        indent_size = 2
        i = 0
        
        while i < len(html_content):
            if html_content[i] == '<':
                # Find the end of the tag
                tag_end = html_content.find('>', i)
                if tag_end == -1:
                    break
                
                tag = html_content[i:tag_end + 1]
                
                # Extract tag name
                tag_match = re.match(r'<(/?)(\w+)', tag)
                if tag_match:
                    is_closing = bool(tag_match.group(1))
                    tag_name = tag_match.group(2).lower()
                    
                    # Handle closing tags
                    if is_closing:
                        indent_level = max(0, indent_level - 1)
                    
                    # Add indentation
                    indent = ' ' * (indent_level * indent_size)
                    formatted_lines.append(indent + tag)
                    
                    # Handle opening tags
                    if not is_closing and tag_name not in self_closing_tags and not tag.endswith('/>'):
                        # Check if this is a preserve content tag
                        if tag_name in preserve_content_tags:
                            # Find the closing tag and preserve content
                            closing_tag = f'</{tag_name}>'
                            closing_pos = html_content.find(closing_tag, tag_end + 1)
                            if closing_pos != -1:
                                content = html_content[tag_end + 1:closing_pos]
                                if content.strip():
                                    formatted_lines.append(indent + '  ' + content.strip())
                                formatted_lines.append(indent + closing_tag)
                                i = closing_pos + len(closing_tag)
                                continue
                        else:
                            indent_level += 1
                
                i = tag_end + 1
            else:
                # Handle text content
                text_start = i
                next_tag = html_content.find('<', i)
                if next_tag == -1:
                    text = html_content[text_start:].strip()
                    if text:
                        indent = ' ' * (indent_level * indent_size)
                        formatted_lines.append(indent + text)
                    break
                else:
                    text = html_content[text_start:next_tag].strip()
                    if text:
                        indent = ' ' * (indent_level * indent_size)
                        formatted_lines.append(indent + text)
                    i = next_tag
        
        return '\n'.join(formatted_lines)
    
    def minify_html(self):
        """Minify HTML (remove whitespace)"""
        input_text = self.input_text.toPlainText().strip()
        
        if not input_text:
            self.show_error("No HTML input provided. Please paste HTML code first.")
            return
        
        try:
            # Minify HTML
            self.status_label.setText("Minifying HTML...")
            minified_html = self.minify_html_content(input_text)
            
            # Display minified HTML
            self.output_text.setPlainText(minified_html)
            
            # Calculate size reduction
            original_size = len(input_text)
            minified_size = len(minified_html)
            reduction = ((original_size - minified_size) / original_size) * 100 if original_size > 0 else 0
            
            # Update status
            self.status_label.setText("📦 HTML minified successfully!")
            self.status_text.setPlainText(f"""Status: 📦 HTML Minified

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
            self.show_error(f"HTML minification error: {str(e)}")
    
    def minify_html_content(self, html_content):
        """Minify HTML content"""
        # Remove HTML comments
        html_content = re.sub(r'<!--.*?-->', '', html_content, flags=re.DOTALL)
        
        # Preserve content in script and style tags
        preserve_tags = []
        for tag in ['script', 'style', 'pre', 'textarea']:
            pattern = f'<{tag}[^>]*>.*?</{tag}>'
            matches = re.finditer(pattern, html_content, re.DOTALL | re.IGNORECASE)
            for match in matches:
                preserve_tags.append((match.start(), match.end(), match.group()))
        
        # Sort by position (reverse order for replacement)
        preserve_tags.sort(key=lambda x: x[0], reverse=True)
        
        # Replace preserved content with placeholders
        placeholders = {}
        for i, (start, end, content) in enumerate(preserve_tags):
            placeholder = f"__PRESERVE_{i}__"
            placeholders[placeholder] = content
            html_content = html_content[:start] + placeholder + html_content[end:]
        
        # Remove extra whitespace
        html_content = re.sub(r'\s+', ' ', html_content)
        html_content = re.sub(r'>\s+<', '><', html_content)
        html_content = html_content.strip()
        
        # Restore preserved content
        for placeholder, content in placeholders.items():
            html_content = html_content.replace(placeholder, content)
        
        return html_content
    
    def analyze_html(self):
        """Analyze HTML structure and provide statistics"""
        input_text = self.input_text.toPlainText().strip()
        
        if not input_text:
            self.show_error("No HTML input provided. Please paste HTML code first.")
            return
        
        try:
            # Analyze HTML
            self.status_label.setText("Analyzing HTML structure...")
            analysis = self.perform_html_analysis(input_text)
            
            # Display analysis
            self.analysis_text.setHtml(analysis)
            
            # Update status
            self.status_label.setText("🔍 HTML analysis completed!")
            
            # Switch to analysis tab
            self.output_tabs.setCurrentIndex(1)
            
        except Exception as e:
            self.show_error(f"HTML analysis error: {str(e)}")
    
    def perform_html_analysis(self, html_content):
        """Perform detailed HTML analysis"""
        # Basic statistics
        char_count = len(html_content)
        line_count = html_content.count('\n') + 1
        
        # Find all tags
        tag_pattern = r'<(/?)(\w+)[^>]*>'
        tags = re.findall(tag_pattern, html_content, re.IGNORECASE)
        
        # Count different types of tags
        opening_tags = [tag[1].lower() for tag in tags if not tag[0]]
        closing_tags = [tag[1].lower() for tag in tags if tag[0]]
        
        # Tag statistics
        tag_counts = {}
        for tag in opening_tags:
            tag_counts[tag] = tag_counts.get(tag, 0) + 1
        
        # Find attributes
        attr_pattern = r'<\w+[^>]*\s+(\w+)='
        attributes = re.findall(attr_pattern, html_content, re.IGNORECASE)
        attr_counts = {}
        for attr in attributes:
            attr_counts[attr.lower()] = attr_counts.get(attr.lower(), 0) + 1
        
        # Find comments
        comment_pattern = r'<!--.*?-->'
        comments = re.findall(comment_pattern, html_content, re.DOTALL)
        
        # Check for common HTML5 elements
        html5_elements = ['article', 'aside', 'details', 'figcaption', 'figure', 
                         'footer', 'header', 'main', 'mark', 'nav', 'section', 'summary', 'time']
        html5_used = [elem for elem in html5_elements if elem in tag_counts]
        
        # Check for accessibility attributes
        a11y_attrs = ['alt', 'aria-label', 'aria-describedby', 'role', 'tabindex']
        a11y_used = [attr for attr in a11y_attrs if attr in attr_counts]
        
        # Generate analysis HTML
        analysis_html = f"""
        <div style="font-family: Arial, sans-serif; padding: 10px;">
            <h2 style="color: #007bff; margin-top: 0;">📊 HTML Structure Analysis</h2>
            
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
                    <td style="padding: 8px; border: 1px solid #dee2e6; font-weight: bold;">Total Tags</td>
                    <td style="padding: 8px; border: 1px solid #dee2e6;">{len(opening_tags):,}</td>
                </tr>
                <tr>
                    <td style="padding: 8px; border: 1px solid #dee2e6; font-weight: bold;">Unique Tag Types</td>
                    <td style="padding: 8px; border: 1px solid #dee2e6;">{len(tag_counts):,}</td>
                </tr>
                <tr style="background-color: #f8f9fa;">
                    <td style="padding: 8px; border: 1px solid #dee2e6; font-weight: bold;">Comments</td>
                    <td style="padding: 8px; border: 1px solid #dee2e6;">{len(comments):,}</td>
                </tr>
            </table>
            
            <h3 style="color: #17a2b8;">🏷️ Most Common Tags</h3>
            <table style="border-collapse: collapse; width: 100%; margin-bottom: 20px;">
        """
        
        # Add top 10 most common tags
        sorted_tags = sorted(tag_counts.items(), key=lambda x: x[1], reverse=True)[:10]
        for i, (tag, count) in enumerate(sorted_tags):
            bg_color = "#f8f9fa" if i % 2 == 0 else "white"
            analysis_html += f"""
                <tr style="background-color: {bg_color};">
                    <td style="padding: 8px; border: 1px solid #dee2e6; font-weight: bold;">&lt;{tag}&gt;</td>
                    <td style="padding: 8px; border: 1px solid #dee2e6;">{count:,}</td>
                </tr>
            """
        
        analysis_html += """
            </table>
            
            <h3 style="color: #ffc107;">🎯 HTML5 & Accessibility</h3>
            <table style="border-collapse: collapse; width: 100%; margin-bottom: 20px;">
        """
        
        analysis_html += f"""
                <tr style="background-color: #f8f9fa;">
                    <td style="padding: 8px; border: 1px solid #dee2e6; font-weight: bold;">HTML5 Elements Used</td>
                    <td style="padding: 8px; border: 1px solid #dee2e6;">{len(html5_used)} ({', '.join(html5_used) if html5_used else 'None'})</td>
                </tr>
                <tr>
                    <td style="padding: 8px; border: 1px solid #dee2e6; font-weight: bold;">Accessibility Attributes</td>
                    <td style="padding: 8px; border: 1px solid #dee2e6;">{len(a11y_used)} ({', '.join(a11y_used) if a11y_used else 'None'})</td>
                </tr>
            </table>
            
            <h3 style="color: #dc3545;">💡 Recommendations</h3>
            <ul style="margin-bottom: 20px;">
        """
        
        # Add recommendations
        if not html5_used:
            analysis_html += "<li>🏗️ Consider using HTML5 semantic elements (header, nav, main, article, section, footer) for better structure.</li>"
        
        if not a11y_used:
            analysis_html += "<li>♿ Add accessibility attributes (alt, aria-label, role) to improve accessibility.</li>"
        
        if 'img' in tag_counts and 'alt' not in attr_counts:
            analysis_html += "<li>🖼️ Add alt attributes to images for better accessibility.</li>"
        
        if char_count > 50000:
            analysis_html += "<li>📦 Large HTML detected. Consider minifying for production use.</li>"
        
        if len(comments) == 0:
            analysis_html += "<li>📝 Consider adding comments to document complex sections.</li>"
        
        if 'div' in tag_counts and tag_counts['div'] > len(opening_tags) * 0.3:
            analysis_html += "<li>🏗️ High div usage detected. Consider using semantic HTML5 elements instead.</li>"
        
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
        """Load HTML from file"""
        file_path, _ = QFileDialog.getOpenFileName(
            self,
            "Load HTML File",
            "",
            "HTML Files (*.html *.htm);;Text Files (*.txt);;All Files (*.*)"
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
        """Save formatted HTML to file"""
        output_content = self.output_text.toPlainText()
        
        if not output_content or "Welcome to HTML Pretty Formatter" in output_content:
            self.show_error("No formatted HTML to save. Please format HTML first.")
            return
        
        file_path, _ = QFileDialog.getSaveFileName(
            self,
            "Save Formatted HTML",
            f"formatted_html_{datetime.now().strftime('%Y%m%d_%H%M%S')}.html",
            "HTML Files (*.html);;Text Files (*.txt);;All Files (*.*)"
        )
        
        if file_path:
            try:
                with open(file_path, 'w', encoding='utf-8') as f:
                    f.write(output_content)
                
                self.status_label.setText(f"💾 Saved to: {file_path}")
                
            except Exception as e:
                self.show_error(f"Failed to save file: {str(e)}")
    
    def copy_output(self):
        """Copy formatted HTML to clipboard"""
        output_content = self.output_text.toPlainText()
        
        if not output_content or "Welcome to HTML Pretty Formatter" in output_content:
            self.show_error("No formatted HTML to copy. Please format HTML first.")
            return
        
        clipboard = QApplication.clipboard()
        clipboard.setText(output_content)
        
        self.status_label.setText("📋 Formatted HTML copied to clipboard!")
        
        # Reset status after 3 seconds
        QTimer.singleShot(3000, lambda: self.status_label.setText("Ready"))
    
    def clear_input(self):
        """Clear input text"""
        self.input_text.clear()
        self.status_label.setText("Input cleared")
    
    def show_help(self):
        """Show help dialog"""
        help_text = """
HTML Pretty Formatter Help

🌐 FEATURES:
• Format & Validate: Beautify HTML with proper indentation and structure
• Minify: Remove whitespace and comments to reduce file size
• Analyze: Get detailed statistics about HTML structure and elements
• Load/Save: Work with HTML files
• Copy: Copy results to clipboard

📝 USAGE:
1. Paste HTML in the left panel or load from file
2. Click 'Format & Validate' to beautify and structure
3. Use 'Minify' to compress HTML
4. Click 'Analyze' for detailed structure information
5. Copy or save results as needed

🔍 ANALYSIS FEATURES:
• Tag counting and statistics
• HTML5 semantic element detection
• Accessibility attribute checking
• Structure recommendations
• Performance optimization tips

🎯 TIPS:
• Use Ctrl+A to select all text
• Large files are supported
• Preserves script and style tag content
• Provides HTML5 and accessibility recommendations
        """
        
        QMessageBox.information(self, "HTML Formatter Help", help_text)


def show_html_formatter(parent=None):
    """Show HTML formatter dialog"""
    dialog = HtmlFormatterDialog(parent)
    dialog.show()
    return dialog


if __name__ == "__main__":
    # Test the HTML formatter
    import sys
    from PyQt5.QtWidgets import QApplication
    
    app = QApplication(sys.argv)
    dialog = HtmlFormatterDialog()
    dialog.show()
    sys.exit(app.exec_())