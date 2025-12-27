"""
Dialog classes for the browser application.
Contains AboutDialog and BrowserSettingsDialog.
"""

from PyQt5.QtCore import *
from PyQt5.QtWidgets import *
from PyQt5.QtGui import *
import os
from constants import *


class AboutDialog(QDialog):
    """About dialog showing application information"""
    
    def __init__(self, *args, **kwargs):
        super(AboutDialog, self).__init__(*args, **kwargs)

        QBtn = QDialogButtonBox.Ok
        self.buttonBox = QDialogButtonBox(QBtn)
        self.buttonBox.accepted.connect(self.accept)
        self.buttonBox.rejected.connect(self.reject)

        layout = QVBoxLayout()

        title = QLabel(APP_NAME)
        font = title.font()
        font.setPointSize(ABOUT_TITLE_FONT_SIZE)
        title.setFont(font)

        layout.addWidget(title)

        logo = QLabel()
        logo.setPixmap(QPixmap(os.path.join(IMAGES_DIR, ICON_APP_128)))
        layout.addWidget(logo)

        layout.addWidget(QLabel(f"Version {APP_VERSION}"))
        layout.addWidget(QLabel(APP_COPYRIGHT))

        for i in range(0, layout.count()):
            layout.itemAt(i).setAlignment(Qt.AlignHCenter)

        layout.addWidget(self.buttonBox)
        self.setLayout(layout)


