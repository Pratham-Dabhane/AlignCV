# AlignCV V2 - Phase 3 Setup Guide
## AI Resume Rewriting with Mistral 7B

---

## 📋 Phase 3 Overview

**Phase 3** adds intelligent resume rewriting powered by **Mistral 7B LLM** with:
- 3 professional writing styles (Technical, Management, Creative)
- Quantifiable metrics and ATS-friendly optimization
- Document versioning with diff viewer
- Fallback mode for testing without API key
- Comprehensive error handling and logging

---

## 🎯 What Was Added

### **1. AI Rewrite Engine** (`backend/v2/ai/rewrite_engine.py`)
- Mistral 7B API integration with async httpx
- 3 style-specific prompt templates:
  - **Technical**: Emphasizes skills, tools, metrics
  - **Management**: Focuses on leadership, business impact
  - **Creative**: Highlights innovation and unique contributions
- Structured JSON response parsing
- Intelligent fallback mode when API unavailable
- SpaCy keyphrase extraction for keyword enhancement

### **2. API Routes** (`backend/v2/ai/routes.py`)
- `POST /v2/rewrite` - Rewrite resume with selected style
- `GET /v2/rewrite/versions/{resume_id}` - List all versions
- `GET /v2/rewrite/version/{version_id}` - Get specific version with diff
- HTML diff generation for before/after comparison
- Comprehensive logging to `logs/week3_4.log`

### **3. Database Model** (`backend/v2/models/models.py`)
- **DocumentVersion** table:
  - Links to original document and user
  - Stores original + rewritten text
  - Tracks rewrite style, improvements, impact score
  - Records API latency and status
  - JSON fields for improvements and keyphrases

### **4. Configuration Updates**
- Added `MISTRAL_API_KEY` to config and .env
- Updated requirements.txt with mistralai/openai SDKs
- Configured fallback behavior for testing

### **5. Comprehensive Tests** (`tests/test_v2_ai.py`)
- 15+ test cases covering:
  - Prompt template validation
  - Successful Mistral API calls (mocked)
  - Fallback mode behavior
  - Timeout and HTTP error handling
  - Invalid style handling
  - Keyphrase extraction
  - All three writing styles

---

## 🔧 Installation Steps

### **1. Install Dependencies**

```powershell
# Install new packages for Phase 3
pip install mistralai==0.1.0 openai==1.6.0

# Or install all requirements
pip install -r requirements.txt
```

### **2. Get Mistral API Key**

**Option A: Free Mistral API** (Recommended for testing)
1. Visit https://console.mistral.ai/
2. Sign up for free account
3. Generate API key from dashboard
4. Free tier includes limited credits

**Option B: Test Without API Key**
- Phase 3 works in **fallback mode** without API key
- Returns original text with informative message
- Perfect for testing integration first

### **3. Configure Environment**

Add to your `.env` file:

```bash
# Mistral AI Configuration
MISTRAL_API_KEY=your-mistral-api-key-here
MISTRAL_MODEL=mistral-small-latest
```

**Note**: Leave as `your-mistral-api-key-here` to test fallback mode

---

## 🚀 Running Phase 3

### **1. Start V2 Backend**

```powershell
# From project root
$env:PYTHONPATH="C:\Pra_programming\Projects\ALIGN"
python -m uvicorn backend.v2.app_v2:app_v2 --reload --port 8001
```

**Expected output:**
```
AlignCV V2 Starting...
Initializing database...
Database initialized successfully
Environment: development
Debug mode: True
Storage backend: local
AlignCV V2 ready!
```

### **2. Verify API Documentation**

Open browser to: http://localhost:8001/v2/docs

You should see new endpoints:
- `POST /v2/rewrite` - Rewrite resume
- `GET /v2/rewrite/versions/{resume_id}` - List versions
- `GET /v2/rewrite/version/{version_id}` - Get version detail

---

## 📝 API Usage Examples

### **1. Upload a Resume** (if not already done)

```bash
# First, signup and login to get JWT token
curl -X POST "http://localhost:8001/v2/auth/signup" \
  -H "Content-Type: application/json" \
  -d "{\"name\":\"Test User\",\"email\":\"test@example.com\",\"password\":\"Test123!\"}"

# Response will include access_token - save it
```

```bash
# Upload resume
curl -X POST "http://localhost:8001/v2/upload" \
  -H "Authorization: Bearer YOUR_ACCESS_TOKEN" \
  -F "file=@path/to/resume.pdf"

# Response includes resume_id - save it
```

