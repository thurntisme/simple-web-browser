#!/usr/bin/env python3
"""
Test script for the JSON formatter tool.
"""

import sys
from PyQt5.QtCore import Qt
from PyQt5.QtWidgets import QApplication

def test_json_formatter():
    """Test the JSON formatter tool"""
    
    print("🔧 Testing JSON Formatter Tool")
    print("=" * 50)
    
    # Set Qt attributes before creating QApplication
    QApplication.setAttribute(Qt.AA_ShareOpenGLContexts)
    
    app = QApplication.instance()
    if app is None:
        app = QApplication(sys.argv)
    
    try:
        from json_formatter_tool import JsonFormatterDialog
        
        # Create dialog
        dialog = JsonFormatterDialog()
        print("✅ JSON formatter dialog created successfully")
        
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
        assert "Welcome to JSON Pretty Formatter" in welcome_content
        print("✅ Welcome message displayed")
        
        # Test JSON formatting with valid JSON
        test_json = '{"name": "John", "age": 30, "city": "New York"}'
        dialog.input_text.setPlainText(test_json)
        
        # Simulate format button click
        dialog.format_json()
        
        # Check if formatting worked
        formatted_output = dialog.output_text.toPlainText()
        assert "name" in formatted_output
        assert "John" in formatted_output
        print("✅ JSON formatting works")
        
        # Test minify functionality
        dialog.minify_json()
        minified_output = dialog.output_text.toPlainText()
        assert len(minified_output) < len(formatted_output)
        print("✅ JSON minification works")
        
        # Test analysis functionality
        dialog.analyze_json()
        analysis_output = dialog.analysis_text.toPlainText()
        assert "JSON Structure Analysis" in analysis_output or "objects" in analysis_output.lower()
        print("✅ JSON analysis works")
        
        # Test error handling with invalid JSON
        dialog.input_text.setPlainText('{"invalid": json}')
        dialog.format_json()
        status_output = dialog.status_text.toPlainText()
        assert "Error" in status_output or "error" in status_output.lower()
        print("✅ Error handling works")
        
        print("\n🎉 All JSON Formatter Tests Passed!")
        print("\n📋 Test Results Summary:")
        print("✅ Dialog creation - Working")
        print("✅ UI components - Working")
        print("✅ Output tabs - Working")
        print("✅ Welcome message - Working")
        print("✅ JSON formatting - Working")
        print("✅ JSON minification - Working")
        print("✅ JSON analysis - Working")
        print("✅ Error handling - Working")
        
        print("\n🔧 JSON Formatter Tool is ready!")
        print("\n🚀 Access Methods:")
        print("- Tools menu: 🔧 JSON Formatter (Ctrl+Shift+J)")
        print("- Direct execution: python json_formatter_tool.py")
        
        return True
        
    except Exception as e:
        print(f"\n❌ Test failed: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    success = test_json_formatter()
    sys.exit(0 if success else 1)