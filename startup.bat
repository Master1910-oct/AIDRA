@echo off
REM AIDRA Quick Start Script for Windows
REM This script sets up and launches the AIDRA system

echo.
echo ========================================
echo   AIDRA - Flood Intelligence System
echo ========================================
echo.

REM Check Python installation
python --version >nul 2>&1
if errorlevel 1 (
    echo ERROR: Python not found. Please install Python 3.8+
    echo Visit: https://www.python.org/downloads/
    pause
    exit /b 1
)

echo [1/4] Creating virtual environment...
if not exist venv (
    python -m venv venv
    echo ✓ Virtual environment created
) else (
    echo ✓ Virtual environment already exists
)

echo.
echo [2/4] Activating virtual environment...
call venv\Scripts\activate.bat
echo ✓ Virtual environment activated

echo.
echo [3/4] Installing dependencies...
pip install -q -r requirements.txt
if errorlevel 1 (
    echo ERROR: Failed to install dependencies
    pause
    exit /b 1
)
echo ✓ Dependencies installed

echo.
echo [4/4] Running system tests...
python test_pipeline.py >nul 2>&1
if errorlevel 1 (
    echo WARNING: Some tests failed. System may not work correctly.
    echo Run 'python test_pipeline.py' for details
    pause
) else (
    echo ✓ All tests passed
)

echo.
echo ========================================
echo   Starting AIDRA Dashboard...
echo ========================================
echo.
echo Opening browser to http://localhost:8501
echo Press Ctrl+C to stop the server
echo.

streamlit run app.py

pause
