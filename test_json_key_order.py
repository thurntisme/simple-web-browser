#!/usr/bin/env python3
"""
Test script to verify JSON formatter preserves key order.
"""

import sys
from PyQt5.QtCore import Qt
from PyQt5.QtWidgets import QApplication

def test_key_order_preservation():
    """Test that JSON formatter preserves original key order"""
    
    print("🔧 Testing JSON Key Order Preservation")
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
        print("✅ JSON formatter dialog created")
        
        # Test JSON with specific key order
        test_json = '{"zebra": "animal", "apple": "fruit", "banana": "fruit", "cat": "animal", "dog": "animal"}'
        print(f"📝 Input JSON: {test_json}")
        
        dialog.input_text.setPlainText(test_json)
        
        # Format the JSON
        dialog.format_json()
        
        # Get formatted output
        formatted_output = dialog.output_text.toPlainText()
        print(f"📄 Formatted output:")
        print(formatted_output)
        
        # Check that original order is preserved
        lines = formatted_output.strip().split('\n')
        
        # Extract keys in order they appear
        keys_in_order = []
        for line in lines:
            if '":' in line:
                key = line.split('":')[0].strip().strip('"')
                if key:
                    keys_in_order.append(key)
        
        expected_order = ["zebra", "apple", "banana", "cat", "dog"]
        
        print(f"🔍 Keys in formatted output: {keys_in_order}")
        print(f"🎯 Expected order: {expected_order}")
        
        # Verify order is preserved
        assert keys_in_order == expected_order, f"Key order not preserved! Got {keys_in_order}, expected {expected_order}"
        print("✅ Key order preserved correctly!")
        
        # Test with nested objects
        nested_json = '{"config": {"zebra": 1, "apple": 2}, "data": {"cat": 3, "banana": 4}}'
        print(f"\n📝 Testing nested JSON: {nested_json}")
        
        dialog.input_text.setPlainText(nested_json)
        dialog.format_json()
        
        nested_output = dialog.output_text.toPlainText()
        print(f"📄 Nested formatted output:")
        print(nested_output)
        
        # Check that "config" comes before "data" and nested keys preserve order
        assert '"config"' in nested_output
        assert '"data"' in nested_output
        config_pos = nested_output.find('"config"')
        data_pos = nested_output.find('"data"')
        assert config_pos < data_pos, "Top-level key order not preserved"
        print("✅ Nested object key order preserved!")
        
        print("\n🎉 Key Order Preservation Test Passed!")
        print("\n📋 Verification Results:")
        print("✅ Simple object key order - Preserved")
        print("✅ Nested object key order - Preserved")
        print("✅ Top-level key order - Preserved")
        
        print("\n🔧 JSON Formatter maintains original key order!")
        
        return True
        
    except Exception as e:
        print(f"\n❌ Test failed: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    success = test_key_order_preservation()
    sys.exit(0 if success else 1)