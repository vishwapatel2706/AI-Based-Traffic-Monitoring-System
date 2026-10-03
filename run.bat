@echo off
REM Quick Start Script for Frontend - Windows
REM Run this script to start the React development server

echo.
echo ================================
echo  Traffic Vehicle Classifier
echo  Frontend Start Script
echo ================================
echo.

REM Check if Node.js is installed
node --version >nul 2>&1
if errorlevel 1 (
    echo [ERROR] Node.js is not installed or not in PATH
    echo Please install Node.js from https://nodejs.org/
    pause
    exit /b 1
)

echo [INFO] Node.js is installed
node --version
npm --version

REM Check if node_modules exists
if not exist "node_modules" (
    echo [WARNING] node_modules not found
    echo Installing dependencies...
    call npm install
    if errorlevel 1 (
        echo [ERROR] Failed to install dependencies
        pause
        exit /b 1
    )
)

REM Check if backend is running
echo.
echo [INFO] Checking if backend is running...
curl -s http://localhost:5000/api/health >nul 2>&1
if errorlevel 1 (
    echo [WARNING] Backend server is not running
    echo Start it in another terminal using: cd backend ^&^& python app.py
    echo.
)

REM Start React development server
echo.
echo ================================
echo [INFO] Starting React development server...
echo ================================
echo.
echo Application will open at: http://localhost:3000
echo Press Ctrl+C to stop the server
echo.

call npm start

pause
