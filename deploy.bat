@echo off
REM AlignCV Deployment Script for Windows
REM Optimized for production deployment

echo 🚀 Starting AlignCV Deployment Process
echo ======================================

REM Check if we're in the right directory
if not exist "frontend\app_v2.py" (
    echo ❌ Error: frontend\app_v2.py not found!
    echo    Please run this script from the project root directory
    pause
    exit /b 1
)

REM Set environment variables for optimization
set STREAMLIT_SERVER_FILE_WATCHER_TYPE=none
set STREAMLIT_SERVER_ENABLE_CORS=false
set STREAMLIT_SERVER_ENABLE_XSRF_PROTECTION=false
set STREAMLIT_BROWSER_GATHER_USAGE_STATS=false
set STREAMLIT_LOGGER_LEVEL=error

echo ⚙️  Setting up optimized environment...

REM Install dependencies
echo 📦 Installing optimized dependencies...
pip install -r requirements_optimized.txt

REM Check if installation was successful
if %errorlevel% neq 0 (
    echo ❌ Failed to install dependencies
    pause
    exit /b 1
)

echo ✅ Dependencies installed successfully

REM Test the application
echo 🧪 Testing application...
python -c "import streamlit; print('Streamlit version:', streamlit.__version__)"

REM Start the application
echo 🚀 Starting AlignCV application...
echo    URL: http://localhost:8501
echo    Press Ctrl+C to stop
echo.

streamlit run frontend\app_v2.py ^
    --server.fileWatcherType none ^
    --server.enableCORS false ^
    --server.enableXsrfProtection false ^
    --browser.gatherUsageStats false ^
    --logger.level error ^
    --server.port 8501 ^
    --server.address 0.0.0.0
