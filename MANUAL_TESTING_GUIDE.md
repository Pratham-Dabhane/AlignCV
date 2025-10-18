# 🧪 Phase 5/6 Manual Testing Guide

## Current Status
- ✅ Server Running: Yes (PID: Check with `Get-Process python`)
- ✅ Port: 8001
- ✅ Base URL: http://localhost:8001

---

## 📋 Step-by-Step Testing Instructions

### **STEP 1: Verify Server Health** ✅

Open your browser or use curl:

**Browser Method:**
```
http://localhost:8001/v2/health
```

**PowerShell Method:**
```powershell
curl http://localhost:8001/v2/health
```

**Expected Response:**
```json
{
  "status": "healthy",
  "version": "2.0.0",
  "environment": "development"
}
```

---

### **STEP 2: Open Swagger UI** 🎯

1. **Open your browser and go to:**
   ```
   http://localhost:8001/v2/docs
   ```

2. **You should see:**
   - Interactive API documentation
   - List of all endpoints organized by tags:
     - Auth
     - Documents
     - **Jobs** ← This is what we're testing
     - AI Rewrite

---

### **STEP 3: Authenticate** 🔐

Before testing job endpoints, you need a JWT token:

1. **In Swagger UI, find the Auth section**

2. **Click on `POST /v2/auth/login`**

3. **Click "Try it out"**

4. **Enter the test credentials:**
   ```json
   {
     "email": "test_phase56@example.com",
     "password": "TestPassword123!"
   }
   ```

5. **Click "Execute"**

6. **Copy the `access_token` from the response:**
   ```json
   {
     "user": {...},
     "tokens": {
       "access_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",  ← COPY THIS
       "refresh_token": "..."
     }
   }
   ```

7. **Click the "Authorize" button at the top of the page**

8. **Paste the token in the "Value" field:**
   ```
   Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...
   ```
   ⚠️ **Note:** Include the word "Bearer" followed by a space, then the token

9. **Click "Authorize"** then **"Close"**

---

### **STEP 4: Test Job Ingestion** 💼

This is where we're currently getting the 500 error. Let's see the actual error:

1. **In Swagger UI, scroll down to the "Jobs" section**

2. **Click on `POST /v2/jobs/ingest`**

3. **Click "Try it out"**

4. **Click "Execute"** (no body needed)

5. **Watch the Response:**

   **If SUCCESS (Status 200):**
   ```json
   {
     "total_ingested": 10,
     "new_jobs": 10,
     "updated_jobs": 0,
     "embeddings_created": 10,
     "source": "mock"
   }
   ```

   **If ERROR (Status 500):**
   - Look at the error message in the response
   - **ALSO:** Go to your terminal where the server is running
   - You should see a Python traceback with the actual error

---

### **STEP 5: Check Server Logs** 📝

**In the terminal where the server is running, look for:**

1. **Red ERROR lines** - These show what went wrong
2. **Traceback** - Shows the exact line that failed
3. **Common Issues to Look For:**
   - `ConnectionError` → Qdrant connection issue
   - `APIError` → Mistral API issue
   - `KeyError` → Missing environment variable
   - `ModuleNotFoundError` → Missing dependency

**Example of what you might see:**
```
ERROR: Exception in ASGI application
Traceback (most recent call last):
  File "...", line X, in ingest_jobs
    ...
ConnectionError: Cannot connect to Qdrant at ...
```

---

### **STEP 6: Debug Common Issues** 🔧

#### **Issue A: Qdrant Connection Error**

**Test Qdrant Connection:**
```powershell
.venv\Scripts\python.exe test_qdrant_connection.py
```

**Expected:** "🎉 Qdrant is connected and ready!"

**If it fails:**
- Check `.env` file has correct Qdrant credentials
- Verify the cluster URL is accessible
- Check API key is valid

---

#### **Issue B: Mistral API Error**

**Test Mistral API:**
```powershell
.venv\Scripts\python.exe -c "import os; from dotenv import load_dotenv; load_dotenv(); print('Mistral Key:', os.getenv('MISTRAL_API_KEY')[:20] + '...')"
```

**Should show:** `Mistral Key: Zw7CCC515LLO8072...`

**If the key is wrong or rate-limited:**
- The system will automatically fall back to local embeddings
- But you'll see warnings in the logs

---

#### **Issue C: Missing Dependency**

**If you see `ModuleNotFoundError`:**
```powershell
.venv\Scripts\pip.exe install sentence-transformers qdrant-client beautifulsoup4 feedparser
```

---

### **STEP 7: If Ingestion Works - Test Matching** 🎯

Once ingestion succeeds, test job matching:

