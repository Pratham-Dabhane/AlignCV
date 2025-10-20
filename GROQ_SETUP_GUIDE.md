# 🚀 Quick Start: LLaMA 3 AI Setup with Groq

## Why Groq?

- ✅ **100% FREE** - No credit card required
- ✅ **Fast** - Optimized inference infrastructure
- ✅ **LLaMA 3 8B** - Latest Meta model with 8K context
- ✅ **No Rate Limits** - Generous free tier

---

## Setup Steps (2 minutes)

### 1. Get Your Free API Key

1. Visit: https://console.groq.com/
2. Sign up (free, no credit card)
3. Go to **API Keys** section
4. Click **Create API Key**
5. Copy the key (starts with `gsk_...`)

### 2. Add to Your .env File

```bash
# Open your .env file and add:
GROQ_API_KEY=gsk_your_actual_key_here
```

### 3. Restart Backend

```bash
# In terminal:
uvicorn backend.v2.app_v2:app --reload --port 8000
```

### 4. Test It!

1. Open frontend: http://localhost:8501
2. Go to **Documents** page
3. Upload a resume
4. Click **AI Rewrite** with any style
5. You should see:
   - ✅ `impact_score` > 0 (not 0)
   - ✅ Actual rewritten content
   - ✅ List of improvements

---

## How to Verify It's Working

### Good Response (API Working):
```json
{
  "rewritten_text": "...(actual rewritten content)...",
  "improvements": ["Added quantifiable metrics", "Enhanced technical keywords"],
  "impact_score": 85,
  "api_status": "success"
}
```

### Fallback Response (API Key Missing/Wrong):
```json
{
  "rewritten_text": "...(original content unchanged)...",
  "improvements": ["API unavailable - original content preserved"],
  "impact_score": 0,
  "api_status": "fallback"
}
```

---

## Troubleshooting

### "impact_score": 0
**Problem**: API key not configured or invalid

**Solution**:
1. Check `.env` has `GROQ_API_KEY=gsk_...`
2. Verify key is correct (copy-paste from Groq console)
3. Restart backend server
4. Clear browser cache and try again

### "API timeout" error
**Problem**: Network issue or Groq service down

**Solution**:
1. Check your internet connection
2. Try again in a few seconds
3. Visit https://status.groq.com/ to check service status

### Still Using Mistral?
**Problem**: Old code not updated

**Solution**:
1. Verify `backend/v2/ai/rewrite_engine.py` has `api.groq.com` URL
2. Check config has `settings.groq_api_key`
3. Git pull latest changes

---

## API Usage Limits (Free Tier)

Groq Free Tier Limits:
- **Requests**: Generous (no hard daily limit)
- **Tokens**: High limits per request
- **Rate Limit**: 30 requests/minute
- **Models**: Full access to LLaMA 3 8B

**For AlignCV Usage**:
- Resume rewrite: ~1-3 seconds per request
- Job tailoring: ~2-5 seconds per request
- No cost, no credit card, no expiration

---

## Model Information

**LLaMA 3 8B Instruct**
- Developer: Meta AI
- Parameters: 8 billion
- Context Window: 8,192 tokens
- Use Case: General instruction following
- Best For: Resume rewriting, content optimization

**vs Mistral 7B (old)**
- Similar quality
- Groq infrastructure = faster
- Free (Mistral requires paid API key)

---

## Need Help?

1. **Groq Documentation**: https://console.groq.com/docs/quickstart
2. **Check Logs**: Backend terminal shows API errors
3. **Test API Key**:
   ```bash
   curl https://api.groq.com/openai/v1/models \
     -H "Authorization: Bearer $GROQ_API_KEY"
   ```

---

## ✅ Done!

Your AlignCV now uses LLaMA 3 8B for AI-powered resume optimization - completely free! 🎉
