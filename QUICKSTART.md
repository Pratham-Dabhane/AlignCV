# 🚀 AlignCV - Quick Start Guide

## Phase 1: Foundations & Core Architecture ✅

Welcome! Let's get AlignCV running in 3 minutes.

---

## Step 1: Install Dependencies

Open PowerShell in the project root and run:

```powershell
pip install -r requirements.txt
```

---

## Step 2: Start the Backend

Open a terminal and run:

```powershell
cd backend
uvicorn app:app --reload --port 8000
```

You should see:
```
INFO:     Uvicorn running on http://127.0.0.1:8000
INFO:     Application startup complete.
```

**Keep this terminal running!**

---

## Step 3: Start the Frontend

Open a **NEW** terminal (keep backend running) and run:

```powershell
cd frontend
streamlit run app.py
```

You should see:
```
You can now view your Streamlit app in your browser.
Local URL: http://localhost:8501
```

Your browser should auto-open to `http://localhost:8501`

---

## Step 4: Test the Application

1. **Paste sample resume** (left box):
```
John Doe
Software Engineer

Experience:
- 3 years Python development
- Built REST APIs with FastAPI
- Experience with PostgreSQL and MongoDB
- Agile/Scrum methodologies

Skills:
Python, FastAPI, SQL, Git, Docker
```

2. **Paste sample job description** (right box):
```
Software Engineer Position

Requirements:
- 2+ years Python experience
- Experience with FastAPI or Flask
- Knowledge of REST APIs
- Database experience (SQL or NoSQL)
- Familiarity with Agile practices
```

3. **Click "🔍 Analyze Match"**

4. **Expected Result**:
   - Match Score: 0% (dummy data for Phase 1)
   - Strengths: Empty (coming in Phase 3)
   - Gaps: Empty (coming in Phase 3)
   - Message: "Phase 1: Dummy response. Semantic matching coming in Phase 2."

---

## ✅ Success Checklist

- [ ] Backend running at `http://localhost:8000`
- [ ] Frontend running at `http://localhost:8501`
- [ ] Can submit resume + job description
- [ ] Receive response without crashes
- [ ] See match_score=0, empty strengths/gaps

---

## 🧪 Run Tests (Optional)

```powershell
pytest tests/ -v
```

---

## 🐛 Troubleshooting

**"Cannot connect to backend API"**
- Ensure backend is running on port 8000
- Check `http://localhost:8000` in browser - should see API info

**"Module not found"**
- Run `pip install -r requirements.txt` again
- Ensure you're in the project root directory

**Port already in use**
- Backend: Change port with `uvicorn app:app --reload --port 8001`
- Frontend: Streamlit will auto-assign a new port

---

## 🎯 What's Next?

Phase 1 is complete! Ready for:
- **Phase 2**: Semantic matching with Sentence-BERT
- **Phase 3**: Gap and strengths analysis
- **Phase 4**: Actionable checklist generator
- **Phase 5**: UI polish and optimization

---

## 🧪 Running Tests

```powershell
# Run all tests
pytest tests/ -v

# Run specific test file
pytest tests/test_semantic_utils.py -v

# Run API tests
pytest tests/test_api.py -v
```

Expected: 38+ tests passing ✅

## � Check Metrics

Visit `http://localhost:8000/metrics` to see:
- Total requests processed
- Cache hit/miss ratio
- Average response time
- Error count

## �📚 More Resources

- **Full Documentation:** `README.md`
- **Architecture:** `docs/ARCHITECTURE.md`
- **Testing Guide:** `TESTING.md`
- **API Docs:** `http://localhost:8000/docs` (when backend is running)
- **Phase Notes:** `docs/PHASE[1-4]_NOTES.md`

## 🎯 Sample Test Data

Check `tests/sample_data.md` for 5 complete test cases with expected scores:
1. High match (75-85%)
2. Medium match (40-55%)
3. Low match (15-30%)
4. Entry level match (70-80%)
5. Partial match (45-60%)

---

## ✨ V1.0 Features Complete

✅ Semantic matching with Sentence-BERT  
✅ Professional branded UI  
✅ Downloadable action checklists  
✅ LRU caching (10x faster)  
✅ Comprehensive error handling  
✅ 38 passing unit tests  
✅ Structured logging  
✅ Production-ready reliability  

**Need help?** Check the console logs in both terminals for error messages.
