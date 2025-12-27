#!/usr/bin/env python3
"""
Test script for the Lunar Calendar Tool.
Tests the basic functionality and UI components.
"""

import sys
import datetime
from PyQt5.QtWidgets import QApplication
from lunar_calendar_tool import LunarCalendarDialog


def test_lunar_calendar():
    """Test the lunar calendar functionality"""
    print("🌙 Testing Lunar Calendar Tool...")
    
    app = QApplication(sys.argv)
    
    # Create dialog
    dialog = LunarCalendarDialog()
    
    # Test lunar phase calculation
    test_date = datetime.date(2024, 1, 15)
    lunar_phase = dialog.calculate_lunar_phase(test_date)
    
    print(f"📅 Test Date: {test_date}")
    print(f"🌙 Lunar Phase: {lunar_phase['name']} {lunar_phase['emoji']}")
    print(f"💡 Illumination: {lunar_phase['illumination']:.1f}%")
    print(f"📊 Age: {lunar_phase['age']:.1f} days")
    
    # Test Chinese calendar
    chinese_info = dialog.get_chinese_calendar_info(test_date)
    print(f"🐉 Chinese Year: {chinese_info['year']}")
    print(f"🔥 Element: {chinese_info['element']}")
    
    # Test astronomical events
    events = dialog.get_astronomical_events(test_date)
    if events:
        print(f"⭐ Events: {', '.join(events)}")
    else:
        print("⭐ No special events on this date")
    
    # Test moon times
    moon_times = dialog.calculate_moon_times(test_date)
    print(f"🌅 Moonrise: {moon_times['rise']}")
    print(f"🌇 Moonset: {moon_times['set']}")
    print(f"♈ Moon Sign: {moon_times['sign']}")
    
    print("\n✅ Lunar Calendar Tool test completed successfully!")
    print("🚀 Starting GUI for visual testing...")
    
    # Show dialog for visual testing
    dialog.show()
    
    return app.exec_()


if __name__ == "__main__":
    sys.exit(test_lunar_calendar())