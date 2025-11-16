#!/usr/bin/env python3
"""
Simple startup script for Mock Interview AI System
"""
import subprocess
import sys
import os
import time
import webbrowser
from pathlib import Path

def main():
    print("🎤 Mock Interview AI System")
    print("=" * 50)
    
    # Check Python version
    if sys.version_info < (3, 8):
        print("❌ Python 3.8+ required")
        return
    
    print(f"✅ Python {sys.version.split()[0]}")
    
    # Create .env if it doesn't exist
    if not Path(".env").exists():
        print("📝 Creating .env file...")
        with open(".env", "w") as f:
            f.write("""# Mock Interview AI System Environment Variables
DATABASE_URL=sqlite:///./mock_interview.db
OPENAI_API_KEY=your_openai_api_key_here
SECRET_KEY=your-secret-key-change-in-production
DEBUG=True
HOST=0.0.0.0
PORT=8000
""")
        print("✅ .env file created")
    
    # Install backend dependencies
    print("📦 Installing Python dependencies...")
    try:
        subprocess.check_call([
            sys.executable, "-m", "pip", "install", 
            "fastapi", "uvicorn[standard]", "sqlalchemy", 
            "python-multipart", "python-dotenv", "pydantic",
            "python-jose[cryptography]", "passlib[bcrypt]"
        ])
        print("✅ Dependencies installed")
    except subprocess.CalledProcessError:
        print("❌ Failed to install dependencies")
        return
    
    # Start backend
    print("🚀 Starting backend server...")
    try:
        os.chdir("backend")
        backend_process = subprocess.Popen([
            sys.executable, "-m", "uvicorn", "app.main:app", 
            "--reload", "--host", "0.0.0.0", "--port", "8000"
        ])
        
        time.sleep(3)
        
        print("\n🎉 Mock Interview System is running!")
        print("📱 Backend API: http://localhost:8000")
        print("📚 API Docs: http://localhost:8000/docs")
        print("\nPress Ctrl+C to stop")
        
        # Open browser
        webbrowser.open("http://localhost:8000/docs")
        
        # Wait for process
        backend_process.wait()
        
    except KeyboardInterrupt:
        print("\n🛑 Stopping server...")
        backend_process.terminate()
    except Exception as e:
        print(f"❌ Error: {e}")

if __name__ == "__main__":
    main()








