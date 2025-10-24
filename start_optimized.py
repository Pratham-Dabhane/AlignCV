#!/usr/bin/env python3
"""
Optimized AlignCV Startup Script
Handles inotify limits and runs the application with optimizations
"""

import os
import sys
import subprocess
import platform
from pathlib import Path

def check_system():
    """Check system requirements and inotify limits"""
    print("🔍 Checking system requirements...")
    
    # Check if we're on Linux
    if platform.system() != "Linux":
        print("⚠️  Warning: This optimization is designed for Linux systems")
        print("   The inotify error typically occurs on Linux with limited file watchers")
        return True
    
    # Check current inotify limits
    try:
        with open('/proc/sys/fs/inotify/max_user_watches', 'r') as f:
            current_watches = int(f.read().strip())
        
        with open('/proc/sys/fs/inotify/max_user_instances', 'r') as f:
            current_instances = int(f.read().strip())
        
        print(f"📊 Current inotify limits:")
        print(f"   max_user_watches: {current_watches:,}")
        print(f"   max_user_instances: {current_instances:,}")
        
        # Check if limits are too low
        if current_watches < 100000:
            print("⚠️  Warning: inotify watch limit is low, may cause errors")
            return False
        else:
            print("✅ inotify limits look good")
            return True
            
    except (FileNotFoundError, PermissionError, ValueError) as e:
        print(f"❌ Could not check inotify limits: {e}")
        return False

def fix_inotify_limits():
    """Attempt to fix inotify limits"""
    print("🔧 Attempting to fix inotify limits...")
    
    try:
        # Try to increase limits temporarily
        subprocess.run([
            'sudo', 'sysctl', '-w', 
            'fs.inotify.max_user_watches=524288'
        ], check=True, capture_output=True)
        
        subprocess.run([
            'sudo', 'sysctl', '-w', 
            'fs.inotify.max_user_instances=8192'
        ], check=True, capture_output=True)
        
        subprocess.run([
            'sudo', 'sysctl', '-w', 
            'fs.inotify.max_queued_events=16384'
        ], check=True, capture_output=True)
        
        print("✅ Successfully increased inotify limits")
        return True
        
    except subprocess.CalledProcessError as e:
        print(f"❌ Failed to increase inotify limits: {e}")
        print("   You may need to run this script with sudo or manually fix the limits")
        return False
    except FileNotFoundError:
        print("❌ sudo command not found. Please run manually:")
        print("   sudo sysctl -w fs.inotify.max_user_watches=524288")
        print("   sudo sysctl -w fs.inotify.max_user_instances=8192")
        print("   sudo sysctl -w fs.inotify.max_queued_events=16384")
        return False

def setup_environment():
    """Set up optimized environment variables"""
    print("⚙️  Setting up optimized environment...")
    
    # Set environment variables for optimization
    os.environ['STREAMLIT_SERVER_FILE_WATCHER_TYPE'] = 'none'
    os.environ['STREAMLIT_SERVER_ENABLE_CORS'] = 'false'
    os.environ['STREAMLIT_SERVER_ENABLE_XSRF_PROTECTION'] = 'false'
    os.environ['STREAMLIT_BROWSER_GATHER_USAGE_STATS'] = 'false'
    os.environ['STREAMLIT_LOGGER_LEVEL'] = 'error'
    os.environ['STREAMLIT_CLIENT_SHOW_ERROR_DETAILS'] = 'false'
    os.environ['STREAMLIT_CLIENT_TOOLBAR_MODE'] = 'minimal'
    
    print("✅ Environment variables set for optimization")

def run_streamlit():
    """Run Streamlit with optimized settings"""
    print("🚀 Starting optimized Streamlit application...")
    
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
    
    # Run Streamlit with optimized settings
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
        "--server.address", "0.0.0.0"
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
        sys.exit(1)

def main():
    """Main function"""
    print("🎯 AlignCV Optimized Startup")
    print("=" * 50)
    
    # Check system requirements
    system_ok = check_system()
    
    if not system_ok:
        print("\n🔧 Attempting to fix inotify limits...")
        if not fix_inotify_limits():
            print("\n⚠️  Could not automatically fix inotify limits")
            print("   The application may still work, but you might encounter errors")
            print("   Consider running the fix script manually:")
            print("   chmod +x scripts/fix_inotify_limit.sh")
            print("   ./scripts/fix_inotify_limit.sh")
    
    # Set up environment
    setup_environment()
    
    # Run the application
    run_streamlit()

if __name__ == "__main__":
    main()
