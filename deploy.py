# deploy.py - One-click deployment script
import os
import sys
import subprocess
import webbrowser

def check_python():
    """Check Python version"""
    print("Checking Python version...")
    version = sys.version_info
    if version.major < 3 or (version.major == 3 and version.minor < 8):
        print("Error: Python 3.8 or higher is required")
        return False
    print(f"✓ Python {version.major}.{version.minor}.{version.micro} detected")
    return True

def install_requirements():
    """Install required packages"""
    print("\nInstalling requirements...")
    try:
        subprocess.check_call([sys.executable, "-m", "pip", "install", "-r", "requirements.txt"])
        print("✓ Requirements installed successfully")
        return True
    except subprocess.CalledProcessError:
        print("Error: Failed to install requirements")
        return False

def seed_database():
    """Seed the database with sample data"""
    print("\nSeeding database...")
    try:
        subprocess.check_call([sys.executable, "seed_data.py"])
        print("✓ Database seeded successfully")
        return True
    except subprocess.CalledProcessError:
        print("Error: Failed to seed database")
        return False

def start_application():
    """Start the Flask application"""
    print("\nStarting DL Farm Management System...")
    print("=" * 50)
    print("System is now running!")
    print("Open your browser and go to: http://localhost:5000")
    print("Default login: admin / admin123")
    print("Press Ctrl+C to stop the server")
    print("=" * 50)
    
    # Open browser automatically
    webbrowser.open('http://localhost:5000')
    
    # Start Flask application
    os.system(f'"{sys.executable}" app.py')

def main():
    """Main deployment function"""
    print("DL Farm Management System - Deployment")
    print("=" * 50)
    
    # Step 1: Check Python
    if not check_python():
        sys.exit(1)
    
    # Step 2: Install requirements
    if not install_requirements():
        sys.exit(1)
    
    # Step 3: Seed database
    if not seed_database():
        print("Note: Continuing without database seed...")
    
    # Step 4: Start application
    start_application()

if __name__ == "__main__":
    main()