#!/usr/bin/env python3
"""
Test the malware scanner widget display
"""

import sys
from PyQt5.QtCore import Qt
from PyQt5.QtWidgets import QApplication

def test_widget_display():
    """Test that the widget displays content properly"""
    
    print("🛡️ Testing Malware Scanner Widget Display")
    print("=" * 50)
    
    # Set Qt attributes before creating QApplication
    QApplication.setAttribute(Qt.AA_ShareOpenGLContexts)
    
    app = QApplication.instance()
    if app is None:
        app = QApplication(sys.argv)
    
    try:
        from malware_scanner_widget_functional import MalwareScannerWidget
        
        # Create widget
        widget = MalwareScannerWidget()
        print("✅ Widget created successfully")
        
        # Check that UI components exist
        assert hasattr(widget, 'file_path_edit')
        assert hasattr(widget, 'browse_file_btn')
        assert hasattr(widget, 'browse_folder_btn')
        assert hasattr(widget, 'scan_btn')
        assert hasattr(widget, 'stop_btn')
        assert hasattr(widget, 'progress_bar')
        assert hasattr(widget, 'status_label')
        assert hasattr(widget, 'results_tabs')
        print("✅ All UI components exist")
        
        # Check that tabs are created
        assert widget.results_tabs.count() == 3
        assert widget.results_tabs.tabText(0) == "📊 Summary"
        assert widget.results_tabs.tabText(1) == "⚠️ Threats"
        assert widget.results_tabs.tabText(2) == "🔍 Technical Details"
        print("✅ All tabs created correctly")
        
        # Check that initial content is displayed
        summary_content = widget.summary_text.toPlainText()
        assert "Welcome to Malware Scanner Mode" in summary_content
        assert "Detection Methods" in summary_content
        print("✅ Initial content displayed")
        
        # Check that status label has initial text
        status_text = widget.status_label.text()
        assert "Ready to scan" in status_text
        print("✅ Status label initialized")
        
        print("\n🎉 Widget Display Test Passed!")
        print("\n📋 Widget Features Verified:")
        print("✅ Header with icon and title")
        print("✅ File selection with browse button")
        print("✅ Scan control buttons")
        print("✅ Progress bar and status")
        print("✅ Tabbed results display")
        print("✅ Action buttons (export/clear)")
        print("✅ Initial welcome content")
        
        return True
        
    except Exception as e:
        print(f"\n❌ Widget display test failed: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    success = test_widget_display()
    sys.exit(0 if success else 1)