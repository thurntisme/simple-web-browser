"""
Water Reminder System for the browser.
Helps users stay hydrated with customizable reminders and tracking.
"""

from PyQt5.QtCore import *
from PyQt5.QtWidgets import *
from PyQt5.QtGui import *
import json
import os
from datetime import datetime, timedelta
import sys


class WaterReminderManager(QObject):
    """Manages water reminder notifications and tracking"""
    
    # Signals
    reminder_triggered = pyqtSignal()
    daily_goal_reached = pyqtSignal()
    
    def __init__(self, profile_manager, parent=None):
        super().__init__(parent)
        self.profile_manager = profile_manager
        self.parent_window = parent
        
        # Default settings
        self.settings = {
            "enabled": True,
            "interval_minutes": 30,  # Remind every 30 minutes
            "daily_goal_ml": 2000,   # 2 liters daily goal
            "glass_size_ml": 250,    # Standard glass size
            "work_hours_only": True, # Only remind during work hours
            "work_start": "09:00",   # Work start time
            "work_end": "17:00",     # Work end time
            "sound_enabled": True,   # Play notification sound
            "show_popup": True,      # Show popup notification
            "system_notifications": True,  # Show system notifications
            "countdown_enabled": True      # Show countdown in status bar
        }
        
        # Daily tracking
        self.daily_intake = 0  # ml consumed today
        self.last_drink_time = None
        self.drinks_today = []  # List of drink times and amounts
        
        # Timer for reminders
        self.reminder_timer = QTimer()
        self.reminder_timer.timeout.connect(self.check_reminder)
        
        # Countdown timer (updates every minute)
        self.countdown_timer = QTimer()
        self.countdown_timer.timeout.connect(self.update_countdown)
        self.countdown_timer.start(60000)  # Update every minute
        
        # Countdown tracking
        self.time_since_last_drink = 0  # minutes since last drink
        
        # Load settings and data
        self.load_settings()
        self.load_daily_data()
        
        # Start reminder system
        if self.settings["enabled"]:
            self.start_reminders()
        
        # Initialize countdown
        self.update_countdown()
    
    def get_data_file_path(self):
        """Get path to water reminder data file"""
        return self.profile_manager.get_profile_path("water_reminder.json")
    
    def load_settings(self):
        """Load water reminder settings"""
        try:
            data_file = self.get_data_file_path()
            if os.path.exists(data_file):
                with open(data_file, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                    if 'settings' in data:
                        self.settings.update(data['settings'])
        except Exception as e:
            print(f"Error loading water reminder settings: {e}")
    
    def save_settings(self):
        """Save water reminder settings"""
        try:
            data_file = self.get_data_file_path()
            
            # Load existing data
            data = {}
            if os.path.exists(data_file):
                with open(data_file, 'r', encoding='utf-8') as f:
                    data = json.load(f)
            
            # Update settings
            data['settings'] = self.settings
            
            # Save back to file
            os.makedirs(os.path.dirname(data_file), exist_ok=True)
            with open(data_file, 'w', encoding='utf-8') as f:
                json.dump(data, f, indent=2, ensure_ascii=False)
                
        except Exception as e:
            print(f"Error saving water reminder settings: {e}")
    
    def load_daily_data(self):
        """Load today's water intake data"""
        try:
            data_file = self.get_data_file_path()
            if os.path.exists(data_file):
                with open(data_file, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                    
                    today = datetime.now().strftime("%Y-%m-%d")
                    if 'daily_data' in data and today in data['daily_data']:
                        daily_data = data['daily_data'][today]
                        self.daily_intake = daily_data.get('total_ml', 0)
                        self.drinks_today = daily_data.get('drinks', [])
                        
                        # Parse last drink time
                        if self.drinks_today:
                            last_drink = self.drinks_today[-1]
                            self.last_drink_time = datetime.fromisoformat(last_drink['time'])
                            
        except Exception as e:
            print(f"Error loading daily water data: {e}")
    
    def save_daily_data(self):
        """Save today's water intake data"""
        try:
            data_file = self.get_data_file_path()
            
            # Load existing data
            data = {}
            if os.path.exists(data_file):
                with open(data_file, 'r', encoding='utf-8') as f:
                    data = json.load(f)
            
            # Ensure daily_data exists
            if 'daily_data' not in data:
                data['daily_data'] = {}
            
            # Save today's data
            today = datetime.now().strftime("%Y-%m-%d")
            data['daily_data'][today] = {
                'total_ml': self.daily_intake,
                'drinks': self.drinks_today
            }
            
            # Clean old data (keep only last 30 days)
            cutoff_date = (datetime.now() - timedelta(days=30)).strftime("%Y-%m-%d")
            data['daily_data'] = {
                date: intake for date, intake in data['daily_data'].items()
                if date >= cutoff_date
            }
            
            # Save back to file
            os.makedirs(os.path.dirname(data_file), exist_ok=True)
            with open(data_file, 'w', encoding='utf-8') as f:
                json.dump(data, f, indent=2, ensure_ascii=False)
                
        except Exception as e:
            print(f"Error saving daily water data: {e}")
    
    def start_reminders(self):
        """Start the reminder timer"""
        if self.settings["enabled"]:
            interval_ms = self.settings["interval_minutes"] * 60 * 1000
            self.reminder_timer.start(interval_ms)
    
    def stop_reminders(self):
        """Stop the reminder timer"""
        self.reminder_timer.stop()
    
    def check_reminder(self):
        """Check if it's time to show a reminder"""
        now = datetime.now()
        
        # Check if we're in work hours (if enabled)
        if self.settings["work_hours_only"]:
            work_start = datetime.strptime(self.settings["work_start"], "%H:%M").time()
            work_end = datetime.strptime(self.settings["work_end"], "%H:%M").time()
            current_time = now.time()
            
            if not (work_start <= current_time <= work_end):
                return  # Outside work hours
        
        # Check if enough time has passed since last drink
        if self.last_drink_time:
            time_since_drink = now - self.last_drink_time
            if time_since_drink.total_seconds() < (self.settings["interval_minutes"] * 60):
                return  # Too soon since last drink
        
        # Trigger reminder
        self.show_reminder()
    
    def show_reminder(self):
        """Show water reminder notification"""
        if self.parent_window:
            # Show popup if enabled
            if self.settings["show_popup"]:
                self.show_reminder_popup()
            
            # Play sound if enabled
            if self.settings["sound_enabled"]:
                self.play_reminder_sound()
            
            # Show system notification if enabled
            if self.settings["system_notifications"]:
                self.show_system_notification()
            
            # Update status bar
            self.update_status_message()
        
        # Emit signal
        self.reminder_triggered.emit()
    
    def show_system_notification(self):
        """Show system notification"""
        try:
            progress = self.get_daily_progress()
            
            # Create notification title and message
            title = "💧 Water Reminder"
            message = f"Time to drink water!\n"
            message += f"Progress: {progress['progress_percent']:.0f}% ({progress['total_ml']}ml/{progress['goal_ml']}ml)\n"
            
            if self.time_since_last_drink > 0:
                hours = self.time_since_last_drink // 60
                minutes = self.time_since_last_drink % 60
                if hours > 0:
                    message += f"Last drink: {hours}h {minutes}m ago"
                else:
                    message += f"Last drink: {minutes}m ago"
            
            # Show system notification based on platform
            if sys.platform == "win32":
                self.show_windows_notification(title, message)
            elif sys.platform == "darwin":  # macOS
                self.show_macos_notification(title, message)
            else:  # Linux and others
                self.show_linux_notification(title, message)
                
        except Exception as e:
            print(f"Error showing system notification: {e}")
    
    def show_windows_notification(self, title, message):
        """Show Windows system notification"""
        try:
            # Try plyer first (more reliable)
            from plyer import notification
            notification.notify(
                title=title,
                message=message,
                app_name="Water Reminder",
                timeout=10
            )
        except ImportError:
            try:
                # Fallback to win10toast
                import win10toast
                toaster = win10toast.ToastNotifier()
                toaster.show_toast(title, message, duration=10, threaded=True)
            except (ImportError, Exception):
                # Final fallback to basic Windows notification
                try:
                    import winsound
                    winsound.MessageBeep(winsound.MB_ICONASTERISK)
                    print(f"Water Reminder: {message}")
                except Exception:
                    print(f"Water Reminder: {message}")
    
    def show_macos_notification(self, title, message):
        """Show macOS system notification"""
        try:
            import subprocess
            script = f'display notification "{message}" with title "{title}"'
            subprocess.run(['osascript', '-e', script])
        except Exception:
            print(f"Water Reminder: {message}")
    
    def show_linux_notification(self, title, message):
        """Show Linux system notification"""
        try:
            import subprocess
            subprocess.run(['notify-send', title, message])
        except Exception:
            print(f"Water Reminder: {message}")
    
    def update_countdown(self):
        """Update countdown timer since last drink"""
        if self.last_drink_time:
            now = datetime.now()
            time_diff = now - self.last_drink_time
            self.time_since_last_drink = int(time_diff.total_seconds() / 60)  # minutes
        else:
            self.time_since_last_drink = 0
        
        # Update status bar if countdown is enabled
        if self.settings.get("countdown_enabled", True) and hasattr(self.parent_window, 'water_widget'):
            self.parent_window.water_widget.update_countdown_display()
    
    def get_countdown_text(self):
        """Get formatted countdown text"""
        if self.time_since_last_drink == 0:
            return "Just now"
        elif self.time_since_last_drink < 60:
            return f"{self.time_since_last_drink}m ago"
        else:
            hours = self.time_since_last_drink // 60
            minutes = self.time_since_last_drink % 60
            if minutes == 0:
                return f"{hours}h ago"
            else:
                return f"{hours}h {minutes}m ago"
    
    def show_reminder_popup(self):
        """Show reminder popup dialog"""
        dialog = WaterReminderDialog(self, self.parent_window)
        dialog.show()
    
    def play_reminder_sound(self):
        """Play reminder notification sound"""
        try:
            # Use system beep as fallback
            if sys.platform == "win32":
                import winsound
                winsound.MessageBeep(winsound.MB_ICONASTERISK)
            else:
                # For other platforms, use QApplication beep
                QApplication.beep()
        except Exception:
            # Fallback to Qt beep
            QApplication.beep()
    
    def update_status_message(self):
        """Update status bar with water reminder"""
        if hasattr(self.parent_window, 'status_info'):
            progress = (self.daily_intake / self.settings["daily_goal_ml"]) * 100
            message = f"💧 Time to drink water! Progress: {progress:.0f}% ({self.daily_intake}ml/{self.settings['daily_goal_ml']}ml)"
            self.parent_window.status_info.setText(message)
            
            # Clear message after 5 seconds
            QTimer.singleShot(5000, lambda: self.parent_window.status_info.setText(""))
    
    def add_water_intake(self, amount_ml):
        """Add water intake to daily tracking"""
        now = datetime.now()
        
        # Add to daily intake
        self.daily_intake += amount_ml
        self.last_drink_time = now
        
        # Reset countdown
        self.time_since_last_drink = 0
        
        # Add to drinks list
        drink_entry = {
            'time': now.isoformat(),
            'amount_ml': amount_ml
        }
        self.drinks_today.append(drink_entry)
        
        # Save data
        self.save_daily_data()
        
        # Check if daily goal reached
        if self.daily_intake >= self.settings["daily_goal_ml"]:
            self.daily_goal_reached.emit()
            self.show_goal_reached_message()
        
        # Update status
        self.update_progress_status()
        
        # Update countdown display
        self.update_countdown()
    
    def show_goal_reached_message(self):
        """Show congratulations message for reaching daily goal"""
        if hasattr(self.parent_window, 'status_info'):
            message = f"🎉 Congratulations! Daily water goal reached: {self.daily_intake}ml"
            self.parent_window.status_info.setText(message)
            QTimer.singleShot(7000, lambda: self.parent_window.status_info.setText(""))
    
    def update_progress_status(self):
        """Update status bar with current progress"""
        if hasattr(self.parent_window, 'status_info'):
            progress = (self.daily_intake / self.settings["daily_goal_ml"]) * 100
            message = f"💧 Water logged: {self.daily_intake}ml ({progress:.0f}% of daily goal)"
            self.parent_window.status_info.setText(message)
            QTimer.singleShot(3000, lambda: self.parent_window.status_info.setText(""))
    
    def get_daily_progress(self):
        """Get current daily progress information"""
        progress_percent = (self.daily_intake / self.settings["daily_goal_ml"]) * 100
        remaining_ml = max(0, self.settings["daily_goal_ml"] - self.daily_intake)
        
        return {
            'total_ml': self.daily_intake,
            'goal_ml': self.settings["daily_goal_ml"],
            'progress_percent': progress_percent,
            'remaining_ml': remaining_ml,
            'drinks_count': len(self.drinks_today),
            'last_drink_time': self.last_drink_time
        }
    
    def remove_water_record(self, record_index):
        """Remove a water record by index"""
        try:
            if 0 <= record_index < len(self.drinks_today):
                # Get the record to remove
                removed_record = self.drinks_today[record_index]
                amount_to_subtract = removed_record['amount_ml']
                
                # Remove from list
                self.drinks_today.pop(record_index)
                
                # Update daily intake
                self.daily_intake -= amount_to_subtract
                
                # Update last drink time
                if self.drinks_today:
                    last_drink = self.drinks_today[-1]
                    self.last_drink_time = datetime.fromisoformat(last_drink['time'])
                else:
                    self.last_drink_time = None
                
                # Save updated data
                self.save_daily_data()
                
                return True
        except Exception as e:
            print(f"Error removing water record: {e}")
        
        return False


class WaterReminderDialog(QDialog):
    """Water reminder popup dialog"""
    
    def __init__(self, water_manager, parent=None):
        super().__init__(parent)
        self.water_manager = water_manager
        self.setWindowTitle("💧 Water Reminder")
        self.setFixedSize(450, 700)  # Increased size to accommodate water records
        self.setWindowFlags(Qt.Dialog | Qt.WindowStaysOnTopHint)
        
        self.setup_ui()
        
        # Auto-close timer
        self.auto_close_timer = QTimer()
        self.auto_close_timer.timeout.connect(self.auto_close)
        self.auto_close_timer.start(30000)  # Auto-close after 30 seconds
    
    def setup_ui(self):
        """Setup the dialog UI"""
        layout = QVBoxLayout(self)
        
        # Header
        header_label = QLabel("💧 Time to Drink Water!")
        header_label.setAlignment(Qt.AlignCenter)
        header_label.setStyleSheet("font-size: 18px; font-weight: bold; color: #2196F3; padding: 10px;")
        layout.addWidget(header_label)
        
        # Progress info
        progress = self.water_manager.get_daily_progress()
        
        progress_text = f"""
        <div style="text-align: center; line-height: 1.6;">
            <p><strong>Today's Progress:</strong></p>
            <p>💧 {progress['total_ml']}ml / {progress['goal_ml']}ml ({progress['progress_percent']:.0f}%)</p>
            <p>🥤 {progress['drinks_count']} drinks logged</p>
            <p>📊 {progress['remaining_ml']}ml remaining</p>
        </div>
        """
        
        progress_label = QLabel(progress_text)
        progress_label.setAlignment(Qt.AlignCenter)
        progress_label.setStyleSheet("background-color: #f0f8ff; padding: 15px; border-radius: 5px; margin: 10px;")
        layout.addWidget(progress_label)
        
        # Today's water records
        drinks_count = len(self.water_manager.drinks_today)
        records_group = QGroupBox(f"📋 Today's Water Records ({drinks_count} drinks)")
        records_layout = QVBoxLayout(records_group)
        
        # Create scrollable area for records
        scroll_area = QScrollArea()
        scroll_area.setWidgetResizable(True)
        scroll_area.setMaximumHeight(120)
        scroll_area.setStyleSheet("""
            QScrollArea {
                border: 1px solid #ddd;
                border-radius: 5px;
                background-color: white;
            }
        """)
        
        # Records content widget
        records_widget = QWidget()
        records_content_layout = QVBoxLayout(records_widget)
        records_content_layout.setContentsMargins(10, 5, 10, 5)
        records_content_layout.setSpacing(3)
        
        # Get today's drinks
        drinks_today = self.water_manager.drinks_today
        
        if drinks_today:
            for i, drink in enumerate(reversed(drinks_today[-10:])):  # Show last 10 drinks, most recent first
                try:
                    from datetime import datetime
                    drink_time = datetime.fromisoformat(drink['time'])
                    time_str = drink_time.strftime('%H:%M')
                    amount = drink['amount_ml']
                    
                    # Calculate actual index in the original list (since we're showing reversed)
                    actual_index = len(drinks_today) - 1 - i
                    
                    # Create record item container
                    record_container = QWidget()
                    record_layout = QHBoxLayout(record_container)
                    record_layout.setContentsMargins(5, 2, 5, 2)
                    record_layout.setSpacing(5)
                    
                    # Record info label
                    record_label = QLabel(f"🕐 {time_str} - 💧 {amount}ml")
                    record_label.setStyleSheet("""
                        QLabel {
                            padding: 3px 5px;
                            background-color: transparent;
                            font-size: 12px;
                            color: #495057;
                        }
                    """)
                    record_layout.addWidget(record_label)
                    
                    # Delete button
                    delete_btn = QPushButton("❌")
                    delete_btn.setMaximumWidth(20)
                    delete_btn.setMaximumHeight(20)
                    delete_btn.setToolTip("Delete this record")
                    delete_btn.setStyleSheet("""
                        QPushButton {
                            background-color: #dc3545;
                            color: white;
                            border: none;
                            border-radius: 3px;
                            font-size: 10px;
                            padding: 2px;
                        }
                        QPushButton:hover {
                            background-color: #c82333;
                        }
                        QPushButton:pressed {
                            background-color: #bd2130;
                        }
                    """)
                    
                    # Connect delete button with confirmation
                    delete_btn.clicked.connect(lambda checked, idx=actual_index, amt=amount, time=time_str: 
                                             self.confirm_delete_record(idx, amt, time))
                    record_layout.addWidget(delete_btn)
                    
                    # Style the container
                    record_container.setStyleSheet("""
                        QWidget {
                            background-color: #f8f9fa;
                            border-radius: 3px;
                            margin: 1px;
                        }
                        QWidget:hover {
                            background-color: #e9ecef;
                        }
                    """)
                    
                    records_content_layout.addWidget(record_container)
                except Exception as e:
                    # Skip invalid records
                    continue
        else:
            # No records today
            no_records_label = QLabel("📝 No water intake recorded today")
            no_records_label.setAlignment(Qt.AlignCenter)
            no_records_label.setStyleSheet("""
                QLabel {
                    padding: 20px;
                    color: #6c757d;
                    font-style: italic;
                    font-size: 13px;
                }
            """)
            records_content_layout.addWidget(no_records_label)
        
        # Add stretch to push records to top
        records_content_layout.addStretch()
        
        # Set the widget to scroll area
        scroll_area.setWidget(records_widget)
        records_layout.addWidget(scroll_area)
        
        layout.addWidget(records_group)
        
        # Quick add buttons
        buttons_group = QGroupBox("Quick Add Water")
        buttons_group.setMinimumHeight(120)  # Reset to original height since dialog is larger
        buttons_layout = QGridLayout(buttons_group)
        buttons_layout.setSpacing(10)  # Add gap between buttons
        buttons_layout.setContentsMargins(15, 20, 15, 20)  # Add padding around buttons
        
        # Common drink sizes
        drink_sizes = [
            ("🥤 Small Glass", 200),
            ("🥛 Large Glass", 300),
            ("🍶 Bottle", 500),
            ("💧 Custom", 0)
        ]
        
        # Modern button styling with increased height
        button_style = """
            QPushButton {
                background-color: #4CAF50;
                color: white;
                border: none;
                border-radius: 8px;
                padding: 16px 20px;
                font-size: 14px;
                font-weight: 600;
                min-height: 30px;
                margin: 4px;
            }
            QPushButton:hover {
                background-color: #45a049;
                border: 2px solid #81C784;
            }
            QPushButton:pressed {
                background-color: #3d8b40;
                border: 2px solid #2E7D32;
            }
            QPushButton:focus {
                border: 2px solid #81C784;
            }
        """
        
        for i, (label, amount) in enumerate(drink_sizes):
            btn = QPushButton(label)
            btn.setStyleSheet(button_style)
            btn.clicked.connect(lambda checked, amt=amount: self.add_water(amt))
            buttons_layout.addWidget(btn, i // 2, i % 2)
        
        layout.addWidget(buttons_group)
        
        # Action buttons
        action_layout = QHBoxLayout()
        
        # Action button styling (different from water intake buttons)
        action_button_style = """
            QPushButton {
                background-color: #f8f9fa;
                color: #495057;
                border: 2px solid #dee2e6;
                border-radius: 6px;
                padding: 8px 12px;
                font-size: 13px;
                font-weight: 500;
                min-height: 16px;
                margin: 1px;
            }
            QPushButton:hover {
                background-color: #e9ecef;
                border-color: #adb5bd;
                color: #212529;
            }
            QPushButton:pressed {
                background-color: #dee2e6;
                border-color: #6c757d;
            }
        """
        
        # Snooze button with special styling
        snooze_style = """
            QPushButton {
                background-color: #fff3cd;
                color: #856404;
                border: 2px solid #ffeaa7;
                border-radius: 6px;
                padding: 8px 12px;
                font-size: 13px;
                font-weight: 500;
                min-height: 16px;
                margin: 1px;
            }
            QPushButton:hover {
                background-color: #ffeaa7;
                border-color: #fdcb6e;
                color: #6c5ce7;
            }
            QPushButton:pressed {
                background-color: #fdcb6e;
                border-color: #e17055;
            }
        """
        
        # Close button with special styling
        close_style = """
            QPushButton {
                background-color: #f8d7da;
                color: #721c24;
                border: 2px solid #f5c6cb;
                border-radius: 6px;
                padding: 8px 12px;
                font-size: 13px;
                font-weight: 500;
                min-height: 16px;
                margin: 1px;
            }
            QPushButton:hover {
                background-color: #f5c6cb;
                border-color: #f1b0b7;
                color: #491217;
            }
            QPushButton:pressed {
                background-color: #f1b0b7;
                border-color: #ea868f;
            }
        """
        
        snooze_btn = QPushButton("😴 Snooze 15min")
        snooze_btn.setStyleSheet(snooze_style)
        snooze_btn.clicked.connect(self.snooze_reminder)
        action_layout.addWidget(snooze_btn)
        
        settings_btn = QPushButton("⚙️ Settings")
        settings_btn.setStyleSheet(action_button_style)
        settings_btn.clicked.connect(self.open_settings)
        action_layout.addWidget(settings_btn)
        
        close_btn = QPushButton("❌ Close")
        close_btn.setStyleSheet(close_style)
        close_btn.clicked.connect(self.accept)
        action_layout.addWidget(close_btn)
        
        layout.addLayout(action_layout)
    
    def add_water(self, amount_ml):
        """Add water intake"""
        if amount_ml == 0:  # Custom amount
            amount, ok = QInputDialog.getInt(
                self, "Custom Amount", 
                "Enter water amount (ml):", 
                250, 50, 2000, 50
            )
            if ok:
                amount_ml = amount
            else:
                return
        
        self.water_manager.add_water_intake(amount_ml)
        
        # Show confirmation
        QMessageBox.information(
            self, "Water Logged", 
            f"✅ Added {amount_ml}ml to your daily intake!\n\n"
            f"Total today: {self.water_manager.daily_intake}ml"
        )
        
        self.accept()
    
    def confirm_delete_record(self, record_index, amount_ml, time_str):
        """Confirm deletion of a water record"""
        reply = QMessageBox.question(
            self, "Delete Water Record",
            f"Are you sure you want to delete this water record?\n\n"
            f"🕐 Time: {time_str}\n"
            f"💧 Amount: {amount_ml}ml\n\n"
            f"This will reduce your daily intake by {amount_ml}ml.",
            QMessageBox.Yes | QMessageBox.No,
            QMessageBox.No
        )
        
        if reply == QMessageBox.Yes:
            success = self.water_manager.remove_water_record(record_index)
            if success:
                # Show success message
                QMessageBox.information(
                    self, "Record Deleted",
                    f"✅ Water record deleted successfully!\n\n"
                    f"Removed {amount_ml}ml from daily intake.\n"
                    f"New total: {self.water_manager.daily_intake}ml"
                )
                
                # Refresh the dialog by closing and reopening
                self.accept()
                new_dialog = WaterReminderDialog(self.water_manager, self.parent())
                new_dialog.exec_()
            else:
                QMessageBox.warning(
                    self, "Delete Failed",
                    "❌ Failed to delete the water record.\n\nPlease try again."
                )
    
    def snooze_reminder(self):
        """Snooze reminder for 15 minutes"""
        self.water_manager.last_drink_time = datetime.now()
        
        if hasattr(self.water_manager.parent_window, 'status_info'):
            self.water_manager.parent_window.status_info.setText("😴 Water reminder snoozed for 15 minutes")
            QTimer.singleShot(3000, lambda: self.water_manager.parent_window.status_info.setText(""))
        
        self.accept()
    
    def open_settings(self):
        """Open water reminder settings"""
        settings_dialog = WaterReminderSettingsDialog(self.water_manager, self)
        settings_dialog.exec_()
    
    def auto_close(self):
        """Auto-close the dialog"""
        self.reject()


class WaterReminderSettingsDialog(QDialog):
    """Water reminder settings dialog"""
    
    def __init__(self, water_manager, parent=None):
        super().__init__(parent)
        self.water_manager = water_manager
        self.setWindowTitle("⚙️ Water Reminder Settings")
        self.setFixedSize(500, 600)
        
        self.setup_ui()
        self.load_current_settings()
    
    def setup_ui(self):
        """Setup the settings dialog UI"""
        layout = QVBoxLayout(self)
        
        # Header
        header_label = QLabel("💧 Water Reminder Configuration")
        header_label.setAlignment(Qt.AlignCenter)
        header_label.setStyleSheet("font-size: 16px; font-weight: bold; padding: 10px; background-color: #e3f2fd; border-radius: 5px;")
        layout.addWidget(header_label)
        
        # Scroll area for settings
        scroll = QScrollArea()
        scroll_widget = QWidget()
        scroll_layout = QVBoxLayout(scroll_widget)
        
        # Basic settings
        basic_group = QGroupBox("Basic Settings")
        basic_layout = QGridLayout(basic_group)
        
        # Enable/disable
        self.enabled_cb = QCheckBox("Enable water reminders")
        basic_layout.addWidget(self.enabled_cb, 0, 0, 1, 2)
        
        # Reminder interval
        basic_layout.addWidget(QLabel("Reminder interval:"), 1, 0)
        self.interval_spin = QSpinBox()
        self.interval_spin.setRange(5, 180)
        self.interval_spin.setSuffix(" minutes")
        basic_layout.addWidget(self.interval_spin, 1, 1)
        
        # Daily goal
        basic_layout.addWidget(QLabel("Daily water goal:"), 2, 0)
        self.goal_spin = QSpinBox()
        self.goal_spin.setRange(500, 5000)
        self.goal_spin.setSuffix(" ml")
        basic_layout.addWidget(self.goal_spin, 2, 1)
        
        # Glass size
        basic_layout.addWidget(QLabel("Default glass size:"), 3, 0)
        self.glass_spin = QSpinBox()
        self.glass_spin.setRange(100, 1000)
        self.glass_spin.setSuffix(" ml")
        basic_layout.addWidget(self.glass_spin, 3, 1)
        
        scroll_layout.addWidget(basic_group)
        
        # Work hours settings
        work_group = QGroupBox("Work Hours")
        work_layout = QGridLayout(work_group)
        
        self.work_hours_cb = QCheckBox("Only remind during work hours")
        work_layout.addWidget(self.work_hours_cb, 0, 0, 1, 2)
        
        work_layout.addWidget(QLabel("Work start time:"), 1, 0)
        self.work_start_time = QTimeEdit()
        work_layout.addWidget(self.work_start_time, 1, 1)
        
        work_layout.addWidget(QLabel("Work end time:"), 2, 0)
        self.work_end_time = QTimeEdit()
        work_layout.addWidget(self.work_end_time, 2, 1)
        
        scroll_layout.addWidget(work_group)
        
        # Notification settings
        notification_group = QGroupBox("Notifications")
        notification_layout = QGridLayout(notification_group)
        
        self.sound_cb = QCheckBox("Play notification sound")
        notification_layout.addWidget(self.sound_cb, 0, 0)
        
        self.popup_cb = QCheckBox("Show popup reminder")
        notification_layout.addWidget(self.popup_cb, 1, 0)
        
        self.system_notifications_cb = QCheckBox("Show system notifications")
        notification_layout.addWidget(self.system_notifications_cb, 0, 1)
        
        self.countdown_cb = QCheckBox("Show countdown in status bar")
        notification_layout.addWidget(self.countdown_cb, 1, 1)
        
        scroll_layout.addWidget(notification_group)
        
        # Statistics
        stats_group = QGroupBox("Today's Statistics")
        stats_layout = QVBoxLayout(stats_group)
        
        progress = self.water_manager.get_daily_progress()
        stats_text = f"""
        💧 Total intake: {progress['total_ml']}ml
        🎯 Daily goal: {progress['goal_ml']}ml
        📊 Progress: {progress['progress_percent']:.1f}%
        🥤 Drinks logged: {progress['drinks_count']}
        ⏰ Last drink: {progress['last_drink_time'].strftime('%H:%M') if progress['last_drink_time'] else 'None'}
        """
        
        stats_label = QLabel(stats_text)
        stats_label.setStyleSheet("background-color: #f5f5f5; padding: 10px; border-radius: 5px; font-family: monospace;")
        stats_layout.addWidget(stats_label)
        
        scroll_layout.addWidget(stats_group)
        
        scroll.setWidget(scroll_widget)
        layout.addWidget(scroll)
        
        # Buttons
        button_layout = QHBoxLayout()
        
        reset_btn = QPushButton("🔄 Reset Today")
        reset_btn.clicked.connect(self.reset_today)
        button_layout.addWidget(reset_btn)
        
        button_layout.addStretch()
        
        save_btn = QPushButton("💾 Save")
        save_btn.clicked.connect(self.save_settings)
        button_layout.addWidget(save_btn)
        
        cancel_btn = QPushButton("❌ Cancel")
        cancel_btn.clicked.connect(self.reject)
        button_layout.addWidget(cancel_btn)
        
        layout.addLayout(button_layout)
    
    def load_current_settings(self):
        """Load current settings into the UI"""
        settings = self.water_manager.settings
        
        self.enabled_cb.setChecked(settings["enabled"])
        self.interval_spin.setValue(settings["interval_minutes"])
        self.goal_spin.setValue(settings["daily_goal_ml"])
        self.glass_spin.setValue(settings["glass_size_ml"])
        self.work_hours_cb.setChecked(settings["work_hours_only"])
        
        # Parse time strings
        work_start = QTime.fromString(settings["work_start"], "HH:mm")
        work_end = QTime.fromString(settings["work_end"], "HH:mm")
        self.work_start_time.setTime(work_start)
        self.work_end_time.setTime(work_end)
        
        self.sound_cb.setChecked(settings["sound_enabled"])
        self.popup_cb.setChecked(settings["show_popup"])
        self.system_notifications_cb.setChecked(settings.get("system_notifications", True))
        self.countdown_cb.setChecked(settings.get("countdown_enabled", True))
    
    def save_settings(self):
        """Save settings and apply changes"""
        # Update settings
        self.water_manager.settings.update({
            "enabled": self.enabled_cb.isChecked(),
            "interval_minutes": self.interval_spin.value(),
            "daily_goal_ml": self.goal_spin.value(),
            "glass_size_ml": self.glass_spin.value(),
            "work_hours_only": self.work_hours_cb.isChecked(),
            "work_start": self.work_start_time.time().toString("HH:mm"),
            "work_end": self.work_end_time.time().toString("HH:mm"),
            "sound_enabled": self.sound_cb.isChecked(),
            "show_popup": self.popup_cb.isChecked(),
            "system_notifications": self.system_notifications_cb.isChecked(),
            "countdown_enabled": self.countdown_cb.isChecked()
        })
        
        # Save to file
        self.water_manager.save_settings()
        
        # Restart reminders with new settings
        self.water_manager.stop_reminders()
        if self.water_manager.settings["enabled"]:
            self.water_manager.start_reminders()
        
        # Show confirmation
        if hasattr(self.water_manager.parent_window, 'status_info'):
            self.water_manager.parent_window.status_info.setText("💧 Water reminder settings saved")
            QTimer.singleShot(2000, lambda: self.water_manager.parent_window.status_info.setText(""))
        
        self.accept()
    
    def reset_today(self):
        """Reset today's water intake data"""
        reply = QMessageBox.question(
            self, "Reset Today's Data",
            "Are you sure you want to reset today's water intake data?\n\nThis action cannot be undone.",
            QMessageBox.Yes | QMessageBox.No,
            QMessageBox.No
        )
        
        if reply == QMessageBox.Yes:
            self.water_manager.daily_intake = 0
            self.water_manager.drinks_today = []
            self.water_manager.last_drink_time = None
            self.water_manager.save_daily_data()
            
            QMessageBox.information(self, "Reset Complete", "Today's water intake data has been reset.")
            
            # Refresh the dialog
            self.reject()
            new_dialog = WaterReminderSettingsDialog(self.water_manager, self.parent())
            new_dialog.exec_()


class WaterReminderWidget(QWidget):
    """Compact water reminder widget for status bar"""
    
    def __init__(self, water_manager, parent=None):
        super().__init__(parent)
        self.water_manager = water_manager
        self.setup_ui()
        
        # Connect signals
        self.water_manager.reminder_triggered.connect(self.update_display)
        self.water_manager.daily_goal_reached.connect(self.update_display)
        
        # Update display initially
        self.update_display()
    
    def setup_ui(self):
        """Setup the widget UI"""
        layout = QHBoxLayout(self)
        layout.setContentsMargins(5, 0, 5, 0)
        layout.setSpacing(3)
        
        # Progress display (click to show details)
        self.progress_label = QLabel("0%")
        self.progress_label.setMinimumWidth(65)  # Increased from 46 to 65
        self.progress_label.setMaximumWidth(65)  # Increased from 46 to 65
        self.progress_label.setAlignment(Qt.AlignCenter)
        self.progress_label.setToolTip("Daily water intake progress - Click for details")
        self.progress_label.mousePressEvent = lambda event: self.show_details()
        self.progress_label.setStyleSheet("""
            QLabel {
                border: 1px solid #ccc;
                border-radius: 3px;
                padding: 2px;
                background-color: #f8f8f8;
            }
            QLabel:hover {
                background-color: #e8e8e8;
                border-color: #999;
            }
        """)
        layout.addWidget(self.progress_label)
    
    def update_display(self):
        """Update the widget display"""
        progress = self.water_manager.get_daily_progress()
        
        # Update progress percentage
        self.progress_label.setText(f"💧{progress['progress_percent']:.0f}%")
        
        # Update tooltip with countdown information
        tooltip = f"Water Progress: {progress['total_ml']}ml / {progress['goal_ml']}ml\n"
        tooltip += f"Drinks today: {progress['drinks_count']}\n"
        tooltip += f"Remaining: {progress['remaining_ml']}ml"
        
        if progress['last_drink_time']:
            tooltip += f"\nLast drink: {progress['last_drink_time'].strftime('%H:%M')}"
            # Add countdown information
            countdown_text = self.water_manager.get_countdown_text()
            tooltip += f"\nTime since last drink: {countdown_text}"
        
        tooltip += "\n\nClick for details and to log water intake"
        self.progress_label.setToolTip(tooltip)
        
        # Color coding based on progress and time since last drink
        color = self.get_status_color(progress)
        
        # Update label style with color
        self.progress_label.setStyleSheet(f"""
            QLabel {{
                color: {color};
                font-weight: bold;
                border: 1px solid #ccc;
                border-radius: 3px;
                padding: 2px;
                background-color: #f8f8f8;
            }}
            QLabel:hover {{
                background-color: #e8e8e8;
                border-color: #999;
            }}
        """)
    
    def get_status_color(self, progress):
        """Get status color based on progress and time since last drink"""
        # Check if it's been too long since last drink
        time_since_minutes = self.water_manager.time_since_last_drink
        reminder_interval = self.water_manager.settings["interval_minutes"]
        
        # If overdue for water, show warning colors
        if time_since_minutes >= reminder_interval:
            if time_since_minutes >= reminder_interval * 1.5:
                return "#F44336"  # Red - seriously overdue
            else:
                return "#FF9800"  # Orange - overdue
        
        # Otherwise use progress-based colors
        if progress['progress_percent'] >= 100:
            return "#4CAF50"  # Green - goal reached
        elif progress['progress_percent'] >= 75:
            return "#8BC34A"  # Light green - almost there
        elif progress['progress_percent'] >= 50:
            return "#FFC107"  # Yellow - halfway
        elif progress['progress_percent'] >= 25:
            return "#FF9800"  # Orange - need more
        else:
            return "#F44336"  # Red - way behind
    
    def update_countdown_display(self):
        """Update countdown display (called by manager)"""
        self.update_display()
    
    def show_details(self):
        """Show detailed water reminder dialog"""
        dialog = WaterReminderDialog(self.water_manager, self.parent())
        dialog.exec_()
        self.update_display()