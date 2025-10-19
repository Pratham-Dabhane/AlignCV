# 🚀 AlignCV V2 - Phase 1 Setup Guide

## 📋 **What Was Built in Phase 1**

Phase 1 adds **secure authentication** and **document management** to AlignCV.

### ✅ **Features Implemented:**

1. **User Authentication:**
   - Email/password signup and login
   - JWT-based sessions (15-min access tokens + refresh tokens)
   - Google OAuth2 integration (ready, needs credentials)

2. **Document Management:**
   - Upload PDF or DOCX resumes
   - Automatic text extraction (PyMuPDF + python-docx)
   - NLP parsing with SpaCy (skills, roles, entities)
   - Local file storage (Firebase/S3 ready for Phase 2)

3. **Database:**
   - PostgreSQL with SQLAlchemy ORM
   - User and Document models
   - Async support for high performance
   - Alembic migrations ready

4. **API Endpoints:**
   - `POST /v2/auth/signup` - Register new user
   - `POST /v2/auth/login` - Login
   - `POST /v2/auth/google` - Google OAuth
   - `POST /v2/auth/refresh` - Refresh access token
   - `POST /v2/upload` - Upload document
   - `GET /v2/documents` - List user's documents
   - `GET /v2/documents/{id}` - Get document details
   - `DELETE /v2/documents/{id}` - Delete document

---

## 🔧 **Setup Instructions**

### **Step 1: Install Dependencies**

```powershell
# Activate virtual environment (if not already)
.\.venv\Scripts\Activate.ps1

# Install V2 dependencies
pip install -r requirements.txt

# Download SpaCy model (REQUIRED)
python -m spacy download en_core_web_sm
```

### **Step 2: Setup Environment Variables**

Create a `.env` file from the example:

```powershell
# Copy the example
cp .env.example .env

# Edit .env with your actual credentials
notepad .env
```

### **Step 3: Configure Credentials**

Open `.env` and replace the following placeholders:

#### 🔑 **Required for Basic Functionality:**

```env
# Database (use any free PostgreSQL)
DATABASE_URL=postgresql://username:password@host:5432/database

# JWT Secret (generate random string)
JWT_SECRET_KEY=your_random_secret_key_here

# Storage (start with 'local')
STORAGE_BACKEND=local
```

**Generate JWT Secret:**
```powershell
python -c "import secrets; print(secrets.token_urlsafe(32))"
```

#### 🌐 **Optional (for Google OAuth):**

```env
# Get from: https://console.cloud.google.com/apis/credentials
GOOGLE_CLIENT_ID=your_client_id
GOOGLE_CLIENT_SECRET=your_client_secret
```

#### 🔥 **Optional (for Firebase Storage):**

```env
FIREBASE_PROJECT_ID=your_project_id
FIREBASE_STORAGE_BUCKET=your_project_id.appspot.com
# Download service account JSON from Firebase Console
FIREBASE_SERVICE_ACCOUNT_PATH=./firebase-service-account.json
```

**Other credentials (Mistral, Qdrant, SendGrid, Redis) are for Phase 2+**

---

## 🗄️ **Database Setup**

### **Option A: Use Free PostgreSQL (Recommended)**

**Supabase (500MB free):**
1. Go to https://supabase.com
2. Create new project
3. Copy database URL from Settings > Database
4. Paste into `.env` as `DATABASE_URL`

**Neon (10GB free):**
1. Go to https://neon.tech
2. Create new project
3. Copy connection string
4. Paste into `.env` as `DATABASE_URL`

### **Option B: Local PostgreSQL**

```powershell
# Install PostgreSQL from https://www.postgresql.org/download/windows/

# Create database
createdb aligncv_v2

# Update .env
DATABASE_URL=postgresql://postgres:password@localhost:5432/aligncv_v2
```

### **Initialize Database:**

```powershell
# Tables are created automatically on first run
# Or initialize manually:
python -c "import asyncio; from backend.v2.database import init_db; asyncio.run(init_db())"
```

---

## 🚀 **Running V2**

### **Start V2 Backend (Port 8001):**

```powershell
cd backend
python -m uvicorn v2.app_v2:app_v2 --reload --port 8001
```

### **Access V2 API Docs:**

```
http://localhost:8001/v2/docs
```

### **Keep V1 Running (Optional):**

```powershell
# In another terminal
cd backend
python -m uvicorn app:app --reload --port 8000
```

**V1 remains at:** `http://localhost:8000/docs`

---

## 🧪 **Testing Phase 1**

### **Run All Tests:**

```powershell
# Run V2 tests
pytest tests/test_v2_auth.py -v
pytest tests/test_v2_documents.py -v

# Run all tests (V1 + V2)
pytest tests/ -v
```

