#!/usr/bin/env python3
"""
Test script to demonstrate lunardate library integration in the Lunar Calendar Tool.
Shows the difference between lunardate calculations and fallback calculations.
"""

import sys
import datetime
from PyQt5.QtWidgets import QApplication

def test_lunardate_integration():
    """Test lunardate integration and compare with fallback"""
    print("🌙 Testing Lunardate Library Integration")
    print("=" * 50)
    
    # Initialize QApplication for GUI components
    app = QApplication(sys.argv)
    
    from lunar_calendar_tool import LunarCalendarDialog
    
    # Create dialog instance
    dialog = LunarCalendarDialog()
    
    # Test dates
    test_dates = [
        datetime.date(2024, 1, 15),  # Winter
        datetime.date(2024, 6, 15),  # Summer
        datetime.date(2024, 9, 15),  # Autumn
        datetime.date.today()        # Today
    ]
    
    for test_date in test_dates:
        print(f"\n📅 Testing Date: {test_date.strftime('%A, %B %d, %Y')}")
        print("-" * 40)
        
        # Test lunar phase calculation
        lunar_phase = dialog.calculate_lunar_phase(test_date)
        print(f"🌙 Lunar Phase: {lunar_phase['name']} {lunar_phase['emoji']}")
        print(f"💡 Illumination: {lunar_phase['illumination']:.1f}%")
        print(f"📊 Age: {lunar_phase['age']:.1f} days")
        
        if lunar_phase.get('source') == 'lunardate':
            print(f"📚 Lunar Day: {lunar_phase.get('lunar_day', 'N/A')}")
            print(f"📚 Lunar Month: {lunar_phase.get('lunar_month', 'N/A')}")
            print(f"📚 Lunar Year: {lunar_phase.get('lunar_year', 'N/A')}")
            print(f"✅ Data Source: Accurate (lunardate library)")
        else:
            print(f"⚠️ Data Source: Fallback calculations")
        
        # Test Chinese calendar
        chinese_info = dialog.get_chinese_calendar_info(test_date)
        print(f"🐉 Chinese Year: {chinese_info['year']}")
        print(f"🔥 Element: {chinese_info['element']}")
        print(f"📅 Month: {chinese_info['month']}")
        print(f"📅 Day: {chinese_info['day']}")
        
        if chinese_info.get('lunar_date'):
            print(f"📚 Lunar Date: {chinese_info['lunar_date']}")
        
        if chinese_info.get('source') == 'lunardate':
            print(f"✅ Chinese Calendar Source: Accurate (lunardate library)")
        else:
            print(f"⚠️ Chinese Calendar Source: Fallback calculations")
    
    print("\n" + "=" * 50)
    print("🎯 LUNARDATE LIBRARY BENEFITS")
    print("-" * 30)
    print("✅ More accurate lunar phase calculations")
    print("✅ Precise Chinese lunar calendar dates")
    print("✅ Traditional lunar day/month/year information")
    print("✅ Proper handling of leap months")
    print("✅ Better alignment with traditional calendars")
    print("✅ Fallback support for reliability")
    
    print("\n📦 INSTALLATION")
    print("-" * 15)
    print("pip install lunardate")
    print("# or")
    print("pip install -r requirements.txt")
    
    print("\n🔧 INTEGRATION FEATURES")
    print("-" * 25)
    print("• Automatic detection of lunardate availability")
    print("• Graceful fallback to mathematical calculations")
    print("• Clear data source indicators in UI")
    print("• Enhanced lunar information display")
    print("• Improved Chinese calendar accuracy")
    
    return True

if __name__ == "__main__":
    test_lunardate_integration()