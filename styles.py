"""
Modern styling system for the browser application.
Contains CSS styles and themes for a professional look.
"""

# Color palette for modern dark theme
COLORS = {
    'primary': '#2D3748',           # Dark blue-gray
    'secondary': '#4A5568',         # Medium gray
    'accent': '#3182CE',            # Blue accent
    'success': '#38A169',           # Green
    'warning': '#D69E2E',           # Orange
    'danger': '#E53E3E',            # Red
    'background': '#1A202C',        # Very dark background
    'surface': '#2D3748',           # Card/surface color
    'text_primary': '#FFFFFF',      # White text
    'text_secondary': '#A0AEC0',    # Light gray text
    'border': '#4A5568',            # Border color
    'hover': '#4299E1',             # Hover blue
    'active': '#2B6CB0',            # Active blue
}

# Modern application stylesheet
APP_STYLESHEET = f"""
/* Main Application Styling */
QMainWindow {{
    background-color: {COLORS['background']};
    color: {COLORS['text_primary']};
    font-family: 'Segoe UI', 'San Francisco', 'Helvetica Neue', Arial, sans-serif;
    font-size: 14px;
}}

/* Toolbar Styling */
QToolBar {{
    background: qlineargradient(x1: 0, y1: 0, x2: 0, y2: 1,
                                stop: 0 {COLORS['primary']}, 
                                stop: 1 {COLORS['secondary']});
    border: none;
    spacing: 8px;
    padding: 8px;
    min-height: 48px;
}}

QToolBar::separator {{
    background-color: {COLORS['border']};
    width: 1px;
    margin: 8px 4px;
}}

/* Action Buttons in Toolbar */
QAction {{
    color: {COLORS['text_primary']};
    padding: 8px 16px;
    border-radius: 6px;
    font-weight: 500;
}}

QToolBar QToolButton {{
    background-color: transparent;
    color: {COLORS['text_primary']};
    border: 1px solid transparent;
    border-radius: 6px;
    padding: 8px 16px;
    margin: 2px;
    font-weight: 500;
    min-width: 60px;
}}

QToolBar QToolButton:hover {{
    background-color: {COLORS['hover']};
    border-color: {COLORS['hover']};
}}

QToolBar QToolButton:pressed {{
    background-color: {COLORS['active']};
}}

/* URL Bar Styling */
QLineEdit {{
    background-color: {COLORS['surface']};
    border: 2px solid {COLORS['border']};
    border-radius: 8px;
    padding: 12px 16px;
    color: {COLORS['text_primary']};
    font-size: 14px;
    min-height: 20px;
}}

QLineEdit:focus {{
    border-color: {COLORS['accent']};
    background-color: #374151;
}}

QLineEdit:hover {{
    border-color: {COLORS['hover']};
}}

/* Push Buttons */
QPushButton {{
    background-color: {COLORS['surface']};
    border: 2px solid {COLORS['border']};
    border-radius: 8px;
    color: {COLORS['text_primary']};
    padding: 10px 16px;
    font-weight: 500;
    min-width: 80px;
}}

QPushButton:hover {{
    background-color: {COLORS['hover']};
    border-color: {COLORS['hover']};
}}

QPushButton:pressed {{
    background-color: {COLORS['active']};
}}

QPushButton:checked {{
    background-color: {COLORS['accent']};
    border-color: {COLORS['accent']};
}}

/* Special button styles */
QPushButton#bookmarkBtn {{
    font-size: 16px;
    min-width: 30px;
    padding: 8px;
}}

QPushButton#openWithBtn {{
    font-size: 14px;
    min-width: 35px;
    padding: 8px;
}}

/* Tab Widget Styling */
QTabWidget::pane {{
    border: 1px solid {COLORS['border']};
    background-color: {COLORS['background']};
    border-radius: 8px;
}}

QTabBar::tab {{
    background: qlineargradient(x1: 0, y1: 0, x2: 0, y2: 1,
                                stop: 0 {COLORS['surface']}, 
                                stop: 1 {COLORS['secondary']});
    border: 1px solid {COLORS['border']};
    border-bottom: none;
    color: {COLORS['text_secondary']};
    padding: 12px 20px;
    margin-right: 2px;
    border-top-left-radius: 8px;
    border-top-right-radius: 8px;
    min-width: 120px;
}}

QTabBar::tab:selected {{
    background: qlineargradient(x1: 0, y1: 0, x2: 0, y2: 1,
                                stop: 0 {COLORS['accent']}, 
                                stop: 1 {COLORS['hover']});
    color: {COLORS['text_primary']};
    font-weight: 600;
}}

QTabBar::tab:hover:!selected {{
    background: qlineargradient(x1: 0, y1: 0, x2: 0, y2: 1,
                                stop: 0 {COLORS['hover']}, 
                                stop: 1 {COLORS['secondary']});
    color: {COLORS['text_primary']};
}}

/* Menu Bar Styling */
QMenuBar {{
    background-color: {COLORS['primary']};
    color: {COLORS['text_primary']};
    border-bottom: 1px solid {COLORS['border']};
    padding: 4px;
}}

QMenuBar::item {{
    background-color: transparent;
    padding: 8px 16px;
    border-radius: 4px;
}}

QMenuBar::item:selected {{
    background-color: {COLORS['hover']};
}}

QMenuBar::item:pressed {{
    background-color: {COLORS['active']};
}}

/* Menu Styling */
QMenu {{
    background-color: {COLORS['surface']};
    border: 1px solid {COLORS['border']};
    border-radius: 8px;
    padding: 8px;
    color: {COLORS['text_primary']};
}}

QMenu::item {{
    padding: 8px 16px;
    border-radius: 4px;
    margin: 2px;
}}

QMenu::item:selected {{
    background-color: {COLORS['hover']};
}}

QMenu::separator {{
    height: 1px;
    background-color: {COLORS['border']};
    margin: 4px 8px;
}}

/* Status Bar Styling */
QStatusBar {{
    background: qlineargradient(x1: 0, y1: 0, x2: 0, y2: 1,
                                stop: 0 {COLORS['primary']}, 
                                stop: 1 {COLORS['secondary']});
    border-top: 1px solid {COLORS['border']};
    color: {COLORS['text_primary']};
    padding: 4px;
}}

QStatusBar QLabel {{
    color: {COLORS['text_primary']};
    padding: 4px 8px;
}}

/* Progress Bar Styling */
QProgressBar {{
    border: 2px solid {COLORS['border']};
    border-radius: 8px;
    background-color: {COLORS['surface']};
    text-align: center;
    color: {COLORS['text_primary']};
    font-weight: 500;
}}

QProgressBar::chunk {{
    background: qlineargradient(x1: 0, y1: 0, x2: 1, y2: 0,
                                stop: 0 {COLORS['accent']}, 
                                stop: 1 {COLORS['hover']});
    border-radius: 6px;
}}

/* Splitter Styling */
QSplitter::handle {{
    background-color: {COLORS['border']};
    width: 2px;
    height: 2px;
}}

QSplitter::handle:hover {{
    background-color: {COLORS['accent']};
}}

/* Scroll Bar Styling */
QScrollBar:vertical {{
    background-color: {COLORS['surface']};
    width: 12px;
    border-radius: 6px;
}}

QScrollBar::handle:vertical {{
    background-color: {COLORS['accent']};
    border-radius: 6px;
    min-height: 20px;
}}

QScrollBar::handle:vertical:hover {{
    background-color: {COLORS['hover']};
}}

QScrollBar:horizontal {{
    background-color: {COLORS['surface']};
    height: 12px;
    border-radius: 6px;
}}

QScrollBar::handle:horizontal {{
    background-color: {COLORS['accent']};
    border-radius: 6px;
    min-width: 20px;
}}

QScrollBar::handle:horizontal:hover {{
    background-color: {COLORS['hover']};
}}

/* Dialog Styling */
QDialog {{
    background-color: {COLORS['background']};
    color: {COLORS['text_primary']};
    border-radius: 12px;
}}

QGroupBox {{
    font-weight: 600;
    border: 2px solid {COLORS['border']};
    border-radius: 8px;
    margin-top: 12px;
    padding-top: 8px;
    color: {COLORS['text_primary']};
}}

QGroupBox::title {{
    subcontrol-origin: margin;
    left: 16px;
    padding: 0 8px 0 8px;
    color: {COLORS['accent']};
}}

/* Combo Box Styling */
QComboBox {{
    background-color: {COLORS['surface']};
    border: 2px solid {COLORS['border']};
    border-radius: 8px;
    padding: 8px 12px;
    color: {COLORS['text_primary']};
    min-width: 120px;
}}

QComboBox:hover {{
    border-color: {COLORS['hover']};
}}

QComboBox::drop-down {{
    border: none;
    width: 20px;
}}

QComboBox::down-arrow {{
    image: none;
    border-left: 5px solid transparent;
    border-right: 5px solid transparent;
    border-top: 5px solid {COLORS['text_primary']};
    margin-right: 5px;
}}

QComboBox QAbstractItemView {{
    background-color: {COLORS['surface']};
    border: 1px solid {COLORS['border']};
    border-radius: 8px;
    selection-background-color: {COLORS['hover']};
    color: {COLORS['text_primary']};
}}

/* Spin Box Styling */
QSpinBox {{
    background-color: {COLORS['surface']};
    border: 2px solid {COLORS['border']};
    border-radius: 8px;
    padding: 8px 12px;
    color: {COLORS['text_primary']};
}}

QSpinBox:hover {{
    border-color: {COLORS['hover']};
}}

QSpinBox:focus {{
    border-color: {COLORS['accent']};
}}

/* Check Box Styling */
QCheckBox {{
    color: {COLORS['text_primary']};
    spacing: 8px;
}}

QCheckBox::indicator {{
    width: 18px;
    height: 18px;
    border: 2px solid {COLORS['border']};
    border-radius: 4px;
    background-color: {COLORS['surface']};
}}

QCheckBox::indicator:checked {{
    background-color: {COLORS['accent']};
    border-color: {COLORS['accent']};
}}

QCheckBox::indicator:hover {{
    border-color: {COLORS['hover']};
}}
"""

