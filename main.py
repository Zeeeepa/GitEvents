import os
import logging
import uvicorn
import threading
import time
from dotenv import load_dotenv

# Load environment variables from .env file if it exists
load_dotenv()

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)

def start_api_server():
    """Start the FastAPI server for the main API"""
    from api.api_service import app
    
    port = int(os.getenv("API_PORT", 8001))
    logger.info(f"Starting API server on port {port}")
    
    uvicorn.run(app, host="0.0.0.0", port=port)

def start_webhook_server():
    """Start the FastAPI server for the webhook handler"""
    from api.webhook_handler import app
    
    port = int(os.getenv("WEBHOOK_PORT", 8002))
    logger.info(f"Starting webhook server on port {port}")
    
    uvicorn.run(app, host="0.0.0.0", port=port)

def init_database():
    """Initialize the database"""
    from db.db_manager import DatabaseManager
    
    db_path = os.getenv("GITHUB_EVENTS_DB", "github_events.db")
    logger.info(f"Initializing database at {db_path}")
    
    # Create database manager (which will create tables if they don't exist)
    db_manager = DatabaseManager(db_path)
    
    # Log success
    logger.info("Database initialized successfully")

def start_ngrok_tunnels():
    """Start ngrok tunnels if enabled"""
    # Check if ngrok is enabled
    if os.getenv("ENABLE_NGROK", "false").lower() == "true":
        try:
            from api.ngrok_service import ngrok_service
            
            # Start tunnels
            webhook_port = int(os.getenv("WEBHOOK_PORT", 8002))
            api_port = int(os.getenv("API_PORT", 8001))
            
            webhook_url = ngrok_service.start_webhook_tunnel(webhook_port)
            api_url = ngrok_service.start_api_tunnel(api_port)
            
            if webhook_url:
                logger.info(f"GitHub webhook URL (ngrok): {webhook_url}")
                logger.info("Use this URL in your GitHub repository webhook settings")
            
            if api_url:
                logger.info(f"API URL (ngrok): {api_url}")
        except ImportError:
            logger.error("Failed to import ngrok service. Make sure pyngrok is installed.")
        except Exception as e:
            logger.error(f"Failed to start ngrok tunnels: {e}")

if __name__ == "__main__":
    logger.info("Starting GitHub Events application")
    
    # Initialize database
    init_database()
    
    # Start ngrok tunnels if enabled
    start_ngrok_tunnels()
    
    # Start servers in separate threads
    api_thread = threading.Thread(target=start_api_server)
    webhook_thread = threading.Thread(target=start_webhook_server)
    
    api_thread.daemon = True
    webhook_thread.daemon = True
    
    api_thread.start()
    webhook_thread.start()
    
    # Keep the main thread alive
    try:
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        logger.info("Shutting down GitHub Events application")
