"""
UI helper functions for main window
"""
from PyQt5.QtWidgets import QAction, QInputDialog, QLineEdit, QMessageBox
from PyQt5.QtCore import QUrl
import styles


def update_history_menu(window):
    """Update the History menu with recent entries"""
    window.history_menu.clear()
    
    clear_action = QAction("Clear History", window)
    clear_action.triggered.connect(lambda: clear_history(window))
    window.history_menu.addAction(clear_action)
    
    history = window.history_manager.get_all()
    if history:
        window.history_menu.addSeparator()
        
        # Show history in reverse order (most recent first)
        for entry in reversed(history):
            title = entry.get("title", entry.get("url"))
            url = entry.get("url")
            
            # Truncate long titles
            if len(title) > 50:
                title = title[:47] + "..."
            
            action = QAction(title, window)
            action.setStatusTip(url)
            action.triggered.connect(lambda checked, u=url: navigate_to_url_helper(window, u))
            window.history_menu.addAction(action)
    else:
        empty_action = QAction("No history", window)
        empty_action.setEnabled(False)
        window.history_menu.addAction(empty_action)


def clear_history(window):
    """Clear all browsing history"""
    window.history_manager.clear()
    update_history_menu(window)


def update_bookmarks_menu(window):
    """Update the Bookmarks menu"""
    window.bookmarks_menu.clear()
    
    add_action = QAction("Add Bookmark...", window)
    add_action.setShortcut("Ctrl+D")
    add_action.triggered.connect(lambda: toggle_bookmark(window))
    window.bookmarks_menu.addAction(add_action)
    
    manage_action = QAction("Manage Bookmarks...", window)
    manage_action.triggered.connect(lambda: manage_bookmarks(window))
    window.bookmarks_menu.addAction(manage_action)
    
    bookmarks = window.bookmark_manager.get_all()
    if bookmarks:
        window.bookmarks_menu.addSeparator()
        
        for bookmark in bookmarks:
            title = bookmark.get("title", bookmark.get("url"))
            url = bookmark.get("url")
            
            # Truncate long titles
            if len(title) > 50:
                title = title[:47] + "..."
            
            action = QAction(title, window)
            action.setStatusTip(url)
            action.triggered.connect(lambda checked, u=url: navigate_to_url_helper(window, u))
            window.bookmarks_menu.addAction(action)
    else:
        empty_action = QAction("No bookmarks", window)
        empty_action.setEnabled(False)
        window.bookmarks_menu.addAction(empty_action)


def update_bookmark_button(window):
    """Update bookmark button appearance based on current page"""
    browser = window.get_current_browser()
    if browser:
        url = browser.url().toString()
        is_bookmarked = window.bookmark_manager.is_bookmarked(url)
        
        if is_bookmarked:
            window.bookmark_btn.setText("★")  # Filled star
            window.bookmark_btn.setStatusTip("Remove bookmark")
        else:
            window.bookmark_btn.setText("☆")  # Empty star
            window.bookmark_btn.setStatusTip("Add bookmark")
        
        # Apply modern styling
        window.bookmark_btn.setStyleSheet(styles.get_bookmark_button_style(is_bookmarked))


def toggle_bookmark(window):
    """Toggle bookmark for current page"""
    browser = window.get_current_browser()
    if browser:
        url = browser.url().toString()
        
        # Check if already bookmarked
        index = window.bookmark_manager.find_by_url(url)
        if index >= 0:
            # Remove bookmark
            window.bookmark_manager.remove(index)
            update_bookmarks_menu(window)
            update_bookmark_button(window)
            return
        
        # Add bookmark
        title = browser.page().title()
        new_title, ok = QInputDialog.getText(window, "Add Bookmark", 
                                              "Bookmark name:", 
                                              QLineEdit.Normal, 
                                              title)
        
        if ok and new_title:
            window.bookmark_manager.add(url, new_title)
            update_bookmarks_menu(window)
            update_bookmark_button(window)


def manage_bookmarks(window):
    """Open bookmark management dialog"""
    from bookmark_manager import BookmarkManagerDialog
    dialog = BookmarkManagerDialog(window.bookmark_manager.get_all(), window)
    if dialog.exec_() == 2:  # QDialog.Accepted
        window.bookmark_manager.bookmarks = dialog.get_bookmarks()
        window.bookmark_manager.save()
        update_bookmarks_menu(window)


def update_profile_menu(window):
    """Update the Profile menu"""
    window.profile_menu.clear()
    
    # Current profile label
    current_label = QAction(f"Current: {window.profile_manager.current_profile}", window)
    current_label.setEnabled(False)
    window.profile_menu.addAction(current_label)
    
    window.profile_menu.addSeparator()
    
    # New profile action
    new_profile_action = QAction("New Profile...", window)
    new_profile_action.triggered.connect(lambda: create_new_profile(window))
    window.profile_menu.addAction(new_profile_action)
    
    window.profile_menu.addSeparator()
    
    # List available profiles
    profiles = window.profile_manager.get_available_profiles()
    for profile in profiles:
        action = QAction(profile, window)
        if profile == window.profile_manager.current_profile:
            action.setEnabled(False)
        else:
            action.triggered.connect(lambda checked, p=profile: switch_profile(window, p))
        window.profile_menu.addAction(action)


def create_new_profile(window):
    """Create a new profile"""
    profile_name, ok = QInputDialog.getText(window, "New Profile", "Profile name:")
    
    if ok and profile_name:
        success, message = window.profile_manager.create_profile(profile_name)
        if not success:
            QMessageBox.warning(window, "Error", message)
            return
        
        switch_profile(window, profile_name)


def switch_profile(window, profile_name):
    """Switch to a different profile"""
    window.profile_manager.switch_profile(profile_name)
    
    # Reload data for new profile
    window.config_manager.load()
    window.history_manager.enabled = window.config_manager.get("history_enabled", False)
    window.history_manager.load()
    window.bookmark_manager.load()
    
    # Update UI
    window.history_toggle_btn.setChecked(window.history_manager.enabled)
    update_history_toggle_button(window)
    update_bookmarks_menu(window)
    update_history_menu(window)
    update_profile_menu(window)
    window.status_profile.setText(f"Profile: {window.profile_manager.current_profile}")
    
    QMessageBox.information(window, "Profile Switched", f"Switched to profile: {profile_name}")


def navigate_to_url_helper(window, url):
    """Helper to navigate to URL"""
    browser = window.get_current_browser()
    if browser:
        browser.setUrl(QUrl(url))


def update_history_toggle_button(window):
    """Update history toggle button appearance"""
    enabled = window.history_manager.enabled
    
    if enabled:
        window.history_toggle_btn.setText("History ON")
        window.history_toggle_btn.setStatusTip("Click to disable history tracking")
    else:
        window.history_toggle_btn.setText("History OFF")
        window.history_toggle_btn.setStatusTip("Click to enable history tracking")
    
    # Apply modern styling
    window.history_toggle_btn.setStyleSheet(styles.get_history_button_style(enabled))


def toggle_history(window):
    """Toggle history tracking on/off"""
    window.history_manager.enabled = window.history_toggle_btn.isChecked()
    window.config_manager.set("history_enabled", window.history_manager.enabled)
    update_history_toggle_button(window)
