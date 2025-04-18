import os
import logging
import json
from typing import Dict, Any, List, Optional, Union, Tuple

from sqlalchemy import create_engine, desc
from sqlalchemy.orm import sessionmaker, Session
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.exc import SQLAlchemyError

from db.db_schema import Base, Repository, User, PullRequest, PREvent, BranchEvent, PushEvent

logger = logging.getLogger(__name__)

class DatabaseManager:
    """Manages SQLite database operations for GitHub events"""
    
    def __init__(self, db_path: str = "github_events.db"):
        """Initialize the database manager with the path to the SQLite database"""
        self.db_path = db_path
        self.engine = None
        self.Session = None
        self._initialize_db()
    
    def _initialize_db(self) -> None:
        """Initialize the database connection and create tables if they don't exist"""
        try:
            # Create directory if it doesn't exist
            db_dir = os.path.dirname(self.db_path)
            if db_dir and not os.path.exists(db_dir):
                os.makedirs(db_dir)
            
            # Create SQLite database URL
            db_url = f"sqlite:///{self.db_path}"
            
            # Create engine and session
            self.engine = create_engine(db_url)
            self.Session = sessionmaker(bind=self.engine)
            
            # Create tables if they don't exist
            Base.metadata.create_all(self.engine)
            
            logger.info(f"Database initialized at {self.db_path}")
        except Exception as e:
            logger.error(f"Error initializing database: {e}")
            raise
    
    def get_session(self) -> Session:
        """Get a new database session"""
        if not self.Session:
            raise RuntimeError("Database session factory not initialized")
        return self.Session()
    
    def save_repository(self, repo_data: Dict[str, Any]) -> Repository:
        """Save repository information to the database"""
        with self.get_session() as session:
            try:
                # Check if repository already exists
                existing_repo = session.query(Repository).filter_by(github_id=repo_data['id']).first()
                if existing_repo:
                    # Update existing repository
                    for key, value in repo_data.items():
                        if hasattr(existing_repo, key) and key != 'id':
                            setattr(existing_repo, key, value)
                    repo = existing_repo
                else:
                    # Create new repository
                    repo = Repository(
                        github_id=repo_data['id'],
                        name=repo_data['name'],
                        full_name=repo_data['full_name'],
                        private=repo_data.get('private', False)
                    )
                    session.add(repo)
                
                session.commit()
                return repo
            except SQLAlchemyError as e:
                session.rollback()
                logger.error(f"Error saving repository: {e}")
                raise
    
    def save_user(self, user_data: Dict[str, Any]) -> User:
        """Save user information to the database"""
        with self.get_session() as session:
            try:
                # Check if user already exists
                existing_user = session.query(User).filter_by(github_id=user_data['id']).first()
                if existing_user:
                    # Update existing user
                    for key, value in user_data.items():
                        if hasattr(existing_user, key) and key != 'id':
                            setattr(existing_user, key, value)
                    user = existing_user
                else:
                    # Create new user
                    user = User(
                        github_id=user_data['id'],
                        login=user_data['login'],
                        type=user_data.get('type', 'User')
                    )
                    session.add(user)
                
                session.commit()
                return user
            except SQLAlchemyError as e:
                session.rollback()
                logger.error(f"Error saving user: {e}")
                raise
    
    def save_pull_request(self, pr_data: Dict[str, Any], repo_id: int, user_id: int) -> PullRequest:
        """Save pull request information to the database"""
        with self.get_session() as session:
            try:
                # Check if pull request already exists
                existing_pr = session.query(PullRequest).filter_by(github_id=pr_data['id']).first()
                if existing_pr:
                    # Update existing pull request
                    for key, value in pr_data.items():
                        if hasattr(existing_pr, key) and key not in ('id', 'repository_id', 'user_id'):
                            setattr(existing_pr, key, value)
                    pr = existing_pr
                else:
                    # Create new pull request
                    pr = PullRequest(
                        github_id=pr_data['id'],
                        number=pr_data['number'],
                        title=pr_data['title'],
                        body=pr_data.get('body'),
                        state=pr_data['state'],
                        created_at=pr_data.get('created_at'),
                        updated_at=pr_data.get('updated_at'),
                        merged=pr_data.get('merged', False),
                        merged_at=pr_data.get('merged_at'),
                        repository_id=repo_id,
                        user_id=user_id,
                        head_ref=pr_data.get('head', {}).get('ref'),
                        base_ref=pr_data.get('base', {}).get('ref'),
                        head_sha=pr_data.get('head', {}).get('sha'),
                        base_sha=pr_data.get('base', {}).get('sha')
                    )
                    session.add(pr)
                
                session.commit()
                return pr
            except SQLAlchemyError as e:
                session.rollback()
                logger.error(f"Error saving pull request: {e}")
                raise
    
    def save_pr_event(self, event_type: str, pr_id: int, payload: Dict[str, Any] = None) -> PREvent:
        """Save pull request event to the database"""
        with self.get_session() as session:
            try:
                # Create new PR event
                pr_event = PREvent(
                    event_type=event_type,
                    pull_request_id=pr_id,
                    payload=json.dumps(payload) if payload else None
                )
                session.add(pr_event)
                session.commit()
                return pr_event
            except SQLAlchemyError as e:
                session.rollback()
                logger.error(f"Error saving PR event: {e}")
                raise
    
    def save_branch_event(self, event_type: str, ref: str, repo_id: int, payload: Dict[str, Any] = None) -> BranchEvent:
        """Save branch event to the database"""
        with self.get_session() as session:
            try:
                # Create new branch event
                branch_event = BranchEvent(
                    event_type=event_type,
                    ref=ref,
                    repository_id=repo_id,
                    payload=json.dumps(payload) if payload else None
                )
                session.add(branch_event)
                session.commit()
                return branch_event
            except SQLAlchemyError as e:
                session.rollback()
                logger.error(f"Error saving branch event: {e}")
                raise
    
    def save_push_event(self, push_data: Dict[str, Any], repo_id: int, sender_id: int) -> PushEvent:
        """Save push event to the database"""
        with self.get_session() as session:
            try:
                # Create new push event
                push_event = PushEvent(
                    ref=push_data['ref'],
                    before=push_data['before'],
                    after=push_data['after'],
                    created=push_data.get('created', False),
                    deleted=push_data.get('deleted', False),
                    forced=push_data.get('forced', False),
                    repository_id=repo_id,
                    sender_id=sender_id,
                    commits=json.dumps(push_data.get('commits', [])),
                )
                session.add(push_event)
                session.commit()
                return push_event
            except SQLAlchemyError as e:
                session.rollback()
                logger.error(f"Error saving push event: {e}")
                raise
    
    def get_recent_pr_events(self, limit: int = 10) -> List[Dict[str, Any]]:
        """Get recent pull request events with related data"""
        with self.get_session() as session:
            try:
                events = session.query(PREvent).order_by(desc(PREvent.created_at)).limit(limit).all()
                
                result = []
                for event in events:
                    pr = event.pull_request
                    repo = pr.repository
                    user = pr.user
                    
                    event_data = {
                        'id': event.id,
                        'event_type': event.event_type,
                        'created_at': event.created_at.isoformat(),
                        'pull_request': {
                            'id': pr.id,
                            'number': pr.number,
                            'title': pr.title,
                            'state': pr.state,
                            'created_at': pr.created_at.isoformat() if pr.created_at else None,
                            'merged': pr.merged,
                            'head_ref': pr.head_ref,
                            'base_ref': pr.base_ref,
                        },
                        'repository': {
                            'id': repo.id,
                            'name': repo.name,
                            'full_name': repo.full_name,
                        },
                        'user': {
                            'id': user.id,
                            'login': user.login,
                        },
                        'payload': json.loads(event.payload) if event.payload else None,
                    }
                    result.append(event_data)
                
                return result
            except SQLAlchemyError as e:
                logger.error(f"Error retrieving PR events: {e}")
                raise
    
    def get_recent_branch_events(self, limit: int = 10) -> List[Dict[str, Any]]:
        """Get recent branch events"""
        with self.get_session() as session:
            try:
                events = session.query(BranchEvent).order_by(desc(BranchEvent.created_at)).limit(limit).all()
                
                result = []
                for event in events:
                    event_data = {
                        'id': event.id,
                        'event_type': event.event_type,
                        'ref': event.ref,
                        'created_at': event.created_at.isoformat(),
                        'repository_id': event.repository_id,
                        'payload': json.loads(event.payload) if event.payload else None,
                    }
                    result.append(event_data)
                
                return result
            except SQLAlchemyError as e:
                logger.error(f"Error retrieving branch events: {e}")
                raise
    
    def get_recent_push_events(self, limit: int = 10) -> List[Dict[str, Any]]:
        """Get recent push events"""
        with self.get_session() as session:
            try:
                events = session.query(PushEvent).order_by(desc(PushEvent.created_at)).limit(limit).all()
                
                result = []
                for event in events:
                    event_data = {
                        'id': event.id,
                        'ref': event.ref,
                        'before': event.before,
                        'after': event.after,
                        'created': event.created,
                        'deleted': event.deleted,
                        'forced': event.forced,
                        'created_at': event.created_at.isoformat(),
                        'repository_id': event.repository_id,
                        'sender_id': event.sender_id,
                        'commits': json.loads(event.commits) if event.commits else [],
                    }
                    result.append(event_data)
                
                return result
            except SQLAlchemyError as e:
                logger.error(f"Error retrieving push events: {e}")
                raise
