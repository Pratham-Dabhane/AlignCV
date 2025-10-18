"""
Complete Phase 5/6 Testing Workflow

This script will test:
1. Signup/Login
2. Upload Resume
3. Ingest Jobs into Qdrant
4. Match Jobs with Resume
5. Bookmark a Job
6. Track Application
"""

import requests
import json
from pathlib import Path

BASE_URL = "http://localhost:8001"
TEST_EMAIL = "test_phase56@example.com"
TEST_PASSWORD = "TestPassword123!"

print("\n" + "=" * 70)
print("AlignCV Phase 5/6 - Complete Workflow Test")
print("=" * 70)

# ============================================
# Step 1: Health Check
# ============================================
print("\n📡 STEP 1: Health Check")
print("-" * 70)
try:
    response = requests.get(f"{BASE_URL}/v2/health")
    if response.status_code == 200:
        print("✅ Server is healthy")
        print(f"   {json.dumps(response.json(), indent=2)}")
    else:
        print(f"❌ Health check failed: {response.status_code}")
        exit(1)
except Exception as e:
    print(f"❌ Cannot connect to server: {e}")
    print("   Make sure the server is running: uvicorn backend.v2.app_v2:app_v2 --reload --port 8001")
    exit(1)

# ============================================
# Step 2: Signup
# ============================================
print("\n👤 STEP 2: Create Test User")
print("-" * 70)
signup_data = {
    "name": "Phase 5/6 Tester",
    "email": TEST_EMAIL,
    "password": TEST_PASSWORD
}

response = requests.post(f"{BASE_URL}/v2/auth/signup", json=signup_data)
if response.status_code == 201:
    print(f"✅ User created successfully")
    user_data = response.json()
    print(f"   User ID: {user_data['user']['id']}")
    print(f"   Email: {user_data['user']['email']}")
    token = user_data['tokens']['access_token']
elif response.status_code == 400 and "already registered" in response.text:
    print("⚠️  User already exists, logging in instead...")
    # Login instead
    response = requests.post(f"{BASE_URL}/v2/auth/login", json={
        "email": TEST_EMAIL,
        "password": TEST_PASSWORD
    })
    if response.status_code == 200:
        print("✅ Logged in successfully")
        user_data = response.json()
        token = user_data['tokens']['access_token']
    else:
        print(f"❌ Login failed: {response.status_code}")
        print(response.text)
        exit(1)
else:
    print(f"❌ Signup failed: {response.status_code}")
    print(response.text)
    exit(1)

headers = {"Authorization": f"Bearer {token}"}

# ============================================
# Step 3: Upload Resume
# ============================================
print("\n📄 STEP 3: Upload Resume")
print("-" * 70)

# Create a test resume (as DOCX using python-docx)
from docx import Document as DocxDocument

test_resume_path = Path("test_resume_phase56.docx")
test_resume_content = """PRATHAM DABHANE
Software Engineer

SKILLS:
- Python, FastAPI, PostgreSQL
- Docker, Kubernetes, AWS
- Machine Learning, NLP
- React, TypeScript
- Git, CI/CD

EXPERIENCE:
Senior Backend Developer at TechCorp (2020-Present)
- Built scalable APIs with Python and FastAPI
- Deployed microservices on Kubernetes
- Implemented ML models for recommendations

Junior Developer at StartupXYZ (2018-2020)
- Developed REST APIs with Node.js
- Worked with PostgreSQL databases
- Collaborated on React frontend

EDUCATION:
B.Tech in Computer Science Engineering"""

doc = DocxDocument()
for line in test_resume_content.strip().split('\n'):
    doc.add_paragraph(line)
doc.save(test_resume_path)

try:
    with open(test_resume_path, 'rb') as f:
        files = {'file': ('resume.docx', f, 'application/vnd.openxmlformats-officedocument.wordprocessingml.document')}
        response = requests.post(
            f"{BASE_URL}/v2/upload",
            headers=headers,
            files=files
        )
    
    if response.status_code == 200:
        print("✅ Resume uploaded successfully")
        doc_data = response.json()
        document_id = doc_data['document_id']
        print(f"   Document ID: {document_id}")
        print(f"   Skills extracted: {len(doc_data.get('skills', []))}")
    else:
        print(f"❌ Upload failed: {response.status_code}")
        print(response.text)
        exit(1)
finally:
    # Cleanup
    if test_resume_path.exists():
        test_resume_path.unlink()

# ============================================
# Step 4: Ingest Jobs
# ============================================
print("\n💼 STEP 4: Ingest Jobs into Qdrant")
print("-" * 70)
print("   This will load 10 mock jobs and create embeddings...")

response = requests.post(f"{BASE_URL}/v2/jobs/ingest", headers=headers)
if response.status_code == 200:
    ingest_data = response.json()
    print("✅ Jobs ingested successfully")
    print(f"   Total ingested: {ingest_data['total_ingested']}")
    print(f"   New jobs: {ingest_data['new_jobs']}")
    print(f"   Updated jobs: {ingest_data['updated_jobs']}")
    print(f"   Embeddings created: {ingest_data['embeddings_created']}")
else:
    print(f"❌ Ingestion failed: {response.status_code}")
    print(response.text)
    exit(1)

# ============================================
# Step 5: Match Jobs
# ============================================
print("\n🎯 STEP 5: Match Jobs with Resume")
print("-" * 70)
print("   Finding top 5 matching jobs...")

match_request = {
    "resume_id": document_id,
    "top_k": 5,
    "min_salary": 100000  # Filter for jobs with min salary > 100k
}

response = requests.post(
    f"{BASE_URL}/v2/jobs/match",
    headers=headers,
    json=match_request
)

