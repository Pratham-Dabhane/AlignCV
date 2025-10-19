# AlignCV Phase 5/6 Setup Guide
# Job Matching + Ranking Engine with Qdrant

## 🎯 Overview

Phase 5/6 implements an intelligent job matching and ranking system using:
- **Vector Embeddings**: Mistral 7B API or sentence-transformers fallback
- **Vector Database**: Qdrant (Cloud or Local Docker)
- **Skill Extraction**: SpaCy NLP for gap analysis
- **Job Ingestion**: Mock scraper with extensible architecture

---

## 📋 Prerequisites

### 1. Install Dependencies

```bash
pip install qdrant-client sentence-transformers beautifulsoup4 feedparser
```

Or install from requirements.txt:

```bash
pip install -r requirements.txt
```

### 2. Setup Qdrant

#### Option A: Qdrant Cloud (Recommended)

1. Create account at https://cloud.qdrant.io
2. Create a new cluster
3. Get your API key and URL
4. Add to `.env`:

```env
QDRANT_URL=https://your-cluster.qdrant.io
QDRANT_API_KEY=your_api_key_here
QDRANT_COLLECTION_NAME=aligncv_jobs
```

#### Option B: Local Docker

```bash
docker run -p 6333:6333 qdrant/qdrant
```

Then add to `.env`:

```env
QDRANT_URL=http://localhost:6333
QDRANT_API_KEY=  # Leave empty for local
QDRANT_COLLECTION_NAME=aligncv_jobs
```

### 3. Download SpaCy Model

```bash
python -m spacy download en_core_web_sm
```

---

## 🚀 Quick Start

### 1. Update Database Schema

Run database migration to add Job tables:

```bash
# If using Alembic
alembic revision --autogenerate -m "Add job matching tables"
alembic upgrade head
```

Or the database will auto-create tables on first run.

### 2. Start the Server

```bash
uvicorn backend.v2.app_v2:app_v2 --reload --port 8001
```

### 3. Access API Documentation

Navigate to: http://localhost:8001/v2/docs

---

## 📚 API Endpoints

### Job Ingestion

**POST /v2/jobs/ingest**

Ingest jobs from configured sources (currently mock data for testing).

```bash
curl -X POST "http://localhost:8001/v2/jobs/ingest" \
  -H "Authorization: Bearer YOUR_TOKEN"
```

Response:
```json
{
  "total_ingested": 10,
  "new_jobs": 10,
  "updated_jobs": 0,
  "embeddings_created": 10
}
```

### Job Matching

**POST /v2/jobs/match**

Match a resume with jobs using vector similarity.

```bash
curl -X POST "http://localhost:8001/v2/jobs/match" \
  -H "Authorization: Bearer YOUR_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "resume_id": 1,
    "top_k": 10,
    "min_salary": 120000,
    "location": "San Francisco",
    "experience_level": "senior"
  }'
```

Response:
```json
[
  {
    "job_id": "abc123",
    "title": "Senior Software Engineer",
    "company": "TechCorp",
    "location": "San Francisco, CA",
    "url": "https://example.com/jobs/1",
    "description": "We're looking for...",
    "tags": ["Python", "FastAPI", "PostgreSQL"],
    "salary_min": 150000,
    "salary_max": 200000,
    "employment_type": "full-time",
    "experience_level": "senior",
    "vector_score": 87.5,
    "skill_score": 75.0,
    "combined_score": 83.75,
    "fit_percentage": 84,
    "matched_skills": ["python", "fastapi", "postgresql"],
    "gap_skills": ["kubernetes", "aws"],
    "is_bookmarked": false,
    "is_applied": false
  }
]
```

### Get Jobs

**GET /v2/jobs/?skip=0&limit=20**

Get paginated list of jobs.

```bash
curl -X GET "http://localhost:8001/v2/jobs/?limit=10" \
  -H "Authorization: Bearer YOUR_TOKEN"
```

### Bookmark Job

**POST /v2/jobs/bookmark**

Save a job for later review.

```bash
curl -X POST "http://localhost:8001/v2/jobs/bookmark" \
  -H "Authorization: Bearer YOUR_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "job_id": 1,
    "notes": "Great opportunity, apply by Friday"
  }'
```

### Get Bookmarks

**GET /v2/jobs/bookmarks**

```bash
curl -X GET "http://localhost:8001/v2/jobs/bookmarks" \
  -H "Authorization: Bearer YOUR_TOKEN"
```

### Apply to Job

**POST /v2/jobs/apply**

Track job application.

```bash
curl -X POST "http://localhost:8001/v2/jobs/apply" \
  -H "Authorization: Bearer YOUR_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "job_id": 1,
    "status": "applied",
    "notes": "Applied via LinkedIn"
  }'
```

### Get Applications

**GET /v2/jobs/applications**

```bash
curl -X GET "http://localhost:8001/v2/jobs/applications" \
  -H "Authorization: Bearer YOUR_TOKEN"
```

### Vector DB Stats

**GET /v2/jobs/stats**

Get Qdrant collection statistics.

```bash
curl -X GET "http://localhost:8001/v2/jobs/stats"
```

---

## 🧪 Testing

### Run Test Suite

