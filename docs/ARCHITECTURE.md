# AlignCV - Architecture Documentation

## Overview
AlignCV is a semantic resume matching tool that helps students align their resumes with job descriptions.

## System Architecture

```
┌─────────────────┐         ┌─────────────────┐
│                 │         │                 │
│   Frontend      │◄───────►│   Backend       │
│   (Streamlit)   │  HTTP   │   (FastAPI)     │
│                 │         │                 │
└─────────────────┘         └────────┬────────┘
                                     │
                            ┌────────▼────────┐
                            │                 │
                            │  Future: ML     │
                            │  (Embeddings)   │
                            │                 │
                            └─────────────────┘
```

## Components

### Backend (FastAPI)
- **app.py**: Main application entry point
- **api/**: API route handlers (future expansion)
- **utils/**: Utility modules
  - `text_processing.py`: Text cleaning and preprocessing
  - Future: `embedding_utils.py`, `matching_utils.py`

### Frontend (Streamlit)
- **app.py**: Main UI application
- **components/**: Reusable UI components (future)
- **pages/**: Multi-page app structure (future)

### Data Flow (Phase 1)
1. User inputs resume + job description in frontend
2. Frontend POSTs to `/analyze` endpoint
3. Backend validates input
4. Backend returns dummy response (match_score=0, empty lists)
5. Frontend displays results

### Future Phases
- **Phase 2**: Semantic matching with embeddings
- **Phase 3**: Gap and strengths analysis
- **Phase 4**: Actionable checklist generation
- **Phase 5**: UI polish and optimization

## API Specification

### POST /analyze
**Request:**
```json
{
  "resume_text": "string",
  "job_description_text": "string"
}
```

**Response:**
```json
{
  "match_score": 0.0,
  "strengths": [],
  "gaps": [],
  "message": "Phase 1: Dummy response"
}
```

## Technology Stack
- **Backend**: Python 3.10+, FastAPI, Pydantic
- **Frontend**: Streamlit
- **Future**: Sentence-BERT, scikit-learn
- **Testing**: pytest
- **Deployment**: Docker (future)

## Development Workflow
1. Start backend: `uvicorn app:app --reload --port 8000`
2. Start frontend: `streamlit run app.py`
3. Access at `http://localhost:8501`
4. Test with pytest: `pytest tests/`

## Brand Guidelines
- **Colors**: Deep blue (#1E3A8A), Charcoal gray (#374151), Teal accent (#14B8A6)
- **Tone**: Professional, trustworthy, empowering, clear
- **Tagline**: "Your Career, Aligned"