# Special profile label styling
PROFILE_LABEL_STYLE = f"""
QLabel {{
    background: qlineargradient(x1: 0, y1: 0, x2: 1, y2: 0,
                                stop: 0 {COLORS['success']}, 
                                stop: 1 #48BB78);
    color: white;
    padding: 6px 12px;
    border-radius: 6px;
    font-weight: 600;
    font-size: 12px;
}}
"""

# History toggle button styles
HISTORY_BUTTON_ENABLED_STYLE = f"""
QPushButton {{
    background: qlineargradient(x1: 0, y1: 0, x2: 1, y2: 0,
                                stop: 0 {COLORS['success']}, 
                                stop: 1 #48BB78);
    border: 2px solid {COLORS['success']};
    color: white;
    font-weight: 600;
    border-radius: 6px;
    padding: 8px 12px;
}}
QPushButton:hover {{
    background: qlineargradient(x1: 0, y1: 0, x2: 1, y2: 0,
                                stop: 0 #48BB78, 
                                stop: 1 {COLORS['success']});
}}
"""

HISTORY_BUTTON_DISABLED_STYLE = f"""
QPushButton {{
    background: qlineargradient(x1: 0, y1: 0, x2: 1, y2: 0,
                                stop: 0 {COLORS['danger']}, 
                                stop: 1 #F56565);
    border: 2px solid {COLORS['danger']};
    color: white;
    font-weight: 600;
    border-radius: 6px;
    padding: 8px 12px;
}}
QPushButton:hover {{
    background: qlineargradient(x1: 0, y1: 0, x2: 1, y2: 0,
                                stop: 1 #F56565, 
                                stop: 0 {COLORS['danger']});
}}
"""

