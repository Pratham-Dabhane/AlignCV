#!/usr/bin/env python3
"""
Streamlit Optimization Script
Reduces file watching overhead and optimizes performance
"""

import os
import sys
import subprocess
from pathlib import Path

def optimize_streamlit_config():
    """Create optimized Streamlit configuration"""
    
    # Create .streamlit directory if it doesn't exist
    streamlit_dir = Path.home() / ".streamlit"
    streamlit_dir.mkdir(exist_ok=True)
    
    # Optimized config.toml
    config_content = """[global]
# Disable file watching for better performance
fileWatcherType = "none"

[server]
# Optimize server settings
maxUploadSize = 200
enableCORS = false
enableXsrfProtection = false

[browser]
# Disable automatic browser opening
gatherUsageStats = false

[theme]
# Use light theme by default
base = "light"

[logger]
# Reduce logging overhead
level = "error"

[client]
# Optimize client settings
showErrorDetails = false
toolbarMode = "minimal"
"""
    
    config_file = streamlit_dir / "config.toml"
    with open(config_file, 'w') as f:
        f.write(config_content)
    
    print(f"✅ Created optimized Streamlit config at {config_file}")

def create_streamlit_runner():
    """Create an optimized Streamlit runner script"""
    
    runner_content = """#!/usr/bin/env python3
'''
Optimized Streamlit Runner
Reduces file watching and improves performance
'''

import os
import sys
import subprocess
from pathlib import Path

def run_streamlit():
    \"\"\"Run Streamlit with optimized settings\"\"\"
    
    # Set environment variables for optimization
    os.environ['STREAMLIT_SERVER_FILE_WATCHER_TYPE'] = 'none'
    os.environ['STREAMLIT_SERVER_ENABLE_CORS'] = 'false'
    os.environ['STREAMLIT_SERVER_ENABLE_XSRF_PROTECTION'] = 'false'
    os.environ['STREAMLIT_BROWSER_GATHER_USAGE_STATS'] = 'false'
    os.environ['STREAMLIT_LOGGER_LEVEL'] = 'error'
    
    # Get the app file path
    app_file = Path(__file__).parent / "app_v2.py"
    
    if not app_file.exists():
        print("❌ app_v2.py not found!")
        sys.exit(1)
    
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
        "--client.toolbarMode", "minimal"
    ]
    
    print("🚀 Starting optimized Streamlit application...")
    print(f"📁 App file: {app_file}")
    print("⚡ File watching disabled for better performance")
    
    try:
        subprocess.run(cmd, check=True)
    except KeyboardInterrupt:
        print("\\n👋 Shutting down gracefully...")
    except subprocess.CalledProcessError as e:
        print(f"❌ Error running Streamlit: {e}")
        sys.exit(1)

if __name__ == "__main__":
    run_streamlit()
"""
    
    runner_file = Path("frontend/run_optimized.py")
    with open(runner_file, 'w') as f:
        f.write(runner_content)
    
    # Make it executable
    os.chmod(runner_file, 0o755)
    
    print(f"✅ Created optimized runner at {runner_file}")

def create_docker_optimization():
    """Create Docker optimization for production"""
    
    dockerfile_content = """# Optimized Dockerfile for Streamlit
FROM python:3.11-slim

# Set environment variables
ENV PYTHONUNBUFFERED=1
ENV STREAMLIT_SERVER_FILE_WATCHER_TYPE=none
ENV STREAMLIT_SERVER_ENABLE_CORS=false
ENV STREAMLIT_SERVER_ENABLE_XSRF_PROTECTION=false
ENV STREAMLIT_BROWSER_GATHER_USAGE_STATS=false
ENV STREAMLIT_LOGGER_LEVEL=error

# Install system dependencies
RUN apt-get update && apt-get install -y \\
    gcc \\
    g++ \\
    && rm -rf /var/lib/apt/lists/*

# Set working directory
WORKDIR /app

# Copy requirements first for better caching
COPY requirements.txt .

# Install Python dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Copy application code
COPY . .

# Create non-root user
RUN useradd -m -u 1000 appuser && chown -R appuser:appuser /app
USER appuser

# Expose port
EXPOSE 8501

# Health check
HEALTHCHECK --interval=30s --timeout=10s --start-period=5s --retries=3 \\
    CMD curl -f http://localhost:8501/_stcore/health || exit 1

# Run the application
CMD ["python", "-m", "streamlit", "run", "frontend/app_v2.py", \\
     "--server.fileWatcherType", "none", \\
     "--server.enableCORS", "false", \\
     "--server.enableXsrfProtection", "false", \\
     "--browser.gatherUsageStats", "false", \\
     "--logger.level", "error"]
"""
    
    with open("Dockerfile.optimized", 'w') as f:
        f.write(dockerfile_content)
    
    print("✅ Created optimized Dockerfile")

def main():
    """Main optimization function"""
    print("🔧 Optimizing Streamlit application...")
    
    # Create optimized config
    optimize_streamlit_config()
    
    # Create optimized runner
    create_streamlit_runner()
    
    # Create Docker optimization
    create_docker_optimization()
    
    print("\\n✅ Optimization complete!")
    print("\\n📋 Next steps:")
    print("1. Run: chmod +x scripts/fix_inotify_limit.sh")
    print("2. Run: ./scripts/fix_inotify_limit.sh")
    print("3. Use: python frontend/run_optimized.py")
    print("\\n🚀 Your Streamlit app should now run without inotify errors!")

if __name__ == "__main__":
    main()
"""
