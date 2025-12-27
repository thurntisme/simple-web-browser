#!/usr/bin/env python3
"""
Demo script for the Lunar Calendar Extension.
Shows key features and sample output.
"""

import sys
import datetime
from lunar_calendar_tool import LunarCalendarDialog

def demo_lunar_calendar():
    """Demonstrate lunar calendar features"""
    print("🌙 Lunar Calendar Extension Demo")
    print("=" * 50)
    
    # Create a mock dialog for calculations (no GUI)
    class MockLunarCalendar:
        def __init__(self):
            pass
            
        def calculate_lunar_phase(self, date):
            """Calculate lunar phase for given date"""
            import math
            known_new_moon = datetime.date(2000, 1, 6)
            lunar_cycle = 29.53058867
            
            days_since = (date - known_new_moon).days
            lunar_age = days_since % lunar_cycle
            illumination = 50 * (1 - math.cos(2 * math.pi * lunar_age / lunar_cycle))
            
            if lunar_age < 1.84566:
                phase_name, emoji = "New Moon", "🌑"
            elif lunar_age < 5.53699:
                phase_name, emoji = "Waxing Crescent", "🌒"
            elif lunar_age < 9.22831:
                phase_name, emoji = "First Quarter", "🌓"
            elif lunar_age < 12.91963:
                phase_name, emoji = "Waxing Gibbous", "🌔"
            elif lunar_age < 16.61096:
                phase_name, emoji = "Full Moon", "🌕"
            elif lunar_age < 20.30228:
                phase_name, emoji = "Waning Gibbous", "🌖"
            elif lunar_age < 23.99361:
                phase_name, emoji = "Last Quarter", "🌗"
            else:
                phase_name, emoji = "Waning Crescent", "🌘"
            
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
                'next_full_moon': next_full_moon
            }
        
        def get_chinese_calendar_info(self, date):
            """Get Chinese calendar information"""
            zodiac_animals = [
                ("Rat", "🐭"), ("Ox", "🐂"), ("Tiger", "🐅"), ("Rabbit", "🐰"),
                ("Dragon", "🐉"), ("Snake", "🐍"), ("Horse", "🐎"), ("Goat", "🐐"),
                ("Monkey", "🐒"), ("Rooster", "🐓"), ("Dog", "🐕"), ("Pig", "🐷")
            ]
            
            elements = ["Metal", "Water", "Wood", "Fire", "Earth"]
            
            zodiac_index = (date.year - 1900) % 12
            zodiac_name, zodiac_emoji = zodiac_animals[zodiac_index]
            
            element_index = ((date.year - 1900) // 2) % 5
            element = elements[element_index]
            
            return {
                'year': f"{date.year} ({zodiac_name})",
                'zodiac': zodiac_name,
                'zodiac_emoji': zodiac_emoji,
                'element': element
            }
    
    # Demo with current date
    lunar_calc = MockLunarCalendar()
    today = datetime.date.today()
    
    print(f"📅 Demo Date: {today.strftime('%A, %B %d, %Y')}")
    print()
    
    # Lunar phase information
    lunar_phase = lunar_calc.calculate_lunar_phase(today)
    print("🌙 LUNAR PHASE INFORMATION")
    print("-" * 30)
    print(f"Phase: {lunar_phase['name']} {lunar_phase['emoji']}")
    print(f"Illumination: {lunar_phase['illumination']:.1f}%")
    print(f"Age: {lunar_phase['age']:.1f} days")
    print(f"Next New Moon: {lunar_phase['next_new_moon'].strftime('%B %d, %Y')}")
    print(f"Next Full Moon: {lunar_phase['next_full_moon'].strftime('%B %d, %Y')}")
    print()
    
    # Chinese calendar information
    chinese_info = lunar_calc.get_chinese_calendar_info(today)
    print("🐉 CHINESE CALENDAR")
    print("-" * 20)
    print(f"Year: {chinese_info['year']} {chinese_info['zodiac_emoji']}")
    print(f"Element: {chinese_info['element']}")
    print()
    
    # Show lunar phases for the next 7 days
    print("📊 UPCOMING LUNAR PHASES (Next 7 Days)")
    print("-" * 45)
    for i in range(7):
        future_date = today + datetime.timedelta(days=i)
        phase_info = lunar_calc.calculate_lunar_phase(future_date)
        day_name = future_date.strftime('%a')
        date_str = future_date.strftime('%m/%d')
        print(f"{day_name} {date_str}: {phase_info['name']} {phase_info['emoji']} ({phase_info['illumination']:.0f}%)")
    
    print()
    print("🎯 EXTENSION FEATURES")
    print("-" * 25)
    print("✅ Interactive calendar navigation")
    print("✅ Accurate lunar phase calculations (lunardate)")
    print("✅ Precise Chinese zodiac and elements")
    print("✅ Traditional lunar calendar dates")
    print("✅ Astronomical events detection")
    print("✅ Moon rise/set time estimates")
    print("✅ Status bar date widget: 'Sat 27 Dec (MM-DD) 🌙'")
    print("✅ Moon icon positioned on the right")
    print("✅ Click status widget to open full calendar")
    print("✅ Wider popup window (1200x700)")
    print("✅ Navigation buttons in same row")
    print("✅ Improved layout proportions (7:5 ratio)")
    print("✅ Wider month dropdown with margins")
    print("✅ Data source indicators (accurate vs fallback)")
    print("✅ Simplified interface (no settings/export)")
    print("✅ Keyboard shortcuts (Ctrl+Shift+M)")
    
    print()
    print("📚 LUNARDATE LIBRARY INTEGRATION")
    print("-" * 40)
    print("✅ Accurate lunar phase calculations")
    print("✅ Precise Chinese lunar calendar dates")
    print("✅ Traditional lunar day/month/year")
    print("✅ Leap month detection")
    print("✅ Fallback calculations if library unavailable")
    print("✅ Data source indicators for transparency")
    
    print()
    print("🚀 HOW TO ACCESS IN BROWSER")
    print("-" * 35)
    print("1. Start browser: python3 main.py")
    print("2. Look for date widget in status bar: Sat 27 Dec (11-08) 🌙")
    print("3. Click date widget for quick access to lunar calendar")
    print("4. For zoom controls: Help → Browser Settings → Appearance")
    print("5. Or go to: Tools → Extensions → 🌙 Lunar Calendar")
    print("6. Or press: Ctrl+Shift+M")
    
    print()
    print("📖 For complete documentation, see:")
    print("   lunar_calendar_extension_guide.md")
    
    return True

if __name__ == "__main__":
    demo_lunar_calendar()