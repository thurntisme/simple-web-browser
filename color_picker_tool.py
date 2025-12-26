"""
Advanced Color Picker Tool for the browser.
Provides comprehensive color selection, palette generation, and color analysis.
"""

import sys
import colorsys
import json
from datetime import datetime
from PyQt5.QtWidgets import *
from PyQt5.QtCore import *
from PyQt5.QtGui import *


class ColorPickerDialog(QDialog):
    """Advanced color picker dialog with multiple features"""
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("🎨 Advanced Color Picker")
        self.setMinimumSize(900, 700)
        self.resize(1200, 800)
        
        # Current color
        self.current_color = QColor(255, 0, 0)
        
        # Color history
        self.color_history = []
        
        # Saved palettes
        self.saved_palettes = []
        
        # Eyedropper mode
        self.eyedropper_active = False
        self.original_cursor = None
        
        self.setup_ui()
        self.update_color_displays()
    
    def setup_ui(self):
        """Setup the user interface"""
        layout = QVBoxLayout(self)
        
        # Create tab widget
        tab_widget = QTabWidget()
        layout.addWidget(tab_widget)
        
        # Color Picker Tab
        picker_tab = self.create_picker_tab()
        tab_widget.addTab(picker_tab, "🎨 Color Picker")
        
        # Palette Generator Tab
        palette_tab = self.create_palette_tab()
        tab_widget.addTab(palette_tab, "🎭 Palette Generator")
        
        # Color Analyzer Tab
        analyzer_tab = self.create_analyzer_tab()
        tab_widget.addTab(analyzer_tab, "🔍 Color Analyzer")
        
        # Gradient Generator Tab
        gradient_tab = self.create_gradient_tab()
        tab_widget.addTab(gradient_tab, "🌈 Gradient Generator")
        
        # Color History Tab
        history_tab = self.create_history_tab()
        tab_widget.addTab(history_tab, "📚 History & Palettes")
        
        # Buttons
        button_layout = QHBoxLayout()
        
        self.eyedropper_button = QPushButton("🎯 Eyedropper Mode")
        self.eyedropper_button.setCheckable(True)
        self.eyedropper_button.clicked.connect(self.toggle_eyedropper_mode)
        
        self.copy_button = QPushButton("📋 Copy Color")
        self.save_palette_button = QPushButton("💾 Save Palette")
        self.export_button = QPushButton("📤 Export")
        close_button = QPushButton("❌ Close")
        
        button_layout.addWidget(self.eyedropper_button)
        button_layout.addStretch()
        button_layout.addWidget(self.copy_button)
        button_layout.addWidget(self.save_palette_button)
        button_layout.addWidget(self.export_button)
        button_layout.addWidget(close_button)
        
        layout.addLayout(button_layout)
        
        # Connect buttons
        self.copy_button.clicked.connect(self.copy_current_color)
        self.save_palette_button.clicked.connect(self.save_current_palette)
        self.export_button.clicked.connect(self.export_colors)
        close_button.clicked.connect(self.accept)
    
    def create_picker_tab(self):
        """Create the main color picker tab"""
        widget = QWidget()
        layout = QHBoxLayout(widget)
        
        # Left side - Color wheel and controls
        left_layout = QVBoxLayout()
        
        # Color wheel
        self.color_wheel = ColorWheelWidget()
        self.color_wheel.colorChanged.connect(self.on_color_changed)
        left_layout.addWidget(self.color_wheel)
        
        # RGB sliders
        rgb_group = QGroupBox("RGB Values")
        rgb_layout = QVBoxLayout(rgb_group)
        
        self.red_slider = self.create_color_slider("Red", 255, 0)
        self.green_slider = self.create_color_slider("Green", 255, 0)
        self.blue_slider = self.create_color_slider("Blue", 255, 255)
        
        rgb_layout.addWidget(self.red_slider['widget'])
        rgb_layout.addWidget(self.green_slider['widget'])
        rgb_layout.addWidget(self.blue_slider['widget'])
        
        left_layout.addWidget(rgb_group)
        
        # HSV sliders
        hsv_group = QGroupBox("HSV Values")
        hsv_layout = QVBoxLayout(hsv_group)
        
        self.hue_slider = self.create_color_slider("Hue", 360, 0)
        self.saturation_slider = self.create_color_slider("Saturation", 100, 100)
        self.value_slider = self.create_color_slider("Value", 100, 100)
        
        hsv_layout.addWidget(self.hue_slider['widget'])
        hsv_layout.addWidget(self.saturation_slider['widget'])
        hsv_layout.addWidget(self.value_slider['widget'])
        
        left_layout.addWidget(hsv_group)
        
        layout.addLayout(left_layout)
        
        # Right side - Color display and formats
        right_layout = QVBoxLayout()
        
        # Current color display
        color_display_group = QGroupBox("Current Color")
        color_display_layout = QVBoxLayout(color_display_group)
        
        self.color_preview = QLabel()
        self.color_preview.setMinimumHeight(100)
        self.color_preview.setStyleSheet("border: 2px solid #ccc; border-radius: 5px;")
        color_display_layout.addWidget(self.color_preview)
        
        right_layout.addWidget(color_display_group)
        
        # Color formats
        formats_group = QGroupBox("Color Formats")
        formats_layout = QVBoxLayout(formats_group)
        
        self.hex_input = self.create_format_input("HEX", "#FF0000")
        self.rgb_input = self.create_format_input("RGB", "rgb(255, 0, 0)")
        self.rgba_input = self.create_format_input("RGBA", "rgba(255, 0, 0, 1.0)")
        self.hsl_input = self.create_format_input("HSL", "hsl(0, 100%, 50%)")
        self.hsla_input = self.create_format_input("HSLA", "hsla(0, 100%, 50%, 1.0)")
        self.cmyk_input = self.create_format_input("CMYK", "cmyk(0%, 100%, 100%, 0%)")
        
        formats_layout.addWidget(self.hex_input)
        formats_layout.addWidget(self.rgb_input)
        formats_layout.addWidget(self.rgba_input)
        formats_layout.addWidget(self.hsl_input)
        formats_layout.addWidget(self.hsla_input)
        formats_layout.addWidget(self.cmyk_input)
        
        right_layout.addWidget(formats_group)
        
        # Quick colors
        quick_colors_group = QGroupBox("Quick Colors")
        quick_colors_layout = QGridLayout(quick_colors_group)
        
        quick_colors = [
            "#FF0000", "#00FF00", "#0000FF", "#FFFF00", "#FF00FF", "#00FFFF",
            "#000000", "#FFFFFF", "#808080", "#800000", "#008000", "#000080",
            "#808000", "#800080", "#008080", "#C0C0C0", "#FFA500", "#FFC0CB"
        ]
        
        for i, color_hex in enumerate(quick_colors):
            row, col = divmod(i, 6)
            color_button = QPushButton()
            color_button.setFixedSize(30, 30)
            color_button.setStyleSheet(f"background-color: {color_hex}; border: 1px solid #ccc;")
            color_button.clicked.connect(lambda checked, c=color_hex: self.set_color_from_hex(c))
            quick_colors_layout.addWidget(color_button, row, col)
        
        right_layout.addWidget(quick_colors_group)
        
        # Eyedropper section
        eyedropper_group = QGroupBox("Eyedropper Tool")
        eyedropper_layout = QVBoxLayout(eyedropper_group)
        
        eyedropper_info = QLabel("🎯 Click 'Eyedropper Mode' to sample colors directly from the webpage")
        eyedropper_info.setWordWrap(True)
        eyedropper_info.setStyleSheet("color: #666; font-size: 11px;")
        eyedropper_layout.addWidget(eyedropper_info)
        
        self.eyedropper_tab_button = QPushButton("🎯 Activate Eyedropper")
        self.eyedropper_tab_button.clicked.connect(self.toggle_eyedropper_mode)
        eyedropper_layout.addWidget(self.eyedropper_tab_button)
        
        right_layout.addWidget(eyedropper_group)
        
        layout.addLayout(right_layout)
        
        return widget
    
    def create_palette_tab(self):
        """Create the palette generator tab"""
        widget = QWidget()
        layout = QVBoxLayout(widget)
        
        # Controls
        controls_layout = QHBoxLayout()
        
        controls_layout.addWidget(QLabel("Base Color:"))
        self.palette_color_button = QPushButton()
        self.palette_color_button.setFixedSize(50, 30)
        self.palette_color_button.clicked.connect(self.choose_palette_base_color)
        controls_layout.addWidget(self.palette_color_button)
        
        controls_layout.addWidget(QLabel("Palette Type:"))
        self.palette_type_combo = QComboBox()
        self.palette_type_combo.addItems([
            "Monochromatic", "Analogous", "Complementary", 
            "Triadic", "Tetradic", "Split Complementary"
        ])
        self.palette_type_combo.currentTextChanged.connect(self.generate_palette)
        controls_layout.addWidget(self.palette_type_combo)
        
        generate_button = QPushButton("🎨 Generate Palette")
        generate_button.clicked.connect(self.generate_palette)
        controls_layout.addWidget(generate_button)
        
        controls_layout.addStretch()
        layout.addLayout(controls_layout)
        
        # Palette display
        self.palette_display = QScrollArea()
        self.palette_widget = QWidget()
        self.palette_layout = QVBoxLayout(self.palette_widget)
        self.palette_display.setWidget(self.palette_widget)
        self.palette_display.setWidgetResizable(True)
        
        layout.addWidget(self.palette_display)
        
        # Initialize with current color
        self.update_palette_base_color()
        self.generate_palette()
        
        return widget
    
    def create_analyzer_tab(self):
        """Create the color analyzer tab"""
        widget = QWidget()
        layout = QVBoxLayout(widget)
        
        # Color input
        input_layout = QHBoxLayout()
        input_layout.addWidget(QLabel("Analyze Color:"))
        
        self.analyze_color_input = QLineEdit()
        self.analyze_color_input.setPlaceholderText("Enter color (hex, rgb, hsl, etc.)")
        self.analyze_color_input.textChanged.connect(self.analyze_color)
        input_layout.addWidget(self.analyze_color_input)
        
        analyze_button = QPushButton("🔍 Analyze")
        analyze_button.clicked.connect(self.analyze_color)
        input_layout.addWidget(analyze_button)
        
        layout.addLayout(input_layout)
        
        # Analysis results
        self.analysis_text = QTextEdit()
        self.analysis_text.setReadOnly(True)
        self.analysis_text.setStyleSheet("font-family: monospace; background-color: #f8f9fa;")
        layout.addWidget(self.analysis_text)
        
        return widget
    
    def create_gradient_tab(self):
        """Create the gradient generator tab"""
        widget = QWidget()
        layout = QVBoxLayout(widget)
        
        # Gradient controls
        controls_layout = QHBoxLayout()
        
        controls_layout.addWidget(QLabel("Start Color:"))
        self.gradient_start_button = QPushButton()
        self.gradient_start_button.setFixedSize(50, 30)
        self.gradient_start_button.clicked.connect(self.choose_gradient_start)
        controls_layout.addWidget(self.gradient_start_button)
        
        controls_layout.addWidget(QLabel("End Color:"))
        self.gradient_end_button = QPushButton()
        self.gradient_end_button.setFixedSize(50, 30)
        self.gradient_end_button.clicked.connect(self.choose_gradient_end)
        controls_layout.addWidget(self.gradient_end_button)
        
        controls_layout.addWidget(QLabel("Steps:"))
        self.gradient_steps_spin = QSpinBox()
        self.gradient_steps_spin.setRange(2, 20)
        self.gradient_steps_spin.setValue(5)
        self.gradient_steps_spin.valueChanged.connect(self.generate_gradient)
        controls_layout.addWidget(self.gradient_steps_spin)
        
        generate_gradient_button = QPushButton("🌈 Generate Gradient")
        generate_gradient_button.clicked.connect(self.generate_gradient)
        controls_layout.addWidget(generate_gradient_button)
        
        controls_layout.addStretch()
        layout.addLayout(controls_layout)
        
        # Gradient display
        self.gradient_display = QScrollArea()
        self.gradient_widget = QWidget()
        self.gradient_layout = QVBoxLayout(self.gradient_widget)
        self.gradient_display.setWidget(self.gradient_widget)
        self.gradient_display.setWidgetResizable(True)
        
        layout.addWidget(self.gradient_display)
        
        # CSS output
        css_layout = QHBoxLayout()
        css_layout.addWidget(QLabel("CSS Gradient:"))
        
        self.css_gradient_output = QLineEdit()
        self.css_gradient_output.setReadOnly(True)
        css_layout.addWidget(self.css_gradient_output)
        
        copy_css_button = QPushButton("📋 Copy CSS")
        copy_css_button.clicked.connect(self.copy_css_gradient)
        css_layout.addWidget(copy_css_button)
        
        layout.addLayout(css_layout)
        
        # Initialize gradient
        self.gradient_start_color = QColor(255, 0, 0)
        self.gradient_end_color = QColor(0, 0, 255)
        self.update_gradient_buttons()
        self.generate_gradient()
        
        return widget
    
    def create_history_tab(self):
        """Create the history and saved palettes tab"""
        widget = QWidget()
        layout = QVBoxLayout(widget)
        
        # History section
        history_group = QGroupBox("Color History")
        history_layout = QVBoxLayout(history_group)
        
        self.history_list = QListWidget()
        self.history_list.itemClicked.connect(self.load_color_from_history)
        history_layout.addWidget(self.history_list)
        
        history_buttons = QHBoxLayout()
        clear_history_button = QPushButton("🗑️ Clear History")
        clear_history_button.clicked.connect(self.clear_history)
        history_buttons.addWidget(clear_history_button)
        history_buttons.addStretch()
        
        history_layout.addLayout(history_buttons)
        layout.addWidget(history_group)
        
        # Saved palettes section
        palettes_group = QGroupBox("Saved Palettes")
        palettes_layout = QVBoxLayout(palettes_group)
        
        self.palettes_list = QListWidget()
        self.palettes_list.itemClicked.connect(self.load_palette)
        palettes_layout.addWidget(self.palettes_list)
        
        palette_buttons = QHBoxLayout()
        delete_palette_button = QPushButton("🗑️ Delete Palette")
        delete_palette_button.clicked.connect(self.delete_palette)
        palette_buttons.addWidget(delete_palette_button)
        palette_buttons.addStretch()
        
        palettes_layout.addLayout(palette_buttons)
        layout.addWidget(palettes_group)
        
        return widget
    
    def create_color_slider(self, name, max_val, initial_val):
        """Create a color slider with label and value display"""
        widget = QWidget()
        layout = QHBoxLayout(widget)
        
        label = QLabel(f"{name}:")
        label.setMinimumWidth(80)
        layout.addWidget(label)
        
        slider = QSlider(Qt.Horizontal)
        slider.setRange(0, max_val)
        slider.setValue(initial_val)
        layout.addWidget(slider)
        
        value_label = QLabel(str(initial_val))
        value_label.setMinimumWidth(40)
        layout.addWidget(value_label)
        
        # Connect slider to update value label and color
        slider.valueChanged.connect(lambda v: value_label.setText(str(v)))
        slider.valueChanged.connect(self.update_color_from_sliders)
        
        return {
            'widget': widget,
            'slider': slider,
            'label': value_label
        }
    
    def create_format_input(self, format_name, initial_value):
        """Create a format input field"""
        widget = QWidget()
        layout = QHBoxLayout(widget)
        
        label = QLabel(f"{format_name}:")
        label.setMinimumWidth(60)
        layout.addWidget(label)
        
        input_field = QLineEdit(initial_value)
        input_field.returnPressed.connect(lambda: self.parse_color_input(input_field.text()))
        layout.addWidget(input_field)
        
        copy_button = QPushButton("📋")
        copy_button.setFixedSize(30, 25)
        copy_button.clicked.connect(lambda: self.copy_to_clipboard(input_field.text()))
        layout.addWidget(copy_button)
        
        widget.input_field = input_field
        return widget
    
    def on_color_changed(self, color):
        """Handle color change from color wheel"""
        self.current_color = color
        self.update_color_displays()
        self.add_to_history(color)
    
    def update_color_from_sliders(self):
        """Update color based on slider values"""
        r = self.red_slider['slider'].value()
        g = self.green_slider['slider'].value()
        b = self.blue_slider['slider'].value()
        
        self.current_color = QColor(r, g, b)
        self.update_color_displays(skip_sliders=True)
        self.add_to_history(self.current_color)
    
    def update_color_displays(self, skip_sliders=False):
        """Update all color displays"""
        color = self.current_color
        
        # Update color preview
        self.color_preview.setStyleSheet(f"background-color: {color.name()}; border: 2px solid #ccc; border-radius: 5px;")
        
        # Update sliders
        if not skip_sliders:
            self.red_slider['slider'].setValue(color.red())
            self.green_slider['slider'].setValue(color.green())
            self.blue_slider['slider'].setValue(color.blue())
            
            h, s, v, _ = color.getHsv()
            self.hue_slider['slider'].setValue(h if h != -1 else 0)
            self.saturation_slider['slider'].setValue(int(s * 100 / 255))
            self.value_slider['slider'].setValue(int(v * 100 / 255))
        
        # Update format inputs
        self.hex_input.input_field.setText(color.name().upper())
        self.rgb_input.input_field.setText(f"rgb({color.red()}, {color.green()}, {color.blue()})")
        self.rgba_input.input_field.setText(f"rgba({color.red()}, {color.green()}, {color.blue()}, 1.0)")
        
        # HSL conversion
        h, s, l = colorsys.rgb_to_hls(color.red()/255, color.green()/255, color.blue()/255)
        self.hsl_input.input_field.setText(f"hsl({int(h*360)}, {int(s*100)}%, {int(l*100)}%)")
        self.hsla_input.input_field.setText(f"hsla({int(h*360)}, {int(s*100)}%, {int(l*100)}%, 1.0)")
        
        # CMYK conversion
        c, m, y, k = self.rgb_to_cmyk(color.red(), color.green(), color.blue())
        self.cmyk_input.input_field.setText(f"cmyk({c}%, {m}%, {y}%, {k}%)")
        
        # Update color wheel
        self.color_wheel.set_color(color)
    
    def rgb_to_cmyk(self, r, g, b):
        """Convert RGB to CMYK"""
        r, g, b = r/255.0, g/255.0, b/255.0
        k = 1 - max(r, g, b)
        if k == 1:
            return 0, 0, 0, 100
        c = (1 - r - k) / (1 - k)
        m = (1 - g - k) / (1 - k)
        y = (1 - b - k) / (1 - k)
        return int(c*100), int(m*100), int(y*100), int(k*100)
    
    def set_color_from_hex(self, hex_color):
        """Set color from hex string"""
        color = QColor(hex_color)
        if color.isValid():
            self.current_color = color
            self.update_color_displays()
            self.add_to_history(color)
    
    def parse_color_input(self, color_string):
        """Parse color from various input formats"""
        color_string = color_string.strip()
        
        # Try hex format
        if color_string.startswith('#'):
            color = QColor(color_string)
            if color.isValid():
                self.current_color = color
                self.update_color_displays()
                self.add_to_history(color)
                return
        
        # Try rgb format
        if color_string.startswith('rgb'):
            import re
            match = re.search(r'rgb\s*\(\s*(\d+)\s*,\s*(\d+)\s*,\s*(\d+)\s*\)', color_string)
            if match:
                r, g, b = map(int, match.groups())
                color = QColor(r, g, b)
                if color.isValid():
                    self.current_color = color
                    self.update_color_displays()
                    self.add_to_history(color)
                    return
    
    def add_to_history(self, color):
        """Add color to history"""
        color_hex = color.name().upper()
        if color_hex not in [c.name().upper() for c in self.color_history]:
            self.color_history.append(color)
            if len(self.color_history) > 50:  # Limit history size
                self.color_history.pop(0)
            self.update_history_display()
    
    def update_history_display(self):
        """Update the history list display"""
        self.history_list.clear()
        for color in reversed(self.color_history):  # Show most recent first
            item = QListWidgetItem(f"{color.name().upper()} - RGB({color.red()}, {color.green()}, {color.blue()})")
            item.setData(Qt.UserRole, color)
            # Set background color
            item.setBackground(QBrush(color))
            # Set text color based on brightness
            if color.lightness() < 128:
                item.setForeground(QBrush(QColor(255, 255, 255)))
            else:
                item.setForeground(QBrush(QColor(0, 0, 0)))
            self.history_list.addItem(item)
    
    def load_color_from_history(self, item):
        """Load color from history item"""
        color = item.data(Qt.UserRole)
        if color:
            self.current_color = color
            self.update_color_displays()
    
    def clear_history(self):
        """Clear color history"""
        self.color_history.clear()
        self.history_list.clear()
    
    def copy_current_color(self):
        """Copy current color to clipboard"""
        color_hex = self.current_color.name().upper()
        self.copy_to_clipboard(color_hex)
    
    def copy_to_clipboard(self, text):
        """Copy text to clipboard"""
        clipboard = QApplication.clipboard()
        clipboard.setText(text)
        
        # Show temporary status message
        if hasattr(self.parent(), 'status_info'):
            self.parent().status_info.setText(f"📋 Copied: {text}")
            QTimer.singleShot(2000, lambda: self.parent().status_info.setText(""))
    
    def choose_palette_base_color(self):
        """Choose base color for palette generation"""
        color = QColorDialog.getColor(self.current_color, self)
        if color.isValid():
            self.current_color = color
            self.update_palette_base_color()
            self.generate_palette()
    
    def update_palette_base_color(self):
        """Update palette base color button"""
        if hasattr(self, 'palette_color_button'):
            self.palette_color_button.setStyleSheet(f"background-color: {self.current_color.name()}; border: 1px solid #ccc;")
    
    def generate_palette(self):
        """Generate color palette based on selected type"""
        palette_type = self.palette_type_combo.currentText()
        base_color = self.current_color
        
        # Clear existing palette
        for i in reversed(range(self.palette_layout.count())):
            self.palette_layout.itemAt(i).widget().setParent(None)
        
        colors = []
        
        if palette_type == "Monochromatic":
            colors = self.generate_monochromatic_palette(base_color)
        elif palette_type == "Analogous":
            colors = self.generate_analogous_palette(base_color)
        elif palette_type == "Complementary":
            colors = self.generate_complementary_palette(base_color)
        elif palette_type == "Triadic":
            colors = self.generate_triadic_palette(base_color)
        elif palette_type == "Tetradic":
            colors = self.generate_tetradic_palette(base_color)
        elif palette_type == "Split Complementary":
            colors = self.generate_split_complementary_palette(base_color)
        
        # Display palette
        self.display_palette(colors, palette_type)
        self.current_palette = colors
    
    def generate_monochromatic_palette(self, base_color):
        """Generate monochromatic color palette"""
        colors = []
        h, s, v, _ = base_color.getHsv()
        
        # Generate different values (brightness levels)
        for i in range(5):
            new_v = max(50, min(255, v + (i - 2) * 40))
            color = QColor.fromHsv(h, s, new_v)
            colors.append(color)
        
        return colors
    
    def generate_analogous_palette(self, base_color):
        """Generate analogous color palette"""
        colors = []
        h, s, v, _ = base_color.getHsv()
        
        # Generate colors with hue variations
        for i in range(5):
            new_h = (h + (i - 2) * 30) % 360
            color = QColor.fromHsv(new_h, s, v)
            colors.append(color)
        
        return colors
    
    def generate_complementary_palette(self, base_color):
        """Generate complementary color palette"""
        colors = [base_color]
        h, s, v, _ = base_color.getHsv()
        
        # Complementary color (opposite on color wheel)
        comp_h = (h + 180) % 360
        comp_color = QColor.fromHsv(comp_h, s, v)
        colors.append(comp_color)
        
        # Add variations
        for color in [base_color, comp_color]:
            h, s, v, _ = color.getHsv()
            # Lighter version
            light_color = QColor.fromHsv(h, max(0, s - 50), min(255, v + 50))
            colors.append(light_color)
            # Darker version
            dark_color = QColor.fromHsv(h, min(255, s + 50), max(0, v - 50))
            colors.append(dark_color)
        
        return colors[:6]
    
    def generate_triadic_palette(self, base_color):
        """Generate triadic color palette"""
        colors = [base_color]
        h, s, v, _ = base_color.getHsv()
        
        # Two other colors 120 degrees apart
        for offset in [120, 240]:
            new_h = (h + offset) % 360
            color = QColor.fromHsv(new_h, s, v)
            colors.append(color)
        
        # Add variations
        for color in colors[:3]:
            h, s, v, _ = color.getHsv()
            light_color = QColor.fromHsv(h, max(0, s - 30), min(255, v + 30))
            colors.append(light_color)
        
        return colors
    
    def generate_tetradic_palette(self, base_color):
        """Generate tetradic (square) color palette"""
        colors = [base_color]
        h, s, v, _ = base_color.getHsv()
        
        # Three other colors 90 degrees apart
        for offset in [90, 180, 270]:
            new_h = (h + offset) % 360
            color = QColor.fromHsv(new_h, s, v)
            colors.append(color)
        
        return colors
    
    def generate_split_complementary_palette(self, base_color):
        """Generate split complementary color palette"""
        colors = [base_color]
        h, s, v, _ = base_color.getHsv()
        
        # Split complementary colors
        for offset in [150, 210]:
            new_h = (h + offset) % 360
            color = QColor.fromHsv(new_h, s, v)
            colors.append(color)
        
        # Add variations
        for color in colors[:3]:
            h, s, v, _ = color.getHsv()
            light_color = QColor.fromHsv(h, max(0, s - 40), min(255, v + 40))
            colors.append(light_color)
        
        return colors
    
    def display_palette(self, colors, palette_name):
        """Display color palette"""
        # Palette title
        title_label = QLabel(f"{palette_name} Palette")
        title_label.setStyleSheet("font-weight: bold; font-size: 14px; margin: 10px 0;")
        self.palette_layout.addWidget(title_label)
        
        # Color swatches
        swatch_widget = QWidget()
        swatch_layout = QHBoxLayout(swatch_widget)
        
        for i, color in enumerate(colors):
            color_frame = QFrame()
            color_frame.setFixedSize(80, 80)
            color_frame.setStyleSheet(f"""
                background-color: {color.name()};
                border: 2px solid #ccc;
                border-radius: 5px;
            """)
            
            # Add click handler
            color_frame.mousePressEvent = lambda event, c=color: self.select_palette_color(c)
            
            swatch_layout.addWidget(color_frame)
            
            # Color info
            info_widget = QWidget()
            info_layout = QVBoxLayout(info_widget)
            info_layout.setContentsMargins(0, 0, 0, 0)
            
            hex_label = QLabel(color.name().upper())
            hex_label.setAlignment(Qt.AlignCenter)
            hex_label.setStyleSheet("font-family: monospace; font-size: 10px;")
            info_layout.addWidget(hex_label)
            
            rgb_label = QLabel(f"RGB({color.red()}, {color.green()}, {color.blue()})")
            rgb_label.setAlignment(Qt.AlignCenter)
            rgb_label.setStyleSheet("font-size: 9px; color: #666;")
            info_layout.addWidget(rgb_label)
            
            swatch_layout.addWidget(info_widget)
        
        self.palette_layout.addWidget(swatch_widget)
        
        # Add separator
        separator = QFrame()
        separator.setFrameShape(QFrame.HLine)
        separator.setFrameShadow(QFrame.Sunken)
        self.palette_layout.addWidget(separator)
    
    def select_palette_color(self, color):
        """Select color from palette"""
        self.current_color = color
        self.update_color_displays()
        self.add_to_history(color)
    
    def save_current_palette(self):
        """Save current palette"""
        if hasattr(self, 'current_palette') and self.current_palette:
            name, ok = QInputDialog.getText(self, 'Save Palette', 'Enter palette name:')
            if ok and name:
                palette_data = {
                    'name': name,
                    'colors': [color.name() for color in self.current_palette],
                    'created': datetime.now().isoformat()
                }
                self.saved_palettes.append(palette_data)
                self.update_palettes_display()
    
    def update_palettes_display(self):
        """Update saved palettes display"""
        self.palettes_list.clear()
        for palette in self.saved_palettes:
            item = QListWidgetItem(f"{palette['name']} ({len(palette['colors'])} colors)")
            item.setData(Qt.UserRole, palette)
            self.palettes_list.addItem(item)
    
    def load_palette(self, item):
        """Load saved palette"""
        palette_data = item.data(Qt.UserRole)
        if palette_data:
            colors = [QColor(hex_color) for hex_color in palette_data['colors']]
            self.display_palette(colors, palette_data['name'])
            self.current_palette = colors
    
    def delete_palette(self):
        """Delete selected palette"""
        current_item = self.palettes_list.currentItem()
        if current_item:
            palette_data = current_item.data(Qt.UserRole)
            self.saved_palettes.remove(palette_data)
            self.update_palettes_display()
    
    def choose_gradient_start(self):
        """Choose gradient start color"""
        color = QColorDialog.getColor(self.gradient_start_color, self)
        if color.isValid():
            self.gradient_start_color = color
            self.update_gradient_buttons()
            self.generate_gradient()
    
    def choose_gradient_end(self):
        """Choose gradient end color"""
        color = QColorDialog.getColor(self.gradient_end_color, self)
        if color.isValid():
            self.gradient_end_color = color
            self.update_gradient_buttons()
            self.generate_gradient()
    
    def update_gradient_buttons(self):
        """Update gradient color buttons"""
        self.gradient_start_button.setStyleSheet(f"background-color: {self.gradient_start_color.name()}; border: 1px solid #ccc;")
        self.gradient_end_button.setStyleSheet(f"background-color: {self.gradient_end_color.name()}; border: 1px solid #ccc;")
    
    def generate_gradient(self):
        """Generate color gradient"""
        steps = self.gradient_steps_spin.value()
        start_color = self.gradient_start_color
        end_color = self.gradient_end_color
        
        # Clear existing gradient
        for i in reversed(range(self.gradient_layout.count())):
            self.gradient_layout.itemAt(i).widget().setParent(None)
        
        # Generate gradient colors
        gradient_colors = []
        for i in range(steps):
            ratio = i / (steps - 1) if steps > 1 else 0
            
            r = int(start_color.red() + (end_color.red() - start_color.red()) * ratio)
            g = int(start_color.green() + (end_color.green() - start_color.green()) * ratio)
            b = int(start_color.blue() + (end_color.blue() - start_color.blue()) * ratio)
            
            color = QColor(r, g, b)
            gradient_colors.append(color)
        
        # Display gradient
        gradient_widget = QWidget()
        gradient_layout = QHBoxLayout(gradient_widget)
        
        for color in gradient_colors:
            color_frame = QFrame()
            color_frame.setFixedSize(60, 60)
            color_frame.setStyleSheet(f"""
                background-color: {color.name()};
                border: 1px solid #ccc;
            """)
            gradient_layout.addWidget(color_frame)
        
        self.gradient_layout.addWidget(gradient_widget)
        
        # Generate CSS
        css_colors = [color.name() for color in gradient_colors]
        css_gradient = f"linear-gradient(90deg, {', '.join(css_colors)})"
        self.css_gradient_output.setText(css_gradient)
    
    def copy_css_gradient(self):
        """Copy CSS gradient to clipboard"""
        css_text = self.css_gradient_output.text()
        self.copy_to_clipboard(css_text)
    
    def analyze_color(self):
        """Analyze the entered color"""
        color_input = self.analyze_color_input.text().strip()
        if not color_input:
            return
        
        # Try to parse the color
        color = QColor(color_input)
        if not color.isValid():
            # Try parsing RGB format
            import re
            rgb_match = re.search(r'rgb\s*\(\s*(\d+)\s*,\s*(\d+)\s*,\s*(\d+)\s*\)', color_input)
            if rgb_match:
                r, g, b = map(int, rgb_match.groups())
                color = QColor(r, g, b)
        
        if not color.isValid():
            self.analysis_text.setText("❌ Invalid color format. Please enter a valid color (hex, rgb, etc.)")
            return
        
        # Perform analysis
        analysis = self.perform_color_analysis(color)
        self.analysis_text.setText(analysis)
    
    def perform_color_analysis(self, color):
        """Perform comprehensive color analysis"""
        lines = []
        lines.append("🔍 COLOR ANALYSIS REPORT")
        lines.append("=" * 50)
        lines.append("")
        
        # Basic information
        lines.append("📊 BASIC INFORMATION:")
        lines.append(f"  HEX: {color.name().upper()}")
        lines.append(f"  RGB: ({color.red()}, {color.green()}, {color.blue()})")
        
        # HSV values
        h, s, v, _ = color.getHsv()
        lines.append(f"  HSV: ({h if h != -1 else 0}, {int(s*100/255)}%, {int(v*100/255)}%)")
        
        # HSL values
        h_hsl, s_hsl, l_hsl = colorsys.rgb_to_hls(color.red()/255, color.green()/255, color.blue()/255)
        lines.append(f"  HSL: ({int(h_hsl*360)}, {int(s_hsl*100)}%, {int(l_hsl*100)}%)")
        
        # CMYK values
        c, m, y, k = self.rgb_to_cmyk(color.red(), color.green(), color.blue())
        lines.append(f"  CMYK: ({c}%, {m}%, {y}%, {k}%)")
        lines.append("")
        
        # Color properties
        lines.append("🎨 COLOR PROPERTIES:")
        
        # Brightness
        brightness = color.lightness()
        if brightness > 200:
            brightness_desc = "Very Light"
        elif brightness > 150:
            brightness_desc = "Light"
        elif brightness > 100:
            brightness_desc = "Medium"
        elif brightness > 50:
            brightness_desc = "Dark"
        else:
            brightness_desc = "Very Dark"
        
        lines.append(f"  Brightness: {brightness}/255 ({brightness_desc})")
        
        # Saturation
        saturation = int(s * 100 / 255) if s != -1 else 0
        if saturation > 80:
            sat_desc = "Highly Saturated"
        elif saturation > 60:
            sat_desc = "Saturated"
        elif saturation > 40:
            sat_desc = "Moderately Saturated"
        elif saturation > 20:
            sat_desc = "Low Saturation"
        else:
            sat_desc = "Desaturated/Gray"
        
        lines.append(f"  Saturation: {saturation}% ({sat_desc})")
        
        # Temperature
        if color.red() > color.blue():
            temp_desc = "Warm"
        elif color.blue() > color.red():
            temp_desc = "Cool"
        else:
            temp_desc = "Neutral"
        
        lines.append(f"  Temperature: {temp_desc}")
        lines.append("")
        
        # Accessibility
        lines.append("♿ ACCESSIBILITY:")
        
        # Contrast ratios with common colors
        white_contrast = self.calculate_contrast_ratio(color, QColor(255, 255, 255))
        black_contrast = self.calculate_contrast_ratio(color, QColor(0, 0, 0))
        
        lines.append(f"  Contrast with White: {white_contrast:.2f}:1")
        lines.append(f"  Contrast with Black: {black_contrast:.2f}:1")
        
        # WCAG compliance
        if white_contrast >= 4.5:
            lines.append("  ✅ WCAG AA compliant with white text")
        elif white_contrast >= 3.0:
            lines.append("  ⚠️ WCAG AA compliant for large text with white")
        else:
            lines.append("  ❌ Not WCAG compliant with white text")
        
        if black_contrast >= 4.5:
            lines.append("  ✅ WCAG AA compliant with black text")
        elif black_contrast >= 3.0:
            lines.append("  ⚠️ WCAG AA compliant for large text with black")
        else:
            lines.append("  ❌ Not WCAG compliant with black text")
        
        lines.append("")
        
        # Color harmony
        lines.append("🎭 COLOR HARMONY:")
        lines.append(f"  Complementary: {QColor.fromHsv((h + 180) % 360, s, v).name().upper()}")
        lines.append(f"  Triadic 1: {QColor.fromHsv((h + 120) % 360, s, v).name().upper()}")
        lines.append(f"  Triadic 2: {QColor.fromHsv((h + 240) % 360, s, v).name().upper()}")
        lines.append("")
        
        # Usage recommendations
        lines.append("💡 USAGE RECOMMENDATIONS:")
        
        if brightness > 200:
            lines.append("  • Good for backgrounds and subtle accents")
            lines.append("  • Use dark text for readability")
        elif brightness < 50:
            lines.append("  • Good for text and strong accents")
            lines.append("  • Use light text for readability")
        else:
            lines.append("  • Versatile color for various uses")
            lines.append("  • Test contrast with intended text colors")
        
        if saturation > 80:
            lines.append("  • High impact color, use sparingly")
            lines.append("  • Great for call-to-action elements")
        elif saturation < 20:
            lines.append("  • Neutral color, good for backgrounds")
            lines.append("  • Pairs well with more saturated colors")
        
        return '\n'.join(lines)
    
    def calculate_contrast_ratio(self, color1, color2):
        """Calculate contrast ratio between two colors"""
        def get_relative_luminance(color):
            r, g, b = color.red()/255, color.green()/255, color.blue()/255
            
            def adjust_color(c):
                if c <= 0.03928:
                    return c / 12.92
                else:
                    return pow((c + 0.055) / 1.055, 2.4)
            
            r = adjust_color(r)
            g = adjust_color(g)
            b = adjust_color(b)
            
            return 0.2126 * r + 0.7152 * g + 0.0722 * b
        
        lum1 = get_relative_luminance(color1)
        lum2 = get_relative_luminance(color2)
        
        lighter = max(lum1, lum2)
        darker = min(lum1, lum2)
        
        return (lighter + 0.05) / (darker + 0.05)
    
    def export_colors(self):
        """Export colors and palettes"""
        file_path, _ = QFileDialog.getSaveFileName(
            self,
            "Export Color Data",
            f"color_data_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json",
            "JSON Files (*.json);;All Files (*.*)"
        )
        
        if file_path:
            try:
                export_data = {
                    'current_color': self.current_color.name(),
                    'color_history': [color.name() for color in self.color_history],
                    'saved_palettes': self.saved_palettes,
                    'export_date': datetime.now().isoformat()
                }
                
                with open(file_path, 'w', encoding='utf-8') as f:
                    json.dump(export_data, f, indent=2, ensure_ascii=False)
                
                QMessageBox.information(self, "Export Successful", f"Color data exported to:\n{file_path}")
                
            except Exception as e:
                QMessageBox.critical(self, "Export Failed", f"Failed to export color data:\n{str(e)}")
    
    def toggle_eyedropper_mode(self):
        """Toggle eyedropper mode for color sampling from webpage"""
        if self.eyedropper_active:
            self.deactivate_eyedropper()
        else:
            self.activate_eyedropper()
    
    def activate_eyedropper(self):
        """Activate eyedropper mode"""
        self.eyedropper_active = True
        self.eyedropper_button.setText("🎯 Exit Eyedropper")
        self.eyedropper_button.setStyleSheet("background-color: #e74c3c; color: white; font-weight: bold;")
        
        # Update tab button
        if hasattr(self, 'eyedropper_tab_button'):
            self.eyedropper_tab_button.setText("🎯 Exit Eyedropper")
            self.eyedropper_tab_button.setStyleSheet("background-color: #e74c3c; color: white; font-weight: bold;")
        
        # Minimize the color picker dialog
        self.showMinimized()
        
        # Get the main browser window
        main_window = self.parent()
        if main_window:
            # Inject JavaScript to enable color picking
            self.inject_eyedropper_script(main_window)
            
            # Show instruction message
            if hasattr(main_window, 'status_info'):
                main_window.status_info.setText("🎯 Eyedropper Mode: Click anywhere on the webpage to sample colors. Press ESC to exit.")
    
    def deactivate_eyedropper(self):
        """Deactivate eyedropper mode"""
        self.eyedropper_active = False
        self.eyedropper_button.setText("🎯 Eyedropper Mode")
        self.eyedropper_button.setStyleSheet("")
        
        # Update tab button
        if hasattr(self, 'eyedropper_tab_button'):
            self.eyedropper_tab_button.setText("🎯 Activate Eyedropper")
            self.eyedropper_tab_button.setStyleSheet("")
        
        # Restore the color picker dialog
        self.showNormal()
        self.raise_()
        self.activateWindow()
        
        # Remove eyedropper script from webpage
        main_window = self.parent()
        if main_window:
            self.remove_eyedropper_script(main_window)
            
            # Clear status message
            if hasattr(main_window, 'status_info'):
                main_window.status_info.setText("")
    
    def inject_eyedropper_script(self, main_window):
        """Inject JavaScript for eyedropper functionality"""
        # Get current browser tab
        current_browser = None
        if hasattr(main_window, 'tab_manager'):
            current_browser = main_window.tab_manager.get_current_browser()
        
        if not current_browser:
            return
        
        # JavaScript code for eyedropper functionality
        js_code = """
        (function() {
            // Remove existing eyedropper if any
            if (window.colorPickerEyedropper) {
                window.colorPickerEyedropper.cleanup();
            }
            
            window.colorPickerEyedropper = {
                active: true,
                originalCursor: document.body.style.cursor,
                
                init: function() {
                    // Change cursor to crosshair
                    document.body.style.cursor = 'crosshair';
                    document.documentElement.style.cursor = 'crosshair';
                    
                    // Add event listeners
                    document.addEventListener('click', this.handleClick, true);
                    document.addEventListener('mousemove', this.handleMouseMove, true);
                    document.addEventListener('keydown', this.handleKeyDown, true);
                    
                    // Prevent default behaviors
                    document.addEventListener('contextmenu', this.preventDefault, true);
                    document.addEventListener('selectstart', this.preventDefault, true);
                    
                    // Create color preview tooltip
                    this.createTooltip();
                },
                
                createTooltip: function() {
                    this.tooltip = document.createElement('div');
                    this.tooltip.id = 'color-picker-tooltip';
                    this.tooltip.style.cssText = `
                        position: fixed;
                        z-index: 999999;
                        background: rgba(0, 0, 0, 0.8);
                        color: white;
                        padding: 8px 12px;
                        border-radius: 6px;
                        font-family: monospace;
                        font-size: 12px;
                        pointer-events: none;
                        transform: translate(-50%, -100%);
                        margin-top: -10px;
                        box-shadow: 0 2px 8px rgba(0, 0, 0, 0.3);
                        display: none;
                    `;
                    document.body.appendChild(this.tooltip);
                },
                
                handleMouseMove: function(event) {
                    if (!window.colorPickerEyedropper.active) return;
                    
                    // Get element under cursor
                    const element = document.elementFromPoint(event.clientX, event.clientY);
                    if (!element) return;
                    
                    // Get computed style
                    const style = window.getComputedStyle(element);
                    const bgColor = style.backgroundColor;
                    const textColor = style.color;
                    
                    // Update tooltip
                    const tooltip = window.colorPickerEyedropper.tooltip;
                    if (tooltip) {
                        tooltip.style.left = event.clientX + 'px';
                        tooltip.style.top = event.clientY + 'px';
                        tooltip.style.display = 'block';
                        
                        // Show background color if not transparent
                        if (bgColor && bgColor !== 'rgba(0, 0, 0, 0)' && bgColor !== 'transparent') {
                            tooltip.innerHTML = `
                                <div>Background: ${bgColor}</div>
                                <div>Text: ${textColor}</div>
                                <div style="font-size: 10px; opacity: 0.8;">Click to select</div>
                            `;
                        } else {
                            tooltip.innerHTML = `
                                <div>Text: ${textColor}</div>
                                <div style="font-size: 10px; opacity: 0.8;">Click to select</div>
                            `;
                        }
                    }
                },
                
                handleClick: function(event) {
                    if (!window.colorPickerEyedropper.active) return;
                    
                    event.preventDefault();
                    event.stopPropagation();
                    
                    // Get element under cursor
                    const element = document.elementFromPoint(event.clientX, event.clientY);
                    if (!element) return;
                    
                    // Get computed style
                    const style = window.getComputedStyle(element);
                    let selectedColor = null;
                    
                    // Prefer background color, fallback to text color
                    const bgColor = style.backgroundColor;
                    const textColor = style.color;
                    
                    if (bgColor && bgColor !== 'rgba(0, 0, 0, 0)' && bgColor !== 'transparent') {
                        selectedColor = bgColor;
                    } else {
                        selectedColor = textColor;
                    }
                    
                    // Convert to hex if possible
                    const hexColor = window.colorPickerEyedropper.rgbToHex(selectedColor);
                    
                    // Send color back to Python (this will be handled by the page)
                    console.log('Color picked:', selectedColor, hexColor);
                    
                    // Store the picked color for retrieval
                    window.pickedColor = {
                        original: selectedColor,
                        hex: hexColor,
                        element: element.tagName.toLowerCase(),
                        property: bgColor && bgColor !== 'rgba(0, 0, 0, 0)' && bgColor !== 'transparent' ? 'background' : 'text'
                    };
                    
                    // Visual feedback
                    window.colorPickerEyedropper.showPickedFeedback(event.clientX, event.clientY, hexColor);
                },
                
                showPickedFeedback: function(x, y, color) {
                    const feedback = document.createElement('div');
                    feedback.style.cssText = `
                        position: fixed;
                        left: ${x - 25}px;
                        top: ${y - 25}px;
                        width: 50px;
                        height: 50px;
                        background: ${color};
                        border: 3px solid white;
                        border-radius: 50%;
                        z-index: 1000000;
                        pointer-events: none;
                        box-shadow: 0 0 0 2px black, 0 4px 12px rgba(0, 0, 0, 0.3);
                        animation: colorPickFeedback 1s ease-out forwards;
                    `;
                    
                    // Add animation keyframes
                    if (!document.getElementById('color-pick-animation')) {
                        const style = document.createElement('style');
                        style.id = 'color-pick-animation';
                        style.textContent = `
                            @keyframes colorPickFeedback {
                                0% { transform: scale(0.5); opacity: 1; }
                                50% { transform: scale(1.2); opacity: 1; }
                                100% { transform: scale(1); opacity: 0; }
                            }
                        `;
                        document.head.appendChild(style);
                    }
                    
                    document.body.appendChild(feedback);
                    
                    // Remove after animation
                    setTimeout(() => {
                        if (feedback.parentNode) {
                            feedback.parentNode.removeChild(feedback);
                        }
                    }, 1000);
                },
                
                handleKeyDown: function(event) {
                    if (event.key === 'Escape') {
                        window.colorPickerEyedropper.cleanup();
                    }
                },
                
                preventDefault: function(event) {
                    event.preventDefault();
                    event.stopPropagation();
                },
                
                rgbToHex: function(rgb) {
                    if (!rgb) return '#000000';
                    
                    // Handle hex colors
                    if (rgb.startsWith('#')) {
                        return rgb;
                    }
                    
                    // Handle rgb() and rgba() colors
                    const match = rgb.match(/rgba?\\(([^)]+)\\)/);
                    if (!match) return '#000000';
                    
                    const values = match[1].split(',').map(v => parseInt(v.trim()));
                    if (values.length < 3) return '#000000';
                    
                    const toHex = (n) => {
                        const hex = Math.max(0, Math.min(255, n)).toString(16);
                        return hex.length === 1 ? '0' + hex : hex;
                    };
                    
                    return `#${toHex(values[0])}${toHex(values[1])}${toHex(values[2])}`.toUpperCase();
                },
                
                cleanup: function() {
                    this.active = false;
                    
                    // Restore cursor
                    document.body.style.cursor = this.originalCursor || '';
                    document.documentElement.style.cursor = '';
                    
                    // Remove event listeners
                    document.removeEventListener('click', this.handleClick, true);
                    document.removeEventListener('mousemove', this.handleMouseMove, true);
                    document.removeEventListener('keydown', this.handleKeyDown, true);
                    document.removeEventListener('contextmenu', this.preventDefault, true);
                    document.removeEventListener('selectstart', this.preventDefault, true);
                    
                    // Remove tooltip
                    if (this.tooltip && this.tooltip.parentNode) {
                        this.tooltip.parentNode.removeChild(this.tooltip);
                    }
                    
                    // Clear picked color
                    delete window.pickedColor;
                }
            };
            
            // Initialize eyedropper
            window.colorPickerEyedropper.init();
            
            return 'Eyedropper activated';
        })();
        """
        
        # Execute the JavaScript
        current_browser.page().runJavaScript(js_code)
        
        # Start polling for picked colors
        self.start_color_polling(current_browser)
    
    def start_color_polling(self, browser):
        """Start polling for picked colors"""
        self.color_poll_timer = QTimer()
        self.color_poll_timer.timeout.connect(lambda: self.check_for_picked_color(browser))
        self.color_poll_timer.start(100)  # Check every 100ms
    
    def check_for_picked_color(self, browser):
        """Check if a color was picked from the webpage"""
        if not self.eyedropper_active:
            if hasattr(self, 'color_poll_timer'):
                self.color_poll_timer.stop()
            return
        
        # JavaScript to check for picked color
        js_check = """
        (function() {
            if (window.pickedColor) {
                const color = window.pickedColor;
                delete window.pickedColor;  // Clear it
                return color;
            }
            return null;
        })();
        """
        
        def handle_picked_color(result):
            if result and self.eyedropper_active:
                # Process the picked color
                hex_color = result.get('hex', '#000000')
                original_color = result.get('original', '')
                element_type = result.get('element', '')
                color_property = result.get('property', '')
                
                # Set the picked color
                color = QColor(hex_color)
                if color.isValid():
                    self.current_color = color
                    self.update_color_displays()
                    self.add_to_history(color)
                    
                    # Show feedback
                    main_window = self.parent()
                    if hasattr(main_window, 'status_info'):
                        main_window.status_info.setText(f"🎯 Color picked: {hex_color} from {element_type} {color_property}")
                        QTimer.singleShot(3000, lambda: main_window.status_info.setText("🎯 Eyedropper Mode: Click anywhere to sample colors. Press ESC to exit."))
                    
                    # Restore and show color picker dialog briefly
                    self.showNormal()
                    self.raise_()
                    QTimer.singleShot(1500, lambda: self.showMinimized() if self.eyedropper_active else None)
        
        browser.page().runJavaScript(js_check, handle_picked_color)
    
    def remove_eyedropper_script(self, main_window):
        """Remove eyedropper script from webpage"""
        # Get current browser tab
        current_browser = None
        if hasattr(main_window, 'tab_manager'):
            current_browser = main_window.tab_manager.get_current_browser()
        
        if not current_browser:
            return
        
        # Stop polling timer
        if hasattr(self, 'color_poll_timer'):
            self.color_poll_timer.stop()
        
        # JavaScript to cleanup eyedropper
        js_cleanup = """
        (function() {
            if (window.colorPickerEyedropper) {
                window.colorPickerEyedropper.cleanup();
                delete window.colorPickerEyedropper;
            }
            return 'Eyedropper deactivated';
        })();
        """
        
        current_browser.page().runJavaScript(js_cleanup)
    
    def closeEvent(self, event):
        """Handle dialog close event"""
        # Deactivate eyedropper if active
        if self.eyedropper_active:
            self.deactivate_eyedropper()
        
        super().closeEvent(event)


