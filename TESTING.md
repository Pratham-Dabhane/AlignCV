# 🧪 Quick Testing Guide for AlignCV Phase 2

## ⚡ First Time Setup (IMPORTANT!)

The embedding model loads lazily on first use. The first request may take 1–2 minutes to download the model; subsequent requests are fast.

---

## Prerequisites
✅ Dependencies installed: `sentence-transformers`, `torch`, etc.
✅ Backend running on port 8000
✅ Frontend running on port 8501

---

## Method 1: Manual UI Testing (Easiest)

### Start the Servers

**Terminal 1 - Backend:**
```powershell
cd backend
uvicorn app:app --reload --port 8000
```

**Terminal 2 - Frontend:**
```powershell
cd frontend
streamlit run app.py
```

### Test Case 1: High Match (Expected: 75-85%)

**Resume (paste in left box):**
```
Sarah Johnson
Software Engineer

EXPERIENCE:
Senior Software Engineer at TechCorp (2021-Present)
- Developed REST APIs using Python and FastAPI framework
- Built microservices architecture with Docker and Kubernetes
- Implemented CI/CD pipelines with Jenkins and GitHub Actions
- Worked with PostgreSQL and MongoDB databases
- Led a team of 3 junior developers in Agile/Scrum environment

Software Engineer at StartupXYZ (2019-2021)
- Created web applications using React and Node.js
- Integrated third-party APIs and payment systems
- Wrote unit tests with pytest and maintained 90% code coverage

SKILLS:
Python, FastAPI, Django, JavaScript, React, SQL, MongoDB, Docker, Kubernetes, Git, Agile

EDUCATION:
BS Computer Science, University of California (2019)
```

**Job Description (paste in right box):**
```
Software Engineer Position

We are seeking a talented Software Engineer to join our backend team.

REQUIREMENTS:
- 2+ years of experience in software development
- Strong proficiency in Python
- Experience with FastAPI or Flask framework
- Knowledge of REST API design and implementation
- Familiarity with SQL and NoSQL databases (PostgreSQL, MongoDB)
- Experience with containerization (Docker)
- Understanding of Agile methodologies
- Strong problem-solving and communication skills

NICE TO HAVE:
- Kubernetes experience
- CI/CD pipeline knowledge
- React or frontend development experience
```

**Expected Results:**
- ✅ Match Score: 75-85% (Green "Excellent Match!")
- ✅ Strengths: Should show Python, FastAPI, Docker, PostgreSQL, etc.
- ✅ Gaps: Minimal or none

---

### Test Case 2: Low Match (Expected: 15-30%)

**Resume (paste in left box):**
```
Emily Rodriguez
Marketing Manager

EXPERIENCE:
Marketing Manager at BrandCo (2019-Present)
- Developed marketing strategies and campaigns
- Managed social media accounts (Instagram, Twitter, LinkedIn)
- Analyzed campaign performance with Google Analytics
- Led a team of 5 marketing specialists
- Increased brand awareness by 150%

Marketing Coordinator at MediaAgency (2017-2019)
- Created content for blogs and email campaigns
- Coordinated events and product launches

SKILLS:
Social Media Marketing, Content Creation, Google Analytics, SEO, Email Marketing, Leadership

EDUCATION:
BA Marketing, New York University (2017)
```

**Job Description (paste in right box):**
```
Backend Software Engineer

We need a Backend Engineer for our infrastructure team.

REQUIREMENTS:
- 5+ years backend development experience
- Expert in Java, Go, or Python
- Microservices architecture experience
- Strong knowledge of databases, caching, and message queues
- Cloud platform experience (AWS, GCP, Azure)
- System design and scalability expertise
```

**Expected Results:**
- ✅ Match Score: 15-30% (Red "Needs Improvement")
- ✅ Strengths: Very few or generic ones
- ✅ Gaps: Many technical requirements missing

---

## Method 2: API Testing (For Developers)

### Test with cURL (PowerShell)

```powershell
$body = @{
    resume_text = "Software Engineer with 5 years experience in Python, FastAPI, Docker, and PostgreSQL. Built REST APIs and microservices."
    job_description_text = "Looking for a Software Engineer with Python experience, REST API knowledge, and database skills."
} | ConvertTo-Json

Invoke-RestMethod -Uri "http://localhost:8000/analyze" -Method Post -Body $body -ContentType "application/json"
```

### Test with Python

```python
import requests

response = requests.post(
    "http://localhost:8000/analyze",
    json={
        "resume_text": "Software Engineer with 5 years Python and FastAPI experience...",
        "job_description_text": "Looking for Software Engineer with Python skills..."
    }
)

print(response.json())
```

---

## Method 3: Automated Tests (Most Thorough)

```powershell
# Run all tests
pytest tests/test_api.py -v

# Run specific test
pytest tests/test_api.py::test_analyze_semantic_matching -v
```

---

## What to Look For

### ✅ Success Indicators
- Match score between 0-100%
- Strengths list populated (if good match)
- Gaps list populated (if missing requirements)
- No errors in console
- Response time < 5 seconds (first request may take longer for model loading)

### ❌ Common Issues

**Issue: "Request timed out. Please try again."**
- **Cause:** First run downloads the model and may exceed timeout
- **Solution:** Retry after a minute — the model finishes downloading in the background; subsequent runs are fast (1–2 seconds)

**Issue: "Cannot connect to backend API"**
- Solution: Make sure backend is running on port 8000
- Check: Visit `http://localhost:8000` in browser - should see API info

**Issue: "Model downloading..." (backend logs)**
- This is normal! First run downloads ~80MB model
- Wait 1-2 minutes for initial download
- Subsequent runs will be fast

**Issue: Import errors**
- Solution: Run `pip install -r requirements.txt`
- Make sure you're in the project root directory

---

## Quick Health Check

### 1. Backend Health
Visit: `http://localhost:8000/health`

Should see:
```json
{
  "status": "healthy",
  "api_version": "0.2.0",
  "endpoints": {
    "analyze": "/analyze",
    "health": "/health"
  }
}
```

### 2. API Docs
Visit: `http://localhost:8000/docs`
- Interactive Swagger UI
- Test endpoints directly from browser

---

## Performance Benchmarks

- **First request:** 3-5 seconds (model loading)
- **Subsequent requests:** 1-2 seconds
- **Memory usage:** ~500MB (model + runtime)
- **Model size:** ~80MB (downloads once)

---

## Tips for Best Results

1. **Use detailed resumes** (100+ words)
2. **Use complete job descriptions** (not just titles)
3. **Include technical keywords** (Python, Docker, etc.)
4. **First analysis is slower** (model loading)
5. **Keep backend running** for faster subsequent tests

---

## Need More Test Cases?

Check `tests/sample_data.md` for 5 complete test scenarios:
1. High match (75-85%)
2. Medium match (40-55%)
3. Low match (15-30%)
4. Entry level match (70-80%)
5. Partial match (45-60%)

---

**Ready to test?** Start both servers and paste Sample 1 data! 🚀
