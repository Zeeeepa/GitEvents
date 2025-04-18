#!/bin/bash
# GitEvents - Deployment Script for Linux/macOS
# This script is a simple wrapper around deploy.py

# Set text colors
GREEN='\033[0;32m'
YELLOW='\033[0;33m'
CYAN='\033[0;36m'
RED='\033[0;31m'
NC='\033[0m' # No Color

# Print banner
echo -e "${CYAN}"
echo -e "╔════════════════════════════════════════════════════╗"
echo -e "║  GitEvents - One-Click Deployment and Startup      ║"
echo -e "╚════════════════════════════════════════════════════╝"
echo -e "${NC}"

# Check if Python is installed
if ! command -v python3 &> /dev/null; then
    echo -e "${RED}[ERROR] Python 3 is not installed or not in PATH${NC}"
    echo "Please install Python 3 from https://www.python.org/downloads/"
    exit 1
fi

# Run the Python deployment script
echo -e "${CYAN}Running deployment script...${NC}"
python3 deploy.py "$@"
