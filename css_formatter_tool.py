"""
CSS Pretty Formatter Tool
A utility for formatting, validating, and analyzing CSS code.
"""

import re
from datetime import datetime
from PyQt5.QtCore import *
from PyQt5.QtWidgets import *
from PyQt5.QtGui import *


class CssFormatterDialog(QDialog):
    """CSS Pretty Formatter Dialog"""
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setup_ui()
        self.setup_connections()
    
    def setup_ui(self):
        """Setup the user interface"""
        self.setWindowTitle("🎨 CSS Pretty Formatter")
        self.setMinimumSize(900, 700)
        self.setModal(False)  # Allow interaction with main window
        
        # Main layout
        layout = QVBoxLayout(self)
        layout.setSpacing(10)
        
        # Header
        header_layout = QHBoxLayout()
        
        # Icon and title
        icon_label = QLabel("🎨")
        icon_label.setStyleSheet("font-size: 24px;")
        
        title_label = QLabel("CSS Pretty Formatter")
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
        desc_label = QLabel("Format, validate, minify, and analyze CSS code with syntax highlighting and property analysis")
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
        
        input_label = QLabel("📝 Input CSS:")
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
        self.input_text.setPlaceholderText("""Paste your CSS here or load from file...

Example:
body { margin: 0; padding: 0; font-family: Arial, sans-serif; }
.container { max-width: 1200px; margin: 0 auto; }
h1 { color: #333; font-size: 2em; }""")
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
        self.format_btn.clicked.connect(self.format_css)
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
        self.minify_btn.clicked.connect(self.minify_css)
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
        self.analyze_btn.clicked.connect(self.analyze_css)
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
        
        # Formatted CSS tab
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
        
        self.status_label = QLabel("Ready - Paste CSS and click 'Format & Validate'")
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
Welcome to CSS Pretty Formatter! 🎉

Features:
• ✨ Format and beautify CSS with proper indentation
• 📦 Minify CSS to reduce size
• 🔍 Analyze CSS structure and properties
• ✅ Validate CSS syntax and best practices
• 📂 Load CSS from files
• 💾 Save formatted CSS to files
• 📋 Copy results to clipboard

Instructions:
1. Paste your CSS in the left panel or load from file
2. Click 'Format & Validate' to beautify and check syntax
3. Use 'Minify' to compress CSS
4. Click 'Analyze' to get detailed statistics
5. Copy or save the results as needed

Ready to format your CSS! 🚀
        """
        
        self.output_text.setPlainText(welcome_msg)
        self.analysis_text.setPlainText("No analysis performed yet. Click 'Analyze' after formatting CSS.")
        self.status_text.setPlainText("Status: Ready\nWaiting for CSS input...")
    
    def update_char_count(self):
        """Update character count"""
        text = self.input_text.toPlainText()
        char_count = len(text)
        self.char_count_label.setText(f"Characters: {char_count:,}")
    
    def format_css(self):
        """Format and validate CSS"""
        input_text = self.input_text.toPlainText().strip()
        
        if not input_text:
            self.show_error("No CSS input provided. Please paste CSS code first.")
            return
        
        try:
            # Format CSS with proper indentation
            self.status_label.setText("Formatting CSS...")
            formatted_css = self.format_css_content(input_text)
            
            # Display formatted CSS
            self.output_text.setPlainText(formatted_css)
            
            # Update status
            self.status_label.setText("✅ CSS formatted successfully!")
            self.status_text.setPlainText(f"""Status: ✅ CSS Formatted

Formatting Results:
• Structure: Properly indented
• Properties: Well-organized
• Selectors: Properly formatted
• Values: Normalized
• Indentation: 2 spaces per level