class BrowserSettingsDialog(QDialog):
    """Dialog for browser settings configuration"""
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.parent_window = parent
        self.setWindowTitle("Browser Settings")
        self.setMinimumSize(500, 300)
        
        layout = QVBoxLayout()
        
        # Home URL setting
        home_group = QGroupBox("Home Page")
        home_layout = QVBoxLayout()
        
        self.home_url_input = QLineEdit()
        current_home = parent.config_manager.get("home_url", DEFAULT_HOME_URL)
        self.home_url_input.setText(current_home)
        self.home_url_input.setPlaceholderText("Enter home page URL")
        home_layout.addWidget(QLabel("Home URL:"))
        home_layout.addWidget(self.home_url_input)
        
        # Welcome page checkbox
        self.welcome_page_checkbox = QCheckBox("Set welcome page as homepage")
        use_welcome = parent.config_manager.get("use_welcome_page", True)
        self.welcome_page_checkbox.setChecked(use_welcome)
        self.welcome_page_checkbox.stateChanged.connect(self.toggle_welcome_page)
        home_layout.addWidget(self.welcome_page_checkbox)
        
        # Disable URL input if welcome page is enabled
        self.home_url_input.setEnabled(not use_welcome)
        
        home_group.setLayout(home_layout)
        layout.addWidget(home_group)
        
        # Search Engine setting
        search_group = QGroupBox("Search Engine")
        search_layout = QVBoxLayout()
        
        self.search_engine_combo = QComboBox()
        search_engines = {
            "DuckDuckGo": "https://duckduckgo.com/?q={}",
            "Google": "https://www.google.com/search?q={}",
            "Bing": "https://www.bing.com/search?q={}",
            "Yahoo": "https://search.yahoo.com/search?p={}",
        }
        
        current_search = parent.config_manager.get("search_engine", SEARCH_ENGINE_URL)
        
        for name, url in search_engines.items():
            self.search_engine_combo.addItem(name, url)
            if url == current_search:
                self.search_engine_combo.setCurrentText(name)
        
        search_layout.addWidget(QLabel("Default Search Engine:"))
        search_layout.addWidget(self.search_engine_combo)
        
        search_group.setLayout(search_layout)
        layout.addWidget(search_group)
        
        # Font Size setting
        font_group = QGroupBox("Appearance")
        font_layout = QVBoxLayout()
        
        font_size_layout = QHBoxLayout()
        font_size_layout.addWidget(QLabel("Font Size:"))
        
        self.font_size_spin = QSpinBox()
        self.font_size_spin.setMinimum(8)
        self.font_size_spin.setMaximum(32)
        self.font_size_spin.setSuffix(" px")
        current_font_size = parent.config_manager.get("font_size", 16)
        self.font_size_spin.setValue(current_font_size)
        font_size_layout.addWidget(self.font_size_spin)
        
        font_size_layout.addWidget(QLabel("(Default: 16px)"))
        font_size_layout.addStretch()
        
        font_layout.addLayout(font_size_layout)
        
        # Zoom controls
        zoom_layout = QHBoxLayout()
        zoom_layout.addWidget(QLabel("Zoom Level:"))
        
        # Zoom out button
        self.zoom_out_btn = QPushButton("🔍-")
        self.zoom_out_btn.setMaximumWidth(30)
        self.zoom_out_btn.setToolTip("Zoom Out (Ctrl+-)")
        self.zoom_out_btn.clicked.connect(self.zoom_out)
        zoom_layout.addWidget(self.zoom_out_btn)
        
        # Zoom level display
        self.zoom_level_label = QLabel("100%")
        self.zoom_level_label.setMinimumWidth(50)
        self.zoom_level_label.setAlignment(Qt.AlignCenter)
        self.zoom_level_label.setStyleSheet("QLabel { border: 1px solid #ccc; padding: 4px; background-color: #f8f8f8; }")
        zoom_layout.addWidget(self.zoom_level_label)
        
        # Zoom in button
        self.zoom_in_btn = QPushButton("🔍+")
        self.zoom_in_btn.setMaximumWidth(30)
        self.zoom_in_btn.setToolTip("Zoom In (Ctrl++)")
        self.zoom_in_btn.clicked.connect(self.zoom_in)
        zoom_layout.addWidget(self.zoom_in_btn)
        
        # Reset zoom button
        reset_zoom_btn = QPushButton("Reset")
        reset_zoom_btn.setToolTip("Reset zoom to 100%")
        reset_zoom_btn.clicked.connect(self.reset_zoom)
        zoom_layout.addWidget(reset_zoom_btn)
        
        zoom_layout.addStretch()
        
        font_layout.addLayout(zoom_layout)
        
        font_group.setLayout(font_layout)
        layout.addWidget(font_group)
        
        # Buttons
        button_layout = QHBoxLayout()
        
        save_btn = QPushButton("Save")
        save_btn.clicked.connect(self.accept)
        button_layout.addWidget(save_btn)
        
        cancel_btn = QPushButton("Cancel")
        cancel_btn.clicked.connect(self.reject)
        button_layout.addWidget(cancel_btn)
        
        layout.addLayout(button_layout)
        
        self.setLayout(layout)
        
        # Initialize zoom controls
        self.current_zoom = parent.current_zoom if hasattr(parent, 'current_zoom') else 1.0
        self.zoom_levels = [0.25, 0.33, 0.5, 0.67, 0.75, 0.8, 0.9, 1.0, 1.1, 1.25, 1.5, 1.75, 2.0, 2.5, 3.0, 4.0, 5.0]
        self.current_zoom_index = self.zoom_levels.index(self.current_zoom) if self.current_zoom in self.zoom_levels else self.zoom_levels.index(1.0)
        self.update_zoom_display()
    
    def zoom_in(self):
        """Zoom in"""
        if self.current_zoom_index < len(self.zoom_levels) - 1:
            self.current_zoom_index += 1
            self.apply_zoom()
    
    def zoom_out(self):
        """Zoom out"""
        if self.current_zoom_index > 0:
            self.current_zoom_index -= 1
            self.apply_zoom()
    
    def reset_zoom(self):
        """Reset zoom to 100%"""
        self.current_zoom_index = self.zoom_levels.index(1.0)
        self.apply_zoom()
    
    def apply_zoom(self):
        """Apply current zoom level"""
        self.current_zoom = self.zoom_levels[self.current_zoom_index]
        self.update_zoom_display()
        
        # Apply zoom to parent window's current browser
        if hasattr(self.parent_window, 'get_current_browser'):
            current_browser = self.parent_window.get_current_browser()
            if current_browser and not (
                getattr(self.parent_window, 'api_mode_enabled', False) or 
                getattr(self.parent_window, 'cmd_mode_enabled', False) or 
                getattr(self.parent_window, 'pdf_mode_enabled', False)
            ):
                current_browser.setZoomFactor(self.current_zoom)
        
        # Update parent window's zoom state
        if hasattr(self.parent_window, 'current_zoom'):
            self.parent_window.current_zoom = self.current_zoom
            self.parent_window.current_zoom_index = self.current_zoom_index
    
    def update_zoom_display(self):
        """Update zoom level display"""
        zoom_percentage = int(self.current_zoom * 100)
        self.zoom_level_label.setText(f"{zoom_percentage}%")
        
        # Update button states
        self.zoom_out_btn.setEnabled(self.current_zoom_index > 0)
        self.zoom_in_btn.setEnabled(self.current_zoom_index < len(self.zoom_levels) - 1)
    
    def toggle_welcome_page(self, state):
        """Toggle welcome page checkbox"""
        # Enable/disable URL input based on checkbox
        self.home_url_input.setEnabled(not self.welcome_page_checkbox.isChecked())
    
    def get_settings(self):
        """Return the settings from the dialog"""
        return {
            "home_url": self.home_url_input.text(),
            "search_engine": self.search_engine_combo.currentData(),
            "font_size": self.font_size_spin.value(),
            "use_welcome_page": self.welcome_page_checkbox.isChecked()
        }