class ColorWheelWidget(QWidget):
    """Custom color wheel widget"""
    
    colorChanged = pyqtSignal(QColor)
    
    def __init__(self):
        super().__init__()
        self.setMinimumSize(200, 200)
        self.current_color = QColor(255, 0, 0)
        self.wheel_radius = 0
        self.center = QPoint()
        
    def set_color(self, color):
        """Set the current color"""
        self.current_color = color
        self.update()
    
    def paintEvent(self, event):
        """Paint the color wheel"""
        painter = QPainter(self)
        painter.setRenderHint(QPainter.Antialiasing)
        
        # Calculate dimensions
        size = min(self.width(), self.height())
        self.wheel_radius = size // 2 - 10
        self.center = QPoint(self.width() // 2, self.height() // 2)
        
        # Draw color wheel
        for angle in range(360):
            for radius in range(self.wheel_radius):
                # Calculate position
                x = self.center.x() + radius * cos(radians(angle))
                y = self.center.y() + radius * sin(radians(angle))
                
                # Calculate color
                hue = angle
                saturation = int(255 * radius / self.wheel_radius)
                value = 255
                
                color = QColor.fromHsv(hue, saturation, value)
                painter.setPen(QPen(color))
                painter.drawPoint(int(x), int(y))
        
        # Draw current color indicator
        h, s, v, _ = self.current_color.getHsv()
        if h != -1:  # Valid hue
            angle_rad = radians(h)
            indicator_radius = (s / 255) * self.wheel_radius
            
            x = self.center.x() + indicator_radius * cos(angle_rad)
            y = self.center.y() + indicator_radius * sin(angle_rad)
            
            painter.setPen(QPen(QColor(255, 255, 255), 3))
            painter.drawEllipse(int(x) - 5, int(y) - 5, 10, 10)
            painter.setPen(QPen(QColor(0, 0, 0), 1))
            painter.drawEllipse(int(x) - 5, int(y) - 5, 10, 10)
    
    def mousePressEvent(self, event):
        """Handle mouse press on color wheel"""
        self.update_color_from_position(event.pos())
    
    def mouseMoveEvent(self, event):
        """Handle mouse move on color wheel"""
        if event.buttons() & Qt.LeftButton:
            self.update_color_from_position(event.pos())
    
    def update_color_from_position(self, pos):
        """Update color based on mouse position"""
        # Calculate distance from center
        dx = pos.x() - self.center.x()
        dy = pos.y() - self.center.y()
        distance = (dx * dx + dy * dy) ** 0.5
        
        if distance <= self.wheel_radius:
            # Calculate angle and saturation
            angle = degrees(atan2(dy, dx))
            if angle < 0:
                angle += 360
            
            saturation = int(255 * distance / self.wheel_radius)
            
            # Create new color
            new_color = QColor.fromHsv(int(angle), saturation, 255)
            self.current_color = new_color
            self.colorChanged.emit(new_color)
            self.update()


# Helper functions
def cos(angle):
    """Cosine function for degrees"""
    import math
    return math.cos(math.radians(angle))

def sin(angle):
    """Sine function for degrees"""
    import math
    return math.sin(math.radians(angle))

def radians(degrees):
    """Convert degrees to radians"""
    import math
    return math.radians(degrees)

def degrees(radians):
    """Convert radians to degrees"""
    import math
    return math.degrees(radians)

def atan2(y, x):
    """Arc tangent function"""
    import math
    return math.atan2(y, x)


if __name__ == "__main__":
    app = QApplication(sys.argv)
    dialog = ColorPickerDialog()
    dialog.show()
    sys.exit(app.exec_())