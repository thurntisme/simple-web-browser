"""
Lunar Status Widget - Shows current lunar phase in the browser status bar.
Displays compact lunar information with click-to-expand functionality.
"""

from PyQt5.QtCore import *
from PyQt5.QtWidgets import *
from PyQt5.QtGui import *
import datetime
try:
    from lunardate import LunarDate
    LUNARDATE_AVAILABLE = True
except ImportError:
    LUNARDATE_AVAILABLE = False


class LunarStatusWidget(QWidget):
    """Compact lunar status widget for the status bar"""
    
    # Signal emitted when user clicks to open full lunar calendar
    lunar_calendar_requested = pyqtSignal()
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.parent_window = parent
        
        # Update timer
        self.update_timer = QTimer()
        self.update_timer.timeout.connect(self.update_lunar_data)
        self.update_timer.start(3600000)  # Update every hour
        
        self.setup_ui()
        self.update_lunar_data()
        
    def setup_ui(self):
        """Setup the widget UI"""
        layout = QHBoxLayout(self)
        layout.setContentsMargins(5, 2, 5, 2)
        layout.setSpacing(5)
        
        # Lunar phase text (now comes first)
        self.phase_text = QLabel("Loading...")
        self.phase_text.setStyleSheet("""
            QLabel {
                font-size: 10px;
                color: #495057;
                background: transparent;
                font-weight: 500;
            }
        """)
        layout.addWidget(self.phase_text)
        
        # Lunar phase emoji (now comes after the text)
        self.phase_emoji = QLabel("🌙")
        self.phase_emoji.setFixedSize(30, 26)
        self.phase_emoji.setAlignment(Qt.AlignCenter)
        self.phase_emoji.setStyleSheet("""
            QLabel {
                font-size: 12px;
                background: transparent;
                margin-bottom: 8px;
            }
        """)
        layout.addWidget(self.phase_emoji)
        
        # Set widget properties
        self.setFixedHeight(20)
        self.setMinimumWidth(140)
        self.setMaximumWidth(160)
        
        # Set cursor and tooltip
        self.setCursor(Qt.PointingHandCursor)
        self.setToolTip("Click to open Lunar Calendar")
        
        # Apply styling
        self.setStyleSheet("""
            LunarStatusWidget {
                background-color: #f8f9fa;
                border: 1px solid #dee2e6;
                border-radius: 4px;
                padding: 2px;
            }
            LunarStatusWidget:hover {
                background-color: #e9ecef;
                border-color: #adb5bd;
            }
        """)
        
    def calculate_lunar_phase(self, date):
        """Calculate lunar phase for given date"""
        if LUNARDATE_AVAILABLE:
            try:
                # Convert to LunarDate
                lunar_date = LunarDate.fromSolarDate(date.year, date.month, date.day)
                lunar_day = lunar_date.day
                
                # Calculate illumination based on lunar day
                if lunar_day <= 15:
                    illumination = (lunar_day - 1) / 14 * 100
                else:
                    illumination = (30 - lunar_day) / 14 * 100
                
                # Determine phase name and emoji based on lunar day
                if lunar_day == 1:
                    phase_name, emoji = "New", "🌑"
                elif 1 < lunar_day <= 7:
                    phase_name, emoji = "Waxing", "🌒"
                elif 7 < lunar_day <= 9:
                    phase_name, emoji = "1st Qtr", "🌓"
                elif 9 < lunar_day <= 15:
                    phase_name, emoji = "Waxing", "🌔"
                elif lunar_day == 15:
                    phase_name, emoji = "Full", "🌕"
                elif 15 < lunar_day <= 22:
                    phase_name, emoji = "Waning", "🌖"
                elif 22 < lunar_day <= 24:
                    phase_name, emoji = "3rd Qtr", "🌗"
                else:
                    phase_name, emoji = "Waning", "🌘"
                
                return {
                    'name': phase_name,
                    'emoji': emoji,
                    'illumination': max(0, min(100, illumination)),
                    'lunar_day': lunar_day
                }
                
            except Exception as e:
                print(f"Error using lunardate in status widget: {e}")
                return self.calculate_lunar_phase_fallback(date)
        else:
            return self.calculate_lunar_phase_fallback(date)
    
    def calculate_lunar_phase_fallback(self, date):
        """Fallback lunar phase calculation"""
        import math
        
        # Known new moon: January 6, 2000
        known_new_moon = datetime.date(2000, 1, 6)
        lunar_cycle = 29.53058867
        
        days_since = (date - known_new_moon).days
        lunar_age = days_since % lunar_cycle
        illumination = 50 * (1 - math.cos(2 * math.pi * lunar_age / lunar_cycle))
        
        # Determine phase name and emoji (shortened for status bar)
        if lunar_age < 1.84566:
            phase_name, emoji = "New", "🌑"
        elif lunar_age < 5.53699:
            phase_name, emoji = "Waxing", "🌒"
        elif lunar_age < 9.22831:
            phase_name, emoji = "1st Qtr", "🌓"
        elif lunar_age < 12.91963:
            phase_name, emoji = "Waxing", "🌔"
        elif lunar_age < 16.61096:
            phase_name, emoji = "Full", "🌕"
        elif lunar_age < 20.30228:
            phase_name, emoji = "Waning", "🌖"
        elif lunar_age < 23.99361:
            phase_name, emoji = "3rd Qtr", "🌗"
        else:
            phase_name, emoji = "Waning", "🌘"
        
        return {
            'name': phase_name,
            'emoji': emoji,
            'illumination': illumination
        }
    
    def update_lunar_data(self):
        """Update lunar data display"""
        try:
            today = datetime.date.today()
            lunar_info = self.calculate_lunar_phase(today)
            
            # Update emoji
            self.phase_emoji.setText(lunar_info['emoji'])
            
            # Format date as "Sat 27 Dec (lunar date)"
            day_name = today.strftime('%a')  # Sat
            day_num = today.day  # 27
            month_name = today.strftime('%b')  # Dec
            
            # Get lunar date if available
            lunar_date_str = ""
            if LUNARDATE_AVAILABLE:
                try:
                    lunar_date = LunarDate.fromSolarDate(today.year, today.month, today.day)
                    lunar_date_str = f"({lunar_date.month:02d}-{lunar_date.day:02d})"
                except:
                    lunar_date_str = "(--)"
            else:
                lunar_date_str = "(--)"
            
            # Create the display text
            date_text = f"{day_name} {day_num} {month_name} {lunar_date_str}"
            self.phase_text.setText(date_text)
            
            # Update tooltip with detailed lunar information
            illumination = lunar_info['illumination']
            tooltip_text = f"🌙 Lunar Phase: {lunar_info['name']} {lunar_info['emoji']}\n"
            tooltip_text += f"💡 Illumination: {illumination:.1f}%\n"
            
            if 'lunar_day' in lunar_info:
                tooltip_text += f"📅 Lunar Day: {lunar_info['lunar_day']}\n"
            
            tooltip_text += f"📅 Solar Date: {today.strftime('%A, %B %d, %Y')}\n"
            
            if LUNARDATE_AVAILABLE:
                try:
                    lunar_date = LunarDate.fromSolarDate(today.year, today.month, today.day)
                    tooltip_text += f"📅 Lunar Date: {lunar_date.year}-{lunar_date.month:02d}-{lunar_date.day:02d}\n"
                except:
                    tooltip_text += f"📅 Lunar Date: Not available\n"
            
            tooltip_text += "\nClick to open full Lunar Calendar"
            
            self.setToolTip(tooltip_text)
            
        except Exception as e:
            print(f"Error updating lunar status widget: {e}")
            self.phase_emoji.setText("🌙")
            self.phase_text.setText("Error")
            self.setToolTip("Lunar data unavailable - Click to open Lunar Calendar")
    
    def mousePressEvent(self, event):
        """Handle mouse click to open lunar calendar"""
        if event.button() == Qt.LeftButton:
            # Emit signal to request lunar calendar
            self.lunar_calendar_requested.emit()
            
            # Alternative: directly call parent method if available
            if hasattr(self.parent_window, 'show_lunar_calendar'):
                self.parent_window.show_lunar_calendar()
        
        super().mousePressEvent(event)
    
    def enterEvent(self, event):
        """Handle mouse enter for hover effect"""
        self.setStyleSheet("""
            LunarStatusWidget {
                background-color: #e9ecef;
                border: 1px solid #adb5bd;
                border-radius: 4px;
                padding: 2px;
            }
        """)
        super().enterEvent(event)
    
    def leaveEvent(self, event):
        """Handle mouse leave to restore normal appearance"""
        self.setStyleSheet("""
            LunarStatusWidget {
                background-color: #f8f9fa;
                border: 1px solid #dee2e6;
                border-radius: 4px;
                padding: 2px;
            }
        """)
        super().leaveEvent(event)
    
    def refresh(self):
        """Manually refresh lunar data"""
        self.update_lunar_data()


if __name__ == "__main__":
    import sys
    app = QApplication(sys.argv)
    
    widget = LunarStatusWidget()
    widget.show()
    
    sys.exit(app.exec_())