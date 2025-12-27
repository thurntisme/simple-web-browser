#!/usr/bin/env python3
"""
Test script for the HTML formatter tool.
"""

import sys
from PyQt5.QtCore import Qt
from PyQt5.QtWidgets import QApplication

def test_html_formatter():
    """Test the HTML formatter tool"""
    
    print("🌐 Testing HTML Formatter Tool")
    print("=" * 50)
    
    # Set Qt attributes before creating QApplication
    QApplication.setAttribute(Qt.AA_ShareOpenGLContexts)
    
    app = QApplication.instance()
    if app is None:
        app = QApplication(sys.argv)
    
    try:
        from html_formatter_tool import HtmlFormatterDialog
        
        # Create dialog
        dialog = HtmlFormatterDialog()
        print("✅ HTML formatter dialog created successfully")
        
        # Test UI components exist
        assert hasattr(dialog, 'input_text')
        assert hasattr(dialog, 'output_text')
        assert hasattr(dialog, 'analysis_text')
        assert hasattr(dialog, 'status_text')
        assert hasattr(dialog, 'format_btn')
        assert hasattr(dialog, 'minify_btn')
        assert hasattr(dialog, 'analyze_btn')
        print("✅ All UI components exist")
        
        # Test tabs
        assert dialog.output_tabs.count() == 3
        assert dialog.output_tabs.tabText(0) == "📄 Formatted"
        assert dialog.output_tabs.tabText(1) == "🔍 Analysis"
        assert dialog.output_tabs.tabText(2) == "⚠️ Status"
        print("✅ Output tabs created correctly")
        
        # Test initial content
        welcome_content = dialog.output_text.toPlainText()
        assert "Welcome to HTML Pretty Formatter" in welcome_content
        print("✅ Welcome message displayed")
        
        # Test HTML formatting with valid HTML
        test_html = '<html><head><title>Test</title></head><body><h1>Hello World</h1><p>This is a paragraph.</p></body></html>'
        dialog.input_text.setPlainText(test_html)
        
        # Simulate format button click
        dialog.format_html()
        
        # Check if formatting worked
        formatted_output = dialog.output_text.toPlainText()
        assert "<html>" in formatted_output
        assert "<title>" in formatted_output
        assert "Hello World" in formatted_output
        # Check for proper indentation
        assert "  <head>" in formatted_output or "  <body>" in formatted_output
        print("✅ HTML formatting works")
        
        # Test minify functionality
        dialog.minify_html()
        minified_output = dialog.output_text.toPlainText()
        assert len(minified_output) < len(formatted_output)
        assert "<html><head>" in minified_output or "<html> <head>" in minified_output
        print("✅ HTML minification works")
        
        # Test analysis functionality
        dialog.analyze_html()
        analysis_output = dialog.analysis_text.toPlainText()
        assert "HTML Structure Analysis" in analysis_output or "tags" in analysis_output.lower()
        print("✅ HTML analysis works")
        
        # Test with more complex HTML
        complex_html = '''
        <html>
        <head>
            <title>Complex Test</title>
            <meta charset="utf-8">
        </head>
        <body>
            <header>
                <nav>
                    <ul>
                        <li><a href="#home">Home</a></li>
                        <li><a href="#about">About</a></li>
                    </ul>
                </nav>
            </header>
            <main>
                <article>
                    <h1>Article Title</h1>
                    <p>Article content with <strong>bold</strong> text.</p>
                </article>
            </main>
            <footer>
                <p>&copy; 2024 Test Site</p>
            </footer>
        </body>
        </html>
        '''
        
        dialog.input_text.setPlainText(complex_html)
        dialog.format_html()
        
        complex_formatted = dialog.output_text.toPlainText()
        assert "<header>" in complex_formatted
        assert "<nav>" in complex_formatted
        assert "<main>" in complex_formatted
        assert "<article>" in complex_formatted
        assert "<footer>" in complex_formatted
        print("✅ Complex HTML formatting works")
        
        # Test analysis with complex HTML
        dialog.analyze_html()
        complex_analysis = dialog.analysis_text.toPlainText()
        assert "header" in complex_analysis.lower() or "nav" in complex_analysis.lower()
        print("✅ Complex HTML analysis works")
        
        print("\n🎉 All HTML Formatter Tests Passed!")
        print("\n📋 Test Results Summary:")
        print("✅ Dialog creation - Working")
        print("✅ UI components - Working")
        print("✅ Output tabs - Working")
        print("✅ Welcome message - Working")
        print("✅ HTML formatting - Working")
        print("✅ HTML minification - Working")
        print("✅ HTML analysis - Working")
        print("✅ Complex HTML handling - Working")
        
        print("\n🌐 HTML Formatter Tool is ready!")
        print("\n🚀 Access Methods:")
        print("- Tools menu: 🌐 HTML Formatter (Ctrl+Shift+H)")
        print("- Direct execution: python html_formatter_tool.py")
        
        return True
        
    except Exception as e:
        print(f"\n❌ Test failed: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    success = test_html_formatter()
    sys.exit(0 if success else 1)