#!/usr/bin/env python3
"""
Test script for the CSS formatter tool.
"""

import sys
from PyQt5.QtCore import Qt
from PyQt5.QtWidgets import QApplication

def test_css_formatter():
    """Test the CSS formatter tool"""
    
    print("🎨 Testing CSS Formatter Tool")
    print("=" * 50)
    
    # Set Qt attributes before creating QApplication
    QApplication.setAttribute(Qt.AA_ShareOpenGLContexts)
    
    app = QApplication.instance()
    if app is None:
        app = QApplication(sys.argv)
    
    try:
        from css_formatter_tool import CssFormatterDialog
        
        # Create dialog
        dialog = CssFormatterDialog()
        print("✅ CSS formatter dialog created successfully")
        
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
        assert "Welcome to CSS Pretty Formatter" in welcome_content
        print("✅ Welcome message displayed")
        
        # Test CSS formatting with valid CSS
        test_css = 'body { margin: 0; padding: 0; font-family: Arial, sans-serif; } .container { max-width: 1200px; margin: 0 auto; }'
        dialog.input_text.setPlainText(test_css)
        
        # Simulate format button click
        dialog.format_css()
        
        # Check if formatting worked
        formatted_output = dialog.output_text.toPlainText()
        assert "body" in formatted_output
        assert "margin" in formatted_output
        assert "container" in formatted_output
        print("✅ CSS formatting works")
        
        # Test minify functionality
        dialog.minify_css()
        minified_output = dialog.output_text.toPlainText()
        assert len(minified_output) < len(formatted_output)
        assert "body{" in minified_output or "body {" in minified_output
        print("✅ CSS minification works")
        
        # Test analysis functionality
        dialog.analyze_css()
        analysis_output = dialog.analysis_text.toPlainText()
        assert "CSS Structure Analysis" in analysis_output or "properties" in analysis_output.lower()
        print("✅ CSS analysis works")
        
        # Test with more complex CSS
        complex_css = '''
        /* Main styles */
        body {
            margin: 0;
            padding: 0;
            font-family: 'Arial', sans-serif;
            background-color: #f5f5f5;
        }
        
        .header {
            background: linear-gradient(45deg, #007bff, #0056b3);
            padding: 20px;
            box-shadow: 0 2px 4px rgba(0,0,0,0.1);
        }
        
        .nav ul {
            list-style: none;
            display: flex;
            gap: 20px;
        }
        
        @media (max-width: 768px) {
            .header {
                padding: 10px;
            }
            .nav ul {
                flex-direction: column;
            }
        }
        '''
        
        dialog.input_text.setPlainText(complex_css)
        dialog.format_css()
        
        complex_formatted = dialog.output_text.toPlainText()
        assert "body" in complex_formatted
        assert "header" in complex_formatted
        assert "nav" in complex_formatted
        print("✅ Complex CSS formatting works")
        
        # Test analysis with complex CSS
        dialog.analyze_css()
        complex_analysis = dialog.analysis_text.toPlainText()
        assert "media" in complex_analysis.lower() or "selector" in complex_analysis.lower()
        print("✅ Complex CSS analysis works")
        
        print("\n🎉 All CSS Formatter Tests Passed!")
        print("\n📋 Test Results Summary:")
        print("✅ Dialog creation - Working")
        print("✅ UI components - Working")
        print("✅ Output tabs - Working")
        print("✅ Welcome message - Working")
        print("✅ CSS formatting - Working")
        print("✅ CSS minification - Working")
        print("✅ CSS analysis - Working")
        print("✅ Complex CSS handling - Working")
        
        print("\n🎨 CSS Formatter Tool is ready!")
        print("\n🚀 Access Methods:")
        print("- Tools menu: 🎨 CSS Formatter (Ctrl+Shift+S)")
        print("- Direct execution: python css_formatter_tool.py")
        
        return True
        
    except Exception as e:
        print(f"\n❌ Test failed: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    success = test_css_formatter()
    sys.exit(0 if success else 1)