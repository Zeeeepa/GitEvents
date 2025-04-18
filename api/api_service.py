from fastapi import FastAPI, Depends, HTTPException, Query
from fastapi.middleware.cors import CORSMiddleware
from typing import Dict, List, Optional, Any
import os
import logging
from pydantic import BaseModel

from db.db_manager import DatabaseManager
from managers.auto_branch_pr_manager import AutoBranchPRManager

# Configure logging
logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(name)s - %(levelname)s - %(message)s")
logger = logging.getLogger(__name__)

# Initialize database manager
db_path = os.getenv("GITHUB_EVENTS_DB", "github_events.db")
db_manager = DatabaseManager(db_path)

# Initialize auto branch PR manager
auto_pr_manager = AutoBranchPRManager()

# Initialize FastAPI app
app = FastAPI(title="GitHub Events API", description="API for GitHub events stored in the database")

# Add CORS middleware to allow requests from React app
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # For development; restrict in production
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

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
@app.get("/api/settings/status", response_model=SettingsResponse)
async def get_system_status():
    """Get the current system status and settings"""
    try:
        # Get settings from auto_pr_manager
        auto_pr_settings = auto_pr_manager.config.get("auto_pr_settings", {})
        post_merge_settings = auto_pr_manager.config.get("post_merge_scripts", {})
        
        # Prepare response
        settings = {
            "notifications": {"enabled": True},
            "auto_pr": {
                "enabled": auto_pr_manager.config.get("auto_pr_enabled", False),
                "running": auto_pr_manager.running,
                "add_comment": auto_pr_settings.get("add_comment", False),
                "comment_text": auto_pr_settings.get("comment_text", "")
            },
            "post_merge_scripts": {
                "enabled": post_merge_settings.get("enabled", False),
                "selected_project": post_merge_settings.get("selected_project", ""),
                "selected_script": post_merge_settings.get("selected_script", "")
            },
            "projects": auto_pr_manager.get_projects(),
            "scripts": auto_pr_manager.get_post_merge_scripts()
        }
        
        return settings
    except Exception as e:
        logger.error(f"Error retrieving system status: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/api/settings/update")
async def update_system_settings(settings: Dict[str, Any]):
    """Update system settings"""
    try:
        # Update auto_pr_manager settings
        new_config = {}
        
        if "auto_pr" in settings:
            auto_pr = settings["auto_pr"]
            new_config["auto_pr_enabled"] = auto_pr.get("enabled", False)
            
            if "add_comment" in auto_pr or "comment_text" in auto_pr:
                new_config["auto_pr_settings"] = {}
                if "add_comment" in auto_pr:
                    new_config["auto_pr_settings"]["add_comment"] = auto_pr["add_comment"]
                if "comment_text" in auto_pr:
                    new_config["auto_pr_settings"]["comment_text"] = auto_pr["comment_text"]
        
        if "post_merge_scripts" in settings:
            post_merge = settings["post_merge_scripts"]
            new_config["post_merge_scripts"] = {
                "enabled": post_merge.get("enabled", False)
            }
            
            if "selected_project" in post_merge:
                new_config["post_merge_scripts"]["selected_project"] = post_merge["selected_project"]
            
            if "selected_script" in post_merge:
                new_config["post_merge_scripts"]["selected_script"] = post_merge["selected_script"]
        
        # Update the configuration
        success = auto_pr_manager.update_config(new_config)
        
        # Start or stop the branch monitor based on settings
        if "auto_pr" in settings and "enabled" in settings["auto_pr"]:
            if settings["auto_pr"]["enabled"] and not auto_pr_manager.running:
                # Initialize with a dummy token for now
                # In a real app, this would use a stored token
                auto_pr_manager.initialize("dummy_token")
                auto_pr_manager.start_branch_monitor()
            elif not settings["auto_pr"]["enabled"] and auto_pr_manager.running:
                auto_pr_manager.stop_branch_monitor()
        
        if success:
            return {"success": True, "message": "Settings updated successfully"}
        else:
            raise HTTPException(status_code=400, detail="Failed to update settings")
    except Exception as e:
        logger.error(f"Error updating system settings: {e}")
        raise HTTPException(status_code=500, detail=str(e))

if __name__ == "__main__":
    import uvicorn
    port = int(os.getenv("API_PORT", 8001))
    uvicorn.run(app, host="0.0.0.0", port=port)
