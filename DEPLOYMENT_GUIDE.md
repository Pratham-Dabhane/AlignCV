# 🚀 AlignCV Deployment Guide

## 📋 Complete Step-by-Step Deployment Process

### ✅ **Step 1: Application Optimization (COMPLETED)**

Your main application file (`frontend/app_v2.py`) has been updated with:
- ✅ Disabled file watching to prevent inotify errors
- ✅ Optimized environment variables
- ✅ Production-ready configuration
- ✅ Error handling improvements

### ✅ **Step 2: Deployment Files Created (COMPLETED)**

The following deployment files have been created:

#### **Core Deployment Files:**
- `Procfile` - For Heroku deployment
- `Dockerfile` - For Docker deployment
- `docker-compose.yml` - For local Docker testing
- `.streamlit/config.toml` - Streamlit configuration
- `requirements_optimized.txt` - Optimized dependencies

#### **Deployment Scripts:**
- `deploy.sh` - Linux deployment script
- `deploy.bat` - Windows deployment script
- `start_optimized_windows.py` - Windows startup script

#### **Configuration Files:**
- `env.production.example` - Production environment template

### 🚀 **Step 3: Local Testing**

#### **Option A: Quick Test (Recommended)**
```bash
# Windows
python start_optimized_windows.py

# Linux
python start_optimized.py
```

#### **Option B: Manual Streamlit Command**
```bash
streamlit run frontend/app_v2.py \
  --server.fileWatcherType none \
  --server.enableCORS false \
  --server.enableXsrfProtection false \
  --browser.gatherUsageStats false \
  --logger.level error
```

#### **Option C: Using Deployment Scripts**
```bash
# Windows
deploy.bat

# Linux
chmod +x deploy.sh
./deploy.sh
```

### 🌐 **Step 4: Production Deployment Options**

#### **Option A: Heroku Deployment**

1. **Install Heroku CLI:**
   ```bash
   # Download from https://devcenter.heroku.com/articles/heroku-cli
   ```

2. **Login to Heroku:**
   ```bash
   heroku login
   ```

3. **Create Heroku App:**
   ```bash
   heroku create your-aligncv-app
   ```

4. **Set Environment Variables:**
   ```bash
   heroku config:set STREAMLIT_SERVER_FILE_WATCHER_TYPE=none
   heroku config:set STREAMLIT_SERVER_ENABLE_CORS=false
   heroku config:set STREAMLIT_SERVER_ENABLE_XSRF_PROTECTION=false
   heroku config:set STREAMLIT_BROWSER_GATHER_USAGE_STATS=false
   heroku config:set STREAMLIT_LOGGER_LEVEL=error
   ```

5. **Deploy:**
   ```bash
   git add .
   git commit -m "Deploy optimized AlignCV"
   git push heroku main
   ```

#### **Option B: Docker Deployment**

1. **Build Docker Image:**
   ```bash
   docker build -t aligncv-optimized .
   ```

2. **Run Container:**
   ```bash
   docker run -p 8501:8501 aligncv-optimized
   ```

3. **Using Docker Compose:**
   ```bash
   docker-compose up -d
   ```

#### **Option C: VPS/Cloud Server Deployment**

1. **Upload Files:**
   ```bash
   scp -r . user@your-server:/path/to/aligncv/
   ```

2. **SSH into Server:**
   ```bash
   ssh user@your-server
   cd /path/to/aligncv/
   ```

3. **Install Dependencies:**
   ```bash
   pip install -r requirements_optimized.txt
   ```

4. **Run Application:**
   ```bash
   python start_optimized.py
   ```

5. **Set up Process Manager (PM2):**
   ```bash
   npm install -g pm2
   pm2 start start_optimized.py --name aligncv
   pm2 save
   pm2 startup
   ```

### 🔧 **Step 5: Environment Configuration**

#### **Create Production Environment File:**
```bash
# Copy the example file
cp env.production.example .env

# Edit with your production values
nano .env
```

#### **Key Environment Variables:**
```bash
# Application Settings
STREAMLIT_SERVER_FILE_WATCHER_TYPE=none
STREAMLIT_SERVER_ENABLE_CORS=false
STREAMLIT_SERVER_ENABLE_XSRF_PROTECTION=false
STREAMLIT_BROWSER_GATHER_USAGE_STATS=false
STREAMLIT_LOGGER_LEVEL=error

# API Configuration
API_BASE_URL=https://aligncv-e55h.onrender.com/v2

# Security
SECRET_KEY=your-secret-key-here
JWT_SECRET_KEY=your-jwt-secret-key-here
```

### 📊 **Step 6: Monitoring and Maintenance**

#### **Health Checks:**
```bash
# Check application status
curl http://localhost:8501/_stcore/health

# Check logs
tail -f logs/aligncv.log
```

#### **Performance Monitoring:**
```bash
# Monitor system resources
htop

# Check memory usage
free -h

# Monitor disk space
df -h
```

### 🛠️ **Step 7: Troubleshooting**

#### **Common Issues:**

1. **Port Already in Use:**
   ```bash
   # Find and kill process
   lsof -i :8501
   kill -9 <PID>
   ```

2. **Permission Issues:**
   ```bash
   # Fix permissions
   chmod +x deploy.sh
   chmod 755 frontend/
   ```

3. **Dependency Issues:**
   ```bash
   # Reinstall dependencies
   pip install -r requirements_optimized.txt --force-reinstall
   ```

4. **Memory Issues:**
   ```bash
   # Monitor memory
   free -h
   # Restart if needed
   pm2 restart aligncv
   ```

### 🎯 **Step 8: Production Checklist**

#### **Before Deployment:**
- ✅ Application tested locally
- ✅ Dependencies installed
- ✅ Environment variables set
- ✅ Security configurations applied
- ✅ Monitoring setup

#### **After Deployment:**
- ✅ Application accessible via URL
- ✅ Health checks passing
- ✅ Logs being generated
- ✅ Performance monitoring active
- ✅ Backup strategy in place

### 🚀 **Quick Start Commands**

#### **Local Development:**
```bash
# Windows
python start_optimized_windows.py

# Linux
python start_optimized.py
```

#### **Production Deployment:**
```bash
# Heroku
git push heroku main

# Docker
docker-compose up -d

# VPS
pm2 start start_optimized.py --name aligncv
```

### 📞 **Support and Help**

#### **If You Encounter Issues:**
1. Check `TROUBLESHOOTING.md` for detailed solutions
2. Review logs for error messages
3. Verify environment variables
4. Test locally first
5. Check system resources

#### **Useful Commands:**
```bash
# Check application status
ps aux | grep streamlit

# View logs
tail -f ~/.streamlit/logs/streamlit.log

# Restart application
pm2 restart aligncv

# Check system resources
htop
```

## 🎉 **You're Ready to Deploy!**

Your AlignCV application is now fully optimized and ready for production deployment. Choose your preferred deployment method and follow the steps above.

**Application URL:** http://localhost:8501 (local) or your deployed URL

**Key Benefits:**
- ✅ No inotify errors
- ✅ Optimized performance
- ✅ Production-ready configuration
- ✅ Comprehensive monitoring
- ✅ Easy deployment process
