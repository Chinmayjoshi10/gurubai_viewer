#!/bin/bash

# Exit on error
set -e

# Check if virtual environment exists
if [ ! -d "venv" ]; then
    echo "Creating virtual environment..."
    python3 -m venv venv
fi

# Activate virtual environment
source venv/bin/activate

# Upgrade pip
pip install --upgrade pip

# Install requirements
echo "Installing requirements..."
pip install -r requirements.txt

# Create assets directory if it doesn't exist
mkdir -p assets

# Create executable with PyInstaller
echo "Building executable..."
pyinstaller --onefile \
    --name gurbani-viewer \
    --icon=assets/icon.ico \
    --add-data "src/*:src" \
    --hidden-import=banidb \
    src/main.py

# Make executable
chmod +x dist/gurbani-viewer

echo "Build completed successfully!" 
echo "Executable created at: $(pwd)/dist/gurbani-viewer" 