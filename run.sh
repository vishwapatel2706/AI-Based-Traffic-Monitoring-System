#!/bin/bash
# Quick Start Script for Backend - Linux/Mac
# Run this script to automatically start the backend server

echo ""
echo "================================"
echo " Traffic Vehicle Classifier"
echo " Backend Start Script"
echo "================================"
echo ""

# Check if Python is installed
if ! command -v python3 &> /dev/null; then
    echo "[ERROR] Python 3 is not installed"
    echo "Please install Python 3.8 or higher"
    exit 1
fi

echo "[INFO] Python is installed"
python3 --version

# Check if models folder exists
if [ ! -d "models" ]; then
    echo "[WARNING] models folder not found"
    echo "Creating models folder..."
    mkdir -p models
fi

# Check if model files exist
if [ ! -f "models/traffic_model.keras" ]; then
    echo "[ERROR] models/traffic_model.keras not found"
    echo "Please download from Google Drive and place in models/ folder"
fi

if [ ! -f "models/label_encoder.pkl" ]; then
    echo "[ERROR] models/label_encoder.pkl not found"
    echo "Please download from Google Drive and place in models/ folder"
fi

# Check if uploads folder exists
if [ ! -d "uploads" ]; then
    echo "[INFO] Creating uploads folder..."
    mkdir -p uploads
fi

# Check if requirements are installed
echo ""
echo "[INFO] Checking if dependencies are installed..."
python3 -c "import flask" 2>/dev/null
if [ $? -ne 0 ]; then
    echo "[WARNING] Dependencies not installed"
    echo "Installing requirements..."
    pip3 install -r requirements.txt
    if [ $? -ne 0 ]; then
        echo "[ERROR] Failed to install requirements"
        exit 1
    fi
fi

# Make script executable
chmod +x run.sh 2>/dev/null

# Start Flask server
echo ""
echo "================================"
echo "[INFO] Starting Flask server..."
echo "================================"
echo ""
echo "Server will run at: http://localhost:5000"
echo "Press Ctrl+C to stop the server"
echo ""

python3 app.py
