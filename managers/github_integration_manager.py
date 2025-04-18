import os
import logging
from typing import Optional, Dict

from ngrok_manager import NgrokManager
from webhook_manager import WebhookManager

logger = logging.getLogger(__name__)

class GitHubIntegrationManager:
    """Manages GitHub integration with webhook server and ngrok tunnel"""
    
    def __init__(self, config: Dict, webhook_port: int = 8000):
        """Initialize the GitHub integration manager"""
        self.config = config
        self.webhook_port = webhook_port
        self.ngrok_manager = None
        self.webhook_manager = None
        
    def initialize(self, github_token: str, ngrok_token: Optional[str] = None) -> bool:
        """Initialize the integration with GitHub token and optional ngrok token"""
        try:
            # Initialize webhook manager
            self.webhook_manager = WebhookManager(self.config)
            if not self.webhook_manager.initialize(github_token):
                logger.error("Failed to initialize webhook manager")
                return False
                
            # Initialize ngrok manager if token provided
            self.ngrok_manager = NgrokManager(self.webhook_port, ngrok_token)
            
            logger.info("GitHub integration initialized successfully")
            return True
        except Exception as e:
            logger.error(f"Error initializing GitHub integration: {e}")
            return False
    
    def start_services(self) -> bool:
        """Start ngrok tunnel and webhook server"""
        try:
            # Start ngrok tunnel
            if self.ngrok_manager:
                webhook_url = self.ngrok_manager.start_tunnel()
                if not webhook_url:
                    logger.error("Failed to start ngrok tunnel")
                    return False
                
                # Update webhook URL to use ngrok URL
                os.environ["WEBHOOK_URL"] = webhook_url
                logger.info(f"Webhook URL set to {webhook_url}")
            
            # Start webhook server
            if self.webhook_manager:
                if not self.webhook_manager.start_server():
                    logger.error("Failed to start webhook server")
                    return False
            
            logger.info("GitHub integration services started successfully")
            return True
        except Exception as e:
            logger.error(f"Error starting GitHub integration services: {e}")
            return False
    
    def stop_services(self) -> bool:
        """Stop webhook server and ngrok tunnel"""
        success = True
        
        # Stop webhook server
        if self.webhook_manager:
            try:
                self.webhook_manager.stop_server()
            except Exception as e:
                logger.error(f"Error stopping webhook server: {e}")
                success = False
        
        # Stop ngrok tunnel
        if self.ngrok_manager:
            try:
                if not self.ngrok_manager.stop_tunnel():
                    logger.error("Failed to stop ngrok tunnel")
                    success = False
            except Exception as e:
                logger.error(f"Error stopping ngrok tunnel: {e}")
                success = False
        
        if success:
            logger.info("GitHub integration services stopped successfully")
        
        return success
    
    def setup_webhooks(self) -> Dict[str, str]:
        """Set up webhooks for all repositories"""
        if not self.webhook_manager:
            logger.error("Webhook manager not initialized")
            return {"status": "Webhook manager not initialized"}
        
        return self.webhook_manager.setup_webhooks_for_all_repos()