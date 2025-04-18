#!/usr/bin/env python3
"""
GitEvents - One-Click Deployment and Startup Script

This script provides a seamless way to deploy and start the GitEvents system.
It handles all the necessary setup steps, including:
- Environment setup
- Dependency installation
- Database initialization
- Starting the backend and frontend servers

Usage:
    python deploy.py [--no-frontend] [--no-browser] [--debug]

Options:
    --no-frontend    Skip starting the frontend server
    --no-browser     Don't open browser automatically
    --debug          Enable debug mode with verbose logging
"""

import os
import sys
import platform
import subprocess
import argparse
import logging
import json
import time
import shutil
import webbrowser
from pathlib import Path
from typing import Dict, Any, List, Optional, Tuple

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger("GitEvents-Deploy")

# Define color codes for terminal output
class Colors:
    RESET = "\033[0m"
    GREEN = "\033[32m"
    YELLOW = "\033[33m"
    CYAN = "\033[36m"
    RED = "\033[31m"
    BOLD = "\033[1m"
    
    @staticmethod
    def init():
        """Initialize colors for Windows"""
        if platform.system() == "Windows":
            try:
                import colorama
                colorama.init()
            except ImportError:
                # If colorama is not installed, disable colors
                for attr in dir(Colors):
                    if not attr.startswith("__") and attr != "init":
                        setattr(Colors, attr, "")

# Initialize colors
Colors.init()

def print_banner():
    """Print a fancy banner for the script"""
    banner = f"""
{Colors.CYAN}╔════════════════════════════════════════════════════╗
║  {Colors.BOLD}GitEvents - One-Click Deployment and Startup{Colors.RESET}{Colors.CYAN}  ║
╚════════════════════════════════════════════════════╝{Colors.RESET}
"""
    print(banner)

def run_command(command: str, shell: bool = True, cwd: Optional[str] = None) -> Tuple[int, str, str]:
    """Run a shell command and return the exit code, stdout, and stderr"""
    try:
        logger.debug(f"Running command: {command}")
        process = subprocess.Popen(
            command,
            shell=shell,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True,
            cwd=cwd
        )
        stdout, stderr = process.communicate()
        return process.returncode, stdout, stderr
    except Exception as e:
        logger.error(f"Error running command: {e}")
        return 1, "", str(e)

def check_prerequisites() -> bool:
    """Check if all prerequisites are installed"""
    print(f"{Colors.CYAN}Checking prerequisites...{Colors.RESET}")
    
    # Check Python version
    python_version = platform.python_version_tuple()
    python_version_str = f"{python_version[0]}.{python_version[1]}.{python_version[2]}"
    if int(python_version[0]) < 3 or (int(python_version[0]) == 3 and int(python_version[1]) < 6):
        print(f"{Colors.RED}[ERROR] Python 3.6+ is required, but found version {python_version_str}{Colors.RESET}")
        return False
    print(f"{Colors.GREEN}[OK] Python {python_version_str} detected{Colors.RESET}")
    
    # Check Node.js
    returncode, stdout, stderr = run_command("node --version")
    if returncode != 0:
        print(f"{Colors.RED}[ERROR] Node.js is not installed or not in PATH{Colors.RESET}")
        print("Please install Node.js from https://nodejs.org/")
        return False
    node_version = stdout.strip()
    print(f"{Colors.GREEN}[OK] Node.js {node_version} detected{Colors.RESET}")
    
    # Check npm
    returncode, stdout, stderr = run_command("npm --version")
    if returncode != 0:
        print(f"{Colors.RED}[ERROR] npm is not installed or not in PATH{Colors.RESET}")
        print("Please reinstall Node.js from https://nodejs.org/")
        return False
    npm_version = stdout.strip()
    print(f"{Colors.GREEN}[OK] npm {npm_version} detected{Colors.RESET}")
    
    # Check Git
    returncode, stdout, stderr = run_command("git --version")
    if returncode != 0:
        print(f"{Colors.RED}[ERROR] Git is not installed or not in PATH{Colors.RESET}")
        print("Please install Git from https://git-scm.com/downloads")
        return False
    git_version = stdout.strip()
    print(f"{Colors.GREEN}[OK] {git_version} detected{Colors.RESET}")
    
    return True

