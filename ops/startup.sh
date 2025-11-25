#!/bin/bash
# ForgeWeb - Unified Management Script
# Handles setup, start, stop, and restart operations

set -e  # Exit on error

# Colors for pretty output
GREEN='\033[0;32m'
BLUE='\033[0;34m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
NC='\033[0m' # No Color

# Script directory (forgeweb root)
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
cd "$SCRIPT_DIR"

# Function to show usage
show_usage() {
    echo -e "${BLUE}"
    echo "╔═══════════════════════════════════════════════════════╗"
    echo "║                                                       ║"
    echo "║              🚀  ForgeWeb Manager  🚀                 ║"
    echo "║                                                       ║"
    echo "║          Easy Website Builder for GitHub Pages       ║"
    echo "║                                                       ║"
    echo "╚═══════════════════════════════════════════════════════╝"
    echo -e "${NC}"
    echo ""
    echo "Usage: $0 [command]"
    echo ""
    echo "Commands:"
    echo "  start     Start ForgeWeb server (default)"
    echo "  stop      Stop ForgeWeb server"
    echo "  restart   Restart ForgeWeb server"
    echo "  setup     Run initial setup only"
    echo "  status    Show server status"
    echo "  help      Show this help message"
    echo ""
    echo "Examples:"
    echo "  $0              # Start server (with setup if needed)"
    echo "  $0 start        # Same as above"
    echo "  $0 stop         # Stop server"
    echo "  $0 restart      # Restart server"
    echo "  $0 setup        # Run setup only"
    echo ""
}

# Function to check if server is running
is_server_running() {
    lsof -Pi :8000 -sTCP:LISTEN -t >/dev/null 2>&1
}

# Function to get server PID
get_server_pid() {
    lsof -Pi :8000 -sTCP:LISTEN -t 2>/dev/null || echo ""
}

# Function to stop server
stop_server() {
    local pid=$(get_server_pid)
    if [ -n "$pid" ]; then
        echo -e "${BLUE}Stopping ForgeWeb server (PID: $pid)...${NC}"
        kill "$pid" 2>/dev/null || true
        sleep 2
        if is_server_running; then
            echo -e "${YELLOW}Force stopping server...${NC}"
            kill -9 "$pid" 2>/dev/null || true
            sleep 1
        fi
        if ! is_server_running; then
            echo -e "${GREEN}✓${NC} Server stopped"
        else
            echo -e "${RED}❌ Failed to stop server${NC}"
            return 1
        fi
    else
        echo -e "${YELLOW}⚠️${NC} Server is not running"
    fi
}

# Function to check system requirements
check_requirements() {
    echo -e "${BLUE}Checking system requirements...${NC}"

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
    PYTHON_VERSION=$(python3 --version 2>&1 | awk '{print $2}' | cut -d. -f1-2)
    PYTHON_MAJOR=$(echo "$PYTHON_VERSION" | cut -d. -f1)
    PYTHON_MINOR=$(echo "$PYTHON_VERSION" | cut -d. -f2)

    if [ "$PYTHON_MAJOR" -lt 3 ] || ([ "$PYTHON_MAJOR" -eq 3 ] && [ "$PYTHON_MINOR" -lt 8 ]); then
        echo -e "${RED}❌ Python version $PYTHON_VERSION is too old!${NC}"
        echo "ForgeWeb requires Python 3.8 or higher."
        echo "Please upgrade your Python installation."
        exit 1
    fi

    echo -e "${GREEN}✓${NC} Found Python $PYTHON_VERSION"
}

