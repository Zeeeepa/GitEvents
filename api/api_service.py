"""
API Service for GitEvents

This module provides the API endpoints for the GitEvents application.
"""

import os
import json
import logging
from typing import Dict, Any, Optional, List
from fastapi import FastAPI, HTTPException, Depends, Query
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from dotenv import load_dotenv

load_dotenv()

from db.db_manager import DatabaseManager

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = FastAPI(title="GitEvents API", description="API for GitEvents application")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

db_type = os.getenv("DB_TYPE", "SQLite").lower()
if db_type == "sqlite":
    db_path = os.getenv("GITHUB_EVENTS_DB", "github_events.db")
    db_manager = DatabaseManager(db_path)
else:
    db_manager = DatabaseManager(
        db_name=os.getenv("DB_NAME", "github_events"),
        db_type="mysql",
        db_host=os.getenv("DB_HOST", "localhost"),
        db_port=int(os.getenv("DB_PORT", 3306)),
        db_user=os.getenv("DB_USER", "admin"),
        db_password=os.getenv("DB_PASSWORD", "password")
    )

class SettingsUpdate(BaseModel):
    github_token: Optional[str] = None
    enable_ngrok: Optional[bool] = None
    ngrok_auth_token: Optional[str] = None
    db_type: Optional[str] = None
    db_host: Optional[str] = None
    db_port: Optional[int] = None
    db_name: Optional[str] = None
    db_user: Optional[str] = None
    db_password: Optional[str] = None

class DatabaseConfig(BaseModel):
    type: str
    path: Optional[str] = None
    host: Optional[str] = None
    port: Optional[str] = None
    name: Optional[str] = None
    user: Optional[str] = None
    password: Optional[str] = None
    create_new: Optional[bool] = False

@app.get("/api/database/info")
async def get_database_info():
    try:
        db_info = db_manager.get_db_info()
        return db_info
    except Exception as e:
        logger.error(f"Error getting database info: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to get database info: {str(e)}")

@app.post("/api/database/test-connection")
async def test_database_connection(config: DatabaseConfig):
    try:
        config_dict = config.dict()
        result = db_manager.test_connection(config_dict)
        return result
    except Exception as e:
        logger.error(f"Error testing database connection: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to test database connection: {str(e)}")

@app.post("/api/database/update-config")
async def update_database_config(config: DatabaseConfig):
    try:
        config_dict = config.dict()
        result = db_manager.update_db_config(config_dict)
        
        from api.settings_service import settings_service
        
        settings_update = {
            "db_type": config.type
        }
        
        if config.type.lower() == "sqlite":
            settings_update["github_events_db"] = config.path
        else:
            settings_update["db_host"] = config.host
            settings_update["db_port"] = config.port
            settings_update["db_name"] = config.name
            settings_update["db_user"] = config.user
            if config.password:
                settings_update["db_password"] = config.password
        
        settings_service.update_settings(settings_update)
        
        return result
    except Exception as e:
        logger.error(f"Error updating database config: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to update database config: {str(e)}")

@app.post("/api/database/create-sqlite")
async def create_sqlite_database(db_path: str = Query(...)):
    try:
        db_dir = os.path.dirname(db_path)
        if db_dir and not os.path.exists(db_dir):
            os.makedirs(db_dir)
        
        if os.path.exists(db_path):
            os.remove(db_path)
        
        new_db_manager = DatabaseManager(db_path)
        result = new_db_manager.initialize_database()
        
        from api.settings_service import settings_service
        settings_service.update_settings({
            "db_type": "SQLite",
            "github_events_db": db_path
        })
        
        return result
    except Exception as e:
        logger.error(f"Error creating SQLite database: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to create SQLite database: {str(e)}")

@app.get("/api/settings")
async def get_settings():
    try:
        from api.settings_service import settings_service
        settings = settings_service.get_settings()
        
        if "github_token" in settings and settings["github_token"]:
            settings["github_token"] = "••••" + settings["github_token"][-4:]
        
        if "ngrok_auth_token" in settings and settings["ngrok_auth_token"]:
            settings["ngrok_auth_token"] = "••••" + settings["ngrok_auth_token"][-4:]
        
        if "db_password" in settings and settings["db_password"]:
            settings["db_password"] = "••••••"
        
        return settings
    except Exception as e:
        logger.error(f"Error getting settings: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to get settings: {str(e)}")

@app.post("/api/settings")
async def update_settings(settings: SettingsUpdate):
    try:
        from api.settings_service import settings_service
        
        settings_dict = {k: v for k, v in settings.dict().items() if v is not None}
        
        result = settings_service.update_settings(settings_dict)
        
        if not result["success"]:
            raise HTTPException(status_code=400, detail=result["message"])
        
        return result
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error updating settings: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to update settings: {str(e)}")

if __name__ == "__main__":
    import uvicorn
    port = int(os.getenv("API_PORT", 8001))
    uvicorn.run(app, host="0.0.0.0", port=port)