def setup_environment() -> bool:
    """Set up the environment for GitEvents"""
    print(f"{Colors.CYAN}Setting up environment...{Colors.RESET}")
    
    # Create data directory if it doesn't exist
    data_dir = Path("data")
    if not data_dir.exists():
        data_dir.mkdir()
        print(f"{Colors.GREEN}[OK] Created data directory{Colors.RESET}")
    
    # Check if .env file exists, if not create from example
    env_file = Path(".env")
    env_example = Path(".env.example")
    
    if not env_file.exists():
        if env_example.exists():
            print(f"{Colors.YELLOW}Creating .env file from .env.example...{Colors.RESET}")
            shutil.copy(env_example, env_file)
            print(f"{Colors.GREEN}[OK] Created .env file from example{Colors.RESET}")
            print(f"{Colors.YELLOW}[NOTE] Please edit .env file with your configuration{Colors.RESET}")
        else:
            print(f"{Colors.YELLOW}Creating default .env file...{Colors.RESET}")
            with open(env_file, "w") as f:
                f.write("""# GitEvents Environment Variables

# API Configuration
API_PORT=8001
WEBHOOK_PORT=8002

# GitHub Configuration
GITHUB_TOKEN=your_github_token_here
GITHUB_WEBHOOK_SECRET=your_webhook_secret_here

# Database Configuration
# SQLite Configuration (Default)
GITHUB_EVENTS_DB=github_events.db

# MySQL Configuration (Optional)
# DB_TYPE=mysql
# DB_HOST=localhost
# DB_PORT=3306
# DB_NAME=github_events
# DB_USER=your_db_username
# DB_PASSWORD=your_db_password

# Frontend Configuration
REACT_APP_API_URL=http://localhost:8001/api

# Ngrok Configuration
ENABLE_NGROK=false
NGROK_AUTH_TOKEN=your_ngrok_auth_token_here

# Windows-specific Configuration
# Set to true to automatically open the frontend in browser when starting the application
OPEN_BROWSER=false
""")
            print(f"{Colors.GREEN}[OK] Created default .env file{Colors.RESET}")
            print(f"{Colors.YELLOW}[NOTE] Please edit .env file with your configuration{Colors.RESET}")
    else:
        print(f"{Colors.GREEN}[OK] .env file already exists{Colors.RESET}")
    
    return True

def setup_python_environment() -> bool:
    """Set up Python virtual environment and install dependencies"""
    print(f"{Colors.CYAN}Setting up Python environment...{Colors.RESET}")
    
    # Determine the virtual environment directory and activation script
    is_windows = platform.system() == "Windows"
    venv_dir = "venv"
    venv_activate = os.path.join(venv_dir, "Scripts", "activate.bat") if is_windows else os.path.join(venv_dir, "bin", "activate")
    
    # Create virtual environment if it doesn't exist
    if not os.path.exists(venv_dir):
        print(f"{Colors.YELLOW}Creating Python virtual environment...{Colors.RESET}")
        returncode, stdout, stderr = run_command(f"python -m venv {venv_dir}")
        if returncode != 0:
            print(f"{Colors.RED}[ERROR] Failed to create virtual environment: {stderr}{Colors.RESET}")
            return False
        print(f"{Colors.GREEN}[OK] Created virtual environment{Colors.RESET}")
    else:
        print(f"{Colors.GREEN}[OK] Virtual environment already exists{Colors.RESET}")
    
    # Install Python dependencies
    print(f"{Colors.YELLOW}Installing Python dependencies...{Colors.RESET}")
    
    # Construct the pip install command based on the platform
    if is_windows:
        pip_cmd = f"{venv_dir}\\Scripts\\pip install -r requirements.txt"
    else:
        pip_cmd = f"source {venv_activate} && pip install -r requirements.txt"
    
    # Try up to 3 times to install dependencies
    max_retries = 3
    for attempt in range(1, max_retries + 1):
        returncode, stdout, stderr = run_command(pip_cmd, shell=True)
        if returncode == 0:
            print(f"{Colors.GREEN}[OK] Python dependencies installed successfully{Colors.RESET}")
            break
        else:
            if attempt < max_retries:
                print(f"{Colors.YELLOW}[WARNING] Failed to install Python dependencies (Attempt {attempt}/{max_retries}). Retrying...{Colors.RESET}")
                time.sleep(2)
            else:
                print(f"{Colors.RED}[ERROR] Failed to install Python dependencies after {max_retries} attempts: {stderr}{Colors.RESET}")
                return False
    
    return True