# Bookmark button styles
BOOKMARK_BUTTON_ACTIVE_STYLE = f"""
QPushButton {{
    background: qlineargradient(x1: 0, y1: 0, x2: 1, y2: 0,
                                stop: 0 {COLORS['warning']}, 
                                stop: 1 #ECC94B);
    border: 2px solid {COLORS['warning']};
    color: white;
    font-weight: 600;
    border-radius: 6px;
    font-size: 16px;
}}
QPushButton:hover {{
    background: qlineargradient(x1: 0, y1: 0, x2: 1, y2: 0,
                                stop: 0 #ECC94B, 
                                stop: 1 {COLORS['warning']});
}}
"""

BOOKMARK_BUTTON_INACTIVE_STYLE = f"""
QPushButton {{
    background-color: {COLORS['surface']};
    border: 2px solid {COLORS['border']};
    color: {COLORS['text_secondary']};
    font-weight: 500;
    border-radius: 6px;
    font-size: 16px;
}}
QPushButton:hover {{
    background-color: {COLORS['hover']};
    border-color: {COLORS['hover']};
    color: {COLORS['text_primary']};
}}
"""


def apply_modern_theme(app):
    """Apply the modern dark theme to the entire application (deprecated - use apply_theme)"""
    apply_theme(app, "dark")


