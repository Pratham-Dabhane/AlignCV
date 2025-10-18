# Changelog

All notable changes to AlignCV will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

---

## [2.0.0] - 2025-10-19

### 🎉 V2.0 Release - Complete Career Management Platform with AI Resume Tailoring!

Major version release with complete V2 architecture, Phase 9 AI Resume Tailoring (THE KILLER FEATURE), and critical bug fixes.

### 🎯 Added - Phase 9: AI Resume Tailoring

**The feature that sets AlignCV apart from all competitors!**

#### Backend (`backend/v2/ai/`)
- ✨ **AI Tailoring Engine** (`rewrite_engine.py`):
  - `tailor_resume_to_job()` function with Mistral AI integration
  - Three tailoring levels: Conservative, Moderate, Aggressive
  - Sophisticated prompt engineering for each level
  - Fallback mode when API unavailable
  - Timeout handling (45 seconds)
  - JSON parsing and validation
  
- 🚀 **New API Endpoint** (`routes.py`):
  - `POST /v2/rewrite/tailor-to-job` - Tailor resume to specific job
  - `TailorResumeRequest` Pydantic schema with validation
  - `TailorResumeResponse` schema with 11 comprehensive fields
  - JWT authentication and document ownership verification
  - Full error handling with HTTPException

#### Frontend (`frontend/pages/documents.py`)
- 🎨 **New UI Tab**: "🎯 Tailor to Job" (4th tab in Documents page)
- **Input Components**:
  - Resume selector dropdown
  - Large job description textarea (250px height)
  - Tailoring level slider with emoji indicators
  - Original resume preview (optional)
  - Real-time validation (50 char minimum for JD)
  
- **Results Dashboard**:
  - Match score metric with color coding (🟢 80%+, 🟡 60-79%, 🔴 <60%)
  - Changes count display
  - Processing time metric
  - Missing skills analysis with red badges (❌)
  - Priority improvements list (top 3-5 critical changes)
  - Keyword suggestions (expandable section)
  - Detailed changes log (expandable section)
  - Before/after side-by-side comparison (400px text areas)
  - Download tailored resume button (TXT)
  - Download analysis report button (TXT)
  - Pro tips and success guidance (expandable)

#### Documentation
- 📚 **PHASE9_COMPLETE.md** (400+ lines):
  - Complete feature documentation
  - Technical implementation details
  - Use cases and benefits
  - Testing checklist
  - Pro tips for users
  - Known limitations
  - Future enhancements roadmap

