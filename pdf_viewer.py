"""
PDF Viewer widget for the browser application.
Provides PDF viewing capabilities with zoom, navigation, and basic controls.
"""

from PyQt5.QtCore import *
from PyQt5.QtWidgets import *
from PyQt5.QtGui import *
import os
import sys

try:
    import fitz  # PyMuPDF
    PYMUPDF_AVAILABLE = True
except ImportError:
    PYMUPDF_AVAILABLE = False

from constants import PDF_ZOOM_LEVELS, DEFAULT_PDF_ZOOM, PDF_FILE_FILTER


class PDFViewerWidget(QWidget):
    """PDF viewer widget with navigation and zoom controls"""
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.parent_window = parent
        self.current_pdf = None
        self.current_page = 0
        self.total_pages = 0
        self.zoom_level = DEFAULT_PDF_ZOOM
        
        # Enable drag and drop
        self.setAcceptDrops(True)
        
        self.setup_ui()
        
    def setup_ui(self):
        """Setup the PDF viewer UI"""
        layout = QVBoxLayout(self)
        
        # Toolbar
        toolbar = self.create_toolbar()
        layout.addWidget(toolbar)
        
        # Main content area
        content_layout = QHBoxLayout()
        
        # PDF display area
        self.scroll_area = QScrollArea()
        self.scroll_area.setWidgetResizable(True)
        self.scroll_area.setAlignment(Qt.AlignCenter)
        
        self.pdf_label = QLabel()
        self.pdf_label.setAlignment(Qt.AlignCenter)
        self.pdf_label.setStyleSheet("background-color: white; border: 1px solid #ccc;")
        self.scroll_area.setWidget(self.pdf_label)
        
        content_layout.addWidget(self.scroll_area)
        layout.addLayout(content_layout)
        
        # Status bar
        self.status_bar = QLabel("No PDF loaded")
        self.status_bar.setStyleSheet("padding: 5px; background-color: #f0f0f0; border-top: 1px solid #ccc;")
        layout.addWidget(self.status_bar)
        
        # Show initial message
        self.show_welcome_message()
    
    def create_toolbar(self):
        """Create PDF viewer toolbar"""
        toolbar = QToolBar()
        toolbar.setToolButtonStyle(Qt.ToolButtonTextBesideIcon)
        
        # Open PDF button
        open_action = QAction("📄 Open PDF", self)
        open_action.setStatusTip("Open a PDF file")
        open_action.triggered.connect(self.open_pdf)
        toolbar.addAction(open_action)
        
        toolbar.addSeparator()
        
        # Navigation controls
        self.prev_btn = QAction("⬅️ Previous", self)
        self.prev_btn.setStatusTip("Go to previous page")
        self.prev_btn.triggered.connect(self.previous_page)
        self.prev_btn.setEnabled(False)
        toolbar.addAction(self.prev_btn)
        
        # Page info
        self.page_label = QLabel("Page: 0/0")
        self.page_label.setMinimumWidth(80)
        self.page_label.setAlignment(Qt.AlignCenter)
        toolbar.addWidget(self.page_label)
        
        self.next_btn = QAction("➡️ Next", self)
        self.next_btn.setStatusTip("Go to next page")
        self.next_btn.triggered.connect(self.next_page)
        self.next_btn.setEnabled(False)
        toolbar.addAction(self.next_btn)
        
        toolbar.addSeparator()
        
        # Zoom controls
        zoom_out_action = QAction("🔍➖ Zoom Out", self)
        zoom_out_action.setStatusTip("Zoom out")
        zoom_out_action.triggered.connect(self.zoom_out)
        toolbar.addAction(zoom_out_action)
        
        self.zoom_combo = QComboBox()
        self.zoom_combo.setMinimumWidth(80)
        for zoom in PDF_ZOOM_LEVELS:
            self.zoom_combo.addItem(f"{int(zoom * 100)}%", zoom)
        self.zoom_combo.setCurrentText("100%")
        self.zoom_combo.currentTextChanged.connect(self.on_zoom_changed)
        toolbar.addWidget(self.zoom_combo)
        
        zoom_in_action = QAction("🔍➕ Zoom In", self)
        zoom_in_action.setStatusTip("Zoom in")
        zoom_in_action.triggered.connect(self.zoom_in)
        toolbar.addAction(zoom_in_action)
        
        toolbar.addSeparator()
        
        # Fit controls
        fit_width_action = QAction("📏 Fit Width", self)
        fit_width_action.setStatusTip("Fit page width to window")
        fit_width_action.triggered.connect(self.fit_width)
        toolbar.addAction(fit_width_action)
        
        fit_page_action = QAction("📄 Fit Page", self)
        fit_page_action.setStatusTip("Fit entire page to window")
        fit_page_action.triggered.connect(self.fit_page)
        toolbar.addAction(fit_page_action)
        
        return toolbar
    
    def show_welcome_message(self):
        """Show welcome message when no PDF is loaded"""
        if not PYMUPDF_AVAILABLE:
            message = """
            <div style='text-align: center; padding: 50px; font-family: Arial, sans-serif;'>
                <h2>📄 PDF Reader Mode</h2>
                <p style='color: #e74c3c; font-size: 16px; margin: 20px;'>
                    <strong>PyMuPDF library not found!</strong>
                </p>
                <p style='color: #666; font-size: 14px; margin: 20px;'>
                    To use the PDF reader, please install PyMuPDF:<br>
                    <code style='background: #f8f9fa; padding: 5px; border-radius: 3px;'>pip install PyMuPDF</code>
                </p>
                <p style='color: #666; font-size: 12px; margin: 20px;'>
                    After installation, restart the application to use PDF viewing features.
                </p>
            </div>
            """
        else:
            message = """
            <div style='text-align: center; padding: 50px; font-family: Arial, sans-serif;'>
                <h2>📄 PDF Reader Mode</h2>
                <p style='color: #666; font-size: 16px; margin: 20px;'>
                    Click "Open PDF" to load a PDF document<br>
                    or drag and drop a PDF file here
                </p>
                <p style='color: #888; font-size: 14px; margin: 20px;'>
                    Features available:
                </p>
                <ul style='color: #888; font-size: 12px; text-align: left; display: inline-block;'>
                    <li>Page navigation (Previous/Next, Arrow keys)</li>
                    <li>Zoom controls (25% - 400%)</li>
                    <li>Fit to width/page options</li>
                    <li>Scroll through pages</li>
                    <li>Drag and drop PDF files</li>
                    <li>Keyboard shortcuts (Home/End, Page Up/Down)</li>
                </ul>
            </div>
            """
        
        self.pdf_label.setText(message)
        self.status_bar.setText("Ready - Click 'Open PDF' to load a document")
    
    def open_pdf(self):
        """Open a PDF file"""
        if not PYMUPDF_AVAILABLE:
            QMessageBox.warning(
                self, 
                "PyMuPDF Required", 
                "PDF viewing requires PyMuPDF library.\n\n"
                "Please install it using:\npip install PyMuPDF\n\n"
                "Then restart the application."
            )
            return
        
        file_path, _ = QFileDialog.getOpenFileName(
            self,
            "Open PDF File",
            "",
            PDF_FILE_FILTER
        )
        
        if file_path:
            self.load_pdf(file_path)
    
    def load_pdf(self, file_path):
        """Load a PDF file"""
        try:
            self.current_pdf = fitz.open(file_path)
            self.total_pages = len(self.current_pdf)
            self.current_page = 0
            
            # Update UI
            self.update_page_display()
            self.update_navigation_buttons()
            
            # Update status
            filename = os.path.basename(file_path)
            self.status_bar.setText(f"Loaded: {filename} ({self.total_pages} pages)")
            
            # Update parent window title if available
            if hasattr(self.parent_window, 'setWindowTitle'):
                self.parent_window.setWindowTitle(f"{filename} - PDF Reader")
                
        except Exception as e:
            QMessageBox.critical(
                self,
                "Error Loading PDF",
                f"Failed to load PDF file:\n{str(e)}"
            )
    
    def update_page_display(self):
        """Update the current page display"""
        if not self.current_pdf:
            return
        
        try:
            # Get the current page
            page = self.current_pdf[self.current_page]
            
            # Create transformation matrix for zoom
            mat = fitz.Matrix(self.zoom_level, self.zoom_level)
            
            # Render page to pixmap
            pix = page.get_pixmap(matrix=mat)
            
            # Convert to QPixmap
            img_data = pix.tobytes("ppm")
            qimg = QImage.fromData(img_data)
            pixmap = QPixmap.fromImage(qimg)
            
            # Display in label
            self.pdf_label.setPixmap(pixmap)
            self.pdf_label.resize(pixmap.size())
            
            # Update page label
            self.page_label.setText(f"Page: {self.current_page + 1}/{self.total_pages}")
            
        except Exception as e:
            self.status_bar.setText(f"Error displaying page: {str(e)}")
    
    def update_navigation_buttons(self):
        """Update navigation button states"""
        self.prev_btn.setEnabled(self.current_page > 0)
        self.next_btn.setEnabled(self.current_page < self.total_pages - 1)
    
    def previous_page(self):
        """Go to previous page"""
        if self.current_page > 0:
            self.current_page -= 1
            self.update_page_display()
            self.update_navigation_buttons()
    
    def next_page(self):
        """Go to next page"""
        if self.current_page < self.total_pages - 1:
            self.current_page += 1
            self.update_page_display()
            self.update_navigation_buttons()
    
    def zoom_in(self):
        """Zoom in"""
        current_index = self.zoom_combo.currentIndex()
        if current_index < len(PDF_ZOOM_LEVELS) - 1:
            self.zoom_combo.setCurrentIndex(current_index + 1)
    
    def zoom_out(self):
        """Zoom out"""
        current_index = self.zoom_combo.currentIndex()
        if current_index > 0:
            self.zoom_combo.setCurrentIndex(current_index - 1)
    
    def on_zoom_changed(self, text):
        """Handle zoom level change"""
        try:
            # Extract zoom value from text (e.g., "100%" -> 1.0)
            zoom_percent = int(text.replace('%', ''))
            self.zoom_level = zoom_percent / 100.0
            self.update_page_display()
        except ValueError:
            pass
    
    def fit_width(self):
        """Fit page width to window"""
        if not self.current_pdf:
            return
        
        try:
            # Get current page
            page = self.current_pdf[self.current_page]
            page_rect = page.rect
            
            # Calculate zoom to fit width
            available_width = self.scroll_area.viewport().width() - 20  # Some margin
            zoom = available_width / page_rect.width
            
            # Find closest zoom level or set custom
            closest_zoom = min(PDF_ZOOM_LEVELS, key=lambda x: abs(x - zoom))
            if abs(closest_zoom - zoom) < 0.1:
                self.zoom_level = closest_zoom
                # Update combo box
                for i, level in enumerate(PDF_ZOOM_LEVELS):
                    if level == closest_zoom:
                        self.zoom_combo.setCurrentIndex(i)
                        break
            else:
                self.zoom_level = zoom
                self.zoom_combo.setCurrentText(f"{int(zoom * 100)}%")
            
            self.update_page_display()
            
        except Exception as e:
            self.status_bar.setText(f"Error fitting width: {str(e)}")
    
    def fit_page(self):
        """Fit entire page to window"""
        if not self.current_pdf:
            return
        
        try:
            # Get current page
            page = self.current_pdf[self.current_page]
            page_rect = page.rect
            
            # Calculate zoom to fit both width and height
            available_width = self.scroll_area.viewport().width() - 20
            available_height = self.scroll_area.viewport().height() - 20
            
            zoom_width = available_width / page_rect.width
            zoom_height = available_height / page_rect.height
            zoom = min(zoom_width, zoom_height)
            
            # Find closest zoom level or set custom
            closest_zoom = min(PDF_ZOOM_LEVELS, key=lambda x: abs(x - zoom))
            if abs(closest_zoom - zoom) < 0.1:
                self.zoom_level = closest_zoom
                # Update combo box
                for i, level in enumerate(PDF_ZOOM_LEVELS):
                    if level == closest_zoom:
                        self.zoom_combo.setCurrentIndex(i)
                        break
            else:
                self.zoom_level = zoom
                self.zoom_combo.setCurrentText(f"{int(zoom * 100)}%")
            
            self.update_page_display()
            
        except Exception as e:
            self.status_bar.setText(f"Error fitting page: {str(e)}")
    
    def keyPressEvent(self, event):
        """Handle key press events for navigation"""
        if event.key() == Qt.Key_Left or event.key() == Qt.Key_PageUp:
            self.previous_page()
        elif event.key() == Qt.Key_Right or event.key() == Qt.Key_PageDown:
            self.next_page()
        elif event.key() == Qt.Key_Home:
            if self.current_pdf:
                self.current_page = 0
                self.update_page_display()
                self.update_navigation_buttons()
        elif event.key() == Qt.Key_End:
            if self.current_pdf:
                self.current_page = self.total_pages - 1
                self.update_page_display()
                self.update_navigation_buttons()
        else:
            super().keyPressEvent(event)
    
    def dragEnterEvent(self, event):
        """Handle drag enter event"""
        if event.mimeData().hasUrls():
            # Check if any of the URLs are PDF files
            for url in event.mimeData().urls():
                if url.toLocalFile().lower().endswith('.pdf'):
                    event.acceptProposedAction()
                    return
        event.ignore()
    
    def dropEvent(self, event):
        """Handle drop event"""
        if event.mimeData().hasUrls():
            for url in event.mimeData().urls():
                file_path = url.toLocalFile()
                if file_path.lower().endswith('.pdf'):
                    self.load_pdf(file_path)
                    event.acceptProposedAction()
                    return
        event.ignore()