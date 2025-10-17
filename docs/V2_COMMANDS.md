# 🚀 AlignCV V2 - Quick Command Reference

## 🔧 **Setup Commands**

```powershell
# Install all dependencies
pip install -r requirements.txt

# Download SpaCy model (REQUIRED)
python -m spacy download en_core_web_sm

# Create .env file
cp .env.example .env

# Generate JWT secret
python -c "import secrets; print(secrets.token_urlsafe(32))"

# Verify setup
python scripts/verify_v2_setup.py
```

---

## 🚀 **Run Commands**

### **Start V2 Backend (Port 8001)**
```powershell
cd backend
python -m uvicorn v2.app_v2:app_v2 --reload --port 8001
```

### **Start V1 Backend (Port 8000) - Optional**
```powershell
cd backend
python -m uvicorn app:app --reload --port 8000
```

### **Start V1 Frontend (Streamlit)**
```powershell
cd frontend
streamlit run app.py
```

---

## 🧪 **Test Commands**

```powershell
# Run V2 tests
pytest tests/test_v2_auth.py -v
pytest tests/test_v2_documents.py -v

# Run all tests (V1 + V2)
pytest tests/ -v

# With coverage
pytest tests/ --cov=backend/v2 --cov-report=html

# Run specific test
pytest tests/test_v2_auth.py::test_signup_success -v
```

---

## 🌐 **Access URLs**

| Service | URL |
|---------|-----|
| **V2 API Docs** | http://localhost:8001/v2/docs |
| **V2 ReDoc** | http://localhost:8001/v2/redoc |
| **V2 Health** | http://localhost:8001/v2/health |
| **V1 API Docs** | http://localhost:8000/docs |
| **V1 Frontend** | http://localhost:8501 or 8502 |

---

## 🔐 **API Testing Commands**

### **1. Signup**
```powershell
curl -X POST http://localhost:8001/v2/auth/signup `
  -H "Content-Type: application/json" `
  -d '{
    "name": "Test User",
    "email": "test@example.com",
    "password": "SecurePass123!"
  }'
```

### **2. Login**
```powershell
curl -X POST http://localhost:8001/v2/auth/login `
  -H "Content-Type: application/json" `
  -d '{
    "email": "test@example.com",
    "password": "SecurePass123!"
  }'
```

### **3. Upload Document**
```powershell
# Replace YOUR_ACCESS_TOKEN with token from login
curl -X POST http://localhost:8001/v2/upload `
  -H "Authorization: Bearer YOUR_ACCESS_TOKEN" `
  -F "file=@path/to/resume.pdf"
```

### **4. List Documents**
```powershell
curl -X GET http://localhost:8001/v2/documents `
  -H "Authorization: Bearer YOUR_ACCESS_TOKEN"
```

### **5. Get Document**
```powershell
curl -X GET http://localhost:8001/v2/documents/1 `
  -H "Authorization: Bearer YOUR_ACCESS_TOKEN"
```

### **6. Delete Document**
```powershell
curl -X DELETE http://localhost:8001/v2/documents/1 `
  -H "Authorization: Bearer YOUR_ACCESS_TOKEN"
```

---

## 🗄️ **Database Commands**

### **Initialize Database**
```powershell
python -c "import asyncio; from backend.v2.database import init_db; asyncio.run(init_db())"
```

### **Alembic Migrations (Future)**
```powershell
# Create migration
alembic revision --autogenerate -m "Description"

# Apply migrations
alembic upgrade head

# Rollback
alembic downgrade -1

# Show current version
alembic current
```

---

## 📦 **Dependency Commands**

```powershell
# Update all dependencies
pip install --upgrade -r requirements.txt

# Freeze current versions
pip freeze > requirements-frozen.txt

# Check for outdated packages
pip list --outdated

# Install single package
pip install package-name
```

---

## 🔍 **Debugging Commands**

```powershell
# Check Python version
python --version

# Check if package is installed
python -c "import package_name; print(package_name.__version__)"

# List installed packages
pip list

# Show package info
pip show package-name

# Check SpaCy model
python -m spacy info en_core_web_sm

# Validate SpaCy installation
python -m spacy validate
```

---

## 📝 **Git Commands (For Committing V2)**

```powershell
# Check status
git status

# Add V2 files
git add backend/v2/
git add tests/test_v2_*.py
git add docs/V2_*.md
git add requirements.txt
git add .env.example
git add .gitignore

# Commit
git commit -m "feat: Add V2 Phase 1 - Authentication & Document Hub"

# Push
git push origin main
```

---

## 🧹 **Cleanup Commands**

```powershell
# Remove Python cache
Get-ChildItem -Recurse -Filter "__pycache__" | Remove-Item -Recurse -Force
Get-ChildItem -Recurse -Filter "*.pyc" | Remove-Item -Force

# Remove test cache
Remove-Item -Recurse -Force .pytest_cache

# Clean uploaded files (CAREFUL!)
Remove-Item -Recurse -Force storage/uploads/*

# Reset database (CAREFUL!)
# Delete your database and recreate
```

---

## 🔄 **Environment Commands**

```powershell
# Activate virtual environment
.\.venv\Scripts\Activate.ps1

# Deactivate
deactivate

# Create new venv
python -m venv .venv

# Install in venv
.\.venv\Scripts\python.exe -m pip install -r requirements.txt
```

---

## 📊 **Monitoring Commands**

```powershell
# Watch logs (if using file logging)
Get-Content logs/v2_app.log -Wait -Tail 50

# Check server processes
Get-Process | Where-Object {$_.ProcessName -like "*python*"}

# Kill process on port
netstat -ano | findstr :8001
# Then: taskkill /PID <PID> /F
```

---

## 🎯 **Quick Start Workflow**

```powershell
# 1. Setup (first time only)
pip install -r requirements.txt
python -m spacy download en_core_web_sm
cp .env.example .env
# Edit .env with credentials

# 2. Verify setup
python scripts/verify_v2_setup.py

# 3. Start V2
cd backend
python -m uvicorn v2.app_v2:app_v2 --reload --port 8001

# 4. Test
pytest tests/test_v2_*.py -v

# 5. Access
# Open browser: http://localhost:8001/v2/docs
```

---

## 💡 **Pro Tips**

```powershell
# Run in background (PowerShell)
Start-Process python -ArgumentList "-m", "uvicorn", "v2.app_v2:app_v2", "--reload", "--port", "8001" -WindowStyle Hidden

# Multiple terminals in VS Code
# Ctrl+Shift+` (create new terminal)
# Split terminal: Ctrl+Shift+5

# Quick test single file
pytest tests/test_v2_auth.py -v -k "test_signup"

# Debug mode
python -m uvicorn v2.app_v2:app_v2 --reload --port 8001 --log-level debug
```

---

**📚 Full documentation:** `docs/V2_PHASE1_SETUP.md`