1. **First, upload a resume (if you haven't):**
   - In Swagger UI: `POST /v2/upload`
   - Upload a PDF/DOCX file
   - Note the `document_id` from response

2. **Test Job Matching:**
   - In Swagger UI: `POST /v2/jobs/match`
   - Click "Try it out"
   - Enter request body:
   ```json
   {
     "resume_id": 5,
     "top_k": 5,
     "min_salary": 100000
   }
   ```
   - Click "Execute"

3. **Expected Response:**
   ```json
   [
     {
       "job_id": "mock-001",
       "title": "Senior Software Engineer",
       "company": "TechCorp",
       "fit_percentage": 85,
       "vector_score": 78.5,
       "skill_score": 92.3,
       "matched_skills": ["Python", "FastAPI", "AWS"],
       "gap_skills": ["Golang", "gRPC"],
       ...
     },
     ...
   ]
   ```

---

### **STEP 8: Test Other Endpoints** 📊

**Get All Jobs:**
```
GET /v2/jobs/?limit=10
```

**Bookmark a Job:**
```json
POST /v2/jobs/bookmark
{
  "job_id": 1,
  "notes": "Great company culture!"
}
```

**Track Application:**
```json
POST /v2/jobs/apply
{
  "job_id": 1,
  "status": "applied",
  "notes": "Applied via company website"
}
```

**Get Qdrant Stats:**
```
GET /v2/jobs/stats
```

---

## 🐛 Debugging Checklist

If you encounter errors, check these in order:

### 1. **Server Running?**
```powershell
Get-Process python | Where-Object {$_.Path -like "*\.venv\*"}
```

### 2. **Port Available?**
```powershell
netstat -ano | findstr :8001
```

### 3. **Environment Variables Loaded?**
```powershell
Get-Content .env | Select-String "QDRANT|MISTRAL"
```

### 4. **Qdrant Reachable?**
```powershell
curl https://97d88b43-0b84-4101-a216-157bd3dc167d.europe-west3-0.gcp.cloud.qdrant.io:6333/collections
```

### 5. **Database Created?**
```powershell
Test-Path .\aligncv_test.db
```

### 6. **Dependencies Installed?**
```powershell
.venv\Scripts\pip.exe list | Select-String "qdrant|sentence-transformers"
```

---

## 📸 What to Check in Terminal

**When you run the ingest endpoint, watch for:**

```
✅ GOOD SIGNS:
- "Loading mock jobs..."
- "Creating embeddings..."
- "Upserting to Qdrant..."
- "Successfully ingested X jobs"

❌ ERROR SIGNS:
- "ERROR: ..." (any red text)
- "ConnectionError"
- "401 Unauthorized"
- "500 Internal Server Error"
- Traceback messages
```

---

## 🎯 Quick Test Commands

**Run all at once:**
```powershell
# 1. Test health
curl http://localhost:8001/v2/health

# 2. Get login token
$response = Invoke-RestMethod -Uri "http://localhost:8001/v2/auth/login" -Method POST -Body (@{email="test_phase56@example.com"; password="TestPassword123!"} | ConvertTo-Json) -ContentType "application/json"
$token = $response.tokens.access_token

# 3. Test ingestion
Invoke-RestMethod -Uri "http://localhost:8001/v2/jobs/ingest" -Method POST -Headers @{Authorization="Bearer $token"} -ContentType "application/json"
```

---

## 📞 Next Steps Based on Results

### ✅ **If Everything Works:**
Run the full automated test:
```powershell
.venv\Scripts\python.exe scripts\test_complete_workflow.py
```

### ❌ **If You Get Errors:**
1. **Copy the error message** from the terminal
2. **Copy the traceback** (if shown)
3. **Check which step failed** (ingestion, matching, etc.)
4. The error message will tell us exactly what to fix!

---

## 🔍 Most Likely Issue

Based on the 500 error, it's probably one of these:

1. **Qdrant collection creation failing** (most likely)
   - Solution: Check if collection already exists or needs recreation

2. **Embedding generation timing out**
   - Solution: Use local embeddings only (faster)

3. **Mock data format issue**
   - Solution: Validate the job schema

**To find out:** Just run the ingestion in Swagger UI and look at the terminal output!

---

## ✨ Expected Final Result

When everything works, you should be able to:

1. ✅ Login successfully
2. ✅ Upload a resume
3. ✅ Ingest 10 mock jobs into Qdrant
4. ✅ Match jobs with resume (get ranked results)
5. ✅ Bookmark interesting jobs
6. ✅ Track job applications
7. ✅ View statistics

---

**Ready? Start with Step 1 and work your way through!** 🚀

The most important step is **STEP 4** - that's where we'll see the actual error message.
