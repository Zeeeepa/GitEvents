import os
import sys
import logging
import uvicorn
import threading
import time
import platform
import webbrowser
from dotenv import load_dotenv

# Load environment variables from .env file if it exists
load_dotenv()

# Configure logging with colors for Windows
is_windows = platform.system() == "Windows"
if is_windows:
    try:
        import colorama
        colorama.init()  # Initialize colorama for Windows color support
        
        # Define color codes
        RESET = colorama.Style.RESET_ALL
        GREEN = colorama.Fore.GREEN
        YELLOW = colorama.Fore.YELLOW
        CYAN = colorama.Fore.CYAN
        RED = colorama.Fore.RED
    except ImportError:
        # Fallback if colorama is not installed
        RESET = GREEN = YELLOW = CYAN = RED = ""
else:
    # ANSI color codes for non-Windows platforms
    RESET = "\033[0m"
    GREEN = "\033[32m"
    YELLOW = "\033[33m"
    CYAN = "\033[36m"
    RED = "\033[31m"

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format=f"{GREEN}%(asctime)s{RESET} - {CYAN}%(name)s{RESET} - {YELLOW}%(levelname)s{RESET} - %(message)s"
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
    
    # Get database configuration from environment
    db_type = os.getenv("DB_TYPE", "sqlite").lower()
    
    if db_type == "mysql":
        db_host = os.getenv("DB_HOST", "localhost")
        db_port = os.getenv("DB_PORT", "3306")
        db_name = os.getenv("DB_NAME", "github_events")
        logger.info(f"Initializing MySQL database at {db_host}:{db_port}/{db_name}")
    else:
        db_path = os.getenv("GITHUB_EVENTS_DB", "github_events.db")
        logger.info(f"Initializing SQLite database at {db_path}")
        # Create database manager (which will create tables if they don't exist)
        db_manager = DatabaseManager(db_path)
    
    # Log success
    logger.info(f"{GREEN}Database initialized successfully{RESET}")

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
                logger.info(f"{GREEN}GitHub webhook URL (ngrok): {webhook_url}{RESET}")
                logger.info("Use this URL in your GitHub repository webhook settings")
            
            if api_url:
                logger.info(f"{GREEN}API URL (ngrok): {api_url}{RESET}")
                
            # Open ngrok dashboard in browser on Windows
            if is_windows and (webhook_url or api_url):
                logger.info("Opening ngrok dashboard in browser...")
                ngrok_service.open_ngrok_dashboard()
                
        except ImportError:
            logger.error(f"{RED}Failed to import ngrok service. Make sure pyngrok is installed.{RESET}")
        except Exception as e:
            logger.error(f"{RED}Failed to start ngrok tunnels: {e}{RESET}")

def print_startup_banner():
    """Print a startup banner with instructions"""
    banner = f"""
{GREEN}╔═══════════════════════════════════════════════════════════════╗
║                      GitEvents Server                          ║
╚═══════════════════════════════════════════════════════════════╝{RESET}

{CYAN}API Server:{RESET}        http://localhost:{os.getenv("API_PORT", 8001)}
{CYAN}Webhook Server:{RESET}    http://localhost:{os.getenv("WEBHOOK_PORT", 8002)}
{CYAN}Database:{RESET}          {os.getenv("DB_TYPE", "sqlite").upper()} ({os.getenv("GITHUB_EVENTS_DB", "github_events.db") if os.getenv("DB_TYPE", "sqlite").lower() == "sqlite" else f"{os.getenv('DB_HOST', 'localhost')}:{os.getenv('DB_PORT', '3306')}/{os.getenv('DB_NAME', 'github_events')}"})
{CYAN}Ngrok Enabled:{RESET}     {os.getenv("ENABLE_NGROK", "false").lower() == "true"}

{YELLOW}Press Ctrl+C to stop the server{RESET}
"""
    print(banner)

def open_frontend():
    """Open the frontend in the default browser (Windows convenience)"""
    if is_windows:
        try:
            # Wait a bit for the server to start
            time.sleep(2)
            frontend_url = "http://localhost:3000"
            logger.info(f"Opening frontend in browser: {frontend_url}")
            webbrowser.open(frontend_url)
        except Exception as e:
            logger.error(f"Failed to open frontend in browser: {e}")

if __name__ == "__main__":
    logger.info(f"{GREEN}Starting GitHub Events application{RESET}")
    
    # Initialize database
    init_database()
    
    # Start ngrok tunnels if enabled
    start_ngrok_tunnels()
    
    # Print startup banner
    print_startup_banner()
    
    # Start servers in separate threads
    api_thread = threading.Thread(target=start_api_server)
    webhook_thread = threading.Thread(target=start_webhook_server)
    
    api_thread.daemon = True
    webhook_thread.daemon = True
    
    api_thread.start()
    webhook_thread.start()
    
    # Open frontend in browser on Windows (if requested)
    if is_windows and os.getenv("OPEN_BROWSER", "false").lower() == "true":
        frontend_thread = threading.Thread(target=open_frontend)
        frontend_thread.daemon = True
        frontend_thread.start()
    
    # Keep the main thread alive
    try:
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        logger.info(f"{YELLOW}Shutting down GitHub Events application{RESET}")
        
        # Close ngrok tunnels if enabled
        if os.getenv("ENABLE_NGROK", "false").lower() == "true":
            try:
                from api.ngrok_service import ngrok_service
                ngrok_service.close_tunnels()
            except ImportError:
                pass
            except Exception as e:
                logger.error(f"Error closing ngrok tunnels: {e}")
        
        sys.exit(0)
