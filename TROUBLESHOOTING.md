# AlignCV Troubleshooting Guide

## 🚨 Common Issues and Solutions

### 1. Inotify Watch Limit Error

**Error:** `OSError: [Errno 28] inotify watch limit reached`

**Cause:** Linux systems have a limit on the number of files that can be watched simultaneously. Streamlit watches many files for changes, which can exceed this limit.

**Solutions:**

#### Quick Fix (Temporary)
```bash
# Increase limits temporarily
sudo sysctl -w fs.inotify.max_user_watches=524288
sudo sysctl -w fs.inotify.max_user_instances=8192
sudo sysctl -w fs.inotify.max_queued_events=16384
```

#### Permanent Fix
```bash
# Make changes permanent
echo "fs.inotify.max_user_watches=524288" | sudo tee -a /etc/sysctl.conf
echo "fs.inotify.max_user_instances=8192" | sudo tee -a /etc/sysctl.conf
echo "fs.inotify.max_queued_events=16384" | sudo tee -a /etc/sysctl.conf

# Apply changes
sudo sysctl -p
```

#### Automated Fix
```bash
# Use the provided script
chmod +x scripts/fix_inotify_limit.sh
./scripts/fix_inotify_limit.sh
```

### 2. Streamlit File Watching Issues

**Error:** Streamlit keeps restarting or shows file watching errors

**Solutions:**

#### Disable File Watching
```bash
# Set environment variable
export STREAMLIT_SERVER_FILE_WATCHER_TYPE=none

# Or run with optimized settings
python start_optimized.py
```

#### Use Optimized Configuration
```bash
# Create optimized config
python scripts/optimize_streamlit.py

# Run with optimized settings
streamlit run frontend/app_v2_optimized.py --server.fileWatcherType none
```

### 3. Dependency Conflicts

**Error:** Package version conflicts or import errors

**Solutions:**

#### Use Optimized Requirements
```bash
# Install optimized dependencies
pip install -r requirements_optimized.txt
```

#### Create Virtual Environment
```bash
# Create fresh environment
python -m venv venv_optimized
source venv_optimized/bin/activate  # Linux/Mac
# or
venv_optimized\Scripts\activate  # Windows

# Install dependencies
pip install -r requirements_optimized.txt
```

#### Check for Conflicts
```bash
# Check for conflicting packages
pip check

# List all installed packages
pip list
```

### 4. Memory Issues

**Error:** Out of memory or slow performance

**Solutions:**

#### Optimize Memory Usage
```bash
# Set memory limits
export STREAMLIT_SERVER_MAX_UPLOAD_SIZE=200
export STREAMLIT_SERVER_ENABLE_CORS=false
export STREAMLIT_SERVER_ENABLE_XSRF_PROTECTION=false
```

#### Monitor Memory Usage
```bash
# Check memory usage
htop
# or
free -h
```

### 5. Port Already in Use

**Error:** `Address already in use` or port 8501 is busy

**Solutions:**

#### Find and Kill Process
```bash
# Find process using port 8501
lsof -i :8501

# Kill the process
kill -9 <PID>
```

#### Use Different Port
```bash
# Run on different port
streamlit run frontend/app_v2.py --server.port 8502
```

### 6. Authentication Issues

**Error:** Login not working or session errors

**Solutions:**

#### Clear Session State
```python
# Add to your app
if st.button("Clear Session"):
    for key in list(st.session_state.keys()):
        del st.session_state[key]
    st.rerun()
```

#### Check API Connection
```python
# Test API connection
import requests
try:
    response = requests.get("https://aligncv-e55h.onrender.com/v2/health")
    print(f"API Status: {response.status_code}")
except Exception as e:
    print(f"API Error: {e}")
```

### 7. File Upload Issues

**Error:** File upload fails or files not processing

**Solutions:**

#### Check File Size Limits
```python
# Set file size limit
st.file_uploader(
    "Upload file",
    type=['pdf', 'docx'],
    max_upload_size=5 * 1024 * 1024  # 5MB
)
```