def setup_node_environment() -> bool:
    """Set up Node.js environment and install dependencies"""
    print(f"{Colors.CYAN}Setting up Node.js environment...{Colors.RESET}")
    
    # Install Node.js dependencies
    print(f"{Colors.YELLOW}Installing Node.js dependencies...{Colors.RESET}")
    
    # Try up to 3 times to install dependencies
    max_retries = 3
    for attempt in range(1, max_retries + 1):
        returncode, stdout, stderr = run_command("npm install")
        if returncode == 0:
            print(f"{Colors.GREEN}[OK] Node.js dependencies installed successfully{Colors.RESET}")
            break
        else:
            if attempt < max_retries:
                print(f"{Colors.YELLOW}[WARNING] Failed to install Node.js dependencies (Attempt {attempt}/{max_retries}). Retrying...{Colors.RESET}")
                time.sleep(2)
            else:
                print(f"{Colors.RED}[ERROR] Failed to install Node.js dependencies after {max_retries} attempts: {stderr}{Colors.RESET}")
                return False
    
    # Fix npm vulnerabilities
    print(f"{Colors.YELLOW}Fixing npm vulnerabilities...{Colors.RESET}")
    returncode, stdout, stderr = run_command("npm audit fix --force")
    if returncode != 0:
        print(f"{Colors.YELLOW}[WARNING] Could not fix all npm vulnerabilities: {stderr}{Colors.RESET}")
    else:
        print(f"{Colors.GREEN}[OK] npm vulnerabilities fixed{Colors.RESET}")
    
    return True

def initialize_database() -> bool:
    """Initialize the database"""
    print(f"{Colors.CYAN}Initializing database...{Colors.RESET}")
    
    # Determine the Python executable path based on the platform
    is_windows = platform.system() == "Windows"
    venv_dir = "venv"
    python_exe = os.path.join(venv_dir, "Scripts", "python.exe") if is_windows else os.path.join(venv_dir, "bin", "python")
    
    # Check if the database already exists
    db_path = os.getenv("GITHUB_EVENTS_DB", "github_events.db")
    db_exists = os.path.exists(db_path)
    
    if db_exists:
        print(f"{Colors.YELLOW}Database already exists at {db_path}{Colors.RESET}")
        # Ask if user wants to reinitialize
        response = input("Do you want to reinitialize the database? (y/N): ").strip().lower()
        if response != 'y':
            print(f"{Colors.GREEN}[OK] Using existing database{Colors.RESET}")
            return True
    
    # Initialize the database
    print(f"{Colors.YELLOW}Initializing database...{Colors.RESET}")
    
    # Construct the command to initialize the database
    if is_windows:
        db_init_cmd = f"{python_exe} -c \"from db.db_manager import DatabaseManager; db = DatabaseManager('{db_path}'); db.initialize_database()\""
    else:
        db_init_cmd = f"source {venv_dir}/bin/activate && python -c \"from db.db_manager import DatabaseManager; db = DatabaseManager('{db_path}'); db.initialize_database()\""
    
    returncode, stdout, stderr = run_command(db_init_cmd)
    if returncode != 0:
        print(f"{Colors.RED}[ERROR] Failed to initialize database: {stderr}{Colors.RESET}")
        return False
    
    print(f"{Colors.GREEN}[OK] Database initialized successfully{Colors.RESET}")
    return True

def start_backend_server(debug: bool = False) -> subprocess.Popen:
    """Start the backend server"""
    print(f"{Colors.CYAN}Starting backend server...{Colors.RESET}")
    
    # Determine the Python executable path based on the platform
    is_windows = platform.system() == "Windows"
    venv_dir = "venv"
    python_exe = os.path.join(venv_dir, "Scripts", "python.exe") if is_windows else os.path.join(venv_dir, "bin", "python")
    
    # Construct the command to start the backend server
    if is_windows:
        backend_cmd = f"{python_exe} main.py"
    else:
        backend_cmd = f"source {venv_dir}/bin/activate && python main.py"
    
    # Set environment variables for debugging if needed
    env = os.environ.copy()
    if debug:
        env["DEBUG"] = "1"
    
    # Start the backend server
    try:
        if is_windows:
            # On Windows, use a new console window
            backend_process = subprocess.Popen(
                backend_cmd,
                shell=True,
                creationflags=subprocess.CREATE_NEW_CONSOLE
            )
        else:
            # On Unix-like systems, use a background process
            backend_process = subprocess.Popen(
                backend_cmd,
                shell=True,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                text=True,
                env=env
            )
        
        # Wait a moment for the server to start
        time.sleep(2)
        
        # Check if the process is still running
        if backend_process.poll() is not None:
            print(f"{Colors.RED}[ERROR] Backend server failed to start{Colors.RESET}")
            return None
        
        print(f"{Colors.GREEN}[OK] Backend server started successfully{Colors.RESET}")
        return backend_process
    
    except Exception as e:
        print(f"{Colors.RED}[ERROR] Failed to start backend server: {e}{Colors.RESET}")
        return None

