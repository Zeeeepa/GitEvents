import os
import logging
import platform
import webbrowser
from pyngrok import ngrok, conf
from typing import Optional, Dict, Any

# Configure logging
logger = logging.getLogger(__name__)

class NgrokService:
    """Service to manage ngrok tunnels for webhook endpoints"""
    
    def __init__(self):
        self.webhook_tunnel = None
        self.api_tunnel = None
        self.ngrok_auth_token = os.getenv("NGROK_AUTH_TOKEN")
        self.is_windows = platform.system() == "Windows"
        
        # Configure ngrok (if token is provided)
        if self.ngrok_auth_token:
            conf.get_default().auth_token = self.ngrok_auth_token
            logger.info("Ngrok configured with auth token")
        else:
            logger.warning("No NGROK_AUTH_TOKEN provided. Tunnels will be limited and temporary.")
            
        # Windows-specific logging
        if self.is_windows:
            logger.info("Running on Windows. Ngrok will use port 4040 for web interface.")
    
    def start_webhook_tunnel(self, port: int) -> Optional[str]:
        """Start ngrok tunnel for webhook endpoint"""
        try:
            self.webhook_tunnel = ngrok.connect(port, "http")
            public_url = self.webhook_tunnel.public_url
            logger.info(f"Webhook ngrok tunnel established: {public_url}")
            
            # Extract the webhook URL for GitHub
            webhook_url = f"{public_url}/webhook/github"
            logger.info(f"GitHub webhook URL: {webhook_url}")
            
            # Windows-specific instructions
            if self.is_windows:
                logger.info("On Windows, you can access the ngrok web interface at: http://localhost:4040")
                logger.info("To add this webhook to GitHub:")
                logger.info("1. Go to your GitHub repository")
                logger.info("2. Click on Settings > Webhooks > Add webhook")
                logger.info(f"3. Set Payload URL to: {webhook_url}")
                logger.info("4. Set Content type to: application/json")
                logger.info("5. Set Secret to the value of GITHUB_WEBHOOK_SECRET in your .env file")
                logger.info("6. Select events you want to trigger the webhook (e.g., Pull requests, Pushes)")
                logger.info("7. Click 'Add webhook'")
            
            return webhook_url
        except Exception as e:
            logger.error(f"Failed to establish webhook ngrok tunnel: {e}")
            return None
    
    def start_api_tunnel(self, port: int) -> Optional[str]:
        """Start ngrok tunnel for API endpoint"""
        try:
            self.api_tunnel = ngrok.connect(port, "http")
            public_url = self.api_tunnel.public_url
            logger.info(f"API ngrok tunnel established: {public_url}")
            return public_url
        except Exception as e:
            logger.error(f"Failed to establish API ngrok tunnel: {e}")
            return None
    
    def get_webhook_url(self) -> Optional[str]:
        """Get the current webhook URL"""
        if self.webhook_tunnel:
            return f"{self.webhook_tunnel.public_url}/webhook/github"
        return None
    
    def get_api_url(self) -> Optional[str]:
        """Get the current API URL"""
        if self.api_tunnel:
            return self.api_tunnel.public_url
        return None
    
    def open_ngrok_dashboard(self) -> None:
        """Open the ngrok web interface in the default browser (Windows convenience)"""
        try:
            webbrowser.open("http://localhost:4040")
            logger.info("Opened ngrok dashboard in browser")
        except Exception as e:
            logger.error(f"Failed to open ngrok dashboard: {e}")
    
    def get_tunnel_status(self) -> Dict[str, Any]:
        """Get status information about active tunnels"""
        status = {
            "webhook_active": self.webhook_tunnel is not None,
            "api_active": self.api_tunnel is not None,
            "webhook_url": self.get_webhook_url(),
            "api_url": self.get_api_url(),
            "ngrok_dashboard": "http://localhost:4040" if (self.webhook_tunnel or self.api_tunnel) else None
        }
        return status
    
    def close_tunnels(self) -> None:
        """Close all ngrok tunnels"""
        try:
            ngrok.kill()
            self.webhook_tunnel = None
            self.api_tunnel = None
            logger.info("All ngrok tunnels closed")
        except Exception as e:
            logger.error(f"Error closing ngrok tunnels: {e}")

# Singleton instance
ngrok_service = NgrokService()
