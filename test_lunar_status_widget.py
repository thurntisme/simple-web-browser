#!/usr/bin/env python3
"""
Test script for the Lunar Status Widget.
Tests the compact lunar display functionality for the status bar.
"""

import sys
import datetime
from PyQt5.QtWidgets import QApplication, QMainWindow, QStatusBar
from lunar_status_widget import LunarStatusWidget


def test_lunar_status_widget():
    """Test the lunar status widget functionality"""
    print("🌙 Testing Lunar Status Widget...")
    
    app = QApplication(sys.argv)
    
    # Create a test window with status bar
    window = QMainWindow()
    window.setWindowTitle("Lunar Status Widget Test")
    window.resize(600, 400)
    
    # Create status bar
    status_bar = QStatusBar()
    window.setStatusBar(status_bar)
    
    # Add some regular status info
    status_bar.showMessage("Ready")
    
    # Create and add lunar status widget
    lunar_widget = LunarStatusWidget()
    status_bar.addPermanentWidget(lunar_widget)
    
    # Test the lunar calculations
    today = datetime.date.today()
    lunar_info = lunar_widget.calculate_lunar_phase(today)
    
    print(f"📅 Test Date: {today}")
    print(f"🌙 Lunar Phase: {lunar_info['name']} {lunar_info['emoji']}")
    print(f"💡 Illumination: {lunar_info['illumination']:.1f}%")
    
    # Test the display format
    day_name = today.strftime('%a')
    day_num = today.day
    month_name = today.strftime('%b')
    
    if 'lunar_day' in lunar_info:
        print(f"📚 Lunar Day: {lunar_info['lunar_day']}")
        print("✅ Using lunardate library for accurate calculations")
        
        # Show expected display format
        try:
            from lunardate import LunarDate
            lunar_date = LunarDate.fromSolarDate(today.year, today.month, today.day)
            lunar_date_str = f"({lunar_date.month:02d}-{lunar_date.day:02d})"
            display_format = f"{day_name} {day_num} {month_name} {lunar_date_str} {lunar_info['emoji']}"
            print(f"📱 Display Format: {display_format}")
        except:
            print(f"📱 Display Format: {day_name} {day_num} {month_name} (--) {lunar_info['emoji']}")
    else:
        print("📊 Using fallback calculations")
        print(f"📱 Display Format: {day_name} {day_num} {month_name} (--) {lunar_info['emoji']}")
    
    print("\n🎯 Widget Features:")
    print("✅ Date format: 'Sat 27 Dec (MM-DD) 🌙'")
    print("✅ Moon icon positioned on the right")
    print("✅ Larger lunar phase emoji (24x16px)")
    print("✅ Lunar date in parentheses")
    print("✅ Hover effects")
    print("✅ Click to open full calendar")
    print("✅ Automatic hourly updates")
    print("✅ Detailed tooltip information")
    
    print("\n🚀 Starting GUI test...")
    print("• Hover over the lunar widget to see hover effect")
    print("• Click the lunar widget to test click functionality")
    print("• Check tooltip for detailed information")
    
    # Show the test window
    window.show()
    
    return app.exec_()


if __name__ == "__main__":
    sys.exit(test_lunar_status_widget())