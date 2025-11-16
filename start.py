#!/usr/bin/env python3
"""
Mock Interview System - Startup Script
Run this to start the complete application
"""

import subprocess
import sys
import os
import time
import webbrowser
from pathlib import Path

def check_python_version():
    """Check if Python version is compatible"""
    if sys.version_info < (3, 8):
        print("❌ Python 3.8 or higher is required")
        sys.exit(1)
    print(f"✅ Python {sys.version.split()[0]} detected")

def install_dependencies():
    """Install required dependencies"""
    print("📦 Installing dependencies...")
    try:
        subprocess.check_call([sys.executable, "-m", "pip", "install", "-r", "requirements.txt"])
        print("✅ Dependencies installed successfully")
    except subprocess.CalledProcessError:
        print("❌ Failed to install dependencies")
        sys.exit(1)

def setup_environment():
    """Set up environment variables"""
    env_file = Path(".env")
    if not env_file.exists():
        print("📝 Creating .env file...")
        with open(".env", "w") as f:
            f.write("""# Mock Interview System Environment Variables
DATABASE_URL=sqlite:///./mock_interview.db
GEMINI_API_KEY=your_gemini_api_key_here
ADZUNA_APP_ID=your_adzuna_app_id
ADZUNA_APP_KEY=your_adzuna_app_key
HOST=0.0.0.0
PORT=8000
REACT_APP_API_URL=http://localhost:8000
""")
        print("✅ .env file created. Please add your API keys.")
    else:
        print("✅ .env file exists")

def start_backend():
    """Start the FastAPI backend"""
    print("🚀 Starting backend server...")
    backend_path = Path("backend")
    if backend_path.exists():
        os.chdir("backend")
        return subprocess.Popen([sys.executable, "main.py"])
    else:
        print("❌ Backend directory not found")
        return None

def start_frontend():
    """Start the frontend development server"""
    print("🎨 Starting frontend...")
    frontend_path = Path("frontend")
    if frontend_path.exists():
        os.chdir("frontend")
        # Check if node_modules exists
        if not Path("node_modules").exists():
            print("📦 Installing frontend dependencies...")
            subprocess.check_call(["npm", "install"])
        
        return subprocess.Popen(["npm", "start"])
    else:
        print("❌ Frontend directory not found")
        return None

def open_browser():
    """Open the application in browser"""
    print("🌐 Opening application in browser...")
    time.sleep(3)  # Wait for servers to start
    webbrowser.open("http://localhost:3000")

def main():
    """Main startup function"""
    print("🎤 Mock Interview System - Starting...")
    print("=" * 50)
    
    # Change to project root
    os.chdir(Path(__file__).parent)
    
    # Check requirements
    check_python_version()
    
    # Setup environment
    setup_environment()
    
    # Install dependencies
    install_dependencies()
    
    # Start backend
    backend_process = start_backend()
    if not backend_process:
        print("❌ Failed to start backend")
        return
    
    # Go back to root for frontend
    os.chdir(Path(__file__).parent)
    
    # Start frontend
    frontend_process = start_frontend()
    if not frontend_process:
        print("❌ Failed to start frontend")
        backend_process.terminate()
        return
    
    # Open browser
    open_browser()
    
    print("\n🎉 Mock Interview System is running!")
    print("📱 Frontend: http://localhost:3000")
    print("🔧 Backend API: http://localhost:8000")
    print("📚 API Docs: http://localhost:8000/docs")
    print("\nPress Ctrl+C to stop all servers")
    
    try:
        # Wait for user to stop
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        print("\n🛑 Stopping servers...")
        if backend_process:
            backend_process.terminate()
        if frontend_process:
            frontend_process.terminate()
        print("✅ All servers stopped")

if __name__ == "__main__":
    main()
