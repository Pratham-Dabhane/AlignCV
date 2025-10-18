# Quick Phase 5/6 Testing Script
# This will guide you through testing each endpoint

Write-Host "`n=====================================================================" -ForegroundColor Cyan
Write-Host "Phase 5/6 Manual Testing Helper" -ForegroundColor Cyan
Write-Host "=====================================================================" -ForegroundColor Cyan

$BASE_URL = "http://localhost:8001"

# Step 1: Health Check
Write-Host "`n[STEP 1] Testing Server Health..." -ForegroundColor Yellow
try {
    $health = Invoke-RestMethod -Uri "$BASE_URL/v2/health" -Method GET
    Write-Host "✅ Server is healthy!" -ForegroundColor Green
    Write-Host "   Version: $($health.version)" -ForegroundColor Gray
    Write-Host "   Environment: $($health.environment)" -ForegroundColor Gray
} catch {
    Write-Host "❌ Server is not responding!" -ForegroundColor Red
    Write-Host "   Make sure the server is running: .venv\Scripts\python.exe start_server.py" -ForegroundColor Yellow
    exit 1
}

# Step 2: Login
Write-Host "`n[STEP 2] Logging in..." -ForegroundColor Yellow
try {
    $loginBody = @{
        email = "test_phase56@example.com"
        password = "TestPassword123!"
    } | ConvertTo-Json

    $loginResponse = Invoke-RestMethod -Uri "$BASE_URL/v2/auth/login" -Method POST -Body $loginBody -ContentType "application/json"
    $token = $loginResponse.tokens.access_token
    Write-Host "✅ Login successful!" -ForegroundColor Green
    Write-Host "   User ID: $($loginResponse.user.id)" -ForegroundColor Gray
    Write-Host "   Email: $($loginResponse.user.email)" -ForegroundColor Gray
    Write-Host "   Token (first 40 chars): $($token.Substring(0, 40))..." -ForegroundColor Gray
} catch {
    Write-Host "❌ Login failed!" -ForegroundColor Red
    Write-Host "   Error: $($_.Exception.Message)" -ForegroundColor Red
    exit 1
}

$headers = @{
    Authorization = "Bearer $token"
    "Content-Type" = "application/json"
}

# Step 3: Test Job Ingestion
Write-Host "`n[STEP 3] Testing Job Ingestion..." -ForegroundColor Yellow
Write-Host "   This will load 10 mock jobs into Qdrant..." -ForegroundColor Gray
Write-Host "   (This may take 30-60 seconds for embeddings)" -ForegroundColor Gray

try {
    $ingestResponse = Invoke-RestMethod -Uri "$BASE_URL/v2/jobs/ingest" -Method POST -Headers $headers
    Write-Host "✅ Job ingestion successful!" -ForegroundColor Green
    Write-Host "   Total ingested: $($ingestResponse.total_ingested)" -ForegroundColor Gray
    Write-Host "   New jobs: $($ingestResponse.new_jobs)" -ForegroundColor Gray
    Write-Host "   Embeddings created: $($ingestResponse.embeddings_created)" -ForegroundColor Gray
    Write-Host "   Source: $($ingestResponse.source)" -ForegroundColor Gray
} catch {
    Write-Host "❌ Job ingestion failed!" -ForegroundColor Red
    Write-Host "   Status Code: $($_.Exception.Response.StatusCode.Value__)" -ForegroundColor Red
    Write-Host "   Error: $($_.Exception.Message)" -ForegroundColor Red
    
    Write-Host "`n📝 IMPORTANT: Check the server terminal for detailed error!" -ForegroundColor Yellow
    Write-Host "   Look for Python traceback with the actual error message." -ForegroundColor Yellow
    
    Write-Host "`n🔧 Common Issues:" -ForegroundColor Cyan
    Write-Host "   1. Qdrant connection failed - Check .env credentials" -ForegroundColor Gray
    Write-Host "   2. Mistral API rate limit - Will fallback to local embeddings" -ForegroundColor Gray
    Write-Host "   3. Collection creation failed - May need to delete and recreate" -ForegroundColor Gray
    
    Write-Host "`n💡 Next Steps:" -ForegroundColor Yellow
    Write-Host "   1. Open Swagger UI: http://localhost:8001/v2/docs" -ForegroundColor White
    Write-Host "   2. Click 'Authorize' and paste this token:" -ForegroundColor White
    Write-Host "      Bearer $token" -ForegroundColor Cyan
    Write-Host "   3. Try POST /v2/jobs/ingest manually" -ForegroundColor White
    Write-Host "   4. Watch your server terminal for the full error" -ForegroundColor White
    
    exit 1
}

