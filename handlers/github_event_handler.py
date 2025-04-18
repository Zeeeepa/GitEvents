import logging
import os
from typing import Any, Callable, Dict, TypeVar, Optional

from fastapi import Request
from github import Github
from pydantic import BaseModel

from db_manager import DatabaseManager
from codegen.extensions.events.interface import EventHandlerManagerProtocol
from codegen.extensions.github.types.base import GitHubInstallation, GitHubWebhookPayload
from codegen.shared.logging.get_logger import get_logger

logger = get_logger(__name__)
logger.setLevel(logging.DEBUG)

# Type variable for event types
T = TypeVar("T", bound=BaseModel)

class GitHub(EventHandlerManagerProtocol):
    def __init__(self, app):
        self.app = app
        self.registered_handlers = {}
        self._client = None
        
        # Initialize database manager
        db_path = os.getenv("GITHUB_EVENTS_DB", "github_events.db")
        self.db_manager = DatabaseManager(db_path)
        logger.info(f"GitHub event handler initialized with database at {db_path}")

    @property
    def client(self) -> Github:
        if not os.getenv("GITHUB_TOKEN"):
            msg = "GITHUB_TOKEN is not set"
            logger.exception(msg)
            raise ValueError(msg)
        if not self._client:
            self._client = Github(os.getenv("GITHUB_TOKEN"))
        return self._client

    def unsubscribe_all_handlers(self):
        logger.info("[HANDLERS] Clearing all handlers")
        self.registered_handlers.clear()

    def event(self, event_name: str):
        logger.info(f"[EVENT] Registering handler for {event_name}")

        def register_handler(func: Callable[[T], Any]):
            # Get the type annotation from the first parameter
            event_type = func.__annotations__.get("event")
            func_name = func.__qualname__
            logger.info(f"[EVENT] Registering function {func_name} for {event_name}")

            def new_func(raw_event: dict):
                # Only validate if a Pydantic model was specified
                if event_type and issubclass(event_type, BaseModel):
                    try:
                        parsed_event = event_type.model_validate(raw_event)
                        
                        # Store event in database if it's a relevant type
                        self._store_event_in_db(event_name, parsed_event)
                        
                        return func(parsed_event)
                    except Exception as e:
                        logger.exception(f"Error parsing event: {e}")
                        raise
                else:
                    # Pass through raw dict if no type validation needed
                    # Still try to store it if we can determine the type
                    self._store_event_in_db(event_name, raw_event)
                    
                    return func(raw_event)

            self.registered_handlers[event_name] = new_func
            return new_func

        return register_handler
    
    def _store_event_in_db(self, event_name: str, event_data: Any) -> None:
        """Store GitHub event in the database based on its type"""
        try:
            logger.debug(f"Storing event {event_name} in database")
            
            # Handle different event types
            if event_name.startswith('pull_request:'):
                self._store_pr_event(event_name, event_data)
            elif event_name == 'push':
                self._store_push_event(event_data)
            elif event_name in ['create', 'delete'] and getattr(event_data, 'ref_type', None) == 'branch':
                self._store_branch_event(event_name, event_data)
            else:
                logger.debug(f"Event type {event_name} not configured for DB storage")
        except Exception as e:
            logger.error(f"Error storing event in database: {e}")
            # Don't re-raise; we don't want to block event processing if DB fails
    
    def _store_pr_event(self, event_name: str, event_data: Any) -> None:
        """Store pull request event in the database"""
        try:
            # Extract the event type (after the colon)
            event_type = event_name.split(':', 1)[1] if ':' in event_name else event_name
            
            # Get repository data
            repo_data = event_data.repository if hasattr(event_data, 'repository') else None
            if not repo_data:
                logger.warning("Repository data missing in PR event")
                return
            
            # Save repository
            repo = self.db_manager.save_repository({
                'id': repo_data.id,
                'name': repo_data.name,
                'full_name': repo_data.full_name,
                'private': repo_data.private,
            })
            
            # Get user data
            user_data = event_data.sender if hasattr(event_data, 'sender') else None
            if not user_data:
                logger.warning("User data missing in PR event")
                return
            
            # Save user
            user = self.db_manager.save_user({
                'id': user_data.id,
                'login': user_data.login,
                'type': user_data.type,
            })
            
            # Get pull request data
            pr_data = event_data.pull_request if hasattr(event_data, 'pull_request') else None
            if not pr_data:
                logger.warning("Pull request data missing in PR event")
                return
            
            # Save pull request
            pr = self.db_manager.save_pull_request({
                'id': pr_data.id,
                'number': pr_data.number,
                'title': pr_data.title,
                'body': pr_data.body,
                'state': pr_data.state,
                'created_at': pr_data.created_at,
                'updated_at': pr_data.updated_at,
                'merged': getattr(pr_data, 'merged', False),
                'merged_at': getattr(pr_data, 'merged_at', None),
                'head': {
                    'ref': pr_data.head.ref,
                    'sha': pr_data.head.sha,
                },
                'base': {
                    'ref': pr_data.base.ref,
                    'sha': pr_data.base.sha,
                },
            }, repo.id, user.id)
            
            # Save PR event with payload
            payload = {}
            if hasattr(event_data, 'label'):
                payload['label'] = {
                    'name': event_data.label.name,
                    'color': event_data.label.color,
                }
            
            self.db_manager.save_pr_event(event_type, pr.id, payload)
            logger.info(f"Stored PR event: {event_type} for PR #{pr_data.number}")
        except Exception as e:
            logger.error(f"Error storing PR event: {e}")
    
    def _store_push_event(self, event_data: Any) -> None:
        """Store push event in the database"""
        try:
            # Check if this is a branch event (push to a branch)
            if not event_data.ref.startswith('refs/heads/'):
                logger.debug(f"Push event is not to a branch: {event_data.ref}")
                return
            
            # Get repository data
            repo_data = event_data.repository if hasattr(event_data, 'repository') else None
            if not repo_data:
                logger.warning("Repository data missing in push event")
                return
            
            # Save repository
            repo = self.db_manager.save_repository({
                'id': repo_data.id,
                'name': repo_data.name,
                'full_name': repo_data.full_name,
                'private': repo_data.private,
            })
            
            # Get user data
            user_data = event_data.sender if hasattr(event_data, 'sender') else None
            if not user_data:
                logger.warning("User data missing in push event")
                return
            
            # Save user
            user = self.db_manager.save_user({
                'id': user_data.id,
                'login': user_data.login,
                'type': user_data.type,
            })
            
            # Extract commit data
            commits = []
            if hasattr(event_data, 'commits'):
                for commit in event_data.commits:
                    commits.append({
                        'id': commit.id,
                        'message': commit.message,
                        'timestamp': commit.timestamp,
                        'author': {
                            'name': commit.author.name,
                            'email': commit.author.email,
                            'username': commit.author.username,
                        },
                        'added': commit.added,
                        'removed': commit.removed,
                        'modified': commit.modified,
                    })
            
            # Save push event
            self.db_manager.save_push_event({
                'ref': event_data.ref,
                'before': event_data.before,
                'after': event_data.after,
                'created': event_data.created,
                'deleted': event_data.deleted,
                'forced': event_data.forced,
                'commits': commits,
            }, repo.id, user.id)
            
            # Also save as a branch event if it's a creation or deletion
            if event_data.created:
                self.db_manager.save_branch_event('created', event_data.ref, repo.id)
            elif event_data.deleted:
                self.db_manager.save_branch_event('deleted', event_data.ref, repo.id)
            
            logger.info(f"Stored push event for branch {event_data.ref}")
        except Exception as e:
            logger.error(f"Error storing push event: {e}")
    
    def _store_branch_event(self, event_name: str, event_data: Any) -> None:
        """Store branch event in the database"""
        try:
            # Get repository data
            repo_data = event_data.repository if hasattr(event_data, 'repository') else None
            if not repo_data:
                logger.warning("Repository data missing in branch event")
                return
            
            # Save repository
            repo = self.db_manager.save_repository({
                'id': repo_data.id,
                'name': repo_data.name,
                'full_name': repo_data.full_name,
                'private': repo_data.private,
            })
            
            # Get ref name (branch name)
            ref = f"refs/heads/{event_data.ref}" if hasattr(event_data, 'ref') else None
            if not ref:
                logger.warning("Branch ref missing in branch event")
                return
            
            # Save branch event
            self.db_manager.save_branch_event(
                event_name, 
                ref, 
                repo.id,
                {
                    'sender': event_data.sender.login if hasattr(event_data, 'sender') else None,
                }
            )
            
            logger.info(f"Stored branch event: {event_name} for branch {ref}")
        except Exception as e:
            logger.error(f"Error storing branch event: {e}")

    async def handle(self, event: dict, request: Request | None = None) -> dict:
        """Handle both webhook events and installation callbacks."""
        logger.info("[HANDLER] Handling GitHub event")

        # Check if this is an installation event
        if "installation_id" in event and "code" in event:
            installation = GitHubInstallation.model_validate(event)
            logger.info("=====[GITHUB APP INSTALLATION]=====")
            logger.info(f"Code: {installation.code}")
            logger.info(f"Installation ID: {installation.installation_id}")
            logger.info(f"Setup Action: {installation.setup_action}")
            return {
                "message": "GitHub app installation details received",
                "details": {
                    "code": installation.code,
                    "installation_id": installation.installation_id,
                    "setup_action": installation.setup_action,
                },
            }

        # Extract headers for webhook events if request is provided
        headers = {}
        if request:
            headers = {
                "x-github-event": request.headers.get("x-github-event"),
                "x-github-delivery": request.headers.get("x-github-delivery"),
                "x-github-hook-id": request.headers.get("x-github-hook-id"),
                "x-github-hook-installation-target-id": request.headers.get("x-github-hook-installation-target-id"),
                "x-github-hook-installation-target-type": request.headers.get("x-github-hook-installation-target-type"),
            }

        # Handle webhook events
        try:
            # For simulation, use event data directly
            if not request:
                event_type = f"pull_request:{event['action']}" if "action" in event else event.get("type", "unknown")
                if event_type not in self.registered_handlers:
                    logger.info(f"[HANDLER] No handler found for event type: {event_type}")
                    
                    # Still store the event in DB even if no handler is registered
                    try:
                        self._store_event_in_db(event_type, event)
                    except Exception as e:
                        logger.error(f"Error storing unhandled event in DB: {e}")
                    
                    return {"message": "Event type not handled"}
                else:
                    logger.info(f"[HANDLER] Handling event: {event_type}")
                    handler = self.registered_handlers[event_type]
                    return handler(event)

            # For actual webhooks, use the full payload
            webhook = GitHubWebhookPayload.model_validate({"headers": headers, "event": event})
            event_type = webhook.headers.event_type
            action = webhook.event.action
            full_event_type = f"{event_type}:{action}" if action else event_type

            if full_event_type not in self.registered_handlers:
                logger.info(f"[HANDLER] No handler found for event type: {full_event_type}")
                
                # Still store the event in DB even if no handler is registered
                try:
                    self._store_event_in_db(full_event_type, webhook.event)
                except Exception as e:
                    logger.error(f"Error storing unhandled webhook event in DB: {e}")
                
                return {"message": "Event type not handled"}
            else:
                logger.info(f"[HANDLER] Handling event: {full_event_type}")
                handler = self.registered_handlers[full_event_type]
                return handler(event)

        except Exception as e:
            logger.exception(f"Error handling webhook: {e}")
            raise