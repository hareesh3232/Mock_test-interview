@echo off
echo 🎤 Mock Interview System - Starting...
echo ================================

:: Check if Python is installed
python --version >nul 2>&1
if errorlevel 1 (
    echo ❌ Python is not installed or not in PATH
    echo Please install Python 3.8+ and try again
    pause
    exit /b 1
)

:: Create .env file if it doesn't exist
if not exist .env (
    echo 📝 Creating .env file...
    copy env.example .env
    echo ✅ .env file created. Please add your API keys.
)

:: Install Python dependencies
echo 📦 Installing Python dependencies...
pip install -r requirements.txt
if errorlevel 1 (
    echo ❌ Failed to install Python dependencies
    pause
    exit /b 1
)

:: Start backend server
echo 🚀 Starting backend server...
start "Backend Server" cmd /k "cd backend && python main.py"

:: Wait a bit for backend to start
timeout /t 3 /nobreak >nul

:: Check if Node.js is installed
node --version >nul 2>&1
if errorlevel 1 (
    echo ❌ Node.js is not installed
    echo Opening browser with simple HTML interface...
    start frontend_test.html
    echo ✅ Backend running on http://localhost:8000
    echo 📚 API docs: http://localhost:8000/docs
    pause
    exit /b 0
)

:: Install frontend dependencies and start
if exist frontend\node_modules (
    echo ✅ Frontend dependencies already installed
) else (
    echo 📦 Installing frontend dependencies...
    cd frontend
    npm install
    if errorlevel 1 (
        echo ❌ Failed to install frontend dependencies
        cd ..
        echo Opening browser with simple HTML interface...
        start frontend_test.html
        pause
        exit /b 0
    )
    cd ..
)

:: Start frontend
echo 🎨 Starting frontend server...
start "Frontend Server" cmd /k "cd frontend && npm start"

:: Wait for servers to start
timeout /t 5 /nobreak >nul

echo.
echo 🎉 Mock Interview System is running!
echo ================================
echo 📱 Frontend: http://localhost:3000
echo 🔧 Backend API: http://localhost:8000  
echo 📚 API Docs: http://localhost:8000/docs
echo.
echo Press any key to open the application...
pause >nul

:: Open application in browser
start http://localhost:3000

echo.
echo ✅ Application opened in browser
echo Press any key to exit...
pause >nul
