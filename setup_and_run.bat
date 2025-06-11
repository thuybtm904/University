@echo off
chcp 65001 >nul 2>&1

echo ============================================
echo    SETUP AND RUN DJANGO PROJECT
echo      SQL Server + Existing Database
echo ============================================

echo [1/8] Checking Python installation...
python --version >nul 2>&1
if errorlevel 1 (
    echo ERROR: Python not installed!
    echo Please install Python from: https://www.python.org/downloads/
    pause
    exit /b 1
)
echo SUCCESS: Python is installed

echo [2/8] Removing old virtual environment...
if exist venv (
    rmdir /s /q venv
    echo SUCCESS: Old venv removed
) else (
    echo INFO: No old venv found
)

echo [3/8] Creating new virtual environment...
python -m venv venv
if errorlevel 1 (
    echo ERROR: Cannot create virtual environment!
    pause
    exit /b 1
)
echo SUCCESS: Virtual environment created

echo [4/8] Activating virtual environment...
call venv\Scripts\activate.bat
echo SUCCESS: Virtual environment activated

echo [5/8] Installing packages...
echo Installing Django...
pip install Django==4.2.7 --quiet

echo Installing SQL Server support...
pip install mssql-django==1.5 --quiet

echo Installing pyodbc...
pip install pyodbc --quiet

echo Installing other packages...
pip install pytz requests python-decouple python-dotenv python-dateutil --quiet

echo SUCCESS: All packages installed

echo [6/8] Setting up Django...
echo Applying Django migrations...
python manage.py migrate --run-syncdb

echo [7/8] Creating admin user...
python manage.py createadmin


echo [8/8] Starting Django server...
echo.
echo ============================================
echo               SUCCESS!
echo ============================================
echo.
echo Django Server: http://127.0.0.1:8000
echo Database: SQL Server University
echo.
echo Fixed Issues:
echo [OK] Conversion errors resolved
echo [OK] Encoding issues fixed
echo [OK] Simple queries implemented
echo.
echo Your university data is now accessible!
echo Press Ctrl+C to stop server
echo ============================================

python manage.py runserver
pause
