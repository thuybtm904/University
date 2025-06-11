@echo off
chcp 65001 >nul 2>&1

echo ============================================
echo         RUN DJANGO SERVER
echo ============================================

echo Activating virtual environment...
if exist venv\Scripts\activate.bat (
    call venv\Scripts\activate.bat
    echo SUCCESS: Virtual environment activated
) else (
    echo ERROR: Virtual environment not found!
    echo Please run setup_and_run.bat first
    pause
    exit /b 1
)

echo Starting Django development server...
echo.
echo Django Server: http://127.0.0.1:8000
echo Press Ctrl+C to stop server
echo ============================================

python manage.py runserver
pause
