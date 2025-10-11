# AlignCV - Your Career, Aligned

**Goal:** Students paste resumes + job descriptions → semantic match → strengths & gaps → actionable checklist.

## 🚀 Quick Start

### Backend (FastAPI)
```bash
# Install dependencies
pip install -r requirements.txt

# Run backend server
cd backend
uvicorn app:app --reload --port 8000
```

Backend will run at: `http://localhost:8000`

### Frontend (Streamlit)
```bash
# In a new terminal
cd frontend
streamlit run app.py
```

Frontend will run at: `http://localhost:8501`

## 📁 Project Structure

```
/backend
    /api          - API routes and endpoints
    /utils        - Utility functions (future: semantic matching)
    app.py        - Main FastAPI application
/frontend
    /components   - Reusable UI components
    /pages        - Streamlit pages
    app.py        - Main Streamlit app
/tests           - Unit and integration tests
/docs            - Documentation
```

## 🎨 Brand Concept
- Professional, trustworthy, empowering, clear
- Colors: Deep blue (#1E3A8A), Charcoal gray (#374151), Teal accent (#14B8A6)

## 📋 Development Phases
- [x] Phase 1: Foundations & Core Architecture
- [x] Phase 2: Semantic Matching & Scoring
- [ ] Phase 3: TBD
- [ ] Phase 4: TBD
- [ ] Phase 5: TBD

## 🔧 Tech Stack
- Backend: Python + FastAPI
- Frontend: Streamlit (MVP) / React (future)
- **Semantic Matching: Sentence-BERT (all-MiniLM-L6-v2) ✅**
- Vector Similarity: Cosine similarity with PyTorch
- Cost: 100% Free (local computation, no API calls)
