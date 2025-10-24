#!/bin/bash

# AlignCV Deployment Script
# Optimized for production deployment

echo "🚀 Starting AlignCV Deployment Process"
echo "======================================"

# Check if we're in the right directory
if [ ! -f "frontend/app_v2.py" ]; then
    echo "❌ Error: frontend/app_v2.py not found!"
    echo "   Please run this script from the project root directory"
    exit 1
fi

# Set environment variables for optimization
export STREAMLIT_SERVER_FILE_WATCHER_TYPE=none
export STREAMLIT_SERVER_ENABLE_CORS=false
export STREAMLIT_SERVER_ENABLE_XSRF_PROTECTION=false
export STREAMLIT_BROWSER_GATHER_USAGE_STATS=false
export STREAMLIT_LOGGER_LEVEL=error

echo "⚙️  Setting up optimized environment..."

# Install dependencies
echo "📦 Installing optimized dependencies..."
pip install -r requirements_optimized.txt

# Check if installation was successful
if [ $? -eq 0 ]; then
    echo "✅ Dependencies installed successfully"
else
    echo "❌ Failed to install dependencies"
    exit 1
fi

# Test the application
echo "🧪 Testing application..."
python -c "import streamlit; print('Streamlit version:', streamlit.__version__)"

# Start the application
echo "🚀 Starting AlignCV application..."
echo "   URL: http://localhost:8501"
echo "   Press Ctrl+C to stop"
echo ""

streamlit run frontend/app_v2.py \
    --server.fileWatcherType none \
    --server.enableCORS false \
    --server.enableXsrfProtection false \
    --browser.gatherUsageStats false \
    --logger.level error \
    --server.port 8501 \
    --server.address 0.0.0.0
