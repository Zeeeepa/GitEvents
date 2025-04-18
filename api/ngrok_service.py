import os
import logging
from pyngrok import ngrok, conf

# Configure logging
logger = logging.getLogger(__name__)

class NgrokService:
    """Service to manage ngrok tunnels for webhook endpoints"""
    
    def __init__(self):
        self.webhook_tunnel = None
        self.api_tunnel = None
        self.ngrok_auth_token = os.getenv("NGROK_AUTH_TOKEN")
        
        # Configure ngrok (if token is provided)
        if self.ngrok_auth_token:
            conf.get_default().auth_token = self.ngrok_auth_token
            logger.info("Ngrok configured with auth token")
        else:
            logger.warning("No NGROK_AUTH_TOKEN provided. Tunnels will be limited and temporary.")
    
    def start_webhook_tunnel(self, port):
        """Start ngrok tunnel for webhook endpoint"""
        try:
            self.webhook_tunnel = ngrok.connect(port, "http")
            public_url = self.webhook_tunnel.public_url
            logger.info(f"Webhook ngrok tunnel established: {public_url}")
            
            # Extract the webhook URL for GitHub
            webhook_url = f"{public_url}/webhook/github"
            logger.info(f"GitHub webhook URL: {webhook_url}")
            
            return webhook_url
        except Exception as e:
            logger.error(f"Failed to establish webhook ngrok tunnel: {e}")
            return None
    
    def start_api_tunnel(self, port):
        """Start ngrok tunnel for API endpoint"""
        try:
            self.api_tunnel = ngrok.connect(port, "http")
            public_url = self.api_tunnel.public_url
            logger.info(f"API ngrok tunnel established: {public_url}")
            return public_url
        except Exception as e:
            logger.error(f"Failed to establish API ngrok tunnel: {e}")
            return None
    
    def get_webhook_url(self):
        """Get the current webhook URL"""
        if self.webhook_tunnel:
            return f"{self.webhook_tunnel.public_url}/webhook/github"
        return None
    
    def get_api_url(self):
        """Get the current API URL"""
        if self.api_tunnel:
            return self.api_tunnel.public_url
        return None
    
    def close_tunnels(self):
        """Close all ngrok tunnels"""
        try:
            ngrok.kill()
            logger.info("All ngrok tunnels closed")
        except Exception as e:
            logger.error(f"Error closing ngrok tunnels: {e}")

# Singleton instance
ngrok_service = NgrokService()
