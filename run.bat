@echo off
TITLE SnapTubeX Downloader Server
COLOR 0A
echo ========================================================
echo       Starting SnapTubeX Video Downloader Server...
echo ========================================================
echo.

python --version >nul 2>&1
if errorlevel 1 (
    echo [ERROR] Python is not installed or not added to PATH.
    echo Please install Python from https://www.python.org/ and try again.
    pause
    exit /b
)

echo [1/4] Installing / Upgrading Python dependencies (yt-dlp)...
pip install -r requirements.txt --upgrade --quiet

echo [2/4] Ensuring yt-dlp is latest version...
pip install --upgrade yt-dlp --quiet

echo [3/4] Starting Flask server...
start /b python app.py

echo [4/4] Opening browser at http://127.0.0.1:5000 ...
timeout /t 2 >nul
start http://127.0.0.1:5000

echo.
echo ========================================================
echo   Server is running! Keep this window open while downloading.
echo   To stop the server, press Ctrl+C or close this window.
echo ========================================================
echo.
pause
