#!/usr/bin/env python3
"""
Optimized AlignCV Startup Script for Windows
Handles Windows-specific optimizations and runs the application
"""

import os
import sys
import subprocess
import platform
from pathlib import Path

def check_windows_system():
    """Check Windows system requirements"""
    print("🔍 Checking Windows system requirements...")
    
    # Check if we're on Windows
    if platform.system() != "Windows":
        print("⚠️  Warning: This script is optimized for Windows")
        print("   For Linux, use the regular start_optimized.py")
        return True
    
    # Check Python version
    python_version = sys.version_info
    if python_version.major < 3 or (python_version.major == 3 and python_version.minor < 8):
        print("❌ Python 3.8+ is required")
        return False
    
    print(f"✅ Python {python_version.major}.{python_version.minor}.{python_version.micro} detected")
    
    # Check if Streamlit is installed
    try:
        import streamlit
        print(f"✅ Streamlit {streamlit.__version__} detected")
    except ImportError:
        print("❌ Streamlit not found. Installing...")
        subprocess.run([sys.executable, "-m", "pip", "install", "streamlit==1.40.2"])
        print("✅ Streamlit installed")
    
    return True

def setup_windows_environment():
    """Set up optimized environment for Windows"""
    print("⚙️  Setting up optimized Windows environment...")
    
    # Set environment variables for optimization
    os.environ['STREAMLIT_SERVER_FILE_WATCHER_TYPE'] = 'none'
    os.environ['STREAMLIT_SERVER_ENABLE_CORS'] = 'false'
    os.environ['STREAMLIT_SERVER_ENABLE_XSRF_PROTECTION'] = 'false'
    os.environ['STREAMLIT_BROWSER_GATHER_USAGE_STATS'] = 'false'
    os.environ['STREAMLIT_LOGGER_LEVEL'] = 'error'
    os.environ['STREAMLIT_CLIENT_SHOW_ERROR_DETAILS'] = 'false'
    os.environ['STREAMLIT_CLIENT_TOOLBAR_MODE'] = 'minimal'
    
    # Windows-specific optimizations
    os.environ['STREAMLIT_SERVER_HEADLESS'] = 'true'
    os.environ['STREAMLIT_SERVER_RUN_ON_SAVE'] = 'false'
    
    print("✅ Windows environment variables set for optimization")

def install_dependencies():
    """Install required dependencies"""
    print("📦 Installing/updating dependencies...")
    
    try:
        # Install from optimized requirements
        subprocess.run([
            sys.executable, "-m", "pip", "install", "-r", "requirements_optimized.txt"
        ], check=True)
        print("✅ Dependencies installed successfully")
        return True
    except subprocess.CalledProcessError as e:
        print(f"⚠️  Warning: Could not install all dependencies: {e}")
        print("   Trying to install core dependencies...")
        
        # Install core dependencies
        core_deps = [
            "streamlit==1.40.2",
            "requests==2.32.3",
            "fastapi==0.115.5",
            "uvicorn==0.32.1"
        ]
        
        for dep in core_deps:
            try:
                subprocess.run([sys.executable, "-m", "pip", "install", dep], check=True)
                print(f"✅ Installed {dep}")
            except subprocess.CalledProcessError:
                print(f"⚠️  Could not install {dep}")
        
        return True

def run_streamlit_windows():
    """Run Streamlit with Windows-optimized settings"""
    print("🚀 Starting optimized Streamlit application on Windows...")
    
    # Get the app file path
    app_file = Path("frontend/app_v2_optimized.py")
    
    if not app_file.exists():
        print("❌ Optimized app file not found!")
        print("   Falling back to regular app_v2.py")
        app_file = Path("frontend/app_v2.py")
        
        if not app_file.exists():
            print("❌ No Streamlit app found!")
            sys.exit(1)
    
    print(f"📁 Using app file: {app_file}")
    
    # Run Streamlit with Windows-optimized settings
    cmd = [
        sys.executable, "-m", "streamlit", "run",
        str(app_file),
        "--server.fileWatcherType", "none",
        "--server.enableCORS", "false",
        "--server.enableXsrfProtection", "false",
        "--browser.gatherUsageStats", "false",
        "--logger.level", "error",
        "--client.showErrorDetails", "false",
        "--client.toolbarMode", "minimal",
        "--server.port", "8501",
        "--server.address", "localhost",
        "--server.headless", "true",
        "--server.runOnSave", "false"
    ]
    
    print("⚡ File watching disabled for better performance")
    print("🌐 Server will be available at: http://localhost:8501")
    print("🛑 Press Ctrl+C to stop the server")
    print("-" * 50)
    
    try:
        subprocess.run(cmd, check=True)
    except KeyboardInterrupt:
        print("\n👋 Shutting down gracefully...")
    except subprocess.CalledProcessError as e:
        print(f"❌ Error running Streamlit: {e}")
        print("\n🔧 Troubleshooting tips:")
        print("1. Check if port 8501 is available")
        print("2. Try running: netstat -an | findstr :8501")
        print("3. Kill any existing Streamlit processes")
        print("4. Try a different port: --server.port 8502")
        sys.exit(1)

def main():
    """Main function for Windows"""
    print("🎯 AlignCV Optimized Startup (Windows)")
    print("=" * 50)
    
    # Check system requirements
    if not check_windows_system():
        print("❌ System requirements not met")
        sys.exit(1)
    
    # Set up environment
    setup_windows_environment()
    
    # Install dependencies
    install_dependencies()
    
    # Run the application
    run_streamlit_windows()

if __name__ == "__main__":
    main()