### **2. Rewrite Resume**

```bash
curl -X POST "http://localhost:8001/v2/rewrite" \
  -H "Authorization: Bearer YOUR_ACCESS_TOKEN" \
  -H "Content-Type: application/json" \
  -d "{\"resume_id\":1,\"rewrite_style\":\"Technical\"}"
```

**Response (Fallback Mode - No API Key):**
```json
{
  "version_id": 1,
  "resume_id": 1,
  "original_text": "John Doe\nSoftware Engineer...",
  "rewritten_text": "John Doe\nSoftware Engineer...",
  "diff_html": "<div class=\"diff-viewer\">...</div>",
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

**Response (With Valid API Key):**
```json
{
  "version_id": 1,
  "resume_id": 1,
  "original_text": "Worked on backend systems using Python...",
  "rewritten_text": "Architected and optimized backend microservices serving 100K+ requests/day using Python...",
  "diff_html": "<div class=\"diff-viewer\">...</div>",
  "improvements": [
    "Added quantifiable metrics (100K+ requests/day)",
    "Enhanced technical terminology",
    "Improved ATS keyword density",
    "Structured content for better readability"
  ],
  "impact_score": 88,
  "style": "Technical",
  "latency": 2.34,
  "api_status": "success"
}
```

### **3. List All Versions**

```bash
curl -X GET "http://localhost:8001/v2/rewrite/versions/1" \
  -H "Authorization: Bearer YOUR_ACCESS_TOKEN"
```

**Response:**
```json
{
  "resume_id": 1,
  "versions": [
    {
      "version_id": 1,
      "style": "Technical",
      "impact_score": 88,
      "improvements": ["Added quantifiable metrics", "Enhanced terminology"],
      "keyphrases": ["python", "backend systems", "microservices"],
      "created_at": "2025-10-17T10:30:00",
      "api_status": "success"
    },
    {
      "version_id": 2,
      "style": "Management",
      "impact_score": 85,
      "improvements": ["Emphasized leadership", "Added business metrics"],
      "created_at": "2025-10-17T10:35:00",
      "api_status": "success"
    }
  ]
}
```

### **4. Get Specific Version**

```bash
curl -X GET "http://localhost:8001/v2/rewrite/version/1" \
  -H "Authorization: Bearer YOUR_ACCESS_TOKEN"
```

---

## 🧪 Testing Phase 3

### **Run All Tests**

```powershell
# Run Phase 3 tests only
pytest tests/test_v2_ai.py -v

# Run all V2 tests
pytest tests/test_v2*.py -v

# Run with coverage
pytest tests/test_v2_ai.py --cov=backend.v2.ai --cov-report=html
```

**Expected output:**
```
tests/test_v2_ai.py::test_style_prompts_exist PASSED
tests/test_v2_ai.py::test_style_prompts_have_placeholder PASSED
tests/test_v2_ai.py::test_fallback_response_preserves_text PASSED
tests/test_v2_ai.py::test_fallback_response_with_error PASSED
tests/test_v2_ai.py::test_rewrite_resume_no_api_key PASSED
tests/test_v2_ai.py::test_rewrite_resume_success PASSED
tests/test_v2_ai.py::test_rewrite_resume_invalid_style PASSED
tests/test_v2_ai.py::test_rewrite_resume_timeout PASSED
tests/test_v2_ai.py::test_rewrite_resume_http_error PASSED
...

=============== 15 passed in 2.34s ===============
```

### **Test Standalone Rewrite Engine**

Create `scripts/test_rewrite.py`:

```python
import asyncio
from backend.v2.ai.rewrite_engine import rewrite_resume

sample_text = """
John Doe
Senior Software Engineer

Experience:
- Worked on backend systems
- Used Python and SQL
- Fixed bugs and added features

Skills: Python, SQL, JavaScript, Docker
"""

async def main():
    result = await rewrite_resume(sample_text, "Technical")
    print(f"Status: {result['api_status']}")
    print(f"Impact Score: {result['impact_score']}")
    print(f"\nOriginal ({result['original_length']} chars):")
    print(sample_text[:200])
    print(f"\nRewritten ({result['rewritten_length']} chars):")
    print(result['rewritten_text'][:200])
    print(f"\nImprovements:")
    for imp in result['improvements']:
        print(f"  - {imp}")

