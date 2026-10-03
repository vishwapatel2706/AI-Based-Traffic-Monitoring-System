#!/bin/bash
# Quick Start Script for Frontend - Linux/Mac
# Run this script to start the React development server

echo ""
echo "================================"
echo " Traffic Vehicle Classifier"
echo " Frontend Start Script"
echo "================================"
echo ""

# Check if Node.js is installed
if ! command -v node &> /dev/null; then
    echo "[ERROR] Node.js is not installed"
    echo "Please install Node.js from https://nodejs.org/"
    exit 1
fi

echo "[INFO] Node.js is installed"
node --version
npm --version

# Check if node_modules exists
if [ ! -d "node_modules" ]; then
    echo "[WARNING] node_modules not found"
    echo "Installing dependencies..."
    npm install
    if [ $? -ne 0 ]; then
        echo "[ERROR] Failed to install dependencies"
        exit 1
    fi
fi

# Check if backend is running
echo ""
echo "[INFO] Checking if backend is running..."
if ! curl -s http://localhost:5000/api/health > /dev/null 2>&1; then
    echo "[WARNING] Backend server is not running"
    echo "Start it in another terminal using: cd backend && python3 app.py"
    echo ""
fi

# Make script executable
chmod +x run.sh 2>/dev/null

# Start React development server
echo ""
echo "================================"
echo "[INFO] Starting React development server..."
echo "================================"
echo ""
echo "Application will open at: http://localhost:3000"
echo "Press Ctrl+C to stop the server"
echo ""

npm start
