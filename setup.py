"""
GitEvents Setup Script

This script helps set up the GitEvents application by:
1. Checking Python and Node.js versions
2. Installing required Python packages
3. Creating necessary directories
4. Initializing the database

Usage:
    python setup.py
"""

import os
import sys
import subprocess
import platform
import json
from pathlib import Path

def check_python_version():
    """Check if Python version is compatible"""
    print("Checking Python version...")
    major, minor = sys.version_info.major, sys.version_info.minor
    if major < 3 or (major == 3 and minor < 6):
        print(f"ERROR: Python 3.6+ is required, but found {major}.{minor}")
        return False
    print(f"OK: Python {major}.{minor} detected")
    return True

def check_node_version():
    """Check if Node.js is installed and version is compatible"""
    print("Checking Node.js version...")
    try:
        result = subprocess.run(["node", "--version"], capture_output=True, text=True)
        if result.returncode != 0:
            print("ERROR: Node.js is not installed or not in PATH")
            return False
        version = result.stdout.strip()
        print(f"OK: Node.js {version} detected")
        return True
    except FileNotFoundError:
        print("ERROR: Node.js is not installed or not in PATH")
        return False

def install_python_packages():
    """Install required Python packages"""
    print("Installing Python packages...")
    requirements_file = Path("requirements.txt")
    if not requirements_file.exists():
        print("ERROR: requirements.txt not found")
        return False
    
    try:
        result = subprocess.run([sys.executable, "-m", "pip", "install", "-r", "requirements.txt"], 
                               capture_output=True, text=True)
        if result.returncode != 0:
            print(f"ERROR: Failed to install Python packages: {result.stderr}")
            return False
        print("OK: Python packages installed successfully")
        return True
    except Exception as e:
        print(f"ERROR: Failed to install Python packages: {e}")
        return False

def create_directories():
    """Create necessary directories if they don't exist"""
    print("Creating necessary directories...")
    directories = ["data", "src/components/dashboard", "public"]
    
    for directory in directories:
        dir_path = Path(directory)
        if not dir_path.exists():
            try:
                dir_path.mkdir(parents=True, exist_ok=True)
                print(f"OK: Created directory {directory}")
            except Exception as e:
                print(f"ERROR: Failed to create directory {directory}: {e}")
                return False
    
    return True

def test_database_connection(db_config):
    """Test database connection with provided configuration"""
    print("Testing database connection...")
    try:
        # Import here to ensure dependencies are installed first
        from dotenv import load_dotenv
        load_dotenv()
        
        from db.db_manager import DatabaseManager
        
        db_type = db_config.get("DB_TYPE", "SQLite")
        
        if db_type.lower() == "sqlite":
            db_path = db_config.get("GITHUB_EVENTS_DB", "github_events.db")
            db_manager = DatabaseManager(db_path)
            result = db_manager.test_connection()
        else:  # MySQL
            db_manager = DatabaseManager(
                db_name=db_config.get("DB_NAME", "github_events"),
                db_type="mysql",
                db_host=db_config.get("DB_HOST", "localhost"),
                db_port=int(db_config.get("DB_PORT", 3306)),
                db_user=db_config.get("DB_USER", "admin"),
                db_password=db_config.get("DB_PASSWORD", "password")
            )
            result = db_manager.test_connection()
        
        if result["success"]:
            print(f"OK: Database connection successful: {result['message']}")
            return True
        else:
            print(f"ERROR: Failed to connect to database: {result['message']}")
            return False
    except Exception as e:
        print(f"ERROR: Failed to test database connection: {e}")
        return False

def initialize_database(db_config):
    """Initialize the database"""
    print("Initializing database...")
    try:
        # Import here to ensure dependencies are installed first
        from dotenv import load_dotenv
        load_dotenv()
        
        from db.db_manager import DatabaseManager
        
        db_type = db_config.get("DB_TYPE", "SQLite")
        
        if db_type.lower() == "sqlite":
            db_path = db_config.get("GITHUB_EVENTS_DB", "github_events.db")
            db_manager = DatabaseManager(db_path)
            result = db_manager.initialize_database()
        else:  # MySQL
            db_manager = DatabaseManager(
                db_name=db_config.get("DB_NAME", "github_events"),
                db_type="mysql",
                db_host=db_config.get("DB_HOST", "localhost"),
                db_port=int(db_config.get("DB_PORT", 3306)),
                db_user=db_config.get("DB_USER", "admin"),
                db_password=db_config.get("DB_PASSWORD", "password")
            )
            result = db_manager.initialize_database()
        
        if result["success"]:
            print(f"OK: Database initialized successfully: {result['message']}")
            return True
        else:
            print(f"ERROR: Failed to initialize database: {result['message']}")
            return False
    except Exception as e:
        print(f"ERROR: Failed to initialize database: {e}")
        return False

