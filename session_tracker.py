"""
Session tracking functionality
"""
import os
import json
from datetime import datetime, date
from constants import *


class SessionTracker:
    """Tracks browser usage sessions"""
    
    def __init__(self, profile_manager):
        self.profile_manager = profile_manager
        self.session_file = "sessions.json"
        self.session_start = datetime.now()
        self.sessions_data = self.load_sessions()
        self.start_session()
    
    def get_session_file_path(self):
        """Get full path for sessions file"""
        return self.profile_manager.get_profile_path(self.session_file)
    
    def load_sessions(self):
        """Load session data from JSON file"""
        session_file = self.get_session_file_path()
        try:
            if os.path.exists(session_file):
                with open(session_file, 'r', encoding='utf-8') as f:
                    return json.load(f)
        except Exception as e:
            print(f"Error loading sessions: {e}")
        return {
            "total_time_seconds": 0,
            "sessions": [],
            "daily_stats": {}
        }
    
    def save_sessions(self):
        """Save session data to JSON file"""
        session_file = self.get_session_file_path()
        try:
            with open(session_file, 'w', encoding='utf-8') as f:
                json.dump(self.sessions_data, f, indent=2, ensure_ascii=False)
        except Exception as e:
            print(f"Error saving sessions: {e}")
    
    def start_session(self):
        """Start a new session"""
        self.session_start = datetime.now()
        today = str(date.today())
        
        # Initialize today's stats if not exists
        if today not in self.sessions_data["daily_stats"]:
            self.sessions_data["daily_stats"][today] = {
                "sessions_count": 0,
                "total_time_seconds": 0
            }
        
        # Increment session count
        self.sessions_data["daily_stats"][today]["sessions_count"] += 1
        self.save_sessions()
    
    def end_session(self):
        """End current session and save data"""
        session_duration = (datetime.now() - self.session_start).total_seconds()
        today = str(date.today())
        
        # Add session record
        session_record = {
            "start": self.session_start.isoformat(),
            "end": datetime.now().isoformat(),
            "duration_seconds": int(session_duration)
        }
        self.sessions_data["sessions"].append(session_record)
        
        # Update total time
        self.sessions_data["total_time_seconds"] += int(session_duration)
        
        # Update today's time
        if today in self.sessions_data["daily_stats"]:
            self.sessions_data["daily_stats"][today]["total_time_seconds"] += int(session_duration)
        
        # Keep only last 100 sessions
        if len(self.sessions_data["sessions"]) > 100:
            self.sessions_data["sessions"] = self.sessions_data["sessions"][-100:]
        
        self.save_sessions()
    
    def get_total_time_formatted(self):
        """Get total time spent formatted as HH:MM:SS"""
        total_seconds = self.sessions_data["total_time_seconds"]
        hours = total_seconds // 3600
        minutes = (total_seconds % 3600) // 60
        seconds = total_seconds % 60
        return f"{hours:02d}:{minutes:02d}:{seconds:02d}"
    
    def get_sessions_today(self):
        """Get number of sessions today"""
        today = str(date.today())
        if today in self.sessions_data["daily_stats"]:
            return self.sessions_data["daily_stats"][today]["sessions_count"]
        return 0
    
    def get_time_today_formatted(self):
        """Get time spent today formatted as HH:MM:SS"""
        today = str(date.today())
        if today in self.sessions_data["daily_stats"]:
            total_seconds = self.sessions_data["daily_stats"][today]["total_time_seconds"]
            hours = total_seconds // 3600
            minutes = (total_seconds % 3600) // 60
            seconds = total_seconds % 60
            return f"{hours:02d}:{minutes:02d}:{seconds:02d}"
        return "00:00:00"