# Function to setup environment
setup_environment() {
    echo -e "${YELLOW}📦 Setting up ForgeWeb environment...${NC}"
    echo ""

    # Create virtual environment if it doesn't exist
    if [ ! -d "venv" ]; then
        echo -e "${BLUE}Creating virtual environment...${NC}"
        python3 -m venv venv
        echo -e "${GREEN}✓${NC} Virtual environment created"
    fi

    # Activate virtual environment
    source venv/bin/activate

    # Upgrade pip if needed
    echo -e "${BLUE}Ensuring pip is up to date...${NC}"
    pip install --upgrade pip --quiet
    echo -e "${GREEN}✓${NC} Pip is ready"

    # Install/update dependencies
    echo -e "${BLUE}Installing/updating required packages...${NC}"
    echo "  - requests (for API calls)"
    echo "  - python-dotenv (for configuration)"
    echo "  - pillow (for image processing)"
    echo "  - jinja2 (for template rendering)"
    pip install requests python-dotenv pillow jinja2 --quiet
    echo -e "${GREEN}✓${NC} All packages installed"

    # Create necessary directories
    echo -e "${BLUE}Creating project directories...${NC}"
    mkdir -p assets/images assets/css assets/js
    mkdir -p templates
    mkdir -p uploads
    mkdir -p user_assets
    echo -e "${GREEN}✓${NC} Directories ready"

    # Initialize database if needed
    if [ ! -f "admin/database.db" ] && [ -f "admin/database.py" ]; then
        echo -e "${BLUE}Initializing database...${NC}"
        python3 admin/database.py
        echo -e "${GREEN}✓${NC} Database ready"
    fi

    # Create .env file if it doesn't exist
    if [ ! -f ".env" ]; then
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

    echo -e "${GREEN}╔═══════════════════════════════════════════════════════╗${NC}"
    echo -e "${GREEN}║                                                       ║${NC}"
    echo -e "${GREEN}║              ✨  Setup Complete!  ✨                  ║${NC}"
    echo -e "${GREEN}║                                                       ║${NC}"
    echo -e "${GREEN}╚═══════════════════════════════════════════════════════╝${NC}"
    echo ""
}

# Function to start server
start_server() {
    # Check if server is already running
    if is_server_running; then
        echo -e "${YELLOW}⚠️  ForgeWeb server is already running!${NC}"
        echo ""
        echo "Access it at: http://localhost:8000/admin/"
        echo ""
        read -p "Do you want to restart it? (y/n) " -n 1 -r
        echo ""
        if [[ $REPLY =~ ^[Yy]$ ]]; then
            stop_server
            sleep 1
        else
            exit 0
        fi
    fi

    # Check if file-api.py exists
    if [ ! -f "admin/file-api.py" ]; then
        echo -e "${RED}❌ Error: admin/file-api.py not found!${NC}"
        echo "Make sure you're running this script from the ForgeWeb directory."
        exit 1
    fi

    echo -e "${BLUE}🚀 Starting ForgeWeb server...${NC}"
    echo ""

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
    echo "  • Use '$0 stop' to stop the server"
    echo ""
    echo -e "${BLUE}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
    echo ""

    # Start the server
    cd admin
    python3 file-api.py &
    SERVER_PID=$!

    # Wait a moment for server to start
    sleep 2

    if kill -0 $SERVER_PID 2>/dev/null; then
        echo -e "${GREEN}✓${NC} Server started successfully (PID: $SERVER_PID)"
        echo ""
        echo "Press Ctrl+C to stop the server"
        wait $SERVER_PID
    else
        echo -e "${RED}❌ Failed to start server${NC}"
        exit 1
    fi
}

# Function to show status
show_status() {
    if is_server_running; then
        local pid=$(get_server_pid)
        echo -e "${GREEN}✓${NC} ForgeWeb server is running (PID: $pid)"
        echo "  Access at: http://localhost:8000/admin/"
    else
        echo -e "${RED}❌${NC} ForgeWeb server is not running"
        echo "  Use '$0 start' to start it"
    fi
}

# Main script logic
COMMAND=${1:-start}

case $COMMAND in
    start)
        check_requirements
        setup_environment
        start_server
        ;;
    stop)
        stop_server
        ;;
    restart)
        stop_server
        sleep 1
        check_requirements
        setup_environment
        start_server
        ;;
    setup)
        check_requirements
        setup_environment
        echo -e "${GREEN}Setup complete! Use '$0 start' to start the server.${NC}"
        ;;
    status)
        show_status
        ;;
    help|--help|-h)
        show_usage
        ;;
    *)
        echo -e "${RED}❌ Unknown command: $COMMAND${NC}"
        echo ""
        show_usage
        exit 1
        ;;
esac