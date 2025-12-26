#!/usr/bin/env python3
"""
Test the folder scanning functionality
"""

import sys
import os
import tempfile
from PyQt5.QtCore import Qt
from PyQt5.QtWidgets import QApplication

def test_folder_scan():
    """Test that the folder scanning functionality works"""
    
    print("📁 Testing Folder Scan Functionality")
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
        
        # Check that folder browse button exists
        assert hasattr(widget, 'browse_folder_btn')
        assert widget.browse_folder_btn.text() == "📁 Browse Folders"
        print("✅ Folder browse button exists")
        
        # Check that file browse button still exists
        assert hasattr(widget, 'browse_file_btn')
        assert widget.browse_file_btn.text() == "📂 Browse Files"
        print("✅ File browse button exists")
        
        # Check that browse_folder method exists
        assert hasattr(widget, 'browse_folder')
        assert callable(widget.browse_folder)
        print("✅ Folder browse method exists")
        
        # Check that placeholder text mentions folders
        placeholder = widget.file_path_edit.placeholderText()
        assert "folder" in placeholder.lower()
        print("✅ Placeholder text mentions folders")
        
        # Check that initial content mentions folder scanning
        initial_content = widget.summary_text.toPlainText()
        assert "folder" in initial_content.lower() or "directories" in initial_content.lower()
        print("✅ Initial content mentions folder scanning")
        
        # Check that finish_folder_scan method exists
        assert hasattr(widget, 'finish_folder_scan')
        assert callable(widget.finish_folder_scan)
        print("✅ Folder scan completion method exists")
        
        # Test with a temporary folder
        with tempfile.TemporaryDirectory() as temp_dir:
            # Create some test files
            test_files = [
                os.path.join(temp_dir, "test.txt"),
                os.path.join(temp_dir, "script.bat"),
                os.path.join(temp_dir, "document.pdf")
            ]
            
            for file_path in test_files:
                with open(file_path, 'w') as f:
                    f.write("test content")
            
            print(f"✅ Created test folder with {len(test_files)} files")
            
            # Set the folder path
            widget.file_path_edit.setText(temp_dir)
            
            # Verify the path is set
            assert widget.file_path_edit.text() == temp_dir
            print("✅ Folder path set successfully")
        
        print("\n🎉 Folder Scan Test Passed!")
        print("\n📋 Folder Scan Features Verified:")
        print("✅ Folder browse button")
        print("✅ Folder browse method")
        print("✅ Updated placeholder text")
        print("✅ Updated initial content")
        print("✅ Folder scan completion method")
        print("✅ Path setting functionality")
        
        return True
        
    except Exception as e:
        print(f"\n❌ Folder scan test failed: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    success = test_folder_scan()
    sys.exit(0 if success else 1)