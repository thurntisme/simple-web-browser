# 🌙 Lunar Calendar Extension Guide

## Overview

The Lunar Calendar extension provides comprehensive lunar and astronomical information within your browser application. This extension offers detailed lunar phase calculations, Chinese calendar data, astronomical events, and moon timing information.

## Features

### 🌙 Lunar Phase Information
- **Current Phase**: Displays the current lunar phase with emoji representation
- **Illumination Percentage**: Shows how much of the moon is currently illuminated
- **Lunar Age**: Days since the last new moon
- **Next Events**: Dates for upcoming new moon and full moon

### 🐉 Chinese Calendar Integration
- **Zodiac Year**: Current Chinese zodiac animal with emoji
- **Five Elements**: Traditional Chinese element for the year
- **Month and Day**: Chinese calendar month and day information

### ⭐ Astronomical Events
- **Seasonal Events**: Equinoxes and solstices
- **Meteor Showers**: Major meteor shower dates throughout the year
- **Special Moon Events**: New moon and full moon notifications

### 🌅 Moon Times (Approximate)
- **Moonrise/Moonset**: Calculated rise and set times
- **Moon Sign**: Current astrological sign of the moon

## How to Access

### Via Menu
1. Open the browser application
2. Go to **Tools** → **🧩 Extensions** → **🌙 Lunar Calendar**
3. Or use the keyboard shortcut: **Ctrl+Shift+M**

### Features Available
- **Calendar Navigation**: Browse different months and years
- **Date Selection**: Click any date to see lunar information
- **Export Function**: Save lunar data to text file
- **Settings**: Customize display options and location

## User Interface

### Main Window
- **Left Panel**: Interactive calendar widget for date selection
- **Right Panel**: Detailed lunar and astronomical information
- **Navigation**: Previous/Next month buttons and "Today" button
- **Actions**: Export, Settings, and Close buttons

### Information Sections
1. **📅 Selected Date**: Basic date information
2. **🌙 Lunar Phase**: Current moon phase details
3. **🐉 Chinese Calendar**: Traditional calendar information
4. **⭐ Astronomical Events**: Special events for the selected date
5. **🌙 Moon Times**: Rise/set times and astrological sign

## Calculations and Accuracy

### Lunar Phase Calculation
- Uses astronomical algorithms based on known lunar cycles
- Calculates from a reference new moon date (January 6, 2000)
- Lunar cycle length: 29.53058867 days (synodic month)
- Provides accurate phase names and illumination percentages

### Chinese Calendar
- 12-year zodiac cycle starting from 1900 (Rat year)
- Five-element cycle integration
- Simplified month and day calculations

### Astronomical Events
- Seasonal events (equinoxes and solstices)
- Major meteor shower dates
- Moon phase event notifications

### Moon Times
- Simplified calculations based on lunar age
- Approximate rise/set times (varies by location)
- Astrological moon sign progression

## Export Functionality

The extension allows you to export lunar calendar data to a text file:

1. Click **📄 Export Calendar**
2. Choose save location and filename
3. Generated file includes:
   - Selected date information
   - Complete lunar phase data
   - Chinese calendar details
   - Astronomical events
   - Moon timing information

## Settings and Customization

Access settings via the **⚙️ Settings** button:

### Display Options
- Show/hide Chinese calendar information
- Show/hide astronomical events
- Show/hide moon rise/set times
- 24-hour vs 12-hour time format

### Location Settings
- Latitude and longitude input for accurate moon times
- Default coordinates can be customized

## Technical Implementation

### File Structure
```
lunar_calendar_tool.py          # Main extension file
test_lunar_calendar.py          # Test script
lunar_calendar_extension_guide.md # This documentation
```

### Integration Points
- Added to browser's Tools → Extensions menu
- Keyboard shortcut: Ctrl+Shift+M
- Follows browser's styling and theme system
- Integrated with browser's dialog management

### Dependencies
- PyQt5 for GUI components
- Python datetime and calendar modules
- Mathematical calculations for lunar phases

## Usage Examples

### Viewing Current Lunar Phase
1. Open the Lunar Calendar extension
2. The current date is automatically selected
3. View the lunar phase information in the right panel

### Planning by Moon Phases
1. Navigate to future months using arrow buttons
2. Click on specific dates to see lunar phases
3. Use this information for gardening, photography, or spiritual practices

### Checking Astronomical Events
1. Browse through different months
2. Look for special event notifications
3. Plan stargazing sessions around new moons
4. Prepare for meteor showers and seasonal events

### Exporting Lunar Data
1. Select your desired date
2. Click "Export Calendar"
3. Save the comprehensive lunar report
4. Use for offline reference or sharing

## Keyboard Shortcuts

- **Ctrl+Shift+M**: Open Lunar Calendar
- **Arrow Keys**: Navigate calendar (when calendar widget is focused)
- **Enter**: Select highlighted date
- **Escape**: Close dialog

## Troubleshooting

### Common Issues

**Extension not appearing in menu:**
- Ensure lunar_calendar_tool.py is in the same directory as browser_window.py
- Check that the import statement is correctly added to browser_window.py

**Calculation accuracy:**
- Moon times are approximate and vary by geographic location
- For precise astronomical data, consider using specialized astronomy software
- The extension provides general guidance rather than precise scientific calculations

**Performance:**
- The extension is lightweight and should not impact browser performance
- Calculations are performed on-demand when dates are selected

## Future Enhancements

Potential improvements for future versions:
- GPS location detection for accurate moon times
- Integration with online astronomical databases
- Additional calendar systems (Islamic, Hebrew, etc.)
- Moon phase notifications and reminders
- Tidal information based on lunar cycles
- Integration with weather data
- Customizable themes and layouts

## Support and Feedback

This extension is part of the browser's tool ecosystem. For issues or suggestions:
1. Test functionality using the included test script
2. Check console output for error messages
3. Verify all dependencies are properly installed
4. Ensure PyQt5 is correctly configured

## Version History

**v1.0** - Initial release
- Basic lunar phase calculations
- Chinese calendar integration
- Astronomical events
- Export functionality
- Settings dialog
- Calendar navigation

---

*The Lunar Calendar extension brings the wisdom of lunar cycles and astronomical events to your browsing experience. Whether you're planning activities by moon phases, learning about traditional calendars, or simply curious about celestial events, this tool provides comprehensive lunar information at your fingertips.*