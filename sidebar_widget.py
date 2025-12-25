"""
Vertical sidebar widget for the browser application.
Provides quick access to bookmarks/shortcuts with add/delete functionality.
"""

from PyQt5.QtCore import *
from PyQt5.QtWidgets import *
from PyQt5.QtGui import *
import json
import os
from constants import *


class SidebarItem(QWidget):
    """Individual sidebar item widget"""
    
    item_clicked = pyqtSignal(str, str)  # url, title
    item_deleted = pyqtSignal(str)  # item_id
    
    def __init__(self, item_id, title, url, parent=None):
        super().__init__(parent)
        self.item_id = item_id
        self.title = title
        self.url = url
        self.parent_sidebar = parent
        
        self.setup_ui()
        
    def setup_ui(self):
        """Setup the item UI"""
        self.setFixedSize(60, 60)  # Square item
        self.setToolTip(f"{self.title}\n{self.url}\n\nLeft-click: Open\nRight-click: Menu")
        
        # Enable context menu
        self.setContextMenuPolicy(Qt.CustomContextMenu)
        
        # Main layout
        layout = QVBoxLayout(self)
        layout.setContentsMargins(2, 2, 2, 2)
        layout.setSpacing(0)
        
        # Create main button area
        self.main_widget = QWidget()
        self.main_widget.setFixedSize(56, 56)
        
        # Main button layout
        main_layout = QVBoxLayout(self.main_widget)
        main_layout.setContentsMargins(4, 4, 4, 4)
        main_layout.setSpacing(2)
        
        # Icon/Favicon area (top part)
        self.icon_label = QLabel()
        self.icon_label.setAlignment(Qt.AlignCenter)
        self.icon_label.setFixedHeight(24)
        
        # Try to get favicon or use default
        self.set_icon()
        
        main_layout.addWidget(self.icon_label)
        
        # Title area (bottom part)
        self.title_label = QLabel(self.get_short_title())
        self.title_label.setAlignment(Qt.AlignCenter)
        self.title_label.setWordWrap(True)
        self.title_label.setFixedHeight(20)
        self.title_label.setStyleSheet("""
            QLabel {
                font-size: 8px;
                font-weight: 600;
                color: #495057;
                background: transparent;
                padding: 1px;
            }
        """)
        main_layout.addWidget(self.title_label)
        
        layout.addWidget(self.main_widget)
        
        # Apply styling
        self.apply_styling()
        
    def set_icon(self):
        """Set icon for the item"""
        # Create a more polished icon
        pixmap = QPixmap(24, 24)
        pixmap.fill(Qt.transparent)
        
        painter = QPainter(pixmap)
        painter.setRenderHint(QPainter.Antialiasing)
        
        # Generate color based on URL hash
        color_hash = hash(self.url) % 360
        color = QColor.fromHsv(color_hash, 180, 220)
        
        # Create gradient for more depth
        gradient = QRadialGradient(12, 12, 10)
        gradient.setColorAt(0, color.lighter(120))
        gradient.setColorAt(1, color.darker(110))
        
        painter.setBrush(QBrush(gradient))
        painter.setPen(QPen(color.darker(150), 2))
        painter.drawEllipse(2, 2, 20, 20)
        
        # Add first letter of title with better font
        painter.setPen(QPen(Qt.white))
        font = QFont("Arial", 10, QFont.Bold)
        painter.setFont(font)
        first_letter = self.title[0].upper() if self.title else "?"
        painter.drawText(pixmap.rect(), Qt.AlignCenter, first_letter)
        
        painter.end()
        
        self.icon_label.setPixmap(pixmap)
        
    def get_short_title(self):
        """Get shortened title for display"""
        if len(self.title) <= 8:
            return self.title
        return self.title[:6] + "..."
        
    def apply_styling(self):
        """Apply styling to the item"""
        self.setStyleSheet("""
            SidebarItem {
                background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
                    stop:0 #ffffff, stop:1 #f8f9fa);
                border: 2px solid #e9ecef;
                border-radius: 8px;
                margin: 2px;
            }
            SidebarItem:hover {
                background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
                    stop:0 #e3f2fd, stop:1 #bbdefb);
                border-color: #2196f3;
            }
        """)
        
    def mousePressEvent(self, event):
        """Handle mouse press events"""
        if event.button() == Qt.LeftButton:
            self.item_clicked.emit(self.url, self.title)
        elif event.button() == Qt.RightButton:
            self.show_context_menu(event.globalPos())
        super().mousePressEvent(event)
    
    def show_context_menu(self, position):
        """Show context menu for sidebar item"""
        menu = QMenu(self)
        
        # Open in new tab action
        open_action = QAction("🌐 Open in Current Tab", self)
        open_action.triggered.connect(lambda: self.item_clicked.emit(self.url, self.title))
        menu.addAction(open_action)
        
        # Copy URL action
        copy_url_action = QAction("📋 Copy URL", self)
        copy_url_action.triggered.connect(self.copy_url)
        menu.addAction(copy_url_action)
        
        # Edit item action
        edit_action = QAction("✏️ Edit Item", self)
        edit_action.triggered.connect(self.edit_item)
        menu.addAction(edit_action)
        
        menu.addSeparator()
        
        # Delete action
        delete_action = QAction("🗑️ Remove Item", self)
        delete_action.triggered.connect(self.confirm_delete)
        menu.addAction(delete_action)
        
        # Style the menu
        menu.setStyleSheet("""
            QMenu {
                background-color: #ffffff;
                border: 1px solid #dee2e6;
                border-radius: 6px;
                padding: 4px;
            }
            QMenu::item {
                padding: 6px 12px;
                border-radius: 4px;
                margin: 1px;
            }
            QMenu::item:selected {
                background-color: #e3f2fd;
                color: #1976d2;
            }
            QMenu::separator {
                height: 1px;
                background-color: #dee2e6;
                margin: 4px 8px;
            }
        """)
        
        menu.exec_(position)
    
    def copy_url(self):
        """Copy URL to clipboard"""
        clipboard = QApplication.clipboard()
        clipboard.setText(self.url)
        
        # Show brief feedback
        if hasattr(self.parent_sidebar, 'parent_window') and hasattr(self.parent_sidebar.parent_window, 'status_info'):
            self.parent_sidebar.parent_window.status_info.setText(f"📋 Copied: {self.url}")
            QTimer.singleShot(2000, lambda: self.parent_sidebar.parent_window.status_info.setText(""))
    
    def edit_item(self):
        """Edit sidebar item"""
        dialog = EditSidebarItemDialog(self.title, self.url, self)
        if dialog.exec_() == QDialog.Accepted:
            new_title, new_url = dialog.get_data()
            
            # Update item data
            self.title = new_title
            self.url = new_url
            
            # Update UI
            self.title_label.setText(self.get_short_title())
            self.setToolTip(f"{self.title}\n{self.url}\n\nLeft-click: Open\nRight-click: Menu")
            self.set_icon()  # Regenerate icon with new data
            
            # Update parent sidebar data
            if self.parent_sidebar:
                for item_data in self.parent_sidebar.sidebar_data:
                    if item_data["id"] == self.item_id:
                        item_data["title"] = new_title
                        item_data["url"] = new_url
                        break
                self.parent_sidebar.save_sidebar_data()
                
                # Show feedback
                if hasattr(self.parent_sidebar, 'parent_window') and hasattr(self.parent_sidebar.parent_window, 'status_info'):
                    self.parent_sidebar.parent_window.status_info.setText(f"✏️ Updated: {new_title}")
                    QTimer.singleShot(2000, lambda: self.parent_sidebar.parent_window.status_info.setText(""))
        
    def confirm_delete(self):
        """Show confirmation dialog before deleting"""
        reply = QMessageBox.question(
            self,
            "Delete Sidebar Item",
            f"Are you sure you want to delete '{self.title}'?",
            QMessageBox.Yes | QMessageBox.No,
            QMessageBox.No
        )
        
        if reply == QMessageBox.Yes:
            self.item_deleted.emit(self.item_id)


