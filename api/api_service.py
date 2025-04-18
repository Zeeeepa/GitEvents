from fastapi import FastAPI, Depends, HTTPException, Query
from fastapi.middleware.cors import CORSMiddleware
from typing import Dict, List, Optional, Any
import os
import logging
from pydantic import BaseModel

from db_manager import DatabaseManager

# Configure logging
logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(name)s - %(levelname)s - %(message)s")
logger = logging.getLogger(__name__)

# Initialize database manager
db_path = os.getenv("GITHUB_EVENTS_DB", "github_events.db")
db_manager = DatabaseManager(db_path)

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
            from db_schema import PullRequest, Repository, User
            
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
            from db_schema import PREvent
            
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
            from db_schema import Repository
            
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

if __name__ == "__main__":
    import uvicorn
    port = int(os.getenv("API_PORT", 8001))
    uvicorn.run(app, host="0.0.0.0", port=port)