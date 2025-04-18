"""
Settings Service for GitEvents

This module provides functionality to manage application settings,
including reading and updating the .env file.
"""

import os
import re
from pathlib import Path
from typing import Dict, Any, Optional
from dotenv import load_dotenv, set_key
import logging

logger = logging.getLogger(__name__)

class SettingsService:
    """Service to manage application settings"""
    
    def __init__(self):
        """Initialize the settings service"""
        self.env_file = Path(".env")
        load_dotenv(self.env_file)
    
    def get_settings(self) -> Dict[str, Any]:
        """Get current application settings"""
        try:
            # Reload environment variables
            load_dotenv(self.env_file, override=True)
            
            settings = {
                "github_token": os.getenv("GITHUB_TOKEN", ""),
                "github_events_db": os.getenv("GITHUB_EVENTS_DB", "github_events.db"),
                "api_port": int(os.getenv("API_PORT", 8001)),
                "webhook_port": int(os.getenv("WEBHOOK_PORT", 8002)),
                "enable_ngrok": os.getenv("ENABLE_NGROK", "true").lower() == "true",
                "ngrok_auth_token": os.getenv("NGROK_AUTH_TOKEN", ""),
                "open_browser": os.getenv("OPEN_BROWSER", "true").lower() == "true",
                "db_type": os.getenv("DB_TYPE", "SQLite"),
                "db_host": os.getenv("DB_HOST", "localhost"),
                "db_port": int(os.getenv("DB_PORT", 3306)),
                "db_name": os.getenv("DB_NAME", "github_events"),
                "db_user": os.getenv("DB_USER", "admin"),
                "db_password": os.getenv("DB_PASSWORD", "password")
            }
            
            return settings
        except Exception as e:
            logger.error(f"Error getting settings: {e}")
            return {}
    
    def update_settings(self, settings: Dict[str, Any]) -> Dict[str, Any]:
        """Update application settings in .env file"""
        try:
            # Validate settings
            if not self.env_file.exists():
                return {
                    "success": False,
                    "message": "Environment file not found. Run setup.py to create it."
                }
            
            # Update each setting in the .env file
            for key, value in settings.items():
                env_key = self._convert_to_env_key(key)
                if env_key:
                    # Convert boolean values to strings
                    if isinstance(value, bool):
                        value = str(value).lower()
                    
                    set_key(self.env_file, env_key, str(value))
            
            # Reload environment variables
            load_dotenv(self.env_file, override=True)
            
            return {
                "success": True,
                "message": "Settings updated successfully"
            }
        except Exception as e:
            logger.error(f"Error updating settings: {e}")
            return {
                "success": False,
                "message": f"Failed to update settings: {str(e)}"
            }
    
    def _convert_to_env_key(self, key: str) -> Optional[str]:
        """Convert a camelCase or snake_case key to UPPER_SNAKE_CASE for .env file"""
        if not key:
            return None
        
        # Convert camelCase to snake_case
        s1 = re.sub('(.)([A-Z][a-z]+)', r'\1_\2', key)
        snake_case = re.sub('([a-z0-9])([A-Z])', r'\1_\2', s1).lower()
        
        # Map to actual environment variable names
        key_mapping = {
            "github_token": "GITHUB_TOKEN",
            "github_events_db": "GITHUB_EVENTS_DB",
            "api_port": "API_PORT",
            "webhook_port": "WEBHOOK_PORT",
            "enable_ngrok": "ENABLE_NGROK",
            "ngrok_auth_token": "NGROK_AUTH_TOKEN",
            "open_browser": "OPEN_BROWSER",
            "db_type": "DB_TYPE",
            "db_host": "DB_HOST",
            "db_port": "DB_PORT",
            "db_name": "DB_NAME",
            "db_user": "DB_USER",
            "db_password": "DB_PASSWORD"
        }
        
        return key_mapping.get(snake_case, snake_case.upper())

# Create a singleton instance
settings_service = SettingsService()
