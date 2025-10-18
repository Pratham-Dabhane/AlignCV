# AlignCV API Routes Reference

Complete API route structure for AlignCV v2.

## Base URL
```
Production: https://your-domain.com
Development: http://localhost:8001
```

## Route Structure

All routes follow the pattern: `/v2/{module}/{endpoint}`

---

## 🔐 Authentication (`/v2/auth`)

| Method | Endpoint | Description | Auth Required |
|--------|----------|-------------|---------------|
| POST | `/v2/auth/signup` | Register new user | ❌ |
| POST | `/v2/auth/login` | Login with email/password | ❌ |
| POST | `/v2/auth/refresh` | Refresh access token | ✅ (Refresh Token) |
| GET | `/v2/auth/me` | Get current user profile | ✅ |
| GET | `/v2/auth/google` | Initiate Google OAuth | ❌ |
| GET | `/v2/auth/google/callback` | Google OAuth callback | ❌ |

---

## 📄 Documents (`/v2/documents`)

| Method | Endpoint | Description | Auth Required |
|--------|----------|-------------|---------------|
| POST | `/v2/documents/upload` | Upload resume (PDF/DOCX) | ✅ |
| GET | `/v2/documents/` | List all user documents | ✅ |
| GET | `/v2/documents/{doc_id}` | Get document details | ✅ |
| DELETE | `/v2/documents/{doc_id}` | Delete document | ✅ |

---

## 🤖 AI Rewriting (`/v2/rewrite`)

| Method | Endpoint | Description | Auth Required |
|--------|----------|-------------|---------------|
| POST | `/v2/rewrite/generate` | Generate rewritten resume | ✅ |
| GET | `/v2/rewrite/versions/{doc_id}` | List document versions | ✅ |
| GET | `/v2/rewrite/version/{version_id}` | Get specific version | ✅ |

---

## 💼 Jobs (`/v2/jobs`)

| Method | Endpoint | Description | Auth Required |
|--------|----------|-------------|---------------|
| POST | `/v2/jobs/ingest` | Ingest jobs from RSS feeds | ✅ (Admin) |
| GET | `/v2/jobs/` | List all available jobs | ✅ |
| GET | `/v2/jobs/{job_id}` | Get job details | ✅ |
| POST | `/v2/jobs/match` | Match resume with jobs | ✅ |
| POST | `/v2/jobs/bookmarks` | Bookmark a job | ✅ |
| GET | `/v2/jobs/bookmarks` | List bookmarked jobs | ✅ |
| DELETE | `/v2/jobs/bookmarks/{job_id}` | Remove bookmark | ✅ |
| POST | `/v2/jobs/applications` | Apply to a job | ✅ |
| GET | `/v2/jobs/applications` | List job applications | ✅ |
| PATCH | `/v2/jobs/applications/{app_id}` | Update application status | ✅ |

---

## 🔔 Notifications (`/v2/notifications`)

| Method | Endpoint | Description | Auth Required |
|--------|----------|-------------|---------------|
| GET | `/v2/notifications/settings` | Get notification preferences | ✅ |
| PUT | `/v2/notifications/settings` | Update notification preferences | ✅ |
| GET | `/v2/notifications/` | List user notifications | ✅ |
| PUT | `/v2/notifications/{notif_id}/read` | Mark notification as read | ✅ |
| DELETE | `/v2/notifications/{notif_id}` | Delete notification | ✅ |
| POST | `/v2/notifications/test` | Send test notification | ✅ |

---

## ❤️ Health & Info

| Method | Endpoint | Description | Auth Required |
|--------|----------|-------------|---------------|
| GET | `/v2/` | API root info | ❌ |
| GET | `/v2/health` | Health check | ❌ |
| GET | `/v2/docs` | Swagger UI documentation | ❌ |
| GET | `/v2/redoc` | ReDoc documentation | ❌ |

---

## 🔄 Complete User Workflow

```mermaid
graph LR
    A[Signup/Login] --> B[Upload Resume]
    B --> C[Extract Skills/Roles]
    C --> D[AI Rewrite Resume]
    D --> E[Match with Jobs]
    E --> F[Bookmark Jobs]
    F --> G[Apply to Jobs]
    G --> H[Get Notifications]
    H --> I[Receive Email Alerts]
```

### Step-by-Step Flow:

1. **Authentication** (`POST /v2/auth/signup` or `/v2/auth/login`)
   - Get JWT access token
   - Use in Authorization header: `Bearer <token>`

2. **Upload Resume** (`POST /v2/documents/upload`)
   - Upload PDF or DOCX file
   - Automatic NLP extraction (skills, roles, entities)
   - Returns document ID

3. **AI Rewrite** (`POST /v2/rewrite/generate`)
   - Provide document ID and job description
   - Mistral AI rewrites resume to match job
   - Creates new version

4. **Job Matching** (`POST /v2/jobs/match`)
   - Provide document ID
   - Qdrant vector search finds similar jobs
   - Returns ranked matches with scores

5. **Bookmark/Apply** (`POST /v2/jobs/bookmarks` or `/v2/jobs/applications`)
   - Save interesting jobs
   - Track application status

6. **Notifications** (`GET /v2/notifications/`)
   - Daily digests of new job matches
   - Email alerts via SendGrid
   - Configure preferences

---

## 🔑 Authentication

All protected endpoints require JWT token in the Authorization header:

```http
Authorization: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...
```

### Token Lifecycle:
- **Access Token**: 15 minutes
- **Refresh Token**: 7 days
- Use `/v2/auth/refresh` to get new access token

---

## 📊 Response Format

### Success Response:
```json
{
  "status": "success",
  "data": { ... }
}
```

### Error Response:
```json
{
  "detail": "Error message here"
}
```

### Validation Error:
```json
{
  "detail": [
    {
      "loc": ["body", "email"],
      "msg": "field required",
      "type": "value_error.missing"
    }
  ]
}
```

---

## 🚀 Rate Limiting

- **Auth endpoints**: 5 requests/minute
- **Upload endpoints**: 10 files/hour
- **AI rewrite**: 20 requests/hour
- **Other endpoints**: 100 requests/minute

---

## 📝 Notes

- All timestamps are in UTC
- File uploads limited to 5MB
- Supported file types: PDF, DOCX
- Vector embeddings use BGE-small-en-v1.5 model
- AI rewriting uses Mistral-7B-Instruct

---

## 🔗 Related Documentation

- [API Testing Guide](../TESTING.md)
- [Phase 7 Complete](../PHASE7_COMPLETE.md)
- [Architecture Overview](./ARCHITECTURE.md)