- 📊 **PHASE9_SUMMARY.md** (1000+ lines):
  - Comprehensive overview with examples
  - Success metrics and projections
  - User story (Sarah's journey)
  - Market positioning analysis
  - Launch preparation guide

### 🐛 Fixed - Critical Bug Fixes (October 19, 2025)

#### 1. Documents API Response Structure Mismatch
- **Issue**: Frontend expected array `[]`, backend returned object `{"documents": []}`
- **Error**: `'str' object has no attribute 'get'`
- **Fix**: Added proper JSON parsing with type checking
- **Files**: `frontend/pages/documents.py` (3 sections)

#### 2. Upload Response Key Mismatch
- **Issue**: Frontend used wrong keys (`id`, `filename`, `extracted_text`)
- **Actual**: Backend returns (`document_id`, `file_name`, `parsed_text`)
- **Error**: Display showed "None" for all extracted data
- **Fix**: Updated all keys to match API response
- **Files**: `frontend/pages/documents.py`

#### 3. AI Rewrite Endpoint Path Incorrect
- **Issue**: Frontend calling `/v2/ai/rewrite-resume`
- **Actual**: Endpoint is `/v2/rewrite/`
- **Error**: 404 Not Found
- **Fix**: Corrected API endpoint path
- **Files**: `frontend/pages/documents.py`

#### 4. Missing extracted_text in Documents List
- **Issue**: Documents list only returned `text_preview` (200 chars)
- **Impact**: AI features couldn't access full resume text
- **Fix**: Added `extracted_text` field to list response
- **Files**: `backend/v2/documents/routes.py`

**Documentation**: See [BUGFIXES_SUMMARY.md](BUGFIXES_SUMMARY.md) for detailed analysis.

### 🔄 Changed

#### API Structure
- Updated documents list endpoint to include full `extracted_text`
- Improved error messages across all endpoints
- Enhanced response schemas with more detailed data

#### Frontend
- Changed Documents page from 3 to 4 tabs
- Improved error handling with better user messages
- Added loading spinners with context
- Enhanced success celebrations (balloons, confetti)

#### Documentation
- Updated README.md with V2 features and Phase 9
- Updated QUICKSTART.md for V2 architecture
- Added comprehensive troubleshooting guide
- Updated all badges to version 2.0.0

---

## [1.0.0] - 2025-10-12

### 🎉 V1.0 Release - Production Ready!

Complete implementation of all core features with production-grade reliability.

### Added

#### Phase 1: Foundations & Core Architecture
- Initial project structure with FastAPI backend and Streamlit frontend
- `/analyze` endpoint for resume analysis
- CORS middleware for frontend integration
- Basic API validation with Pydantic models
- Project documentation and setup guides

#### Phase 2: Semantic Matching & Scoring
- Sentence-BERT integration (`all-MiniLM-L6-v2` model)
- Semantic embedding generation
- Cosine similarity computation (0-100% scale)
- Strengths and gaps identification algorithm
- Keyword extraction from resumes and job descriptions
- Sentence-level analysis for detailed matching
- PDF and DOCX text extraction support (for future use)
- Comprehensive test suite with sample data
- Phase 2 documentation and test results

#### Phase 3: Frontend UX & Branding Integration
- Complete UI overhaul with brand identity
- Logo placeholder with glassmorphic design
- Gradient header with brand colors
- Animated progress bar for match scores
- Dynamic color-coded score cards (Red/Orange/Teal/Green)
- Collapsible sections for strengths and gaps
- Card-based design with hover effects
- Actionable checklist generator with download functionality
- Copy to clipboard feature
- Character counter with real-time validation
- Responsive design for mobile devices (< 768px)
- Professional typography with Inter font
- Enhanced error messages and loading indicators
- Preview checklist in expandable section

#### Phase 4: Optimization & Reliability
- LRU caching for embeddings (10x performance boost)
- LRU caching for job description analysis
- Comprehensive input validation and sanitization
- Input size limits (1MB max per field)
- Structured logging with file output to `backend/logs/`
- Request/response logging with timing information
- Error handling with user-friendly messages
- 38 comprehensive unit tests (100% pass rate)
- Metrics tracking endpoint (`/metrics`)
- Cache statistics (hits, misses, size)
- Performance monitoring (avg response time)
- Test suite for semantic_utils module
- Optimized text processing for large inputs
- Enhanced API error responses
- Phase 4 documentation and test results

### Changed
- Improved error messages across all endpoints
- Enhanced validation for resume and job description inputs
- Optimized model loading with lazy initialization
- Better separation of concerns in codebase
- Improved logging format with structured data

### Fixed
- Parameter name mismatch in analyze endpoint (Phase 2.1)
- Timeout issues on first request with model download
- Memory optimization for large text inputs
- Edge cases in keyword extraction
- Cross-browser CSS compatibility

### Performance
- First request: ~3-5 seconds (includes model loading)
- Cached requests: <1 second (10x improvement)
- Memory usage: ~500MB stable
- Model download: One-time 90.9MB download
- Cache hit rate: >80% for typical usage

### Security
- No data storage or persistence
- Local-only processing
- Input sanitization against injection
- Size limits to prevent DoS
- No external API dependencies

### Documentation
- Comprehensive README with all features
- QUICKSTART guide for rapid setup
- TESTING guide with multiple scenarios
- ARCHITECTURE documentation
- Phase-by-phase development notes (PHASE1-4_NOTES.md)
- Test results documentation (PHASE2_TEST_RESULTS.md, PHASE4_TEST_RESULTS.md)
- Sample test data with expected scores

### Testing
- 38 unit tests for semantic_utils
- API endpoint tests
- Error handling tests
- Input validation tests
- Cache functionality tests
- Performance benchmarks

---

## Roadmap for Future Versions

### [1.1.0] - Planned
- PDF/DOCX direct file upload
- Resume history (optional, no storage)
- Export results to PDF
- Dark mode theme

### [1.2.0] - Planned
- Multi-resume comparison
- Industry-specific matching templates
- ATS keyword optimization suggestions
- Enhanced skill extraction

### [2.0.0] - Future
- User accounts (optional)
- Browser extension
- Mobile application
- API rate limiting
- Multi-language support

---

## Version History

- **v1.0.0** (2025-10-12) - Initial production release ✅
- **v0.3.0** (2025-10-12) - Phase 3: UX & Branding
- **v0.2.0** (2025-10-11) - Phase 2: Semantic Matching
- **v0.1.0** (2025-10-11) - Phase 1: Initial Setup

---

[1.0.0]: https://github.com/Pratham-Dabhane/AlignCV/releases/tag/v1.0.0