def get_profile_label_style():
    """Get the profile label styling"""
    if current_theme == "light":
        return f"""
        QLabel {{
            background-color: {LIGHT_COLORS['accent']};
            color: {LIGHT_COLORS['background']};
            padding: 4px 8px;
            font-weight: bold;
            font-size: 12px;
        }}
        """
    else:
        return PROFILE_LABEL_STYLE


def get_history_button_style(enabled):
    """Get history button style based on state"""
    if current_theme == "light":
        if enabled:
            return f"""
            QPushButton {{
                background-color: {LIGHT_COLORS['accent']};
                border: 1px solid {LIGHT_COLORS['accent']};
                color: {LIGHT_COLORS['background']};
                font-weight: bold;
                padding: 6px 10px;
            }}
            QPushButton:hover {{
                background-color: {LIGHT_COLORS['text_secondary']};
                border: 1px solid {LIGHT_COLORS['text_secondary']};
            }}
            """
        else:
            return f"""
            QPushButton {{
                background-color: {LIGHT_COLORS['surface']};
                border: 1px solid {LIGHT_COLORS['border']};
                color: {LIGHT_COLORS['text_secondary']};
                font-weight: normal;
                padding: 6px 10px;
            }}
            QPushButton:hover {{
                background-color: {LIGHT_COLORS['hover']};
                border: 1px solid {LIGHT_COLORS['text_secondary']};
            }}
            """
    else:
        return HISTORY_BUTTON_ENABLED_STYLE if enabled else HISTORY_BUTTON_DISABLED_STYLE


def get_bookmark_button_style(is_bookmarked):
    """Get bookmark button style based on state"""
    if current_theme == "light":
        if is_bookmarked:
            return f"""
            QPushButton {{
                background-color: {LIGHT_COLORS['accent']};
                border: 1px solid {LIGHT_COLORS['accent']};
                color: {LIGHT_COLORS['background']};
                font-weight: bold;
                font-size: 16px;
            }}
            QPushButton:hover {{
                background-color: {LIGHT_COLORS['text_secondary']};
                border: 1px solid {LIGHT_COLORS['text_secondary']};
            }}
            """
        else:
            return f"""
            QPushButton {{
                background-color: {LIGHT_COLORS['surface']};
                border: 1px solid {LIGHT_COLORS['border']};
                color: {LIGHT_COLORS['text_secondary']};
                font-weight: normal;
                font-size: 16px;
            }}
            QPushButton:hover {{
                background-color: {LIGHT_COLORS['hover']};
                border: 1px solid {LIGHT_COLORS['text_secondary']};
                color: {LIGHT_COLORS['text_primary']};
            }}
            """
    else:
        return BOOKMARK_BUTTON_ACTIVE_STYLE if is_bookmarked else BOOKMARK_BUTTON_INACTIVE_STYLE

# Light theme color palette - Minimal design with only white, black, and gray
LIGHT_COLORS = {
    'primary': '#FFFFFF',           # Pure white
    'secondary': '#F5F5F5',         # Light gray
    'accent': '#000000',            # Pure black
    'success': '#666666',           # Medium gray
    'warning': '#333333',           # Dark gray
    'danger': '#000000',            # Pure black
    'background': '#FFFFFF',        # Pure white background
    'surface': '#F5F5F5',           # Light gray surface
    'text_primary': '#000000',      # Pure black text
    'text_secondary': '#666666',    # Medium gray text
    'border': '#CCCCCC',            # Light gray border
    'hover': '#E5E5E5',             # Light gray hover
    'active': '#CCCCCC',            # Medium gray active
}

