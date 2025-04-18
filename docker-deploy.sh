#!/bin/bash
# GitEvents - Docker Deployment Script
# This script provides a simple way to deploy GitEvents using Docker

# Set text colors
GREEN='\033[0;32m'
YELLOW='\033[0;33m'
CYAN='\033[0;36m'
RED='\033[0;31m'
NC='\033[0m' # No Color

# Print banner
echo -e "${CYAN}"
echo -e "╔════════════════════════════════════════════════════╗"
echo -e "║  GitEvents - Docker Deployment                     ║"
echo -e "╚════════════════════════════════════════════════════╝"
echo -e "${NC}"

# Check if Docker is installed
if ! command -v docker &> /dev/null; then
    echo -e "${RED}[ERROR] Docker is not installed or not in PATH${NC}"
    echo "Please install Docker from https://docs.docker.com/get-docker/"
    exit 1
fi

# Check if Docker Compose is installed
if ! command -v docker-compose &> /dev/null; then
    echo -e "${RED}[ERROR] Docker Compose is not installed or not in PATH${NC}"
    echo "Please install Docker Compose from https://docs.docker.com/compose/install/"
    exit 1
fi

# Check if .env file exists, if not create from example
if [ ! -f .env ]; then
    if [ -f .env.example ]; then
        echo -e "${YELLOW}Creating .env file from .env.example...${NC}"
        cp .env.example .env
        echo -e "${GREEN}[OK] Created .env file from example${NC}"
        echo -e "${YELLOW}[NOTE] Please edit .env file with your configuration${NC}"
    else
        echo -e "${YELLOW}Creating default .env file...${NC}"
        cat > .env << EOL
# GitEvents Environment Variables

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
EOL
        echo -e "${GREEN}[OK] Created default .env file${NC}"
        echo -e "${YELLOW}[NOTE] Please edit .env file with your configuration${NC}"
        
        # Prompt user to edit .env file
        read -p "Do you want to edit the .env file now? (y/N): " -n 1 -r
        echo
        if [[ $REPLY =~ ^[Yy]$ ]]; then
            if command -v nano &> /dev/null; then
                nano .env
            elif command -v vim &> /dev/null; then
                vim .env
            else
                echo -e "${YELLOW}[WARNING] No editor found. Please edit .env file manually.${NC}"
            fi
        fi
    fi
fi

# Create data directory if it doesn't exist
if [ ! -d "data" ]; then
    echo -e "${YELLOW}Creating data directory...${NC}"
    mkdir -p data
    echo -e "${GREEN}[OK] Created data directory${NC}"
fi

# Build and start the containers
echo -e "${CYAN}Building and starting Docker containers...${NC}"
docker-compose up --build -d

# Check if containers are running
if [ $? -eq 0 ]; then
    echo -e "${GREEN}[OK] Docker containers started successfully${NC}"
    echo -e "${CYAN}GitEvents is now running!${NC}"
    echo -e "${CYAN}Backend server: http://localhost:8001${NC}"
    echo -e "${CYAN}Frontend server: http://localhost:3000${NC}"
    
    # Open browser if xdg-open (Linux) or open (macOS) is available
    if command -v xdg-open &> /dev/null; then
        echo -e "${YELLOW}Opening browser...${NC}"
        xdg-open http://localhost:3000
    elif command -v open &> /dev/null; then
        echo -e "${YELLOW}Opening browser...${NC}"
        open http://localhost:3000
    fi
else
    echo -e "${RED}[ERROR] Failed to start Docker containers${NC}"
    echo -e "${YELLOW}Check the logs with: docker-compose logs${NC}"
    exit 1
fi

echo -e "${YELLOW}To stop the containers, run: docker-compose down${NC}"
