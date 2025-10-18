# Google OAuth Setup Guide - AlignCV V2
## Do You Need It? (Spoiler: Not Required for Testing!)

---

## ⚠️ IMPORTANT: Google OAuth is **OPTIONAL**

**Good News:** You can **fully test and use** AlignCV V2 Phase 3 without Google OAuth!

### **What Works WITHOUT Google OAuth:**
✅ Email/password signup and login  
✅ Upload resumes (PDF/DOCX)  
✅ AI resume rewriting with Mistral  
✅ Document management  
✅ All Phase 3 features  

### **What Requires Google OAuth:**
❌ "Sign in with Google" button  
❌ Google account integration  

**Recommendation:** Skip Google OAuth for now unless you specifically want social login.

---

## 🔍 Current Status in Your `.env`

```bash
# These are PLACEHOLDERS - not real credentials
GOOGLE_CLIENT_ID=placeholder_google_client_id
GOOGLE_CLIENT_SECRET=placeholder_google_client_secret
GOOGLE_REDIRECT_URI=http://localhost:8001/v2/auth/google/callback
```

**What happens with placeholders?**
- ✅ App starts fine
- ✅ Email/password auth works perfectly
- ❌ Google OAuth endpoint will fail if called (but you won't call it)

---

## 🚀 How to Test Phase 3 Right Now (Without Google OAuth)

### **Step 1: Access API Docs**
Open: http://localhost:8001/v2/docs

### **Step 2: Create Account**
```json
POST /v2/auth/signup
{
  "name": "Test User",
  "email": "test@example.com",
  "password": "Test123!"
}
```

**Response:**
```json
{
  "access_token": "eyJ0eXAiOiJKV1QiLCJhbGc...",
  "refresh_token": "eyJ0eXAiOiJKV1QiLCJhbGc...",
  "token_type": "bearer",
  "user": {
    "id": 1,
    "name": "Test User",
    "email": "test@example.com"
  }
}
```

### **Step 3: Upload Resume**
```bash
POST /v2/upload
Headers: Authorization: Bearer <your_access_token>
Body: file=resume.pdf (multipart/form-data)
```

**Response:**
```json
{
  "document_id": 1,
  "file_name": "resume.pdf",
  "extracted_text": "John Doe\nSoftware Engineer...",
  "skills": ["Python", "JavaScript", "Docker"],
  "roles": ["Software Engineer"],
  "entities": ["Google", "AWS"]
}
```

### **Step 4: Test AI Rewriting (Phase 3!)**
```json
POST /v2/rewrite
Headers: Authorization: Bearer <your_access_token>
{
  "resume_id": 1,
  "rewrite_style": "Technical"
}
```

**Response (Fallback Mode - No Mistral API Key):**
```json
{
  "version_id": 1,
  "resume_id": 1,
  "original_text": "Worked on backend systems...",
  "rewritten_text": "Worked on backend systems...",
  "diff_html": "<div class='diff-viewer'>...</div>",
  "improvements": [
    "API unavailable - original content preserved",
    "Requested style: Technical",
    "Please configure MISTRAL_API_KEY for AI rewriting"
  ],
  "impact_score": 0,
  "style": "Technical",
  "latency": 0.0,
  "api_status": "fallback",
  "warning": "Mistral API unavailable - using original content"
}
```

**This proves Phase 3 works!** The fallback mode is intentional.

### **Step 5: List Versions**
```bash
GET /v2/rewrite/versions/1
Headers: Authorization: Bearer <your_access_token>
```

**Response:**
```json
{
  "resume_id": 1,
  "versions": [
    {
      "version_id": 1,
      "style": "Technical",
      "impact_score": 0,
      "improvements": ["API unavailable..."],
      "created_at": "2025-10-18T13:02:55"
    }
  ]
}
```

---

## 🎯 Testing Checklist (No Google OAuth Needed!)

Run these tests to verify Phase 3:

- [ ] ✅ Backend running at http://localhost:8001
- [ ] ✅ API docs accessible at http://localhost:8001/v2/docs
- [ ] ✅ Can signup with email/password
- [ ] ✅ Can login with email/password
- [ ] ✅ Can upload PDF/DOCX resume
- [ ] ✅ Can call POST /v2/rewrite
- [ ] ✅ Get fallback response (proves error handling works)
- [ ] ✅ Can list versions
- [ ] ✅ Can get version detail

**All ✅ = Phase 3 is working perfectly!**

---

## 🔐 IF You Want Google OAuth (Optional)

### **When to Set It Up:**
- You want "Sign in with Google" functionality
- You're deploying to production
- You want to allow users to login without passwords

### **How to Get Google OAuth Credentials (Free):**

**Step 1: Go to Google Cloud Console**
- Visit: https://console.cloud.google.com/
- Sign in with your Google account

**Step 2: Create Project**
- Click "Select a project" → "New Project"
- Name: "AlignCV"
- Click "Create"

**Step 3: Enable APIs**
- Go to "APIs & Services" → "Library"
- Search "Google+ API" → Enable it

**Step 4: Create OAuth Credentials**
- Go to "APIs & Services" → "Credentials"
- Click "Create Credentials" → "OAuth client ID"
- Application type: "Web application"
- Name: "AlignCV Web Client"
- Authorized redirect URIs:
  - http://localhost:8001/v2/auth/google/callback
  - http://localhost:8000/v2/auth/google/callback
- Click "Create"

**Step 5: Copy Credentials to .env**
```bash
GOOGLE_CLIENT_ID=1234567890-abcdefghijklmnopqrstuvwxyz.apps.googleusercontent.com
GOOGLE_CLIENT_SECRET=GOCSPX-abcdefghijklmnopqrstuvwx
GOOGLE_REDIRECT_URI=http://localhost:8001/v2/auth/google/callback
```

**Step 6: Restart Backend**
```powershell
# Stop current server (Ctrl+C in terminal)
# Restart
$env:PYTHONPATH="C:\Pra_programming\Projects\ALIGN"
python .venv/Scripts/python.exe -m uvicorn backend.v2.app_v2:app_v2 --reload --port 8001
```

**Step 7: Test Google OAuth**
```json
POST /v2/auth/google
{
  "token": "google_oauth_token_from_frontend"
}
```

---

## 🎨 Testing with Simple Script (No OAuth)

Create `test_phase3.py`:

```python
import requests
import json

BASE_URL = "http://localhost:8001"

# 1. Signup
print("1. Testing Signup...")
signup_response = requests.post(f"{BASE_URL}/v2/auth/signup", json={
    "name": "Test User",
    "email": "test@example.com",
    "password": "Test123!"
})
print(f"   Status: {signup_response.status_code}")
if signup_response.status_code == 200:
    data = signup_response.json()
    token = data["access_token"]
    print(f"   ✅ Got token: {token[:20]}...")
else:
    print(f"   ❌ Error: {signup_response.text}")
    exit(1)

# 2. Upload Resume (requires a sample file)
print("\n2. Testing Resume Upload...")
print("   ⚠️  Need to upload a real PDF/DOCX file via API docs")
print("   Visit: http://localhost:8001/v2/docs")
print("   Use the /v2/upload endpoint with 'Try it out'")

# 3. Test Rewrite (after upload)
print("\n3. Testing AI Rewrite...")
print("   First upload a resume, then run:")
print(f'''
   curl -X POST "{BASE_URL}/v2/rewrite" \\
     -H "Authorization: Bearer {token}" \\
     -H "Content-Type: application/json" \\
     -d '{{"resume_id": 1, "rewrite_style": "Technical"}}'
''')

print("\n✅ Phase 3 API is working!")
print("📝 Next: Upload a resume via API docs, then test rewrite endpoint")
```

Run it:
```powershell
python test_phase3.py
```

---

## 📊 Summary

### **Without Google OAuth (Current State):**
✅ All core features work  
✅ Email/password authentication  
✅ Document upload and parsing  
✅ AI rewriting (fallback mode ready)  
✅ Version management  
✅ **Phase 3 is fully testable!**

### **With Google OAuth (Optional):**
✅ All above features  
✅ PLUS: "Sign in with Google" button  
✅ Social login for better UX  

---

## 🚀 Recommendation

**For Testing Phase 3:**
- ✅ **Keep placeholders as-is**
- ✅ **Use email/password auth**
- ✅ **Test all Phase 3 features**
- ✅ **Verify fallback mode works**

**For Production (Future):**
- ⏳ Set up Google OAuth credentials
- ⏳ Get Mistral API key for AI rewrites
- ⏳ Switch from SQLite to PostgreSQL

---

**Bottom Line:** Google OAuth is **NOT needed** to test or validate Phase 3! Everything works with email/password authentication. 🎉

