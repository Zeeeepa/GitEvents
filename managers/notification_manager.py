import logging
import os
import subprocess
import platform
import webbrowser
from typing import Dict, Any, Optional

logger = logging.getLogger(__name__)

class NotificationManager:
    """Handles system notifications for GitHub events"""
    
    def __init__(self):
        """Initialize notification manager"""
        self.enabled = self._check_notification_support()
        self.notification_settings = {
            "pull_request:opened": True,
            "pull_request:closed": True,
            "pull_request:merged": True,
            "branch:created": False,
            "branch:deleted": False,
            "push": False
        }
    
    def _check_notification_support(self) -> bool:
        """Check if notifications are supported on this system"""
        system = platform.system()
        if system == "Windows":
            try:
                # Import Windows-specific libraries
                import win10toast
                return True
            except ImportError:
                logger.warning("win10toast not installed. Windows notifications disabled.")
                return False
        elif system == "Darwin":  # macOS
            return True
        elif system == "Linux":
            # Check for libnotify
            try:
                subprocess.run(["notify-send", "--version"], check=True, capture_output=True)
                return True
            except (subprocess.CalledProcessError, FileNotFoundError):
                logger.warning("notify-send not found. Linux notifications disabled.")
                return False
        return False
    
    def update_settings(self, settings: Dict[str, bool]) -> None:
        """Update notification settings"""
        for key, value in settings.items():
            if key in self.notification_settings:
                self.notification_settings[key] = value
    
    def send_notification(self, title: str, message: str, event_type: str, 
                         url: Optional[str] = None, repo_name: Optional[str] = None) -> bool:
        """Send system notification based on event type"""
        if not self.enabled:
            return False
            
        # Check if notifications for this event type are enabled
        if event_type in self.notification_settings and not self.notification_settings[event_type]:
            return False
            
        system = platform.system()
        success = False
        
        try:
            if system == "Windows":
                success = self._send_windows_notification(title, message, url)
            elif system == "Darwin":  # macOS
                success = self._send_mac_notification(title, message, url)
            elif system == "Linux":
                success = self._send_linux_notification(title, message, url)
            
            if success:
                logger.info(f"Notification sent: {title}")
            return success
        except Exception as e:
            logger.error(f"Error sending notification: {e}")
            return False
    
    def _send_windows_notification(self, title: str, message: str, url: Optional[str] = None) -> bool:
        """Send Windows toast notification"""
        try:
            from win10toast import ToastNotifier
            
            toaster = ToastNotifier()
            
            # If URL provided, set up callback to open browser
            if url:
                # Define a callback function that will be executed on click
                def open_url():
                    webbrowser.open(url)
                
                # Show notification with callback
                toaster.show_toast(
                    title,
                    message,
                    icon_path=None,
                    duration=5,
                    threaded=True,
                    callback_on_click=open_url
                )
            else:
                # Show notification without callback
                toaster.show_toast(
                    title,
                    message,
                    icon_path=None,
                    duration=5,
                    threaded=True
                )
            
            return True
        except Exception as e:
            logger.error(f"Error sending Windows notification: {e}")
            return False
    
    def _send_mac_notification(self, title: str, message: str, url: Optional[str] = None) -> bool:
        """Send macOS notification"""
        try:
            # For macOS, use osascript
            script = f'display notification "{message}" with title "{title}"'
            subprocess.run(["osascript", "-e", script], check=True)
            return True
        except Exception as e:
            logger.error(f"Error sending macOS notification: {e}")
            return False
    
    def _send_linux_notification(self, title: str, message: str, url: Optional[str] = None) -> bool:
        """Send Linux notification"""
        try:
            subprocess.run(["notify-send", title, message], check=True)
            return True
        except Exception as e:
            logger.error(f"Error sending Linux notification: {e}")
            return False
    
    def get_status(self) -> Dict[str, Any]:
        """Get notification manager status"""
        return {
            "enabled": self.enabled,
            "platform": platform.system(),
            "settings": self.notification_settings
        }