import os
import logging
import uvicorn
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
    """Start the FastAPI server"""
    from api.api_service import app
    
    port = int(os.getenv("API_PORT", 8001))
    logger.info(f"Starting API server on port {port}")
    
    uvicorn.run(app, host="0.0.0.0", port=port)

if __name__ == "__main__":
    logger.info("Starting GitHub Events application")
    start_api_server()
