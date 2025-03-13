#!/bin/bash

VENV_DIR=".venv"

# Check if virtual environment exists, create if it doesn't
if [ ! -d "$VENV_DIR" ]; then
    echo "Creating virtual environment..."
    python3 -m venv "$VENV_DIR"
    if [ $? -ne 0 ]; then
        echo "Failed to create virtual environment. Is Python 3 installed?"
        exit 1
    fi
    echo "Virtual environment created successfully."
fi

# Activate virtual environment
echo "Activating virtual environment..."
source "$VENV_DIR/bin/activate"
if [ $? -ne 0 ]; then
    echo "Failed to activate virtual environment."
    exit 1
fi

# Install or update requirements
echo "Installing/updating requirements..."

# First try: Standard installation
pip install -r requirements.txt
if [ $? -ne 0 ]; then
    echo "Standard installation failed. Trying alternative approaches..."
    
    # Second try: Install lxml separately with binary wheel
    echo "Attempting to install lxml as binary wheel..."
    pip install --only-binary :all: lxml
    
    # Third try: Install lxml via system package manager if available
    if [ $? -ne 0 ]; then
        echo "Binary wheel installation failed. Checking for system package manager..."
        
        # Check for homebrew (macOS)
        if command -v brew >/dev/null 2>&1; then
            echo "Homebrew detected. Installing libxml2 and libxslt..."
            brew install libxml2 libxslt
            export LDFLAGS="-L/opt/homebrew/lib"
            export CFLAGS="-I/opt/homebrew/include"
            export CPATH="/opt/homebrew/include"
            pip install lxml
        # Check for apt (Debian/Ubuntu)
        elif command -v apt-get >/dev/null 2>&1; then
            echo "apt detected. You may need to run: sudo apt-get install python3-lxml libxml2-dev libxslt1-dev"
            echo "Then try running this script again."
            deactivate
            exit 1
        # Check for dnf/yum (Fedora/RHEL)
        elif command -v dnf >/dev/null 2>&1 || command -v yum >/dev/null 2>&1; then
            echo "dnf/yum detected. You may need to run: sudo dnf install python3-lxml libxml2-devel libxslt-devel"
            echo "Then try running this script again."
            deactivate
            exit 1
        else
            echo "Couldn't determine your system package manager."
            echo "Please install lxml dependencies manually for your system."
            deactivate
            exit 1
        fi
    fi
    
    # Install remaining requirements without dependencies to avoid reinstalling lxml
    echo "Installing remaining requirements..."
    sed '/lxml/d' requirements.txt > requirements_no_lxml.txt
    pip install -r requirements_no_lxml.txt
    rm requirements_no_lxml.txt
    
    # Check if installation was successful
    if [ $? -ne 0 ]; then
        echo "Failed to install requirements after multiple attempts."
        echo "Please check your Python installation and try again."
        deactivate
        exit 1
    fi
fi

# Run the script
echo "Running Upwork Job Search Alerts..."
python upwork-job-search-alerts.py

# Deactivate virtual environment when the script exits
deactivate