def start_frontend_server() -> subprocess.Popen:
    """Start the frontend server"""
    print(f"{Colors.CYAN}Starting frontend server...{Colors.RESET}")
    
    # Construct the command to start the frontend server
    frontend_cmd = "npm start"
    
    # Start the frontend server
    try:
        is_windows = platform.system() == "Windows"
        
        if is_windows:
            # On Windows, use a new console window
            frontend_process = subprocess.Popen(
                frontend_cmd,
                shell=True,
                creationflags=subprocess.CREATE_NEW_CONSOLE
            )
        else:
            # On Unix-like systems, use a background process
            frontend_process = subprocess.Popen(
                frontend_cmd,
                shell=True,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                text=True
            )
        
        # Wait a moment for the server to start
        time.sleep(5)
        
        # Check if the process is still running
        if frontend_process.poll() is not None:
            print(f"{Colors.RED}[ERROR] Frontend server failed to start{Colors.RESET}")
            return None
        
        print(f"{Colors.GREEN}[OK] Frontend server started successfully{Colors.RESET}")
        return frontend_process
    
    except Exception as e:
        print(f"{Colors.RED}[ERROR] Failed to start frontend server: {e}{Colors.RESET}")
        return None

def open_browser():
    """Open the browser to the frontend URL"""
    frontend_url = "http://localhost:3000"
    print(f"{Colors.YELLOW}Opening browser to {frontend_url}...{Colors.RESET}")
    webbrowser.open(frontend_url)

def main():
    """Main function to deploy and start GitEvents"""
    # Parse command line arguments
    parser = argparse.ArgumentParser(description="GitEvents - One-Click Deployment and Startup")
    parser.add_argument("--no-frontend", action="store_true", help="Skip starting the frontend server")
    parser.add_argument("--no-browser", action="store_true", help="Don't open browser automatically")
    parser.add_argument("--debug", action="store_true", help="Enable debug mode with verbose logging")
    args = parser.parse_args()
    
    # Set up logging level based on debug flag
    if args.debug:
        logger.setLevel(logging.DEBUG)
    
    # Print banner
    print_banner()
    
    # Check prerequisites
    if not check_prerequisites():
        print(f"{Colors.RED}[ERROR] Prerequisites check failed. Please install the required software and try again.{Colors.RESET}")
        return 1
    
    # Set up environment
    if not setup_environment():
        print(f"{Colors.RED}[ERROR] Environment setup failed.{Colors.RESET}")
        return 1
    
    # Set up Python environment
    if not setup_python_environment():
        print(f"{Colors.RED}[ERROR] Python environment setup failed.{Colors.RESET}")
        return 1
    
    # Set up Node.js environment
    if not setup_node_environment():
        print(f"{Colors.RED}[ERROR] Node.js environment setup failed.{Colors.RESET}")
        return 1
    
    # Initialize database
    if not initialize_database():
        print(f"{Colors.RED}[ERROR] Database initialization failed.{Colors.RESET}")
        return 1
    
    # Start backend server
    backend_process = start_backend_server(args.debug)
    if not backend_process:
        print(f"{Colors.RED}[ERROR] Failed to start backend server.{Colors.RESET}")
        return 1
    
    # Start frontend server if not disabled
    frontend_process = None
    if not args.no_frontend:
        frontend_process = start_frontend_server()
        if not frontend_process:
            print(f"{Colors.RED}[ERROR] Failed to start frontend server.{Colors.RESET}")
            # Don't return here, as the backend is already running
    
    # Open browser if not disabled and frontend is running
    if not args.no_browser and frontend_process and not args.no_frontend:
        open_browser()
    
    # Print success message
    print(f"\n{Colors.GREEN}╔════════════════════════════════════════════════════╗")
    print(f"║  {Colors.BOLD}GitEvents is now running!{Colors.RESET}{Colors.GREEN}                     ║")
    print(f"╚════════════════════════════════════════════════════╝{Colors.RESET}")
    print(f"{Colors.CYAN}Backend server: http://localhost:{os.getenv('API_PORT', '8001')}{Colors.RESET}")
    if not args.no_frontend:
        print(f"{Colors.CYAN}Frontend server: http://localhost:3000{Colors.RESET}")
    print(f"\n{Colors.YELLOW}Press Ctrl+C to stop the servers{Colors.RESET}")
    
    # Keep the script running until interrupted
    try:
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        print(f"\n{Colors.YELLOW}Shutting down GitEvents...{Colors.RESET}")
        
        # Terminate processes
        if frontend_process:
            frontend_process.terminate()
        if backend_process:
            backend_process.terminate()
        
        print(f"{Colors.GREEN}[OK] GitEvents has been shut down{Colors.RESET}")
    
    return 0

if __name__ == "__main__":
    sys.exit(main())