asyncio.run(main())
```

Run it:
```powershell
python scripts/test_rewrite.py
```

---

## 📊 Monitoring & Logs

### **Check Logs**

Phase 3 logs to `logs/week3_4.log`:

```powershell
# View real-time logs
Get-Content logs/week3_4.log -Tail 20 -Wait

# Search for errors
Select-String -Path logs/week3_4.log -Pattern "ERROR"

# Check API latency
Select-String -Path logs/week3_4.log -Pattern "Latency"
```

**Example log entries:**
```
2025-10-17 10:30:15 - backend.v2.ai.routes - INFO - Rewrite request - User: test@example.com, Document: 1, Style: Technical
2025-10-17 10:30:15 - backend.v2.ai.rewrite_engine - INFO - Calling Mistral API with style: Technical, text length: 450
2025-10-17 10:30:17 - backend.v2.ai.rewrite_engine - INFO - Mistral API success - Latency: 2.34s, Response length: 612
2025-10-17 10:30:17 - backend.v2.ai.routes - INFO - Rewrite complete - Version: 1, Latency: 2.34s, Status: success
```

---

## ⚠️ Error Handling

### **Common Issues & Solutions**

1. **"Mistral API unavailable" (Fallback Mode)**
   - **Cause**: No API key or invalid key
   - **Solution**: Add valid MISTRAL_API_KEY to .env
   - **Test Mode**: This is expected behavior for testing

2. **"API timeout"**
   - **Cause**: Mistral API taking >30 seconds
   - **Solution**: Check network, try again, or increase timeout
   - **Result**: Falls back to original text

3. **"401 Unauthorized"**
   - **Cause**: Invalid or expired API key
   - **Solution**: Generate new key from Mistral console
   - **Result**: Falls back to original text

4. **"Document has no text content"**
   - **Cause**: PDF/DOCX parsing failed
   - **Solution**: Re-upload document with valid content

5. **ImportError for httpx**
   - **Cause**: httpx not installed
   - **Solution**: `pip install httpx`

---

## 🎨 Writing Style Guide

### **Technical Style**
- **Best For**: Software engineers, developers, data scientists
- **Focus**: Technical skills, tools, quantifiable performance metrics
- **Keywords**: Architecture, optimization, scalability, algorithms
- **Example**: "Architected microservices serving 100K+ requests/day"

### **Management Style**
- **Best For**: Team leads, managers, executives
- **Focus**: Leadership, business impact, team growth
- **Keywords**: Led team of X, increased revenue by Y%, stakeholder management
- **Example**: "Led cross-functional team of 15 engineers, delivering 3 major products"

### **Creative Style**
- **Best For**: Designers, marketers, content creators
- **Focus**: Innovation, unique contributions, engaging language
- **Keywords**: Innovative solutions, creative problem-solving, portfolio highlights
- **Example**: "Pioneered user-centric design system adopted across 5 product lines"

---

## 📈 Phase 3 Metrics

- **New Files**: 4 (rewrite_engine.py, routes.py, test_v2_ai.py, PHASE3_SETUP.md)
- **Lines of Code**: ~700+
- **Database Tables**: +1 (document_versions)
- **API Endpoints**: +3 (rewrite, versions list, version detail)
- **Test Cases**: +15
- **Dependencies**: +2 (mistralai, openai)

---

## ✅ Phase 3 Checklist

Before moving to next phase:

- [ ] Dependencies installed (`pip install -r requirements.txt`)
- [ ] Mistral API key added to .env (or test fallback mode)
- [ ] V2 backend running on port 8001
- [ ] API docs accessible at http://localhost:8001/v2/docs
- [ ] Tests passing (`pytest tests/test_v2_ai.py`)
- [ ] Can upload resume successfully
- [ ] Can rewrite resume (fallback or API mode)
- [ ] Versions saved to database
- [ ] Logs generated in logs/week3_4.log

---

## 🔜 Next Phase Preview

**Phase 4** will add:
- Advanced semantic matching with Qdrant vector database
- Resume-to-job similarity scoring
- Semantic search across job descriptions
- Embedding generation and storage

---

## 🆘 Support

**Issues?**
1. Check logs: `logs/week3_4.log` and `logs/v2_app.log`
2. Verify .env configuration
3. Test fallback mode first (no API key)
4. Run tests to isolate issue
5. Check API docs for endpoint details

**Working?** 🎉
- Phase 3 is production-ready
- Test all three writing styles
- Monitor API latency in logs
- Ready for Phase 4!

---

Generated: October 17, 2025
Version: AlignCV V2 Phase 3
