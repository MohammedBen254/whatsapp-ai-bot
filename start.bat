@echo off
echo ========================================
echo   WhatsApp AI Bot - Starting...
echo ========================================
echo.

cd /d "%~dp0"

echo [1/2] Starting Python API Server...
start "Python API" cmd /k "cd python && .venv\Scripts\activate && python main.py"

timeout /t 3 /nobreak >nul

echo [2/2] Starting JavaScript Bot...
start "JS Bot" cmd /k "npm start"

echo.
echo Both services starting...
echo Python API: http://127.0.0.1:5000
echo JS Bot: http://localhost:3000
echo.
echo Open http://localhost:3000 to scan QR code
pause
