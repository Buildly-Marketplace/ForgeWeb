#!/bin/bash
# ForgeWeb - Easy Start Script
# This script sets up and starts ForgeWeb automatically

set -e  # Exit on error

# Colors for pretty output
GREEN='\033[0;32m'
BLUE='\033[0;34m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
NC='\033[0m' # No Color

# Script directory
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
cd "$SCRIPT_DIR"

echo -e "${BLUE}"
echo "╔═══════════════════════════════════════════════════════╗"
echo "║                                                       ║"
echo "║              🚀  ForgeWeb Startup Wizard  🚀          ║"
echo "║                                                       ║"
echo "║          Easy Website Builder for GitHub Pages       ║"
echo "║                                                       ║"
echo "╚═══════════════════════════════════════════════════════╝"
echo -e "${NC}"
echo ""

# Check if Python 3 is installed
if ! command -v python3 &> /dev/null; then
    echo -e "${RED}❌ Python 3 is not installed!${NC}"
    echo ""
    echo "Please install Python 3.8 or higher:"
    echo "  - Ubuntu/Debian: sudo apt install python3 python3-pip python3-venv"
    echo "  - macOS: brew install python3"
    echo "  - Windows: Download from https://www.python.org/downloads/"
    echo ""
    exit 1
fi

# Check Python version
PYTHON_VERSION=$(python3 --version 2>&1 | grep -oP '\d+\.\d+' | head -1)
PYTHON_MAJOR=$(echo "$PYTHON_VERSION" | cut -d. -f1)
PYTHON_MINOR=$(echo "$PYTHON_VERSION" | cut -d. -f2)

if [ "$PYTHON_MAJOR" -lt 3 ] || ([ "$PYTHON_MAJOR" -eq 3 ] && [ "$PYTHON_MINOR" -lt 8 ]); then
    echo -e "${RED}❌ Python version $PYTHON_VERSION is too old!${NC}"
    echo "ForgeWeb requires Python 3.8 or higher."
    echo "Please upgrade your Python installation."
    exit 1
fi

echo -e "${GREEN}✓${NC} Found Python $PYTHON_VERSION"

# Check if virtual environment exists
if [ ! -d "venv" ]; then
    echo ""
    echo -e "${YELLOW}📦 Setting up ForgeWeb for the first time...${NC}"
    echo ""
    
    # Create virtual environment
    echo -e "${BLUE}Creating virtual environment...${NC}"
    python3 -m venv venv
    echo -e "${GREEN}✓${NC} Virtual environment created"
    
    # Activate virtual environment
    source venv/bin/activate
    
    # Upgrade pip
    echo ""
    echo -e "${BLUE}Upgrading pip...${NC}"
    pip install --upgrade pip --quiet
    echo -e "${GREEN}✓${NC} Pip upgraded"
    
    # Install dependencies
    echo ""
    echo -e "${BLUE}Installing required packages...${NC}"
    echo "  - requests (for API calls)"
    echo "  - python-dotenv (for configuration)"
    echo "  - pillow (for image processing)"
    echo "  - jinja2 (for template rendering)"
    pip install requests python-dotenv pillow jinja2 --quiet
    echo -e "${GREEN}✓${NC} All packages installed"
    
    # Create necessary directories
    echo ""
    echo -e "${BLUE}Creating project directories...${NC}"
    mkdir -p assets/images assets/css assets/js
    mkdir -p templates
    mkdir -p uploads
    mkdir -p user_assets
    echo -e "${GREEN}✓${NC} Directories created"
    
    # Initialize database
    echo ""
    echo -e "${BLUE}Initializing database...${NC}"
    python3 admin/database.py
    echo -e "${GREEN}✓${NC} Database ready"
    
    # Create .env file if it doesn't exist
    if [ ! -f ".env" ]; then
        echo ""
        echo -e "${BLUE}Creating configuration file...${NC}"
        cat > .env << 'EOF'
# ForgeWeb Configuration
# You can edit these settings later if needed

# Server settings
PORT=8000
HOST=localhost

# GitHub Integration (optional - fill in if you want to deploy to GitHub Pages)
GITHUB_TOKEN=
GITHUB_REPO=
GITHUB_BRANCH=gh-pages

# AI Integration (optional - fill in if you want AI writing assistance)
OPENAI_API_KEY=
ANTHROPIC_API_KEY=
EOF
        echo -e "${GREEN}✓${NC} Configuration file created (.env)"
    fi
    
    echo ""
    echo -e "${GREEN}╔═══════════════════════════════════════════════════════╗${NC}"
    echo -e "${GREEN}║                                                       ║${NC}"
    echo -e "${GREEN}║              ✨  Setup Complete!  ✨                  ║${NC}"
    echo -e "${GREEN}║                                                       ║${NC}"
    echo -e "${GREEN}╚═══════════════════════════════════════════════════════╝${NC}"
    echo ""
else
    echo -e "${GREEN}✓${NC} ForgeWeb environment ready"
    echo ""
    
    # Activate existing virtual environment
    source venv/bin/activate
fi

# Check if server is already running
if lsof -Pi :8000 -sTCP:LISTEN -t >/dev/null 2>&1 ; then
    echo -e "${YELLOW}⚠️  Port 8000 is already in use!${NC}"
    echo ""
    echo "ForgeWeb server may already be running."
    echo ""
    read -p "Do you want to stop it and restart? (y/n) " -n 1 -r
    echo ""
    if [[ $REPLY =~ ^[Yy]$ ]]; then
        echo -e "${BLUE}Stopping existing server...${NC}"
        # Kill process on port 8000
        kill $(lsof -t -i:8000) 2>/dev/null || true
        sleep 2
        echo -e "${GREEN}✓${NC} Server stopped"
    else
        echo ""
        echo "Keeping existing server running."
        echo "Access ForgeWeb at: http://localhost:8000/admin/"
        exit 0
    fi
fi

# Start the server
echo ""
echo -e "${BLUE}🚀 Starting ForgeWeb server...${NC}"
echo ""

# Check if file-api.py exists
if [ ! -f "admin/file-api.py" ]; then
    echo -e "${RED}❌ Error: admin/file-api.py not found!${NC}"
    echo "Make sure you're running this script from the ForgeWeb directory."
    exit 1
fi

echo -e "${GREEN}╔═══════════════════════════════════════════════════════╗${NC}"
echo -e "${GREEN}║                                                       ║${NC}"
echo -e "${GREEN}║              🎉  ForgeWeb is Running!  🎉             ║${NC}"
echo -e "${GREEN}║                                                       ║${NC}"
echo -e "${GREEN}╚═══════════════════════════════════════════════════════╝${NC}"
echo ""
echo -e "${BLUE}📍 Open your web browser and go to:${NC}"
echo ""
echo -e "    ${YELLOW}http://localhost:8000/admin/${NC}"
echo ""
echo -e "${BLUE}💡 Tips:${NC}"
echo "  • The admin interface will open where you can build your site"
echo "  • All changes are saved automatically"
echo "  • Press Ctrl+C to stop the server when you're done"
echo ""
echo -e "${BLUE}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
echo ""

# Start the server
cd admin
python3 file-api.py

# This will run when server stops
echo ""
echo -e "${YELLOW}👋 ForgeWeb server stopped.${NC}"
echo ""
echo "To start again, just run: ./start.sh"
echo ""
