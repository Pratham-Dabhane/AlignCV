# 🎯 AlignCV - Your Career, Aligned

**Semantic resume matching tool that helps students align their resumes with job descriptions.**

[![Version](https://img.shields.io/badge/version-1.0.0-blue.svg)](https://github.com/Pratham-Dabhane/AlignCV)
[![Python](https://img.shields.io/badge/python-3.10+-blue.svg)](https://www.python.org/downloads/)
[![License](https://img.shields.io/badge/license-MIT-green.svg)](LICENSE)
[![Status](https://img.shields.io/badge/status-production--ready-brightgreen.svg)]()

## 🌟 Features

✨ **Semantic Matching** - Uses Sentence-BERT embeddings for intelligent similarity analysis (not just keyword matching)  
📊 **Match Score** - Get a 0-100% compatibility score with color-coded feedback  
✅ **Strengths Analysis** - Identify what you're doing right  
⚠️ **Gap Detection** - Discover what's missing from your resume  
📋 **Actionable Checklist** - Download personalized improvement plans  
🎨 **Professional UI** - Clean, branded interface with responsive design  
⚡ **Lightning Fast** - LRU caching for 10x faster repeated analyses  
🔒 **Privacy First** - All processing happens locally, no data storage  
💯 **100% Free** - No API costs, completely open source

## 🚀 Quick Start

### Option 1: Using Virtual Environment (Recommended)

```bash
# Clone the repository
git clone https://github.com/Pratham-Dabhane/AlignCV.git
cd AlignCV

# Create virtual environment
python -m venv .venv

# Activate virtual environment
# Windows:
.\.venv\Scripts\Activate.ps1
# Mac/Linux:
source .venv/bin/activate

# Install dependencies
pip install -r requirements.txt

# Start backend (Terminal 1)
cd backend
python -m uvicorn app:app --reload --port 8000

# Start frontend (Terminal 2)
cd frontend
streamlit run app.py
```

### Option 2: Without Virtual Environment

```bash
# Install dependencies
pip install -r requirements.txt

# Terminal 1: Backend
cd backend
uvicorn app:app --reload --port 8000

# Terminal 2: Frontend
cd frontend
streamlit run app.py
```

**Access the app:**
- Frontend: `http://localhost:8501` (or 8502)
- Backend API: `http://localhost:8000`
- API Docs: `http://localhost:8000/docs`

## 📁 Project Structure

```
AlignCV/
├── backend/
│   ├── api/                    # API modules
│   ├── utils/
│   │   ├── semantic_utils.py   # Core semantic matching engine
│   │   └── text_processing.py  # Text preprocessing utilities
│   ├── logs/                   # Application logs (gitignored)
│   └── app.py                  # FastAPI application
├── frontend/
│   ├── components/             # Reusable UI components
│   ├── pages/                  # Multi-page structure
│   └── app.py                  # Streamlit application
├── tests/
│   ├── test_api.py            # API endpoint tests
│   └── test_semantic_utils.py # Semantic matching tests (38 tests)
├── scripts/
│   ├── prewarm_model.py       # Pre-download ML model
│   └── test_semantic.py       # Quick semantic test
├── docs/
│   ├── ARCHITECTURE.md        # System architecture
│   ├── PHASE1_NOTES.md        # Phase 1 documentation
│   ├── PHASE2_NOTES.md        # Phase 2 documentation
│   ├── PHASE2_TEST_RESULTS.md # Phase 2 test results
│   ├── PHASE3_NOTES.md        # Phase 3 documentation
│   ├── PHASE4_NOTES.md        # Phase 4 documentation
│   └── PHASE4_TEST_RESULTS.md # Phase 4 test results
├── requirements.txt           # Python dependencies
├── TESTING.md                 # Testing guide
├── QUICKSTART.md              # Quick start guide
└── README.md                  # This file
```

## 🎨 Brand Identity

**Values:** Professional • Trustworthy • Empowering • Clear

**Color Palette:**
- Primary: Deep Blue (#1E3A8A)
- Secondary: Charcoal Gray (#374151)
- Accent: Teal (#14B8A6)
- Success: Green (#10B981)
- Warning: Orange (#F59E0B)

**Tagline:** "Your Career, Aligned"

## 🔧 Tech Stack

**Backend:**
- Python 3.10+
- FastAPI (Web framework)
- Sentence-Transformers (Semantic analysis)
- PyTorch (ML backend)
- Pydantic (Data validation)

**Frontend:**
- Streamlit (Rapid prototyping UI)
- Custom CSS (Brand styling)
- Responsive design

**ML/AI:**
- Sentence-BERT: `all-MiniLM-L6-v2` model
- Cosine similarity for matching
- LRU caching for performance

**Testing:**
- pytest (38 unit tests)
- 100% pass rate

**Cost:** 100% Free (local computation, no API calls)

## 📋 Development Phases (All Complete! ✅)

- [x] **Phase 1:** Foundations & Core Architecture
- [x] **Phase 2:** Semantic Matching & Scoring  
- [x] **Phase 3:** Frontend UX & Branding Integration
- [x] **Phase 4:** Optimization & Reliability
- [ ] **Phase 5:** Deployment & Analytics (Optional)

**Status:** ✅ V1.0 Production Ready

## 🎮 How It Works

### 1. **Input Your Information**
Paste your resume text and the job description you're targeting

### 2. **AI-Powered Analysis**
AlignCV uses Sentence-BERT to generate semantic embeddings and compute similarity

### 3. **Get Insights**
- **Match Score:** 0-100% compatibility
- **Strengths:** Requirements you already meet
- **Gaps:** Areas for improvement

### 4. **Take Action**
Download a personalized checklist to improve your resume

## 📸 Screenshots

### Match Score Dashboard
Color-coded score (Red/Orange/Teal/Green) with contextual feedback

### Strengths & Gaps Analysis
Collapsible sections showing detailed matches and missing elements

### Actionable Checklist
Downloadable markdown file with checkbox items and next steps

## 🚀 Performance Metrics

- **First Request:** ~3-5 seconds (model loading)
- **Cached Requests:** <1 second (10x faster)
- **Model Size:** 90.9 MB (downloads once)
- **Memory Usage:** ~500 MB
- **Test Coverage:** 38 passing tests
- **Accuracy:** Semantic similarity, not just keywords

## 🔒 Privacy & Security

- ✅ **No Data Storage:** Resume text is never saved
- ✅ **Local Processing:** All analysis happens on your machine
- ✅ **No External APIs:** No third-party services involved
- ✅ **Open Source:** Fully auditable code
- ✅ **No Tracking:** No analytics or user tracking

## 🧪 Testing

```bash
# Run all tests
pytest tests/ -v

# Run with coverage
pytest tests/ --cov=backend --cov-report=html

# Run specific test file
pytest tests/test_semantic_utils.py -v
```

**Test Results:**
- ✅ 38 tests passing
- ✅ API endpoint validation
- ✅ Semantic matching accuracy
- ✅ Error handling coverage
- ✅ Input validation tests

## 📊 API Endpoints

### POST `/analyze`
Analyze resume against job description

**Request:**
```json
{
  "resume_text": "Your resume text...",
  "job_description_text": "Job description text..."
}
```

**Response:**
```json
{
  "match_score": 77.33,
  "strengths": ["Strength 1", "Strength 2"],
  "gaps": ["Gap 1", "Gap 2"],
  "message": "Analysis complete"
}
```

### GET `/health`
Health check endpoint

### GET `/metrics`
Get application metrics (requests, cache stats, response times)

### GET `/docs`
Interactive API documentation (Swagger UI)

## 🛠️ Configuration

### Environment Variables (Optional)

```bash
# Backend Configuration
API_PORT=8000
LOG_LEVEL=INFO

# Frontend Configuration
FRONTEND_PORT=8501
API_URL=http://localhost:8000
```

### Customization

**Change Model:**
Edit `backend/utils/semantic_utils.py`:
```python
model = SentenceTransformer('all-MiniLM-L6-v2')
# Change to: 'paraphrase-MiniLM-L6-v2', etc.
```

**Adjust Cache Size:**
Edit `backend/utils/semantic_utils.py`:
```python
@lru_cache(maxsize=100)  # Increase for more caching
```

## 🤝 Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

**Areas for Contribution:**
- Additional ML models
- Resume file upload (PDF/DOCX)
- Multi-language support
- Dark mode theme
- Advanced analytics
- Mobile app version

## 📝 License

This project is licensed under the MIT License - see the LICENSE file for details.

## 👤 Author

**Pratham Dabhane**
- GitHub: [@Pratham-Dabhane](https://github.com/Pratham-Dabhane)
- Repository: [AlignCV](https://github.com/Pratham-Dabhane/AlignCV)

## 🙏 Acknowledgments

- Sentence-Transformers library for semantic embeddings
- FastAPI for the excellent web framework
- Streamlit for rapid UI development
- Hugging Face for model hosting

## 📈 Roadmap

**Completed (V1.0):**
- ✅ Semantic matching engine
- ✅ Professional UI/UX
- ✅ Caching & optimization
- ✅ Comprehensive testing
- ✅ Error handling & logging

**Future Enhancements:**
- [ ] PDF/DOCX file upload
- [ ] Multi-resume comparison
- [ ] Industry-specific templates
- [ ] ATS keyword optimization
- [ ] Browser extension
- [ ] Mobile app
- [ ] API rate limiting
- [ ] User accounts (optional)

## 🐛 Known Issues

None! All major issues resolved in V1.0 ✅

Report issues at: https://github.com/Pratham-Dabhane/AlignCV/issues

## 💡 Tips for Best Results

1. **Provide Detailed Resumes:** 100+ words work best
2. **Use Complete Job Descriptions:** Include requirements and responsibilities
3. **Include Technical Keywords:** Languages, frameworks, tools
4. **First Run is Slower:** Model downloads once (~90MB)
5. **Cached Results are Fast:** Repeated JDs return instantly

## 📞 Support

- 📧 Issues: [GitHub Issues](https://github.com/Pratham-Dabhane/AlignCV/issues)
- 📖 Docs: See `/docs` folder for detailed documentation
- 💬 Questions: Open a GitHub Discussion

---

<div align="center">

**🎯 AlignCV - Your Career, Aligned**

Made with ❤️ by Pratham Dabhane

[⭐ Star this repo](https://github.com/Pratham-Dabhane/AlignCV) if you find it helpful!

</div>