class SidebarWidget(QWidget):
    """Vertical sidebar widget"""
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.parent_window = parent
        self.items = {}  # item_id -> SidebarItem
        self.sidebar_data = []
        
        self.setup_ui()
        self.load_sidebar_data()
        
    def setup_ui(self):
        """Setup the sidebar UI"""
        self.setFixedWidth(70)
        self.setMinimumHeight(200)
        
        # Main layout
        layout = QVBoxLayout(self)
        layout.setContentsMargins(5, 5, 5, 5)
        layout.setSpacing(8)  # Consistent spacing throughout sidebar
        
        # Title
        title_label = QLabel("Quick\nAccess")
        title_label.setAlignment(Qt.AlignCenter)
        title_label.setFixedHeight(40)
        title_label.setStyleSheet("""
            QLabel {
                font-size: 10px;
                font-weight: bold;
                color: #495057;
                padding: 8px 4px;
                background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
                    stop:0 #f8f9fa, stop:1 #e9ecef);
                border: 1px solid #dee2e6;
                border-radius: 6px;
                margin: 2px;
            }
        """)
        layout.addWidget(title_label)
        
        # Scroll area for items
        self.scroll_area = QScrollArea()
        self.scroll_area.setWidgetResizable(True)
        self.scroll_area.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        self.scroll_area.setVerticalScrollBarPolicy(Qt.ScrollBarAsNeeded)
        
        # Items container
        self.items_widget = QWidget()
        self.items_layout = QVBoxLayout(self.items_widget)
        self.items_layout.setContentsMargins(0, 0, 0, 0)
        self.items_layout.setSpacing(8)  # Consistent spacing between items
        self.items_layout.addStretch()  # Push items to top
        
        self.scroll_area.setWidget(self.items_widget)
        layout.addWidget(self.scroll_area)
        
        # Add button - icon only with tooltip
        self.add_btn = QPushButton("➕")
        self.add_btn.setFixedSize(20, 60)  # Exact size: 20px wide, 60px tall
        self.add_btn.setMinimumSize(20, 60)  # Ensure minimum size
        self.add_btn.setMaximumSize(20, 60)  # Ensure maximum size
        self.add_btn.setToolTip("Add New Quick Access Item\n\nClick to add a shortcut to your favorite website.\nYou can also use Ctrl+Shift+B to add the current page.")
        self.add_btn.setStyleSheet("""
            QPushButton {
                background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
                    stop:0 #28a745, stop:1 #20c997);
                color: white;
                border: none;
                border-radius: 6px;
                font-size: 14px;
                font-weight: bold;
                padding: 0px;
                margin: 0px;
            }
            QPushButton:hover {
                background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
                    stop:0 #34ce57, stop:1 #2dd4aa);
            }
            QPushButton:pressed {
                background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
                    stop:0 #1e7e34, stop:1 #17a2b8);
            }
        """)
        self.add_btn.clicked.connect(self.add_new_item)
        layout.addWidget(self.add_btn, alignment=Qt.AlignLeft)  # Align left instead of center
        
        # Apply sidebar styling
        self.setStyleSheet("""
            SidebarWidget {
                background-color: #ffffff;
                border-right: 1px solid #ddd;
            }
            QScrollArea {
                border: none;
                background-color: transparent;
            }
        """)
        
    def get_sidebar_file_path(self):
        """Get the path to the sidebar data file"""
        if hasattr(self.parent_window, 'profile_manager'):
            return self.parent_window.profile_manager.get_profile_path("sidebar.json")
        return os.path.join(STORAGE_DIR, "sidebar.json")
        
    def load_sidebar_data(self):
        """Load sidebar data from file"""
        sidebar_file = self.get_sidebar_file_path()
        
        try:
            if os.path.exists(sidebar_file):
                with open(sidebar_file, 'r', encoding='utf-8') as f:
                    self.sidebar_data = json.load(f)
            else:
                # Create default items
                self.sidebar_data = [
                    {
                        "id": "google",
                        "title": "Google",
                        "url": "https://www.google.com"
                    },
                    {
                        "id": "github",
                        "title": "GitHub",
                        "url": "https://github.com"
                    }
                ]
                self.save_sidebar_data()
                
        except Exception as e:
            print(f"Error loading sidebar data: {e}")
            self.sidebar_data = []
            
        self.refresh_items()
        
    def save_sidebar_data(self):
        """Save sidebar data to file"""
        sidebar_file = self.get_sidebar_file_path()
        
        try:
            # Ensure directory exists
            os.makedirs(os.path.dirname(sidebar_file), exist_ok=True)
            
            with open(sidebar_file, 'w', encoding='utf-8') as f:
                json.dump(self.sidebar_data, f, indent=2, ensure_ascii=False)
                
        except Exception as e:
            print(f"Error saving sidebar data: {e}")
            
    def refresh_items(self):
        """Refresh the sidebar items display"""
        # Clear existing items
        for item_id, item_widget in self.items.items():
            item_widget.setParent(None)
            item_widget.deleteLater()
        self.items.clear()
        
        # Add items from data
        for item_data in self.sidebar_data:
            self.create_item_widget(item_data)
            
    def create_item_widget(self, item_data):
        """Create a sidebar item widget"""
        item_widget = SidebarItem(
            item_data["id"],
            item_data["title"],
            item_data["url"],
            self
        )
        
        # Connect signals
        item_widget.item_clicked.connect(self.on_item_clicked)
        item_widget.item_deleted.connect(self.on_item_deleted)
        
        # Add to layout (insert before stretch)
        self.items_layout.insertWidget(self.items_layout.count() - 1, item_widget)
        
        # Store reference
        self.items[item_data["id"]] = item_widget
        
    def on_item_clicked(self, url, title):
        """Handle item click - replace current tab"""
        if hasattr(self.parent_window, 'replace_current_tab'):
            self.parent_window.replace_current_tab(url, title)
        elif hasattr(self.parent_window, 'get_current_browser'):
            # Fallback: navigate current tab
            browser = self.parent_window.get_current_browser()
            if browser:
                browser.setUrl(QUrl(url))
                
    def on_item_deleted(self, item_id):
        """Handle item deletion"""
        # Remove from data
        self.sidebar_data = [item for item in self.sidebar_data if item["id"] != item_id]
        
        # Remove widget
        if item_id in self.items:
            widget = self.items[item_id]
            widget.setParent(None)
            widget.deleteLater()
            del self.items[item_id]
            
        # Save changes
        self.save_sidebar_data()
        
    def add_new_item(self):
        """Add a new sidebar item"""
        dialog = AddSidebarItemDialog(self)
        if dialog.exec_() == QDialog.Accepted:
            title, url = dialog.get_data()
            
            # Generate unique ID
            item_id = f"item_{len(self.sidebar_data)}_{hash(url) % 10000}"
            
            # Add to data
            item_data = {
                "id": item_id,
                "title": title,
                "url": url
            }
            self.sidebar_data.append(item_data)
            
            # Create widget
            self.create_item_widget(item_data)
            
            # Save changes
            self.save_sidebar_data()
            
    def add_current_page(self):
        """Add current page to sidebar"""
        if hasattr(self.parent_window, 'get_current_browser'):
            browser = self.parent_window.get_current_browser()
            if browser:
                url = browser.url().toString()
                title = browser.page().title() or "Untitled"
                
                # Generate unique ID
                item_id = f"current_{hash(url) % 10000}"
                
                # Add to data
                item_data = {
                    "id": item_id,
                    "title": title,
                    "url": url
                }
                self.sidebar_data.append(item_data)
                
                # Create widget
                self.create_item_widget(item_data)
                
                # Save changes
                self.save_sidebar_data()
                
                return True
        return False