# Step 4: Get Job Stats
Write-Host "`n[STEP 4] Getting Qdrant Statistics..." -ForegroundColor Yellow
try {
    $stats = Invoke-RestMethod -Uri "$BASE_URL/v2/jobs/stats" -Method GET
    Write-Host "✅ Qdrant stats retrieved!" -ForegroundColor Green
    Write-Host "   Collection: $($stats.name)" -ForegroundColor Gray
    Write-Host "   Vectors: $($stats.vectors_count)" -ForegroundColor Gray
    Write-Host "   Status: $($stats.status)" -ForegroundColor Gray
} catch {
    Write-Host "⚠️  Could not get stats (may be normal if collection is empty)" -ForegroundColor Yellow
}

# Step 5: List Jobs
Write-Host "`n[STEP 5] Listing Jobs..." -ForegroundColor Yellow
try {
    $jobs = Invoke-RestMethod -Uri "$BASE_URL/v2/jobs/?limit=5" -Method GET -Headers $headers
    Write-Host "✅ Retrieved $($jobs.Count) jobs!" -ForegroundColor Green
    
    foreach ($job in $jobs | Select-Object -First 3) {
        Write-Host "`n   📋 $($job.title) at $($job.company)" -ForegroundColor Cyan
        Write-Host "      Location: $($job.location)" -ForegroundColor Gray
        Write-Host "      Type: $($job.employment_type)" -ForegroundColor Gray
        if ($job.salary_min -and $job.salary_max) {
            Write-Host "      Salary: `$$($job.salary_min)-`$$($job.salary_max)" -ForegroundColor Gray
        }
    }
} catch {
    Write-Host "❌ Could not list jobs: $($_.Exception.Message)" -ForegroundColor Red
}

# Step 6: Check if resume exists
Write-Host "`n[STEP 6] Checking for uploaded resumes..." -ForegroundColor Yellow
try {
    $docs = Invoke-RestMethod -Uri "$BASE_URL/v2/documents" -Method GET -Headers $headers
    
    if ($docs.Count -gt 0) {
        Write-Host "✅ Found $($docs.Count) resume(s)!" -ForegroundColor Green
        $resumeId = $docs[0].id
        Write-Host "   Using resume ID: $resumeId" -ForegroundColor Gray
        
        # Step 7: Test Job Matching
        Write-Host "`n[STEP 7] Testing Job Matching..." -ForegroundColor Yellow
        
        $matchBody = @{
            resume_id = $resumeId
            top_k = 5
            min_salary = 100000
        } | ConvertTo-Json
        
        try {
            $matches = Invoke-RestMethod -Uri "$BASE_URL/v2/jobs/match" -Method POST -Headers $headers -Body $matchBody
            Write-Host "✅ Found $($matches.Count) matching jobs!" -ForegroundColor Green
            
            foreach ($match in $matches | Select-Object -First 3) {
                Write-Host "`n   🎯 $($match.title) at $($match.company)" -ForegroundColor Cyan
                Write-Host "      Fit: $($match.fit_percentage)% (Vector: $([math]::Round($match.vector_score,1))%, Skill: $([math]::Round($match.skill_score,1))%)" -ForegroundColor Gray
                Write-Host "      Matched Skills: $($match.matched_skills -join ', ')" -ForegroundColor Green
                if ($match.gap_skills.Count -gt 0) {
                    Write-Host "      Gap Skills: $($match.gap_skills -join ', ')" -ForegroundColor Yellow
                }
            }
        } catch {
            Write-Host "❌ Job matching failed: $($_.Exception.Message)" -ForegroundColor Red
        }
        
    } else {
        Write-Host "⚠️  No resumes found!" -ForegroundColor Yellow
        Write-Host "   Upload a resume first: POST /v2/upload in Swagger UI" -ForegroundColor Gray
    }
} catch {
    Write-Host "❌ Could not check documents: $($_.Exception.Message)" -ForegroundColor Red
}

# Summary
Write-Host "`n=====================================================================" -ForegroundColor Cyan
Write-Host "Testing Summary" -ForegroundColor Cyan
Write-Host "=====================================================================" -ForegroundColor Cyan
Write-Host "`n✨ Phase 5/6 is working!" -ForegroundColor Green
Write-Host "`n📚 Next steps:" -ForegroundColor Yellow
Write-Host "   1. Open Swagger UI: http://localhost:8001/v2/docs" -ForegroundColor White
Write-Host "   2. Test bookmarking: POST /v2/jobs/bookmark" -ForegroundColor White
Write-Host "   3. Track applications: POST /v2/jobs/apply" -ForegroundColor White
Write-Host "   4. Run full test suite: .venv\Scripts\python.exe scripts\test_complete_workflow.py" -ForegroundColor White
Write-Host ""