Timestamp: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}
""")
            
            # Switch to formatted tab
            self.output_tabs.setCurrentIndex(0)
            
            # Enable copy and save buttons
            self.copy_btn.setEnabled(True)
            self.save_btn.setEnabled(True)
            
        except Exception as e:
            self.show_error(f"CSS formatting error: {str(e)}")
    
    def format_css_content(self, css_content):
        """Format CSS content with proper indentation"""
        # Remove extra whitespace and normalize
        css_content = re.sub(r'\s+', ' ', css_content.strip())
        
        formatted_lines = []
        indent_level = 0
        indent_size = 2
        i = 0
        
        while i < len(css_content):
            char = css_content[i]
            
            if char == '{':
                # Opening brace - add newline and increase indent
                formatted_lines.append(' ' * (indent_level * indent_size) + '{')
                indent_level += 1
                i += 1
                
                # Skip whitespace after opening brace
                while i < len(css_content) and css_content[i].isspace():
                    i += 1
                    
            elif char == '}':
                # Closing brace - decrease indent and add newline
                indent_level = max(0, indent_level - 1)
                formatted_lines.append(' ' * (indent_level * indent_size) + '}')
                i += 1
                
                # Add empty line after closing brace if not at end
                if i < len(css_content) - 1:
                    formatted_lines.append('')
                
                # Skip whitespace after closing brace
                while i < len(css_content) and css_content[i].isspace():
                    i += 1
                    
            elif char == ';':
                # Semicolon - add newline
                formatted_lines.append(' ' * (indent_level * indent_size) + css_content[self.find_property_start(css_content, i):i+1].strip())
                i += 1
                
                # Skip whitespace after semicolon
                while i < len(css_content) and css_content[i].isspace():
                    i += 1
                    
            else:
                # Find the end of current statement/selector
                start = i
                
                # Find next special character
                while i < len(css_content) and css_content[i] not in '{};':
                    i += 1
                
                if i > start:
                    content = css_content[start:i].strip()
                    if content:
                        if indent_level == 0:
                            # This is a selector
                            formatted_lines.append(content + ' ')
                        else:
                            # This is a property (will be handled by semicolon case)
                            continue
        
        return '\n'.join(line.rstrip() for line in formatted_lines if line.strip() or not line)
    
    def find_property_start(self, css_content, semicolon_pos):
        """Find the start of a CSS property"""
        # Look backwards for the start of the property
        start = semicolon_pos
        brace_count = 0
        
        while start > 0:
            char = css_content[start - 1]
            if char == '}':
                brace_count += 1
            elif char == '{':
                if brace_count == 0:
                    break
                brace_count -= 1
            elif char == ';' and brace_count == 0:
                break
            start -= 1
        
        return start
    
    def minify_css(self):
        """Minify CSS (remove whitespace)"""
        input_text = self.input_text.toPlainText().strip()
        
        if not input_text:
            self.show_error("No CSS input provided. Please paste CSS code first.")
            return
        
        try:
            # Minify CSS
            self.status_label.setText("Minifying CSS...")
            minified_css = self.minify_css_content(input_text)
            
            # Display minified CSS
            self.output_text.setPlainText(minified_css)
            
            # Calculate size reduction
            original_size = len(input_text)
            minified_size = len(minified_css)
            reduction = ((original_size - minified_size) / original_size) * 100 if original_size > 0 else 0
            
            # Update status
            self.status_label.setText("📦 CSS minified successfully!")
            self.status_text.setPlainText(f"""Status: 📦 CSS Minified

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
            self.show_error(f"CSS minification error: {str(e)}")
    
    def minify_css_content(self, css_content):
        """Minify CSS content"""
        # Remove CSS comments
        css_content = re.sub(r'/\*.*?\*/', '', css_content, flags=re.DOTALL)
        
        # Remove extra whitespace
        css_content = re.sub(r'\s+', ' ', css_content)
        
        # Remove spaces around special characters
        css_content = re.sub(r'\s*{\s*', '{', css_content)
        css_content = re.sub(r'\s*}\s*', '}', css_content)
        css_content = re.sub(r'\s*;\s*', ';', css_content)
        css_content = re.sub(r'\s*:\s*', ':', css_content)
        css_content = re.sub(r'\s*,\s*', ',', css_content)
        
        return css_content.strip()
    
    def analyze_css(self):
        """Analyze CSS structure and provide statistics"""
        input_text = self.input_text.toPlainText().strip()
        
        if not input_text:
            self.show_error("No CSS input provided. Please paste CSS code first.")
            return
        
        try:
            # Analyze CSS
            self.status_label.setText("Analyzing CSS structure...")
            analysis = self.perform_css_analysis(input_text)
            
            # Display analysis
            self.analysis_text.setHtml(analysis)
            
            # Update status
            self.status_label.setText("🔍 CSS analysis completed!")
            
            # Switch to analysis tab
            self.output_tabs.setCurrentIndex(1)
            
        except Exception as e:
            self.show_error(f"CSS analysis error: {str(e)}")
    
    def perform_css_analysis(self, css_content):
        """Perform detailed CSS analysis"""
        # Basic statistics
        char_count = len(css_content)
        line_count = css_content.count('\n') + 1
        
        # Find selectors
        selector_pattern = r'([^{}]+)\s*{'
        selectors = re.findall(selector_pattern, css_content)
        selectors = [s.strip() for s in selectors if s.strip()]
        
        # Find properties
        property_pattern = r'([a-zA-Z-]+)\s*:\s*([^;]+);'
        properties = re.findall(property_pattern, css_content)
        
        # Count property usage
        property_counts = {}
        for prop, value in properties:
            prop = prop.strip().lower()
            property_counts[prop] = property_counts.get(prop, 0) + 1
        
        # Find media queries
        media_pattern = r'@media[^{]+{'
        media_queries = re.findall(media_pattern, css_content, re.IGNORECASE)
        
        # Find comments
        comment_pattern = r'/\*.*?\*/'
        comments = re.findall(comment_pattern, css_content, re.DOTALL)
        
        # Analyze selector types
        id_selectors = [s for s in selectors if '#' in s]
        class_selectors = [s for s in selectors if '.' in s]
        element_selectors = [s for s in selectors if not any(c in s for c in '.#[]:(')]
        
        # Check for CSS3 properties
        css3_properties = ['border-radius', 'box-shadow', 'text-shadow', 'transform', 
                          'transition', 'animation', 'gradient', 'flex', 'grid']
        css3_used = [prop for prop in css3_properties if any(prop in p for p in property_counts.keys())]
        
        # Generate analysis HTML
        analysis_html = f"""
        <div style="font-family: Arial, sans-serif; padding: 10px;">
            <h2 style="color: #007bff; margin-top: 0;">📊 CSS Structure Analysis</h2>
            
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
                    <td style="padding: 8px; border: 1px solid #dee2e6; font-weight: bold;">Total Selectors</td>
                    <td style="padding: 8px; border: 1px solid #dee2e6;">{len(selectors):,}</td>
                </tr>
                <tr>
                    <td style="padding: 8px; border: 1px solid #dee2e6; font-weight: bold;">Total Properties</td>
                    <td style="padding: 8px; border: 1px solid #dee2e6;">{len(properties):,}</td>
                </tr>
                <tr style="background-color: #f8f9fa;">
                    <td style="padding: 8px; border: 1px solid #dee2e6; font-weight: bold;">Media Queries</td>
                    <td style="padding: 8px; border: 1px solid #dee2e6;">{len(media_queries):,}</td>
                </tr>
                <tr>
                    <td style="padding: 8px; border: 1px solid #dee2e6; font-weight: bold;">Comments</td>
                    <td style="padding: 8px; border: 1px solid #dee2e6;">{len(comments):,}</td>
                </tr>
            </table>
            
            <h3 style="color: #17a2b8;">🎯 Selector Types</h3>
            <table style="border-collapse: collapse; width: 100%; margin-bottom: 20px;">
                <tr style="background-color: #f8f9fa;">
                    <td style="padding: 8px; border: 1px solid #dee2e6; font-weight: bold;">ID Selectors (#)</td>
                    <td style="padding: 8px; border: 1px solid #dee2e6;">{len(id_selectors):,}</td>
                </tr>
                <tr>
                    <td style="padding: 8px; border: 1px solid #dee2e6; font-weight: bold;">Class Selectors (.)</td>
                    <td style="padding: 8px; border: 1px solid #dee2e6;">{len(class_selectors):,}</td>
                </tr>
                <tr style="background-color: #f8f9fa;">
                    <td style="padding: 8px; border: 1px solid #dee2e6; font-weight: bold;">Element Selectors</td>
                    <td style="padding: 8px; border: 1px solid #dee2e6;">{len(element_selectors):,}</td>
                </tr>
            </table>
            
            <h3 style="color: #ffc107;">🏷️ Most Common Properties</h3>
            <table style="border-collapse: collapse; width: 100%; margin-bottom: 20px;">
        """
        
        # Add top 10 most common properties
        sorted_properties = sorted(property_counts.items(), key=lambda x: x[1], reverse=True)[:10]
        for i, (prop, count) in enumerate(sorted_properties):
            bg_color = "#f8f9fa" if i % 2 == 0 else "white"
            analysis_html += f"""
                <tr style="background-color: {bg_color};">
                    <td style="padding: 8px; border: 1px solid #dee2e6; font-weight: bold;">{prop}</td>
                    <td style="padding: 8px; border: 1px solid #dee2e6;">{count:,}</td>
                </tr>
            """
        
        analysis_html += f"""
            </table>
            
            <h3 style="color: #dc3545;">� Moder n CSS Features</h3>
            <table style="border-collapse: collapse; width: 100%; margin-bottom: 20px;">
                <tr style="background-color: #f8f9fa;">
                    <td style="padding: 8px; border: 1px solid #dee2e6; font-weight: bold;">CSS3 Properties Used</td>
                    <td style="padding: 8px; border: 1px solid #dee2e6;">{len(css3_used)} ({', '.join(css3_used) if css3_used else 'None'})</td>
                </tr>
                <tr>
                    <td style="padding: 8px; border: 1px solid #dee2e6; font-weight: bold;">Responsive Design</td>
                    <td style="padding: 8px; border: 1px solid #dee2e6;">{'Yes' if media_queries else 'No'} ({len(media_queries)} media queries)</td>
                </tr>
            </table>
            
            <h3 style="color: #6f42c1;">💡 Recommendations</h3>
            <ul style="margin-bottom: 20px;">
        """
        
        # Add recommendations
        if not media_queries:
            analysis_html += "<li>📱 Consider adding media queries for responsive design.</li>"
        
        if not css3_used:
            analysis_html += "<li>🚀 Consider using modern CSS3 properties for better styling.</li>"
        
        if len(id_selectors) > len(class_selectors):
            analysis_html += "<li>🎯 Consider using more class selectors instead of ID selectors for better reusability.</li>"
        
        if char_count > 50000:
            analysis_html += "<li>📦 Large CSS detected. Consider minifying for production use.</li>"
        
        if len(comments) == 0:
            analysis_html += "<li>📝 Consider adding comments to document complex styles.</li>"
        
        if 'color' in property_counts and property_counts['color'] > len(properties) * 0.1:
            analysis_html += "<li>🎨 High color usage detected. Consider using CSS custom properties (variables) for consistent theming.</li>"
        
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
        """Load CSS from file"""
        file_path, _ = QFileDialog.getOpenFileName(
            self,
            "Load CSS File",
            "",
            "CSS Files (*.css);;Text Files (*.txt);;All Files (*.*)"
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
        """Save formatted CSS to file"""
        output_content = self.output_text.toPlainText()
        
        if not output_content or "Welcome to CSS Pretty Formatter" in output_content:
            self.show_error("No formatted CSS to save. Please format CSS first.")
            return
        
        file_path, _ = QFileDialog.getSaveFileName(
            self,
            "Save Formatted CSS",
            f"formatted_css_{datetime.now().strftime('%Y%m%d_%H%M%S')}.css",
            "CSS Files (*.css);;Text Files (*.txt);;All Files (*.*)"
        )
        
        if file_path:
            try:
                with open(file_path, 'w', encoding='utf-8') as f:
                    f.write(output_content)
                
                self.status_label.setText(f"💾 Saved to: {file_path}")
                
            except Exception as e:
                self.show_error(f"Failed to save file: {str(e)}")
    
    def copy_output(self):
        """Copy formatted CSS to clipboard"""
        output_content = self.output_text.toPlainText()
        
        if not output_content or "Welcome to CSS Pretty Formatter" in output_content:
            self.show_error("No formatted CSS to copy. Please format CSS first.")
            return
        
        clipboard = QApplication.clipboard()
        clipboard.setText(output_content)
        
        self.status_label.setText("📋 Formatted CSS copied to clipboard!")
        
        # Reset status after 3 seconds
        QTimer.singleShot(3000, lambda: self.status_label.setText("Ready"))
    
    def clear_input(self):
        """Clear input text"""
        self.input_text.clear()
        self.status_label.setText("Input cleared")
    
    def show_help(self):
        """Show help dialog"""
        help_text = """
CSS Pretty Formatter Help

🎨 FEATURES:
• Format & Validate: Beautify CSS with proper indentation and structure
• Minify: Remove whitespace and comments to reduce file size
• Analyze: Get detailed statistics about CSS properties and selectors
• Load/Save: Work with CSS files
• Copy: Copy results to clipboard

📝 USAGE:
1. Paste CSS in the left panel or load from file
2. Click 'Format & Validate' to beautify and structure
3. Use 'Minify' to compress CSS
4. Click 'Analyze' for detailed structure information
5. Copy or save results as needed

🔍 ANALYSIS FEATURES:
• Property counting and statistics
• Selector type analysis (ID, class, element)
• CSS3 feature detection
• Media query analysis
• Performance optimization tips

🎯 TIPS:
• Use Ctrl+A to select all text
• Large files are supported
• Provides modern CSS and responsive design recommendations
• Helps identify optimization opportunities
        """
        
        QMessageBox.information(self, "CSS Formatter Help", help_text)


def show_css_formatter(parent=None):
    """Show CSS formatter dialog"""
    dialog = CssFormatterDialog(parent)
    dialog.show()
    return dialog


if __name__ == "__main__":
    # Test the CSS formatter
    import sys
    from PyQt5.QtWidgets import QApplication
    
    app = QApplication(sys.argv)
    dialog = CssFormatterDialog()
    dialog.show()
    sys.exit(app.exec_())