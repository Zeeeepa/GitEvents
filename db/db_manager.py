import os
import logging
import json
import sqlite3
from typing import Dict, Any, List, Optional, Union, Tuple

from sqlalchemy import create_engine, desc, inspect
from sqlalchemy.orm import sessionmaker, Session
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.exc import SQLAlchemyError

from db.db_schema import Base, Repository, User, PullRequest, PREvent, BranchEvent, PushEvent

logger = logging.getLogger(__name__)

class DatabaseManager:
    """Manages database operations for GitHub events"""
    
    def __init__(self, db_path: str = "github_events.db", db_type: str = "sqlite", db_host: str = None, db_port: int = None, db_name: str = None, db_user: str = None, db_password: str = None):
        """Initialize the database manager with the path to the SQLite database or MySQL credentials"""
        self.db_path = db_path
        self.db_type = db_type
        self.db_host = db_host
        self.db_port = db_port
        self.db_name = db_name
        self.db_user = db_user
        self.db_password = db_password
        self.engine = None
        self.Session = None
        self._initialize_db()
    
    def _initialize_db(self) -> None:
        """Initialize the database connection and create tables if they don't exist"""
        try:
            # Determine database type
            db_type = self.db_type.lower() if self.db_type else os.getenv("DB_TYPE", "sqlite").lower()
            
            if db_type == "mysql":
                # MySQL configuration
                db_host = self.db_host or os.getenv("DB_HOST", "localhost")
                db_port = self.db_port or os.getenv("DB_PORT", "3306")
                db_name = self.db_name or os.getenv("DB_NAME", "github_events")
                db_user = self.db_user or os.getenv("DB_USER", "root")
                db_password = self.db_password or os.getenv("DB_PASSWORD", "")
                
                # Create MySQL database URL
                db_url = f"mysql+pymysql://{db_user}:{db_password}@{db_host}:{db_port}/{db_name}"
                logger.info(f"Using MySQL database at {db_host}:{db_port}/{db_name}")
            else:
                # SQLite configuration (default)
                # Create directory if it doesn't exist
                db_dir = os.path.dirname(self.db_path)
                if db_dir and not os.path.exists(db_dir):
                    os.makedirs(db_dir)
                
                # Create SQLite database URL
                db_url = f"sqlite:///{self.db_path}"
                logger.info(f"Using SQLite database at {self.db_path}")
            
            # Create engine and session
            self.engine = create_engine(db_url)
            self.Session = sessionmaker(bind=self.engine)
            
            # Create tables if they don't exist
            Base.metadata.create_all(self.engine)
            
            logger.info("Database initialized successfully")
        except Exception as e:
            logger.error(f"Error initializing database: {e}")
            raise
    
    def initialize_database(self) -> Dict[str, Any]:
        """Initialize the database and create all tables"""
        try:
            # Create tables if they don't exist
            Base.metadata.create_all(self.engine)
            
            # Check if tables were created successfully
            inspector = inspect(self.engine)
            tables = inspector.get_table_names()
            
            # Create initial data if needed
            with self.get_session() as session:
                # Check if we need to create initial data
                repo_count = session.query(Repository).count()
                if repo_count == 0:
                    logger.info("Creating initial data...")
                    # You can add initial data here if needed
            
            return {
                "success": True,
                "message": f"Database initialized successfully with {len(tables)} tables",
                "tables": tables
            }
        except Exception as e:
            logger.error(f"Error initializing database: {e}")
            return {
                "success": False,
                "message": f"Failed to initialize database: {str(e)}"
            }
    
    def get_session(self) -> Session:
        """Get a new database session"""
        if not self.Session:
            raise RuntimeError("Database session factory not initialized")
        return self.Session()
    
    def get_db_info(self) -> Dict[str, Any]:
        """Get information about the current database configuration"""
        db_type = os.getenv("DB_TYPE", "sqlite").lower()
        
        info = {
            "type": db_type,
            "connection_status": "connected" if self.engine else "disconnected"
        }
        
        if db_type == "sqlite":
            info["path"] = self.db_path
        else:  # MySQL
            info["host"] = os.getenv("DB_HOST", "localhost")
            info["port"] = os.getenv("DB_PORT", "3306")
            info["name"] = os.getenv("DB_NAME", "github_events")
            info["user"] = os.getenv("DB_USER", "root")
            # Don't include password in the response for security reasons
        
        # Add table information
        if self.engine:
            try:
                inspector = inspect(self.engine)
                tables = inspector.get_table_names()
                
                table_info = []
                for table in tables:
                    columns = inspector.get_columns(table)
                    row_count = None
                    
                    # Get row count for SQLite
                    if db_type == "sqlite":
                        try:
                            with self.get_session() as session:
                                result = session.execute(f"SELECT COUNT(*) FROM {table}")
                                row_count = result.scalar()
                        except Exception as e:
                            logger.error(f"Error getting row count for table {table}: {e}")
                    
                    table_info.append({
                        "name": table,
                        "columns": len(columns),
                        "rows": row_count
                    })
                
                info["tables"] = table_info
            except Exception as e:
                logger.error(f"Error getting table information: {e}")
                info["tables"] = []
        
        return info
    
    def test_connection(self, db_config: Dict[str, Any] = None) -> Dict[str, Any]:
        """Test a database connection with the provided configuration"""
        try:
            if not db_config:
                # Test current connection
                if not self.engine:
                    return {
                        "success": False,
                        "message": "Database engine not initialized"
                    }
                
                # Try to connect
                conn = self.engine.connect()
                conn.close()
                
                return {
                    "success": True,
                    "message": "Successfully connected to database"
                }
            
            db_type = db_config.get("type", "sqlite").lower()
            
            if db_type == "sqlite":
                db_path = db_config.get("path", "github_events.db")
                
                # Test SQLite connection
                if db_config.get("create_new", False):
                    # Create directory if it doesn't exist
                    db_dir = os.path.dirname(db_path)
                    if db_dir and not os.path.exists(db_dir):
                        os.makedirs(db_dir)
                
                # Test connection by creating a temporary engine
                test_url = f"sqlite:///{db_path}"
                test_engine = create_engine(test_url)
                
                # Try to connect
                conn = test_engine.connect()
                conn.close()
                
                return {
                    "success": True,
                    "message": f"Successfully connected to SQLite database at {db_path}"
                }
            else:  # MySQL
                host = db_config.get("host", "localhost")
                port = db_config.get("port", "3306")
                name = db_config.get("name", "github_events")
                user = db_config.get("user", "root")
                password = db_config.get("password", "")
                
                # Test MySQL connection
                test_url = f"mysql+pymysql://{user}:{password}@{host}:{port}/{name}"
                test_engine = create_engine(test_url)
                
                # Try to connect
                conn = test_engine.connect()
                conn.close()
                
                return {
                    "success": True,
                    "message": f"Successfully connected to MySQL database at {host}:{port}/{name}"
                }
        except Exception as e:
            logger.error(f"Error testing database connection: {e}")
            return {
                "success": False,
                "message": f"Failed to connect to database: {str(e)}"
            }
    
    def update_db_config(self, db_config: Dict[str, Any]) -> Dict[str, Any]:
        """Update the database configuration and reconnect"""
        try:
            db_type = db_config.get("type", "sqlite").lower()
            
            # Set environment variables for the new configuration
            os.environ["DB_TYPE"] = db_type
            
            if db_type == "sqlite":
                db_path = db_config.get("path", "github_events.db")
                self.db_path = db_path
                
                # Create new database if requested
                if db_config.get("create_new", False):
                    # Create directory if it doesn't exist
                    db_dir = os.path.dirname(db_path)
                    if db_dir and not os.path.exists(db_dir):
                        os.makedirs(db_dir)
                    
                    # Remove existing file if it exists
                    if os.path.exists(db_path):
                        os.remove(db_path)
            else:  # MySQL
                os.environ["DB_HOST"] = db_config.get("host", "localhost")
                os.environ["DB_PORT"] = str(db_config.get("port", "3306"))
                os.environ["DB_NAME"] = db_config.get("name", "github_events")
                os.environ["DB_USER"] = db_config.get("user", "root")
                os.environ["DB_PASSWORD"] = db_config.get("password", "")
            
            # Close existing connections
            if self.engine:
                self.engine.dispose()
            
            # Reinitialize the database
            self._initialize_db()
            
            return {
                "success": True,
                "message": f"Database configuration updated successfully"
            }
        except Exception as e:
            logger.error(f"Error updating database configuration: {e}")
            return {
                "success": False,
                "message": f"Failed to update database configuration: {str(e)}"
            }
    
    def create_sqlite_db(self, db_path: str) -> Dict[str, Any]:
        """Create a new SQLite database"""
        try:
            # Create directory if it doesn't exist
            db_dir = os.path.dirname(db_path)
            if db_dir and not os.path.exists(db_dir):
                os.makedirs(db_dir)
            
            # Create SQLite database URL
            db_url = f"sqlite:///{db_path}"
            
            # Create engine and session
            engine = create_engine(db_url)
            
            # Create tables
            Base.metadata.create_all(engine)
            
            return {
                "success": True,
                "message": f"SQLite database created successfully at {db_path}"
            }
        except Exception as e:
            logger.error(f"Error creating SQLite database: {e}")
            return {
                "success": False,
                "message": f"Failed to create SQLite database: {str(e)}"
            }
    
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