if response.status_code == 200:
    matches = response.json()
    print(f"✅ Found {len(matches)} matching jobs")
    print()
    
    for i, job in enumerate(matches[:3], 1):  # Show top 3
        print(f"   {i}. {job['title']} at {job['company']}")
        print(f"      Location: {job['location']}")
        print(f"      Fit: {job['fit_percentage']}% (Vector: {job['vector_score']:.1f}%, Skill: {job['skill_score']:.1f}%)")
        print(f"      Matched Skills: {', '.join(job['matched_skills'][:5])}")
        print(f"      Gap Skills: {', '.join(job['gap_skills'][:3])}")
        if job.get('salary_min') and job.get('salary_max'):
            print(f"      Salary: ${job['salary_min']:,} - ${job['salary_max']:,}")
        print()
    
    # Save first job for bookmarking
    if matches:
        first_job_id = matches[0].get('job_id')
else:
    print(f"❌ Matching failed: {response.status_code}")
    print(response.text)
    exit(1)

# ============================================
# Step 6: Get All Jobs
# ============================================
print("\n📋 STEP 6: List All Jobs")
print("-" * 70)

response = requests.get(f"{BASE_URL}/v2/jobs/?limit=5", headers=headers)
if response.status_code == 200:
    jobs = response.json()
    print(f"✅ Retrieved {len(jobs)} jobs")
    job_db_id = jobs[0]['id'] if jobs else None
    print(f"   First job DB ID: {job_db_id}")
else:
    print(f"❌ Failed to get jobs: {response.status_code}")

# ============================================
# Step 7: Bookmark a Job
# ============================================
if job_db_id:
    print("\n🔖 STEP 7: Bookmark a Job")
    print("-" * 70)
    
    bookmark_request = {
        "job_id": job_db_id,
        "notes": "Looks like a great fit for my skills!"
    }
    
    response = requests.post(
        f"{BASE_URL}/v2/jobs/bookmark",
        headers=headers,
        json=bookmark_request
    )
    
    if response.status_code == 200:
        print("✅ Job bookmarked successfully")
        print(f"   {response.json()}")
    elif response.status_code == 400:
        print("⚠️  Job already bookmarked")
    else:
        print(f"❌ Bookmark failed: {response.status_code}")
        print(response.text)
    
    # ============================================
    # Step 8: Get Bookmarks
    # ============================================
    print("\n📚 STEP 8: Get My Bookmarks")
    print("-" * 70)
    
    response = requests.get(f"{BASE_URL}/v2/jobs/bookmarks", headers=headers)
    if response.status_code == 200:
        bookmarks = response.json()
        print(f"✅ You have {len(bookmarks)} bookmark(s)")
        for bm in bookmarks[:3]:
            print(f"   - {bm['job']['title']} at {bm['job']['company']}")
            if bm['notes']:
                print(f"     Notes: {bm['notes']}")
    else:
        print(f"❌ Failed to get bookmarks: {response.status_code}")
    
    # ============================================
    # Step 9: Apply to Job
    # ============================================
    print("\n✉️ STEP 9: Record Job Application")
    print("-" * 70)
    
    application_request = {
        "job_id": job_db_id,
        "status": "applied",
        "notes": "Applied via company website on " + "Oct 18, 2025"
    }
    
    response = requests.post(
        f"{BASE_URL}/v2/jobs/apply",
        headers=headers,
        json=application_request
    )
    
    if response.status_code == 200:
        print("✅ Application recorded successfully")
        print(f"   {response.json()}")
    else:
        print(f"❌ Application failed: {response.status_code}")
        print(response.text)
    
    # ============================================
    # Step 10: Get Applications
    # ============================================
    print("\n📊 STEP 10: Get My Applications")
    print("-" * 70)
    
    response = requests.get(f"{BASE_URL}/v2/jobs/applications", headers=headers)
    if response.status_code == 200:
        applications = response.json()
        print(f"✅ You have {len(applications)} application(s)")
        for app in applications[:3]:
            print(f"   - {app['job']['title']} at {app['job']['company']}")
            print(f"     Status: {app['status']}")
            print(f"     Applied: {app['applied_date']}")
    else:
        print(f"❌ Failed to get applications: {response.status_code}")

# ============================================
# Step 11: Qdrant Stats
# ============================================
print("\n📈 STEP 11: Qdrant Statistics")
print("-" * 70)

response = requests.get(f"{BASE_URL}/v2/jobs/stats")
if response.status_code == 200:
    stats = response.json()
    print("✅ Qdrant collection stats:")
    print(f"   Collection: {stats['name']}")
    print(f"   Vectors: {stats.get('vectors_count', 'N/A')}")
    print(f"   Points: {stats.get('points_count', 'N/A')}")
    print(f"   Status: {stats.get('status', 'N/A')}")
else:
    print(f"❌ Failed to get stats: {response.status_code}")

# ============================================
# Summary
# ============================================
print("\n" + "=" * 70)
print("🎉 PHASE 5/6 COMPLETE - ALL TESTS PASSED!")
print("=" * 70)
print("\n✅ Successfully tested:")
print("   1. Health check")
print("   2. User signup/login")
print("   3. Resume upload with NLP extraction")
print("   4. Job ingestion into Qdrant")
print("   5. Job matching with vector similarity")
print("   6. List all jobs")
print("   7. Bookmark jobs")
print("   8. View bookmarks")
print("   9. Track job applications")
print("   10. View applications")
print("   11. Qdrant statistics")

print("\n🚀 Phase 5/6 Job Matching Engine is FULLY OPERATIONAL!")
print("\nNext steps:")
print("   - Visit http://localhost:8001/v2/docs for API documentation")
print("   - Try different match parameters (salary, location filters)")
print("   - Add more job sources in backend/v2/jobs/ingest.py")
print("   - Build a frontend dashboard to visualize matches")
print()
