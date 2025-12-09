"""
Profile management functionality
"""
import os
import json
from PyQt5.QtWidgets import QInputDialog, QMessageBox
from constants import *


class ProfileManager:
    """Manages browser profiles"""
    
    def __init__(self):
        self.current_profile = DEFAULT_PROFILE
        self.ensure_profiles_dir()
        self.current_profile = self.load_current_profile()
    
    def ensure_profiles_dir(self):
        """Ensure storage and profiles directory exists"""
        if not os.path.exists(STORAGE_DIR):
            os.makedirs(STORAGE_DIR)
            
        if not os.path.exists(PROFILES_DIR):
            os.makedirs(PROFILES_DIR)
        
        # Create default profile directory
        default_profile_dir = os.path.join(PROFILES_DIR, DEFAULT_PROFILE)
        if not os.path.exists(default_profile_dir):
            os.makedirs(default_profile_dir)
    
    def get_profile_path(self, filename):
        """Get full path for a file in current profile"""
        return os.path.join(PROFILES_DIR, self.current_profile, filename)
    
    def load_current_profile(self):
        """Load the current active profile name"""
        try:
            if os.path.exists(PROFILES_CONFIG_FILE):
                with open(PROFILES_CONFIG_FILE, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                    return data.get("current_profile", DEFAULT_PROFILE)
        except Exception as e:
            print(f"Error loading profile config: {e}")
        return DEFAULT_PROFILE
    
    def save_current_profile(self):
        """Save the current active profile name"""
        try:
            data = {"current_profile": self.current_profile}
            with open(PROFILES_CONFIG_FILE, 'w', encoding='utf-8') as f:
                json.dump(data, f, indent=2, ensure_ascii=False)
        except Exception as e:
            print(f"Error saving profile config: {e}")
    
    def get_available_profiles(self):
        """Get list of available profiles"""
        if not os.path.exists(PROFILES_DIR):
            return [DEFAULT_PROFILE]
        
        profiles = []
        for item in os.listdir(PROFILES_DIR):
            item_path = os.path.join(PROFILES_DIR, item)
            if os.path.isdir(item_path):
                profiles.append(item)
        
        if not profiles:
            profiles.append(DEFAULT_PROFILE)
        
        return sorted(profiles)
    
    def switch_profile(self, profile_name):
        """Switch to a different profile"""
        profile_dir = os.path.join(PROFILES_DIR, profile_name)
        if not os.path.exists(profile_dir):
            os.makedirs(profile_dir)
        
        self.current_profile = profile_name
        self.save_current_profile()
        return True
    
    def create_profile(self, profile_name):
        """Create a new profile"""
        # Validate profile name
        if not profile_name.replace("_", "").replace("-", "").isalnum():
            return False, "Profile name can only contain letters, numbers, hyphens, and underscores."
        
        profile_dir = os.path.join(PROFILES_DIR, profile_name)
        if os.path.exists(profile_dir):
            return False, f"Profile '{profile_name}' already exists."
        
        os.makedirs(profile_dir)
        return True, "Profile created successfully."
