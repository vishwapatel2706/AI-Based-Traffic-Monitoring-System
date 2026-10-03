@echo off
REM Quick Start Script for Backend - Windows
REM Run this script to automatically start the backend server

echo.
echo ================================
echo  Traffic Vehicle Classifier
echo  Backend Start Script
echo ================================
echo.

REM Check if Python is installed
python --version >nul 2>&1
if errorlevel 1 (
    echo [ERROR] Python is not installed or not in PATH
    echo Please install Python 3.8 or higher
    pause
    exit /b 1
)

echo [INFO] Python is installed
python --version

REM Check if models folder exists
if not exist "models" (
    echo [WARNING] models folder not found
    echo Creating models folder...
    mkdir models
)

REM Check if model files exist
if not exist "models\traffic_model.keras" (
    echo [ERROR] models/traffic_model.keras not found
    echo Please download from Google Drive and place in models/ folder
)

if not exist "models\label_encoder.pkl" (
    echo [ERROR] models/label_encoder.pkl not found
    echo Please download from Google Drive and place in models/ folder
)

REM Check if uploads folder exists
if not exist "uploads" (
    echo [INFO] Creating uploads folder...
    mkdir uploads
)

REM Check if requirements are installed
echo.
echo [INFO] Checking if dependencies are installed...
python -c "import flask" >nul 2>&1
if errorlevel 1 (
    echo [WARNING] Dependencies not installed
    echo Installing requirements...
    pip install -r requirements.txt
    if errorlevel 1 (
        echo [ERROR] Failed to install requirements
        pause
        exit /b 1
    )
)

REM Start Flask server
echo.
echo ================================
echo [INFO] Starting Flask server...
echo ================================
echo.
echo Server will run at: http://localhost:5000
echo Press Ctrl+C to stop the server
echo.

python app.py

pause