### **Test Coverage:**

```powershell
pytest tests/ --cov=backend/v2 --cov-report=html
```

### **Manual API Testing:**

1. **Signup:**
```powershell
curl -X POST http://localhost:8001/v2/auth/signup `
  -H "Content-Type: application/json" `
  -d '{
    "name": "Test User",
    "email": "test@example.com",
    "password": "SecurePass123!"
  }'
```

2. **Login:**
```powershell
curl -X POST http://localhost:8001/v2/auth/login `
  -H "Content-Type: application/json" `
  -d '{
    "email": "test@example.com",
    "password": "SecurePass123!"
  }'
```

3. **Upload Document:**
```powershell
# Save access_token from login response

curl -X POST http://localhost:8001/v2/upload `
  -H "Authorization: Bearer YOUR_ACCESS_TOKEN" `
  -F "file=@path/to/resume.pdf"
```

---

## 📁 **What Changed (One-Liners)**

```
✅ Created backend/v2/ - Complete V2 backend structure
✅ Created backend/v2/config.py - Environment configuration with Pydantic
✅ Created backend/v2/database.py - SQLAlchemy async engine and session management
✅ Created backend/v2/models/models.py - User and Document database models
✅ Created backend/v2/auth/ - JWT authentication module with Google OAuth
✅ Created backend/v2/documents/ - Document upload and parsing module
✅ Created backend/v2/nlp/extractor.py - SpaCy NLP for skills/roles extraction
✅ Created backend/v2/storage/handler.py - File storage (local/Firebase/S3)
✅ Created backend/v2/app_v2.py - Main V2 FastAPI application
✅ Created tests/test_v2_auth.py - Authentication tests (15 tests)
✅ Created tests/test_v2_documents.py - Document parsing tests (12 tests)
✅ Updated requirements.txt - Added SQLAlchemy, Alembic, SpaCy, PyMuPDF, etc.
✅ Created .env.example - Complete credential placeholders
✅ Updated .gitignore - Exclude .env, uploads, sensitive files
```

---

## 🎯 **Phase 1 Upgrade Summary**

### **Backend Enhancements:**
- ✅ PostgreSQL database with User and Document models
- ✅ JWT authentication with 15-min access tokens
- ✅ Google OAuth2 ready (needs credentials)
- ✅ PDF/DOCX parsing with PyMuPDF and python-docx
- ✅ SpaCy NLP for skills and roles extraction
- ✅ Local file storage with Firebase/S3 ready
- ✅ Async SQLAlchemy for performance
- ✅ Alembic migrations support

### **API Additions:**
- ✅ 4 auth endpoints (/signup, /login, /google, /refresh)
- ✅ 4 document endpoints (/upload, list, get, delete)
- ✅ JWT bearer token authentication
- ✅ V2 docs at /v2/docs

### **Testing:**
- ✅ 27 new tests (15 auth + 12 documents)
- ✅ Test database with SQLite in-memory
- ✅ 100% V1 compatibility maintained

### **Architecture:**
- ✅ Modular structure (auth, documents, nlp, storage)
- ✅ Pydantic settings for configuration
- ✅ Environment-based credentials
- ✅ Comprehensive logging

---

## 🔑 **Where to Replace Placeholders**

| File | Placeholder | What to Replace |
|------|-------------|-----------------|
| `.env` | `DATABASE_URL` | Your PostgreSQL connection string |
| `.env` | `JWT_SECRET_KEY` | Random secret (use generator command) |
| `.env` | `GOOGLE_CLIENT_ID` | From Google Cloud Console |
| `.env` | `GOOGLE_CLIENT_SECRET` | From Google Cloud Console |
| `.env` | `FIREBASE_*` | From Firebase Console (optional) |

**⚠️ Remember:** NEVER commit `.env` file to git!

---

## ✅ **Verification Checklist**

- [ ] Dependencies installed (`pip install -r requirements.txt`)
- [ ] SpaCy model downloaded (`python -m spacy download en_core_web_sm`)
- [ ] `.env` file created and configured
- [ ] Database URL set in `.env`
- [ ] JWT secret generated and set
- [ ] V2 backend starts without errors
- [ ] Can access http://localhost:8001/v2/docs
- [ ] Tests pass (`pytest tests/test_v2_*.py`)
- [ ] Can signup new user via API
- [ ] Can upload PDF/DOCX document
- [ ] V1 still works at http://localhost:8000

---

## 🎉 **You're Ready for Phase 2!**

Phase 1 is complete! You now have:
- ✅ Secure authentication system
- ✅ Document upload and parsing
- ✅ Database for persistent storage
- ✅ NLP extraction for skills and roles

**Next Phase:** Advanced semantic matching with Qdrant vector DB! 🚀
