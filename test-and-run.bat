@echo off
echo ======================================================================
echo   ASANA CLONING AGENT - AUTOMATED TEST SUITE
echo ======================================================================
echo.

cd /d "%~dp0"
set ROOT_DIR=%cd%

echo [1/5] Verifying System...
python agent\verify_system.py
if errorlevel 1 (
    echo [ERROR] System verification failed!
    pause
    exit /b 1
)
echo.

echo [2/5] Running Full Clone Pipeline...
python agent\run_full_clone.py
if errorlevel 1 (
    echo [WARNING] Pipeline had issues, continuing anyway...
)
echo.

echo [3/5] Installing Frontend Dependencies...
cd frontend
if not exist "node_modules" (
    echo Installing npm packages...
    call npm install
) else (
    echo Dependencies already installed, skipping...
)
echo.

echo [4/5] Building Project...
call npm run build
if errorlevel 1 (
    echo [ERROR] Build failed!
    cd ..
    pause
    exit /b 1
)
echo.

echo [5/5] Starting Development Server...
echo.
echo ======================================================================
echo   Server will start at: http://localhost:3000
echo ======================================================================
echo.
echo   Test these pages:
echo   - Home:     http://localhost:3000/
echo   - Projects: http://localhost:3000/projects
echo   - Tasks:    http://localhost:3000/tasks
echo.
echo   Press Ctrl+C to stop the server
echo ======================================================================
echo.

call npm run dev

cd ..