#### Check File Permissions
```bash
# Ensure proper permissions
chmod 755 frontend/
chmod 644 frontend/*.py
```

### 8. Database Connection Issues

**Error:** Database connection failed

**Solutions:**

#### Check Database URL
```python
# Verify database URL
import os
print(f"Database URL: {os.getenv('DATABASE_URL')}")
```

#### Test Connection
```python
# Test database connection
import psycopg2
try:
    conn = psycopg2.connect(os.getenv('DATABASE_URL'))
    print("Database connection successful")
    conn.close()
except Exception as e:
    print(f"Database connection failed: {e}")
```

## 🔧 Optimization Tips

### 1. Performance Optimization

```bash
# Run with optimized settings
python start_optimized.py

# Or manually set environment variables
export STREAMLIT_SERVER_FILE_WATCHER_TYPE=none
export STREAMLIT_SERVER_ENABLE_CORS=false
export STREAMLIT_SERVER_ENABLE_XSRF_PROTECTION=false
export STREAMLIT_BROWSER_GATHER_USAGE_STATS=false
export STREAMLIT_LOGGER_LEVEL=error
```

### 2. Memory Optimization

```python
# Add to your app
import gc
import psutil

# Monitor memory usage
def check_memory():
    memory = psutil.virtual_memory()
    if memory.percent > 80:
        gc.collect()
        st.warning("High memory usage detected, garbage collection performed")
```

### 3. File Watching Optimization

```python
# Disable file watching in your app
import os
os.environ['STREAMLIT_SERVER_FILE_WATCHER_TYPE'] = 'none'
```

## 🚀 Production Deployment

### 1. Docker Optimization

```dockerfile
# Use optimized Dockerfile
FROM python:3.11-slim

# Set environment variables
ENV STREAMLIT_SERVER_FILE_WATCHER_TYPE=none
ENV STREAMLIT_SERVER_ENABLE_CORS=false
ENV STREAMLIT_SERVER_ENABLE_XSRF_PROTECTION=false

# Install dependencies
COPY requirements_optimized.txt .
RUN pip install --no-cache-dir -r requirements_optimized.txt

# Run application
CMD ["python", "start_optimized.py"]
```

### 2. System Service

```ini
# /etc/systemd/system/aligncv.service
[Unit]
Description=AlignCV Application
After=network.target

[Service]
Type=simple
User=www-data
WorkingDirectory=/path/to/aligncv
Environment=STREAMLIT_SERVER_FILE_WATCHER_TYPE=none
ExecStart=/path/to/venv/bin/python start_optimized.py
Restart=always

[Install]
WantedBy=multi-user.target
```

## 📊 Monitoring and Logs

### 1. Check Application Logs

```bash
# Check Streamlit logs
tail -f ~/.streamlit/logs/streamlit.log

# Check system logs
journalctl -u aligncv.service -f
```

### 2. Monitor System Resources

```bash
# Monitor CPU and memory
htop

# Monitor disk usage
df -h

# Monitor network
netstat -tulpn
```

## 🆘 Getting Help

### 1. Check System Requirements

```bash
# Check Python version
python --version

# Check pip version
pip --version

# Check system info
uname -a
```

### 2. Debug Mode

```bash
# Run with debug information
streamlit run frontend/app_v2.py --logger.level debug
```

### 3. Common Commands

```bash
# Restart application
pkill -f streamlit
python start_optimized.py

# Clear cache
rm -rf ~/.streamlit/cache

# Reset environment
deactivate
source venv/bin/activate
pip install -r requirements_optimized.txt
```

## 📝 Additional Resources

- [Streamlit Documentation](https://docs.streamlit.io/)
- [FastAPI Documentation](https://fastapi.tiangolo.com/)
- [Linux System Administration](https://www.linux.org/)
- [Docker Documentation](https://docs.docker.com/)

## 🔄 Regular Maintenance

### Weekly Tasks
- Check system resources (CPU, memory, disk)
- Review application logs
- Update dependencies if needed

### Monthly Tasks
- Security updates
- Performance optimization
- Backup verification

### Quarterly Tasks
- Full system audit
- Dependency updates
- Security review