class AddSidebarItemDialog(QDialog):
    """Dialog for adding new sidebar items"""
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Add Quick Access Item")
        self.setFixedSize(400, 200)
        
        self.setup_ui()
        
    def setup_ui(self):
        """Setup dialog UI"""
        layout = QVBoxLayout(self)
        
        # Title input
        title_label = QLabel("Title:")
        self.title_input = QLineEdit()
        self.title_input.setPlaceholderText("Enter a title for this item")
        
        layout.addWidget(title_label)
        layout.addWidget(self.title_input)
        
        # URL input
        url_label = QLabel("URL:")
        self.url_input = QLineEdit()
        self.url_input.setPlaceholderText("https://example.com")
        
        layout.addWidget(url_label)
        layout.addWidget(self.url_input)
        
        # Buttons
        button_layout = QHBoxLayout()
        
        self.ok_btn = QPushButton("Add")
        self.ok_btn.clicked.connect(self.accept)
        self.ok_btn.setDefault(True)
        
        self.cancel_btn = QPushButton("Cancel")
        self.cancel_btn.clicked.connect(self.reject)
        
        button_layout.addStretch()
        button_layout.addWidget(self.cancel_btn)
        button_layout.addWidget(self.ok_btn)
        
        layout.addLayout(button_layout)
        
        # Focus on title input
        self.title_input.setFocus()
        
    def get_data(self):
        """Get the entered data"""
        title = self.title_input.text().strip()
        url = self.url_input.text().strip()
        
        # Add protocol if missing
        if url and not url.startswith(('http://', 'https://', 'file://')):
            url = 'https://' + url
            
        return title, url
        
    def accept(self):
        """Validate and accept dialog"""
        title, url = self.get_data()
        
        if not title:
            QMessageBox.warning(self, "Invalid Input", "Please enter a title.")
            return
            
        if not url:
            QMessageBox.warning(self, "Invalid Input", "Please enter a URL.")
            return
            
        super().accept()


