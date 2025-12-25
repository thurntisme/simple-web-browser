# Browser Code Structure

The browser code has been refactored into separate modules for better organization and maintainability.

## Features

### Browser Modes
The application now supports multiple modes accessible via the mode dropdown in the top-right corner:

1. **🌐 Web Browser Mode** (Default) - Standard web browsing with navigation toolbar
2. **🔧 API Tester Mode** - API testing interface (placeholder for future implementation)
3. **💻 Command Line Mode** - Integrated terminal for command execution
4. **📄 PDF Reader Mode** - Built-in PDF document viewer

### PDF Reader Features
- **File Support**: Open PDF files via file dialog or drag-and-drop
- **Navigation**: Previous/Next page buttons, keyboard shortcuts (Arrow keys, Page Up/Down, Home/End)
- **Zoom Controls**: 25% to 400% zoom levels with preset options
- **Fit Options**: Fit to width or fit entire page to window
- **Keyboard Shortcuts**: 
  - `Ctrl+Shift+P` - Switch to PDF mode
  - Arrow keys - Navigate pages
  - Home/End - Jump to first/last page

### Requirements for PDF Reader
The PDF reader requires the PyMuPDF library:
```bash
pip install PyMuPDF
```

## Code Reduction

- **Original main.py**: 661 lines
- **Refactored main.py**: 234 lines
- **Reduction**: 64% smaller!

## Module Files

### Core Modules

1. **main.py** - Main application window and UI setup

   - Contains MainWindow class
   - Handles UI initialization and event connections
   - Uses manager classes for data operations

2. **constants.py** - Application constants and configuration
   - File paths
   - Default values
   - Application metadata

### Manager Modules

3. **profile_manager.py** - Profile management

   - ProfileManager class
   - Create, switch, and manage browser profiles
   - Handle profile directories and configuration

4. **history_manager.py** - Browsing history management

   - HistoryManager class
   - Load, save, add, and clear history
   - Respects history enabled/disabled setting

5. **bookmark_manager.py** - Bookmark management

   - BookmarkManager class
   - BookmarkManagerDialog class
   - Add, remove, update bookmarks
   - Bookmark management UI dialog

6. **config_manager.py** - Configuration management
   - ConfigManager class
   - Load and save profile-specific settings
   - Get/set configuration values

### UI Modules

7. **pdf_viewer.py** - PDF document viewer
   - PDFViewerWidget class
   - PDF rendering with PyMuPDF
   - Zoom, navigation, and fit controls
   - Drag-and-drop support for PDF files

### Helper Modules

8. **ui_helpers.py** - UI update helper functions
   - Menu update functions
   - Button state updates
   - Profile switching logic
   - Bookmark and history UI operations

## Data Storage Structure

```
storage/
├── profiles.json          # Current active profile
└── profiles/
    ├── default/
    │   ├── config.json    # Profile settings
    │   ├── history.json   # Browsing history
    │   └── bookmarks.json # Bookmarks
    └── work/
        ├── config.json
        ├── history.json
        └── bookmarks.json
```

## Usage in main.py

```python
# Initialize managers
self.profile_manager = ProfileManager()
self.config_manager = ConfigManager(self.profile_manager)
self.history_manager = HistoryManager(self.profile_manager)
self.bookmark_manager = BookmarkManager(self.profile_manager)

# Use managers
self.history_manager.add(url, title)
self.bookmark_manager.add(url, title)
self.config_manager.set("key", value)
```

## Benefits

- **Separation of Concerns**: Each module handles a specific feature
- **Reusability**: Managers can be used independently
- **Maintainability**: Easier to find and fix bugs
- **Testability**: Each module can be tested separately
- **Scalability**: Easy to add new features without cluttering main.py
