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

if __name__ == "__main__":
    logger.info("Starting GitHub Events application")
    
    # Initialize database
    init_database()
    
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
