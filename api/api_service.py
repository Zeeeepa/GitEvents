"""
API Service for GitEvents

This module provides the API endpoints for the GitEvents application.
"""

import os
import json
import logging
from typing import Dict, Any, Optional
from fastapi import FastAPI, HTTPException, Depends, Query
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Import database manager
from db.db_manager import DatabaseManager

# Setup logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Create FastAPI app
app = FastAPI(title="GitEvents API", description="API for GitEvents application")

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # In production, replace with specific origins
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Initialize database manager
db_type = os.getenv("DB_TYPE", "SQLite").lower()
if db_type == "sqlite":
    db_path = os.getenv("GITHUB_EVENTS_DB", "github_events.db")
    db_manager = DatabaseManager(db_path)
else:  # MySQL
    db_manager = DatabaseManager(
        db_name=os.getenv("DB_NAME", "github_events"),
        db_type="mysql",
        db_host=os.getenv("DB_HOST", "localhost"),
        db_port=int(os.getenv("DB_PORT", 3306)),
        db_user=os.getenv("DB_USER", "admin"),
        db_password=os.getenv("DB_PASSWORD", "password")
    )

# Models for API requests and responses
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

# Response models
class PREventResponse(BaseModel):
    id: int
    event_type: str
    created_at: str
    pull_request: Dict[str, Any]
    repository: Dict[str, Any]
    user: Dict[str, Any]
    payload: Optional[Dict[str, Any]] = None

class BranchEventResponse(BaseModel):
    id: int
    event_type: str
    ref: str
    created_at: str
    repository_id: int
    payload: Optional[Dict[str, Any]] = None

class PushEventResponse(BaseModel):
    id: int
    ref: str
    before: str
    after: str
    created: bool
    deleted: bool
    forced: bool
    created_at: str
    repository_id: int
    sender_id: int
    commits: List[Dict[str, Any]]

class Project(BaseModel):
    id: str
    name: str
    added_at: str

class Script(BaseModel):
    id: str
    name: str
    project_id: str
    script_path: str
    enabled: bool
    added_at: str

class SettingsResponse(BaseModel):
    notifications: Dict[str, Any]
    auto_pr: Dict[str, Any]
    post_merge_scripts: Dict[str, Any]
    projects: List[Dict[str, Any]]
    scripts: List[Dict[str, Any]]

class DatabaseConfig(BaseModel):
    type: str
    path: Optional[str] = None
    host: Optional[str] = None
    port: Optional[str] = None
    name: Optional[str] = None
    user: Optional[str] = None
    password: Optional[str] = None
    create_new: Optional[bool] = False

# Endpoints
@app.get("/api/events/pr", response_model=List[PREventResponse])
async def get_pr_events(limit: int = Query(10, ge=1, le=100)):
    """Get recent pull request events"""
    try:
        events = db_manager.get_recent_pr_events(limit)
        return events
    except Exception as e:
        logger.error(f"Error retrieving PR events: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/events/branch", response_model=List[BranchEventResponse])
async def get_branch_events(limit: int = Query(10, ge=1, le=100)):
    """Get recent branch events"""
    try:
        events = db_manager.get_recent_branch_events(limit)
        return events
    except Exception as e:
        logger.error(f"Error retrieving branch events: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/events/push", response_model=List[PushEventResponse])
async def get_push_events(limit: int = Query(10, ge=1, le=100)):
    """Get recent push events"""
    try:
        events = db_manager.get_recent_push_events(limit)
        return events
    except Exception as e:
        logger.error(f"Error retrieving push events: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/events/all")
async def get_all_events(limit: int = Query(30, ge=1, le=100)):
    """Get all recent events (PR, branch, push) combined"""
    try:
        pr_events = db_manager.get_recent_pr_events(limit)
        branch_events = db_manager.get_recent_branch_events(limit)
        push_events = db_manager.get_recent_push_events(limit)
        
        # Combine all events with a type identifier
        combined_events = []
        
        for event in pr_events:
            event['event_category'] = 'pull_request'
            combined_events.append(event)
            
        for event in branch_events:
            event['event_category'] = 'branch'
            combined_events.append(event)
            
        for event in push_events:
            event['event_category'] = 'push'
            combined_events.append(event)
        
        # Sort by created_at in descending order
        combined_events.sort(key=lambda x: x['created_at'], reverse=True)
        
        # Limit the total number of events
        return combined_events[:limit]
    except Exception as e:
        logger.error(f"Error retrieving all events: {e}")
        raise HTTPException(status_code=500, detail=str(e))

