"""
Lunar Calendar Tool - Shows lunar phases, Chinese calendar, and astronomical events.
Provides comprehensive lunar information including phases, zodiac signs, and traditional calendar data.
Uses lunardate library for accurate lunar phase calculations.
"""

from PyQt5.QtCore import *
from PyQt5.QtWidgets import *
from PyQt5.QtGui import *
import datetime
import calendar
import math
try:
    from lunardate import LunarDate
    LUNARDATE_AVAILABLE = True
except ImportError:
    LUNARDATE_AVAILABLE = False
    print("Warning: lunardate library not available. Using fallback calculations.")


class LunarCalendarDialog(QDialog):
    """Lunar Calendar Tool Dialog"""
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("🌙 Lunar Calendar")
        self.setMinimumSize(1000, 600)
        self.resize(1200, 700)
        
        # Current date
        self.current_date = datetime.date.today()
        
        self.setup_ui()
        self.update_calendar()
        
    def setup_ui(self):
        """Setup the dialog UI"""
        layout = QVBoxLayout(self)
        layout.setSpacing(10)
        
        # Header with navigation buttons in same row
        header_layout = QHBoxLayout()
        
        # Title
        title_label = QLabel("🌙 Lunar Calendar & Astronomical Events")
        title_label.setStyleSheet("""
            QLabel {
                font-size: 18px;
                font-weight: bold;
                color: #2c3e50;
                padding: 10px;
                background: qlineargradient(x1:0, y1:0, x2:1, y2:0,
                    stop:0 #f8f9fa, stop:1 #e9ecef);
                border-radius: 8px;
                border: 1px solid #dee2e6;
            }
        """)
        header_layout.addWidget(title_label)
        
        # Navigation buttons in same row
        prev_btn = QPushButton("◀ Previous Month")
        prev_btn.clicked.connect(self.previous_month)
        prev_btn.setStyleSheet(self.get_button_style())
        header_layout.addWidget(prev_btn)
        
        today_btn = QPushButton("📅 Today")
        today_btn.clicked.connect(self.go_to_today)
        today_btn.setStyleSheet(self.get_button_style("#28a745"))
        header_layout.addWidget(today_btn)
        
        next_btn = QPushButton("Next Month ▶")
        next_btn.clicked.connect(self.next_month)
        next_btn.setStyleSheet(self.get_button_style())
        header_layout.addWidget(next_btn)
        
        layout.addLayout(header_layout)
        
        # Main content area
        content_layout = QHBoxLayout()
        
        # Left panel - Calendar (7/12 width)
        calendar_group = QGroupBox("📅 Calendar View")
        calendar_group.setStyleSheet(self.get_group_style())
        calendar_layout = QVBoxLayout(calendar_group)
        
        # Month/Year display
        self.month_year_label = QLabel()
        self.month_year_label.setAlignment(Qt.AlignCenter)
        self.month_year_label.setStyleSheet("""
            QLabel {
                font-size: 16px;
                font-weight: bold;
                color: #495057;
                padding: 8px;
                background-color: #f8f9fa;
                border-radius: 6px;
                margin-bottom: 10px;
            }
        """)
        calendar_layout.addWidget(self.month_year_label)
        
        # Calendar widget
        self.calendar_widget = QCalendarWidget()
        self.calendar_widget.setMinimumHeight(300)
        self.calendar_widget.clicked.connect(self.date_selected)
        self.calendar_widget.setStyleSheet("""
            QCalendarWidget {
                background-color: white;
                border: 1px solid #dee2e6;
                border-radius: 6px;
            }
            QCalendarWidget QToolButton {
                height: 30px;
                width: 80px;
                color: #495057;
                font-size: 12px;
                background-color: #f8f9fa;
                border: 1px solid #dee2e6;
                border-radius: 4px;
                margin: 2px;
            }
            QCalendarWidget QToolButton:hover {
                background-color: #e9ecef;
            }
            QCalendarWidget QMenu {
                background-color: white;
                border: 1px solid #dee2e6;
            }
            QCalendarWidget QSpinBox {
                font-size: 12px;
                color: #495057;
                background-color: white;
                border: 1px solid #dee2e6;
                border-radius: 4px;
                min-width: 80px;
                margin: 2px;
            }
            QCalendarWidget QAbstractItemView:enabled {
                font-size: 11px;
                color: #495057;
                background-color: white;
                selection-background-color: #007bff;
                selection-color: white;
            }
        """)
        calendar_layout.addWidget(self.calendar_widget)
        
        content_layout.addWidget(calendar_group, 7)  # 7/12 width
        
        # Right panel - Lunar information (5/12 width)
        info_group = QGroupBox("🌙 Lunar Information")
        info_group.setStyleSheet(self.get_group_style())
        info_layout = QVBoxLayout(info_group)
        
        # Scroll area for lunar info
        scroll_area = QScrollArea()
        scroll_area.setWidgetResizable(True)
        scroll_area.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        
        self.info_widget = QWidget()
        self.info_layout = QVBoxLayout(self.info_widget)
        self.info_layout.setSpacing(15)
        
        scroll_area.setWidget(self.info_widget)
        info_layout.addWidget(scroll_area)
        
        content_layout.addWidget(info_group, 5)  # 5/12 width
        
        # Add some margin to the right
        content_layout.setContentsMargins(0, 0, 20, 0)
        
        layout.addLayout(content_layout)
        
        # Bottom panel - Close button only
        actions_layout = QHBoxLayout()
        
        actions_layout.addStretch()
        
        close_btn = QPushButton("❌ Close")
        close_btn.clicked.connect(self.close)
        close_btn.setStyleSheet(self.get_button_style("#dc3545"))
        actions_layout.addWidget(close_btn)
        
        layout.addLayout(actions_layout)
        
    def get_button_style(self, color="#007bff"):
        """Get button styling"""
        return f"""
            QPushButton {{
                background-color: {color};
                color: white;
                border: none;
                padding: 8px 16px;
                border-radius: 6px;
                font-weight: 600;
                min-width: 100px;
            }}
            QPushButton:hover {{
                background-color: {self.darken_color(color)};
            }}
            QPushButton:pressed {{
                background-color: {self.darken_color(color, 0.2)};
            }}
        """
    
    def get_group_style(self):
        """Get group box styling"""
        return """
            QGroupBox {
                font-weight: bold;
                font-size: 14px;
                color: #495057;
                border: 2px solid #dee2e6;
                border-radius: 8px;
                margin-top: 10px;
                padding-top: 10px;
            }
            QGroupBox::title {
                subcontrol-origin: margin;
                left: 10px;
                padding: 0 8px 0 8px;
                background-color: white;
            }
        """
    
    def darken_color(self, hex_color, factor=0.1):
        """Darken a hex color by a factor"""
        # Remove # if present
        hex_color = hex_color.lstrip('#')
        
        # Convert to RGB
        r = int(hex_color[0:2], 16)
        g = int(hex_color[2:4], 16)
        b = int(hex_color[4:6], 16)
        
        # Darken
        r = max(0, int(r * (1 - factor)))
        g = max(0, int(g * (1 - factor)))
        b = max(0, int(b * (1 - factor)))
        
        return f"#{r:02x}{g:02x}{b:02x}"
    
    def previous_month(self):
        """Go to previous month"""
        if self.current_date.month == 1:
            self.current_date = self.current_date.replace(year=self.current_date.year - 1, month=12)
        else:
            self.current_date = self.current_date.replace(month=self.current_date.month - 1)
        self.update_calendar()
    
    def next_month(self):
        """Go to next month"""
        if self.current_date.month == 12:
            self.current_date = self.current_date.replace(year=self.current_date.year + 1, month=1)
        else:
            self.current_date = self.current_date.replace(month=self.current_date.month + 1)
        self.update_calendar()
    
    def go_to_today(self):
        """Go to current date"""
        self.current_date = datetime.date.today()
        self.update_calendar()
    
    def date_selected(self, date):
        """Handle date selection from calendar"""
        self.current_date = date.toPyDate()
        self.update_lunar_info()
    
    def update_calendar(self):
        """Update calendar display"""
        # Update month/year label
        month_name = calendar.month_name[self.current_date.month]
        self.month_year_label.setText(f"{month_name} {self.current_date.year}")
        
        # Update calendar widget
        qt_date = QDate(self.current_date.year, self.current_date.month, self.current_date.day)
        self.calendar_widget.setSelectedDate(qt_date)
        
        # Update lunar information
        self.update_lunar_info()
    
    def update_lunar_info(self):
        """Update lunar information panel"""
        # Clear existing info
        for i in reversed(range(self.info_layout.count())):
            child = self.info_layout.itemAt(i).widget()
            if child:
                child.setParent(None)
        
        # Current date info
        date_info = self.create_info_section("📅 Selected Date", [
            f"Date: {self.current_date.strftime('%A, %B %d, %Y')}",
            f"Day of Year: {self.current_date.timetuple().tm_yday}",
            f"Week: {self.current_date.isocalendar()[1]}"
        ])
        self.info_layout.addWidget(date_info)
        
        # Lunar phase info
        lunar_phase = self.calculate_lunar_phase(self.current_date)
        phase_items = [
            f"Phase: {lunar_phase['name']} {lunar_phase['emoji']}",
            f"Illumination: {lunar_phase['illumination']:.1f}%",
            f"Age: {lunar_phase['age']:.1f} days"
        ]
        
        # Add additional info if using lunardate
        if lunar_phase.get('source') == 'lunardate':
            phase_items.extend([
                f"Lunar Day: {lunar_phase.get('lunar_day', 'N/A')}",
                f"Lunar Month: {lunar_phase.get('lunar_month', 'N/A')}",
                f"Lunar Year: {lunar_phase.get('lunar_year', 'N/A')}"
            ])
        
        phase_items.extend([
            f"Next New Moon: {lunar_phase['next_new_moon'].strftime('%B %d, %Y')}",
            f"Next Full Moon: {lunar_phase['next_full_moon'].strftime('%B %d, %Y')}"
        ])
        
        # Add data source indicator
        source_indicator = "📚 Accurate (lunardate)" if lunar_phase.get('source') == 'lunardate' else "📊 Calculated (fallback)"
        phase_items.append(f"Data Source: {source_indicator}")
        
        phase_info = self.create_info_section("🌙 Lunar Phase", phase_items)
        self.info_layout.addWidget(phase_info)
        
        # Chinese calendar info
        chinese_info = self.get_chinese_calendar_info(self.current_date)
        chinese_items = [
            f"Year: {chinese_info['year']} ({chinese_info['zodiac']} {chinese_info['zodiac_emoji']})",
            f"Element: {chinese_info['element']}",
            f"Month: {chinese_info['month']}",
            f"Day: {chinese_info['day']}"
        ]
        
        # Add lunar date if available
        if chinese_info.get('lunar_date'):
            chinese_items.append(f"Lunar Date: {chinese_info['lunar_date']}")
        
        # Add data source indicator
        source_indicator = "📚 Accurate (lunardate)" if chinese_info.get('source') == 'lunardate' else "📊 Calculated (fallback)"
        chinese_items.append(f"Data Source: {source_indicator}")
        
        chinese_section = self.create_info_section("🐉 Chinese Calendar", chinese_items)
        self.info_layout.addWidget(chinese_section)
        
        # Astronomical events
        events = self.get_astronomical_events(self.current_date)
        if events:
            events_section = self.create_info_section("⭐ Astronomical Events", events)
            self.info_layout.addWidget(events_section)
        
        # Moon rise/set times (approximate)
        moon_times = self.calculate_moon_times(self.current_date)
        moon_section = self.create_info_section("🌙 Moon Times (Approximate)", [
            f"Moonrise: {moon_times['rise']}",
            f"Moonset: {moon_times['set']}",
            f"Moon Sign: {moon_times['sign']}"
        ])
        self.info_layout.addWidget(moon_section)
        
        # Add stretch to push content to top
        self.info_layout.addStretch()
    
    def create_info_section(self, title, items):
        """Create an information section widget"""
        section = QFrame()
        section.setFrameStyle(QFrame.Box)
        section.setStyleSheet("""
            QFrame {
                background-color: #f8f9fa;
                border: 1px solid #dee2e6;
                border-radius: 6px;
                padding: 5px;
            }
        """)
        
        layout = QVBoxLayout(section)
        layout.setSpacing(5)
        
        # Title
        title_label = QLabel(title)
        title_label.setStyleSheet("""
            QLabel {
                font-weight: bold;
                font-size: 13px;
                color: #495057;
                padding: 5px;
                background-color: #e9ecef;
                border-radius: 4px;
            }
        """)
        layout.addWidget(title_label)
        
        # Items
        for item in items:
            item_label = QLabel(f"• {item}")
            item_label.setStyleSheet("""
                QLabel {
                    font-size: 11px;
                    color: #6c757d;
                    padding: 2px 5px;
                }
            """)
            item_label.setWordWrap(True)
            layout.addWidget(item_label)
        
        return section
    
    def calculate_lunar_phase(self, date):
        """Calculate lunar phase for given date using lunardate library"""
        if LUNARDATE_AVAILABLE:
            return self.calculate_lunar_phase_with_lunardate(date)
        else:
            return self.calculate_lunar_phase_fallback(date)
    
    def calculate_lunar_phase_with_lunardate(self, date):
        """Calculate lunar phase using lunardate library for accuracy"""
        try:
            # Convert to LunarDate
            lunar_date = LunarDate.fromSolarDate(date.year, date.month, date.day)
            
            # Get lunar day (1-30, where 1 is new moon, 15 is full moon)
            lunar_day = lunar_date.day
            
            # Calculate lunar age and illumination based on lunar day
            # Lunar month is typically 29.5 days, so we normalize
            if lunar_day <= 15:
                # Waxing phase (new moon to full moon)
                lunar_age = lunar_day - 1  # 0-14 days
                illumination = (lunar_day - 1) / 14 * 100  # 0-100%
            else:
                # Waning phase (full moon to new moon)
                lunar_age = lunar_day - 1  # 15-29 days
                illumination = (30 - lunar_day) / 14 * 100  # 100-0%
            
            # Determine phase name and emoji based on lunar day
            if lunar_day == 1:
                phase_name, emoji = "New Moon", "🌑"
            elif 1 < lunar_day <= 7:
                phase_name, emoji = "Waxing Crescent", "🌒"
            elif 7 < lunar_day <= 9:
                phase_name, emoji = "First Quarter", "🌓"
            elif 9 < lunar_day <= 15:
                phase_name, emoji = "Waxing Gibbous", "🌔"
            elif lunar_day == 15:
                phase_name, emoji = "Full Moon", "🌕"
            elif 15 < lunar_day <= 22:
                phase_name, emoji = "Waning Gibbous", "🌖"
            elif 22 < lunar_day <= 24:
                phase_name, emoji = "Last Quarter", "🌗"
            else:  # 24 < lunar_day <= 30
                phase_name, emoji = "Waning Crescent", "🌘"
            
            # Calculate next new and full moons
            # Find next new moon (lunar day 1)
            days_to_new = 30 - lunar_day if lunar_day > 1 else 29
            next_new_moon = date + datetime.timedelta(days=days_to_new)
            
            # Find next full moon (lunar day 15)
            if lunar_day < 15:
                days_to_full = 15 - lunar_day
            else:
                days_to_full = (30 - lunar_day) + 15
            next_full_moon = date + datetime.timedelta(days=days_to_full)
            
            return {
                'name': phase_name,
                'emoji': emoji,
                'age': lunar_age,
                'illumination': max(0, min(100, illumination)),
                'lunar_day': lunar_day,
                'lunar_month': lunar_date.month,
                'lunar_year': lunar_date.year,
                'next_new_moon': next_new_moon,
                'next_full_moon': next_full_moon,
                'source': 'lunardate'
            }
            
        except Exception as e:
            print(f"Error using lunardate: {e}")
            return self.calculate_lunar_phase_fallback(date)
    
    def calculate_lunar_phase_fallback(self, date):
        """Fallback lunar phase calculation (original method)"""
        # Known new moon: January 6, 2000
        known_new_moon = datetime.date(2000, 1, 6)
        lunar_cycle = 29.53058867  # Average lunar cycle in days
        
        # Calculate days since known new moon
        days_since = (date - known_new_moon).days
        
        # Calculate current lunar age
        lunar_age = days_since % lunar_cycle
        
        # Calculate illumination percentage
        illumination = 50 * (1 - math.cos(2 * math.pi * lunar_age / lunar_cycle))
        
        # Determine phase name and emoji
        if lunar_age < 1.84566:
            phase_name = "New Moon"
            emoji = "🌑"
        elif lunar_age < 5.53699:
            phase_name = "Waxing Crescent"
            emoji = "🌒"
        elif lunar_age < 9.22831:
            phase_name = "First Quarter"
            emoji = "🌓"
        elif lunar_age < 12.91963:
            phase_name = "Waxing Gibbous"
            emoji = "🌔"
        elif lunar_age < 16.61096:
            phase_name = "Full Moon"
            emoji = "🌕"
        elif lunar_age < 20.30228:
            phase_name = "Waning Gibbous"
            emoji = "🌖"
        elif lunar_age < 23.99361:
            phase_name = "Last Quarter"
            emoji = "🌗"
        else:
            phase_name = "Waning Crescent"
            emoji = "🌘"
        
        # Calculate next new and full moons
        days_to_new = lunar_cycle - lunar_age
        if days_to_new < 1:
            days_to_new += lunar_cycle
        
        days_to_full = (lunar_cycle / 2) - lunar_age
        if days_to_full < 0:
            days_to_full += lunar_cycle
        
        next_new_moon = date + datetime.timedelta(days=days_to_new)
        next_full_moon = date + datetime.timedelta(days=days_to_full)
        
        return {
            'name': phase_name,
            'emoji': emoji,
            'age': lunar_age,
            'illumination': illumination,
            'next_new_moon': next_new_moon,
            'next_full_moon': next_full_moon,
            'source': 'fallback'
        }
    
    def get_chinese_calendar_info(self, date):
        """Get Chinese calendar information using lunardate library"""
        if LUNARDATE_AVAILABLE:
            return self.get_chinese_calendar_with_lunardate(date)
        else:
            return self.get_chinese_calendar_fallback(date)
    
    def get_chinese_calendar_with_lunardate(self, date):
        """Get Chinese calendar information using lunardate library"""
        try:
            # Convert to LunarDate
            lunar_date = LunarDate.fromSolarDate(date.year, date.month, date.day)
            
            # Chinese zodiac animals (12-year cycle)
            zodiac_animals = [
                ("Rat", "🐭"), ("Ox", "🐂"), ("Tiger", "🐅"), ("Rabbit", "🐰"),
                ("Dragon", "🐉"), ("Snake", "🐍"), ("Horse", "🐎"), ("Goat", "🐐"),
                ("Monkey", "🐒"), ("Rooster", "🐓"), ("Dog", "🐕"), ("Pig", "🐷")
            ]
            
            # Five elements (10-year cycle, 2 years per element)
            elements = ["Metal", "Water", "Wood", "Fire", "Earth"]
            
            # Calculate zodiac year (based on lunar year)
            lunar_year = lunar_date.year
            zodiac_index = (lunar_year - 1900) % 12
            zodiac_name, zodiac_emoji = zodiac_animals[zodiac_index]
            
            # Calculate element (simplified)
            element_index = ((lunar_year - 1900) // 2) % 5
            element = elements[element_index]
            
            # Get lunar month and day
            lunar_month = lunar_date.month
            lunar_day = lunar_date.day
            
            # Check if it's a leap month
            is_leap = lunar_date.isLeapMonth if hasattr(lunar_date, 'isLeapMonth') else False
            month_str = f"Month {lunar_month}" + (" (Leap)" if is_leap else "")
            
            return {
                'year': f"{lunar_year} ({zodiac_name})",
                'zodiac': zodiac_name,
                'zodiac_emoji': zodiac_emoji,
                'element': element,
                'month': month_str,
                'day': f"Day {lunar_day}",
                'lunar_date': f"{lunar_year}-{lunar_month:02d}-{lunar_day:02d}",
                'source': 'lunardate'
            }
            
        except Exception as e:
            print(f"Error using lunardate for Chinese calendar: {e}")
            return self.get_chinese_calendar_fallback(date)
    
    def get_chinese_calendar_fallback(self, date):
        """Fallback Chinese calendar calculation"""
        # Chinese zodiac animals (12-year cycle starting from 1900 = Rat)
        zodiac_animals = [
            ("Rat", "🐭"), ("Ox", "🐂"), ("Tiger", "🐅"), ("Rabbit", "🐰"),
            ("Dragon", "🐉"), ("Snake", "🐍"), ("Horse", "🐎"), ("Goat", "🐐"),
            ("Monkey", "🐒"), ("Rooster", "🐓"), ("Dog", "🐕"), ("Pig", "🐷")
        ]
        
        # Five elements (5-year cycle)
        elements = ["Metal", "Water", "Wood", "Fire", "Earth"]
        
        # Calculate zodiac year (1900 = Rat year)
        zodiac_index = (date.year - 1900) % 12
        zodiac_name, zodiac_emoji = zodiac_animals[zodiac_index]
        
        # Calculate element (simplified)
        element_index = ((date.year - 1900) // 2) % 5
        element = elements[element_index]
        
        # Simplified Chinese month and day calculation
        # This is a basic approximation
        chinese_month = ((date.month - 1) % 12) + 1
        chinese_day = date.day
        
        return {
            'year': f"{date.year} ({zodiac_name})",
            'zodiac': zodiac_name,
            'zodiac_emoji': zodiac_emoji,
            'element': element,
            'month': f"Month {chinese_month}",
            'day': f"Day {chinese_day}",
            'source': 'fallback'
        }
    
    def get_astronomical_events(self, date):
        """Get astronomical events for the date"""
        events = []
        
        # Check for seasonal events
        year = date.year
        
        # Approximate dates for equinoxes and solstices
        spring_equinox = datetime.date(year, 3, 20)
        summer_solstice = datetime.date(year, 6, 21)
        autumn_equinox = datetime.date(year, 9, 22)
        winter_solstice = datetime.date(year, 12, 21)
        
        if date == spring_equinox:
            events.append("🌸 Spring Equinox - Equal day and night")
        elif date == summer_solstice:
            events.append("☀️ Summer Solstice - Longest day of the year")
        elif date == autumn_equinox:
            events.append("🍂 Autumn Equinox - Equal day and night")
        elif date == winter_solstice:
            events.append("❄️ Winter Solstice - Shortest day of the year")
        
        # Check for meteor showers (approximate dates)
        meteor_showers = {
            (1, 3): "🌠 Quadrantids Meteor Shower",
            (4, 22): "🌠 Lyrids Meteor Shower",
            (5, 6): "🌠 Eta Aquariids Meteor Shower",
            (8, 12): "🌠 Perseids Meteor Shower",
            (10, 21): "🌠 Orionids Meteor Shower",
            (11, 17): "🌠 Leonids Meteor Shower",
            (12, 14): "🌠 Geminids Meteor Shower"
        }
        
        for (month, day), event in meteor_showers.items():
            if date.month == month and abs(date.day - day) <= 2:
                events.append(event)
        
        # Check lunar phase events
        lunar_phase = self.calculate_lunar_phase(date)
        if lunar_phase['name'] == "New Moon":
            events.append("🌑 New Moon - Best time for stargazing")
        elif lunar_phase['name'] == "Full Moon":
            events.append("🌕 Full Moon - Brightest night of the month")
        
        return events
    
    def calculate_moon_times(self, date):
        """Calculate approximate moon rise/set times"""
        # This is a simplified calculation
        # In reality, moon times vary significantly by location and date
        
        lunar_phase = self.calculate_lunar_phase(date)
        lunar_age = lunar_phase['age']
        
        # Approximate moonrise time based on lunar age
        # New moon rises with sun, full moon rises at sunset
        base_rise_hour = 6 + (lunar_age / 29.53 * 24)
        if base_rise_hour >= 24:
            base_rise_hour -= 24
        
        rise_hour = int(base_rise_hour)
        rise_minute = int((base_rise_hour - rise_hour) * 60)
        
        # Moonset is approximately 12.5 hours after moonrise
        set_time = base_rise_hour + 12.5
        if set_time >= 24:
            set_time -= 24
        
        set_hour = int(set_time)
        set_minute = int((set_time - set_hour) * 60)
        
        # Approximate moon sign (simplified)
        zodiac_signs = [
            "♈ Aries", "♉ Taurus", "♊ Gemini", "♋ Cancer",
            "♌ Leo", "♍ Virgo", "♎ Libra", "♏ Scorpio",
            "♐ Sagittarius", "♑ Capricorn", "♒ Aquarius", "♓ Pisces"
        ]
        
        # Moon moves through zodiac in about 27.3 days
        sign_index = int((lunar_age / 27.3 * 12)) % 12
        moon_sign = zodiac_signs[sign_index]
        
        return {
            'rise': f"{rise_hour:02d}:{rise_minute:02d}",
            'set': f"{set_hour:02d}:{set_minute:02d}",
            'sign': moon_sign
        }


def show_lunar_calendar(parent=None):
    """Show the lunar calendar dialog"""
    dialog = LunarCalendarDialog(parent)
    dialog.show()
    return dialog


if __name__ == "__main__":
    import sys
    app = QApplication(sys.argv)
    
    dialog = LunarCalendarDialog()
    dialog.show()
    
    sys.exit(app.exec_())