def create_env_file():
    """Create .env file if it doesn't exist"""
    print("Checking .env file...")
    env_file = Path(".env")
    
    if env_file.exists():
        print("OK: .env file already exists")
        return True
    
    print("Creating default .env file...")
    default_env = """# GitEvents Environment Configuration
API_PORT=8001
REACT_APP_API_URL=http://localhost:8001/api
WEBHOOK_PORT=8002

GITHUB_TOKEN=your_github_token_here
GITHUB_EVENTS_DB=github_events.db
DB_TYPE=SQLite
DB_HOST=localhost
DB_PORT=3306
DB_NAME=github_events
DB_USER=admin
DB_PASSWORD=password

ENABLE_NGROK=true
NGROK_AUTH_TOKEN=your_ngrok_auth_token_here

OPEN_BROWSER=true
DEV_MODE=true
"""
    
    try:
        with open(env_file, "w") as f:
            f.write(default_env)
        print("OK: Created default .env file")
        print("NOTE: You should update the GitHub token and ngrok auth token in the .env file")
        return True
    except Exception as e:
        print(f"ERROR: Failed to create .env file: {e}")
        return False

def load_env_config():
    """Load configuration from .env file"""
    print("Loading configuration from .env file...")
    try:
        from dotenv import load_dotenv
        load_dotenv()
        
        config = {
            "API_PORT": os.getenv("API_PORT", "8001"),
            "REACT_APP_API_URL": os.getenv("REACT_APP_API_URL", "http://localhost:8001/api"),
            "WEBHOOK_PORT": os.getenv("WEBHOOK_PORT", "8002"),
            "GITHUB_TOKEN": os.getenv("GITHUB_TOKEN", ""),
            "GITHUB_EVENTS_DB": os.getenv("GITHUB_EVENTS_DB", "github_events.db"),
            "DB_TYPE": os.getenv("DB_TYPE", "SQLite"),
            "DB_HOST": os.getenv("DB_HOST", "localhost"),
            "DB_PORT": os.getenv("DB_PORT", "3306"),
            "DB_NAME": os.getenv("DB_NAME", "github_events"),
            "DB_USER": os.getenv("DB_USER", "admin"),
            "DB_PASSWORD": os.getenv("DB_PASSWORD", "password"),
            "ENABLE_NGROK": os.getenv("ENABLE_NGROK", "true").lower() == "true",
            "NGROK_AUTH_TOKEN": os.getenv("NGROK_AUTH_TOKEN", ""),
            "OPEN_BROWSER": os.getenv("OPEN_BROWSER", "true").lower() == "true",
            "DEV_MODE": os.getenv("DEV_MODE", "true").lower() == "true"
        }
        
        print("OK: Configuration loaded successfully")
        return config
    except Exception as e:
        print(f"ERROR: Failed to load configuration: {e}")
        return {}

def main():
    """Main setup function"""
    print("=" * 60)
    print("GitEvents Setup")
    print("=" * 60)
    print()
    
    # Check versions
    if not check_python_version() or not check_node_version():
        print("\nERROR: Version requirements not met. Please fix the issues above.")
        return False
    
    # Create directories
    if not create_directories():
        print("\nERROR: Failed to create necessary directories.")
        return False
    
    # Create .env file
    if not create_env_file():
        print("\nERROR: Failed to create .env file.")
        return False
    
    # Load configuration from .env
    config = load_env_config()
    if not config:
        print("\nERROR: Failed to load configuration.")
        return False
    
    # Install Python packages
    if not install_python_packages():
        print("\nERROR: Failed to install Python packages.")
        return False
    
    # Test database connection
    if not test_database_connection(config):
        print("\nWARNING: Database connection test failed. You may need to update your database configuration.")
        create_db = input("Would you like to create/initialize the database anyway? (y/n): ")
        if create_db.lower() != 'y':
            print("Setup aborted. Please update your database configuration in the .env file and try again.")
            return False
    
    # Initialize database
    if not initialize_database(config):
        print("\nERROR: Failed to initialize database.")
        return False
    
    print("\n" + "=" * 60)
    print("GitEvents setup completed successfully!")
    print("You can now run the application using:")
    print("  - Python backend: python main.py")
    print("  - React frontend: npm start")
    print("=" * 60)
    
    return True

if __name__ == "__main__":
    success = main()
    if not success:
        print("\nSetup failed. Please fix the issues above and try again.")
        sys.exit(1)