# Additional endpoints for specific queries
@app.get("/api/repos/{repo_id}/prs")
async def get_repo_prs(repo_id: int, limit: int = Query(10, ge=1, le=100)):
    """Get pull requests for a specific repository"""
    try:
        with db_manager.get_session() as session:
            from db.db_schema import PullRequest, Repository, User
            
            query = (
                session.query(PullRequest)
                .filter(PullRequest.repository_id == repo_id)
                .order_by(PullRequest.updated_at.desc())
                .limit(limit)
            )
            
            prs = query.all()
            
            # Convert to dictionary format
            result = []
            for pr in prs:
                pr_dict = {
                    'id': pr.id,
                    'github_id': pr.github_id,
                    'number': pr.number,
                    'title': pr.title,
                    'state': pr.state,
                    'created_at': pr.created_at.isoformat() if pr.created_at else None,
                    'updated_at': pr.updated_at.isoformat() if pr.updated_at else None,
                    'merged': pr.merged,
                    'merged_at': pr.merged_at.isoformat() if pr.merged_at else None,
                    'head_ref': pr.head_ref,
                    'base_ref': pr.base_ref,
                }
                result.append(pr_dict)
            
            return result
    except Exception as e:
        logger.error(f"Error retrieving repository PRs: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/prs/{pr_id}/events")
async def get_pr_history(pr_id: int, limit: int = Query(100, ge=1, le=500)):
    """Get event history for a specific pull request"""
    try:
        with db_manager.get_session() as session:
            from db.db_schema import PREvent
            
            query = (
                session.query(PREvent)
                .filter(PREvent.pull_request_id == pr_id)
                .order_by(PREvent.created_at)
                .limit(limit)
            )
            
            events = query.all()
            
            # Convert to dictionary format
            result = []
            for event in events:
                event_dict = {
                    'id': event.id,
                    'event_type': event.event_type,
                    'created_at': event.created_at.isoformat() if event.created_at else None,
                    'payload': event.payload,
                }
                result.append(event_dict)
            
            return result
    except Exception as e:
        logger.error(f"Error retrieving PR history: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/repos")
async def get_repositories():
    """Get all repositories"""
    try:
        with db_manager.get_session() as session:
            from db.db_schema import Repository
            
            repos = session.query(Repository).all()
            
            # Convert to dictionary format
            result = []
            for repo in repos:
                repo_dict = {
                    'id': repo.id,
                    'github_id': repo.github_id,
                    'name': repo.name,
                    'full_name': repo.full_name,
                    'private': repo.private,
                }
                result.append(repo_dict)
            
            return result
    except Exception as e:
        logger.error(f"Error retrieving repositories: {e}")
        raise HTTPException(status_code=500, detail=str(e))

# Database management endpoints
@app.get("/api/database/info")
async def get_database_info():
    """Get information about the current database configuration"""
    try:
        info = db_manager.get_db_info()
        return info
    except Exception as e:
        logger.error(f"Error retrieving database info: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/api/database/test-connection")
async def test_database_connection(db_config: DatabaseConfig):
    """Test a database connection with the provided configuration"""
    try:
        result = db_manager.test_connection(db_config.dict(exclude_none=True))
        return result
    except Exception as e:
        logger.error(f"Error testing database connection: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/api/database/update-config")
async def update_database_config(db_config: DatabaseConfig):
    """Update the database configuration"""
    try:
        result = db_manager.update_db_config(db_config.dict(exclude_none=True))
        if result["success"]:
            return result
        else:
            raise HTTPException(status_code=400, detail=result["message"])
    except Exception as e:
        logger.error(f"Error updating database configuration: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/api/database/create-sqlite")
async def create_sqlite_database(db_path: str = Query(..., description="Path to the new SQLite database")):
    """Create a new SQLite database"""
    try:
        result = db_manager.create_sqlite_db(db_path)
        if result["success"]:
            return result
        else:
            raise HTTPException(status_code=400, detail=result["message"])
    except Exception as e:
        logger.error(f"Error creating SQLite database: {e}")
        raise HTTPException(status_code=500, detail=str(e))

# Project and script management endpoints
@app.get("/api/projects")
async def get_projects():
    """Get all projects"""
    try:
        projects = auto_pr_manager.get_projects()
        return projects
    except Exception as e:
        logger.error(f"Error retrieving projects: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/api/projects")
async def add_project(project: Project):
    """Add a new project"""
    try:
        success = auto_pr_manager.add_project(project.name, project.id)
        if success:
            return {"success": True, "message": f"Project {project.name} added successfully"}
        else:
            raise HTTPException(status_code=400, detail=f"Failed to add project {project.name}")
    except Exception as e:
        logger.error(f"Error adding project: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/scripts")
async def get_scripts():
    """Get all scripts"""
    try:
        scripts = auto_pr_manager.get_post_merge_scripts()
        return scripts
    except Exception as e:
        logger.error(f"Error retrieving scripts: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/api/scripts")
async def add_script(script: Script):
    """Add a new script"""
    try:
        success = auto_pr_manager.add_post_merge_script(
            script.name, 
            script.script_path, 
            repo_patterns=[]
        )
        if success:
            return {"success": True, "message": f"Script {script.name} added successfully"}
        else:
            raise HTTPException(status_code=400, detail=f"Failed to add script {script.name}")
    except Exception as e:
        logger.error(f"Error adding script: {e}")
        raise HTTPException(status_code=500, detail=str(e))

# Settings endpoints
@app.get("/api/settings")
async def get_settings():
    """Get application settings"""
    try:
        from api.settings_service import settings_service
        settings = settings_service.get_settings()
        
        # Mask sensitive information
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
    """Update application settings"""
    try:
        from api.settings_service import settings_service
        
        # Convert model to dict, excluding None values
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
