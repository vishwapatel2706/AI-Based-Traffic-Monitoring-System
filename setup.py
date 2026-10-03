#!/usr/bin/env python3
"""
Setup script for Traffic Vehicle Classifier Backend
Run this script to automatically set up the backend environment
"""

import os
import sys
import subprocess

def print_header(text):
    """Print a formatted header"""
    print("\n" + "=" * 60)
    print(f"  {text}")
    print("=" * 60 + "\n")

def print_success(text):
    """Print success message"""
    print(f"✅ {text}")

def print_error(text):
    """Print error message"""
    print(f"❌ {text}")

def print_warning(text):
    """Print warning message"""
    print(f"⚠️  {text}")

def print_info(text):
    """Print info message"""
    print(f"ℹ️  {text}")

def create_models_folder():
    """Create models folder if it doesn't exist"""
    print_header("Setting up Models Folder")
    
    models_dir = os.path.join(os.path.dirname(__file__), 'models')
    
    if os.path.exists(models_dir):
        print_warning("Models folder already exists")
        return models_dir
    
    os.makedirs(models_dir, exist_ok=True)
    print_success(f"Created models folder at: {models_dir}")
    return models_dir

def check_model_files(models_dir):
    """Check if model files exist"""
    print_header("Checking Model Files")
    
    required_files = ['traffic_model.keras', 'label_encoder.pkl']
    missing_files = []
    
    for file in required_files:
        file_path = os.path.join(models_dir, file)
        if os.path.exists(file_path):
            print_success(f"Found: {file}")
        else:
            print_error(f"Missing: {file}")
            missing_files.append(file)
    
    if missing_files:
        print_warning(f"\nMissing {len(missing_files)} file(s):")
        for f in missing_files:
            print(f"  - {f}")
        print_info("Please download these files from Google Drive and place them in:")
        print(f"  {models_dir}/")
        return False
    
    return True

def install_requirements():
    """Install Python requirements"""
    print_header("Installing Python Dependencies")
    
    requirements_file = os.path.join(os.path.dirname(__file__), 'requirements.txt')
    
    if not os.path.exists(requirements_file):
        print_error(f"requirements.txt not found at {requirements_file}")
        return False
    
    print_info("This may take a few minutes on first install...")
    print_info("(Installing: Flask, TensorFlow, OpenCV, etc.)\n")
    
    try:
        # Check Python version
        python_version = sys.version_info
        if python_version.major < 3 or (python_version.major == 3 and python_version.minor < 8):
            print_error(f"Python 3.8+ required. You have {python_version.major}.{python_version.minor}")
            return False
        
        print_info(f"Using Python {python_version.major}.{python_version.minor}.{python_version.micro}")
        
        # Install requirements
        subprocess.check_call([sys.executable, '-m', 'pip', 'install', '-r', requirements_file])
        print_success("All dependencies installed successfully!")
        return True
        
    except subprocess.CalledProcessError as e:
        print_error(f"Failed to install dependencies: {e}")
        return False
    except Exception as e:
        print_error(f"Error during installation: {e}")
        return False

def create_uploads_folder():
    """Create uploads folder for storing uploaded images"""
    print_header("Setting up Uploads Folder")
    
    uploads_dir = os.path.join(os.path.dirname(__file__), 'uploads')
    os.makedirs(uploads_dir, exist_ok=True)
    print_success(f"Uploads folder ready at: {uploads_dir}")

def print_summary():
    """Print setup summary"""
    print_header("Setup Summary")
    
    print("Backend setup is complete! Here's what was done:\n")
    print("✓ Created models folder")
    print("✓ Verified model files (or warned about missing files)")
    print("✓ Installed Python dependencies")
    print("✓ Created uploads folder\n")
    
    print("Next steps:")
    print("1. If model files were missing, download them from Google Drive")
    print("2. Place them in the 'models' folder:")
    print("   - traffic_model.keras")
    print("   - label_encoder.pkl")
    print("3. Run the Flask server:")
    print("   python app.py")
    print("\nFor more details, see README.md")

def main():
    """Main setup function"""
    print_header("Traffic Vehicle Classifier - Backend Setup")
    print_info("This script will set up your backend environment\n")
    
    # Step 1: Create models folder
    models_dir = create_models_folder()
    
    # Step 2: Check model files
    models_ready = check_model_files(models_dir)
    
    if not models_ready:
        print_warning("Model files are missing!")
        print_info("You can continue with setup and add model files later.")
        response = input("\nContinue anyway? (y/n): ").strip().lower()
        if response != 'y':
            print_error("Setup cancelled.")
            return False
    
    # Step 3: Install requirements
    success = install_requirements()
    if not success:
        print_error("Setup failed during dependency installation")
        return False
    
    # Step 4: Create uploads folder
    create_uploads_folder()
    
    # Step 5: Print summary
    print_summary()
    
    print("\n🎉 Backend setup completed successfully!\n")
    return True

if __name__ == '__main__':
    try:
        success = main()
        sys.exit(0 if success else 1)
    except KeyboardInterrupt:
        print("\n\n⚠️  Setup cancelled by user")
        sys.exit(1)
    except Exception as e:
        print(f"\n\n❌ Unexpected error: {e}")
        sys.exit(1)