```bash
# Run all job matching tests
pytest tests/test_v2_jobs.py -v

# Run with coverage
pytest tests/test_v2_jobs.py -v --cov=backend.v2.jobs

# Run specific test
pytest tests/test_v2_jobs.py::test_match_jobs_with_filters -v
```

### Test Performance

```bash
pytest tests/test_v2_jobs.py::test_embedding_performance -v
pytest tests/test_v2_jobs.py::test_batch_embedding_performance -v
```

Expected performance:
- Single embedding: < 1 second
- Batch 10 embeddings: < 5 seconds
- Job matching: < 2 seconds

---

## 🔧 Configuration

All configuration is in `.env`:

```env
# Qdrant Vector Database
QDRANT_URL=https://your-cluster.qdrant.io
QDRANT_API_KEY=your_api_key
QDRANT_COLLECTION_NAME=aligncv_jobs

# Mistral AI (for embeddings - optional)
MISTRAL_API_KEY=your_mistral_key

# SpaCy NLP
SPACY_MODEL=en_core_web_sm
```

---

## 📊 Architecture

### Embedding Strategy

1. **Primary**: Mistral embeddings API (if configured)
2. **Fallback**: sentence-transformers (all-MiniLM-L6-v2)
   - Dimension: 384
   - Speed: ~50ms per embedding
   - Offline capability

### Job Matching Algorithm

1. **Vector Search** (70% weight)
   - Cosine similarity between resume and job embeddings
   - Qdrant handles efficiently with HNSW index

2. **Skill Match** (30% weight)
   - SpaCy extracts keyphrases from resume and job
   - Calculate matched vs. gap skills
   - Percentage match: `matched / total_required * 100`

3. **Combined Score**
   - `(vector_score * 0.7) + (skill_score * 0.3)`
   - Jobs ranked by this score

### Job Ingestion

Current implementation:
- **MockJobScraper**: 10 sample tech jobs for testing
- **RSSJobScraper**: Generic RSS feed parser

Extensible for:
- LinkedIn API (requires partnership)
- AngelList API
- Indeed RSS feeds
- Custom scrapers

---

## 🐛 Troubleshooting

### Qdrant Connection Error

**Error**: `Could not connect to Qdrant`

**Solution**:
- Check `QDRANT_URL` and `QDRANT_API_KEY` in `.env`
- Verify Qdrant cloud cluster is running
- For local Docker: `docker ps` to check container

### Embedding Dimension Mismatch

**Error**: `Vector dimension mismatch`

**Solution**:
- sentence-transformers uses 384 dimensions
- Mistral embeddings use 1024 dimensions
- Recreate collection with correct dimension:
  ```python
  await create_collection(settings, vector_size=384)  # or 1024
  ```

### SpaCy Model Not Found

**Error**: `Can't find model 'en_core_web_sm'`

**Solution**:
```bash
python -m spacy download en_core_web_sm
```

### Slow Embedding Generation

**Issue**: Embeddings take > 5 seconds

**Solution**:
- First run downloads model (~90MB) - normal delay
- Subsequent runs should be fast
- Use batch embedding for multiple texts:
  ```python
  await get_batch_embeddings(texts, settings)
  ```

---

## 📈 Performance Optimization

### Batch Processing

For ingesting many jobs:

```python
# Instead of one at a time
for job in jobs:
    embedding = await get_job_embedding(job.description)
    
# Do batch processing
texts = [job.description for job in jobs]
embeddings = await get_batch_embeddings(texts, settings)
```

### Caching

Model loaded once and cached:
- sentence-transformers model
- SpaCy NLP model
- Qdrant client

### Indexing

Qdrant uses HNSW index for fast similarity search:
- Search time: O(log N)
- 1000 jobs: ~10ms
- 100,000 jobs: ~50ms

---

## 🔐 Security

### Authentication

All endpoints require JWT token:

```bash
# Get token
curl -X POST "http://localhost:8001/v2/auth/login" \
  -H "Content-Type: application/json" \
  -d '{
    "email": "user@example.com",
    "password": "password123"
  }'

# Use in requests
curl -X POST "http://localhost:8001/v2/jobs/match" \
  -H "Authorization: Bearer YOUR_ACCESS_TOKEN" \
  ...
```

### Data Privacy

- User resumes never sent to external APIs in clear text
- Only embeddings stored in Qdrant
- Bookmarks and applications are user-private

---

## 🚀 Next Steps

1. **Add More Scrapers**:
   - Implement LinkedIn API integration
   - Add Indeed RSS feeds
   - Create custom scrapers for niche job boards

2. **Enhanced Matching**:
   - Add semantic similarity for job titles
   - Factor in location distance
   - Consider company culture fit

3. **Notifications**:
   - Email alerts for new matching jobs
   - Daily/weekly digest of opportunities
   - Application deadline reminders

4. **Analytics**:
   - Track which jobs users apply to
   - Measure match accuracy
   - Improve ranking algorithm with feedback

---

## 📞 Support

For issues or questions:
1. Check logs: `logs/v2_app.log`
2. Run tests: `pytest tests/test_v2_jobs.py -v`
3. Review API docs: http://localhost:8001/v2/docs

---

**Phase 5/6 Complete! ✅**

Your job matching engine is ready to help users discover their perfect opportunities.