# Minimal light theme stylesheet - no border radius, clean lines
LIGHT_APP_STYLESHEET = f"""
/* Minimal Light Theme - Clean, no border radius */
QMainWindow {{
    background-color: {LIGHT_COLORS['background']};
    color: {LIGHT_COLORS['text_primary']};
    font-family: 'Segoe UI', Arial, sans-serif;
    font-size: 14px;
}}

/* Toolbar Styling - Clean and minimal */
QToolBar {{
    background-color: {LIGHT_COLORS['primary']};
    border-bottom: 1px solid {LIGHT_COLORS['border']};
    spacing: 4px;
    padding: 4px;
    min-height: 40px;
}}

QToolBar::separator {{
    background-color: {LIGHT_COLORS['border']};
    width: 1px;
    margin: 4px 2px;
}}

QToolBar QToolButton {{
    background-color: transparent;
    color: {LIGHT_COLORS['text_primary']};
    border: 1px solid transparent;
    padding: 6px 12px;
    margin: 1px;
    font-weight: normal;
    min-width: 50px;
}}

QToolBar QToolButton:hover {{
    background-color: {LIGHT_COLORS['hover']};
    border: 1px solid {LIGHT_COLORS['border']};
}}

QToolBar QToolButton:pressed {{
    background-color: {LIGHT_COLORS['active']};
}}

/* URL Bar - Clean rectangular design */
QLineEdit {{
    background-color: {LIGHT_COLORS['background']};
    border: 1px solid {LIGHT_COLORS['border']};
    padding: 8px 12px;
    color: {LIGHT_COLORS['text_primary']};
    font-size: 14px;
    min-height: 20px;
}}

QLineEdit:focus {{
    border: 2px solid {LIGHT_COLORS['accent']};
}}

QLineEdit:hover {{
    border: 1px solid {LIGHT_COLORS['text_secondary']};
}}

/* Push Buttons - Minimal rectangular design */
QPushButton {{
    background-color: {LIGHT_COLORS['surface']};
    border: 1px solid {LIGHT_COLORS['border']};
    color: {LIGHT_COLORS['text_primary']};
    padding: 8px 12px;
    font-weight: normal;
    min-width: 60px;
}}

QPushButton:hover {{
    background-color: {LIGHT_COLORS['hover']};
    border: 1px solid {LIGHT_COLORS['text_secondary']};
}}

QPushButton:pressed {{
    background-color: {LIGHT_COLORS['active']};
}}

QPushButton:checked {{
    background-color: {LIGHT_COLORS['accent']};
    color: {LIGHT_COLORS['background']};
}}

/* Tab Widget - Clean rectangular tabs */
QTabWidget::pane {{
    border: 1px solid {LIGHT_COLORS['border']};
    background-color: {LIGHT_COLORS['background']};
}}

QTabBar::tab {{
    background-color: {LIGHT_COLORS['surface']};
    border: 1px solid {LIGHT_COLORS['border']};
    border-bottom: none;
    color: {LIGHT_COLORS['text_secondary']};
    padding: 8px 16px;
    margin-right: 1px;
    min-width: 100px;
}}

QTabBar::tab:selected {{
    background-color: {LIGHT_COLORS['background']};
    color: {LIGHT_COLORS['text_primary']};
    font-weight: bold;
    border-bottom: 1px solid {LIGHT_COLORS['background']};
}}

QTabBar::tab:hover:!selected {{
    background-color: {LIGHT_COLORS['hover']};
    color: {LIGHT_COLORS['text_primary']};
}}

/* Menu Bar - Clean and minimal */
QMenuBar {{
    background-color: {LIGHT_COLORS['primary']};
    color: {LIGHT_COLORS['text_primary']};
    border-bottom: 1px solid {LIGHT_COLORS['border']};
    padding: 2px;
}}

QMenuBar::item {{
    background-color: transparent;
    padding: 6px 12px;
}}

QMenuBar::item:selected {{
    background-color: {LIGHT_COLORS['hover']};
}}

/* Menu - Clean dropdown */
QMenu {{
    background-color: {LIGHT_COLORS['background']};
    border: 1px solid {LIGHT_COLORS['border']};
    padding: 4px;
    color: {LIGHT_COLORS['text_primary']};
}}

QMenu::item {{
    padding: 6px 12px;
    margin: 1px;
}}

QMenu::item:selected {{
    background-color: {LIGHT_COLORS['hover']};
}}

QMenu::separator {{
    height: 1px;
    background-color: {LIGHT_COLORS['border']};
    margin: 2px 4px;
}}

/* Status Bar - Clean bottom bar */
QStatusBar {{
    background-color: {LIGHT_COLORS['surface']};
    border-top: 1px solid {LIGHT_COLORS['border']};
    color: {LIGHT_COLORS['text_primary']};
    padding: 2px;
}}

QStatusBar QLabel {{
    color: {LIGHT_COLORS['text_primary']};
    padding: 2px 6px;
}}

/* Progress Bar - Simple rectangular */
QProgressBar {{
    border: 1px solid {LIGHT_COLORS['border']};
    background-color: {LIGHT_COLORS['surface']};
    text-align: center;
    color: {LIGHT_COLORS['text_primary']};
    font-weight: normal;
    height: 16px;
}}

QProgressBar::chunk {{
    background-color: {LIGHT_COLORS['accent']};
}}

/* Splitter - Simple line */
QSplitter::handle {{
    background-color: {LIGHT_COLORS['border']};
    width: 1px;
    height: 1px;
}}

QSplitter::handle:hover {{
    background-color: {LIGHT_COLORS['text_secondary']};
}}

/* Scroll Bars - Minimal design */
QScrollBar:vertical {{
    background-color: {LIGHT_COLORS['surface']};
    width: 16px;
}}

QScrollBar::handle:vertical {{
    background-color: {LIGHT_COLORS['text_secondary']};
    min-height: 20px;
}}

QScrollBar::handle:vertical:hover {{
    background-color: {LIGHT_COLORS['accent']};
}}

QScrollBar:horizontal {{
    background-color: {LIGHT_COLORS['surface']};
    height: 16px;
}}

QScrollBar::handle:horizontal {{
    background-color: {LIGHT_COLORS['text_secondary']};
    min-width: 20px;
}}

QScrollBar::handle:horizontal:hover {{
    background-color: {LIGHT_COLORS['accent']};
}}

/* Dialog - Clean and simple */
QDialog {{
    background-color: {LIGHT_COLORS['background']};
    color: {LIGHT_COLORS['text_primary']};
}}

QGroupBox {{
    font-weight: bold;
    border: 1px solid {LIGHT_COLORS['border']};
    margin-top: 8px;
    padding-top: 4px;
    color: {LIGHT_COLORS['text_primary']};
}}

QGroupBox::title {{
    subcontrol-origin: margin;
    left: 8px;
    padding: 0 4px 0 4px;
    color: {LIGHT_COLORS['text_primary']};
}}

/* Combo Box - Simple dropdown */
QComboBox {{
    background-color: {LIGHT_COLORS['background']};
    border: 1px solid {LIGHT_COLORS['border']};
    padding: 6px 8px;
    color: {LIGHT_COLORS['text_primary']};
    min-width: 100px;
}}

QComboBox:hover {{
    border: 1px solid {LIGHT_COLORS['text_secondary']};
}}

QComboBox::drop-down {{
    border: none;
    width: 16px;
}}

QComboBox::down-arrow {{
    image: none;
    border-left: 4px solid transparent;
    border-right: 4px solid transparent;
    border-top: 4px solid {LIGHT_COLORS['text_primary']};
    margin-right: 4px;
}}

QComboBox QAbstractItemView {{
    background-color: {LIGHT_COLORS['background']};
    border: 1px solid {LIGHT_COLORS['border']};
    selection-background-color: {LIGHT_COLORS['hover']};
    color: {LIGHT_COLORS['text_primary']};
}}

/* Spin Box - Simple number input */
QSpinBox {{
    background-color: {LIGHT_COLORS['background']};
    border: 1px solid {LIGHT_COLORS['border']};
    padding: 6px 8px;
    color: {LIGHT_COLORS['text_primary']};
}}

QSpinBox:hover {{
    border: 1px solid {LIGHT_COLORS['text_secondary']};
}}

QSpinBox:focus {{
    border: 2px solid {LIGHT_COLORS['accent']};
}}

/* Check Box - Simple checkbox */
QCheckBox {{
    color: {LIGHT_COLORS['text_primary']};
    spacing: 6px;
}}

QCheckBox::indicator {{
    width: 16px;
    height: 16px;
    border: 1px solid {LIGHT_COLORS['border']};
    background-color: {LIGHT_COLORS['background']};
}}

QCheckBox::indicator:checked {{
    background-color: {LIGHT_COLORS['accent']};
}}

QCheckBox::indicator:hover {{
    border: 1px solid {LIGHT_COLORS['text_secondary']};
}}
"""

# Theme management
current_theme = "light"  # Default to light theme

def apply_theme(app, theme="dark"):
    """Apply the specified theme to the application"""
    global current_theme
    current_theme = theme
    
    if theme == "light":
        app.setStyleSheet(LIGHT_APP_STYLESHEET)
    else:
        app.setStyleSheet(APP_STYLESHEET)

def get_current_theme():
    """Get the current theme"""
    return current_theme

def toggle_theme(app):
    """Toggle between light and dark themes"""
    new_theme = "light" if current_theme == "dark" else "dark"
    apply_theme(app, new_theme)
    return new_theme