#!/usr/bin/env python3
"""
Test script for the JavaScript formatter tool.
"""

import sys
from PyQt5.QtCore import Qt
from PyQt5.QtWidgets import QApplication

def test_js_formatter():
    """Test the JavaScript formatter tool"""
    
    print("⚡ Testing JavaScript Formatter Tool")
    print("=" * 50)
    
    # Set Qt attributes before creating QApplication
    QApplication.setAttribute(Qt.AA_ShareOpenGLContexts)
    
    app = QApplication.instance()
    if app is None:
        app = QApplication(sys.argv)
    
    try:
        from js_formatter_tool import JsFormatterDialog
        
        # Create dialog
        dialog = JsFormatterDialog()
        print("✅ JavaScript formatter dialog created successfully")
        
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
        assert "Welcome to JavaScript Pretty Formatter" in welcome_content
        print("✅ Welcome message displayed")
        
        # Test JavaScript formatting with valid JavaScript
        test_js = 'function greet(name) { console.log("Hello, " + name + "!"); } const users = [{ id: 1, name: "John" }];'
        dialog.input_text.setPlainText(test_js)
        
        # Simulate format button click
        dialog.format_js()
        
        # Check if formatting worked
        formatted_output = dialog.output_text.toPlainText()
        assert "function greet" in formatted_output
        assert "console.log" in formatted_output
        assert "const users" in formatted_output
        print("✅ JavaScript formatting works")
        
        # Test minify functionality
        dialog.minify_js()
        minified_output = dialog.output_text.toPlainText()
        assert len(minified_output) < len(formatted_output)
        assert "function greet(" in minified_output or "function greet" in minified_output
        print("✅ JavaScript minification works")
        
        # Test analysis functionality
        dialog.analyze_js()
        analysis_output = dialog.analysis_text.toPlainText()
        assert "JavaScript Code Analysis" in analysis_output or "functions" in analysis_output.lower()
        print("✅ JavaScript analysis works")
        
        # Test with more complex JavaScript
        complex_js = '''
        // Modern JavaScript example
        class User {
            constructor(name, email) {
                this.name = name;
                this.email = email;
            }
            
            async fetchData() {
                const response = await fetch('/api/user');
                return response.json();
            }
        }
        
        const users = [
            { id: 1, name: "John" },
            { id: 2, name: "Jane" }
        ];
        
        const greetUser = (user) => {
            console.log(`Hello, ${user.name}!`);
        };
        
        users.forEach(greetUser);
        '''
        
        dialog.input_text.setPlainText(complex_js)
        dialog.format_js()
        
        complex_formatted = dialog.output_text.toPlainText()
        assert "class User" in complex_formatted
        assert "async fetchData" in complex_formatted
        assert "const users" in complex_formatted
        assert "greetUser" in complex_formatted
        print("✅ Complex JavaScript formatting works")
        
        # Test analysis with complex JavaScript
        dialog.analyze_js()
        complex_analysis = dialog.analysis_text.toPlainText()
        assert "arrow" in complex_analysis.lower() or "es6" in complex_analysis.lower() or "class" in complex_analysis.lower()
        print("✅ Complex JavaScript analysis works")
        
        print("\n🎉 All JavaScript Formatter Tests Passed!")
        print("\n📋 Test Results Summary:")
        print("✅ Dialog creation - Working")
        print("✅ UI components - Working")
        print("✅ Output tabs - Working")
        print("✅ Welcome message - Working")
        print("✅ JavaScript formatting - Working")
        print("✅ JavaScript minification - Working")
        print("✅ JavaScript analysis - Working")
        print("✅ Complex JavaScript handling - Working")
        
        print("\n⚡ JavaScript Formatter Tool is ready!")
        print("\n🚀 Access Methods:")
        print("- Tools menu: ⚡ JavaScript Formatter (Ctrl+Shift+L)")
        print("- Direct execution: python js_formatter_tool.py")
        
        return True
        
    except Exception as e:
        print(f"\n❌ Test failed: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    success = test_js_formatter()
    sys.exit(0 if success else 1)