class EditSidebarItemDialog(QDialog):
    """Dialog for editing existing sidebar items"""
    
    def __init__(self, current_title, current_url, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Edit Quick Access Item")
        self.setFixedSize(400, 200)
        
        self.current_title = current_title
        self.current_url = current_url
        
        self.setup_ui()
        
    def setup_ui(self):
        """Setup dialog UI"""
        layout = QVBoxLayout(self)
        
        # Title input
        title_label = QLabel("Title:")
        self.title_input = QLineEdit()
        self.title_input.setText(self.current_title)
        self.title_input.setPlaceholderText("Enter a title for this item")
        
        layout.addWidget(title_label)
        layout.addWidget(self.title_input)
        
        # URL input
        url_label = QLabel("URL:")
        self.url_input = QLineEdit()
        self.url_input.setText(self.current_url)
        self.url_input.setPlaceholderText("https://example.com")
        
        layout.addWidget(url_label)
        layout.addWidget(self.url_input)
        
        # Buttons
        button_layout = QHBoxLayout()
        
        self.ok_btn = QPushButton("Save Changes")
        self.ok_btn.clicked.connect(self.accept)
        self.ok_btn.setDefault(True)
        
        self.cancel_btn = QPushButton("Cancel")
        self.cancel_btn.clicked.connect(self.reject)
        
        button_layout.addStretch()
        button_layout.addWidget(self.cancel_btn)
        button_layout.addWidget(self.ok_btn)
        
        layout.addLayout(button_layout)
        
        # Focus on title input and select all text
        self.title_input.setFocus()
        self.title_input.selectAll()
        
    def get_data(self):
        """Get the entered data"""
        title = self.title_input.text().strip()
        url = self.url_input.text().strip()
        
        # Add protocol if missing
        if url and not url.startswith(('http://', 'https://', 'file://')):
            url = 'https://' + url
            
        return title, url
        
    def accept(self):
        """Validate and accept dialog"""
        title, url = self.get_data()
        
        if not title:
            QMessageBox.warning(self, "Invalid Input", "Please enter a title.")
            return
            
        if not url:
            QMessageBox.warning(self, "Invalid Input", "Please enter a URL.")
            return
            
        super().accept()