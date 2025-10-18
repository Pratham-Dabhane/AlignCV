"""
Simple manual test to see the ACTUAL error from job ingestion
"""
import requests
import json

BASE_URL = "http://localhost:8001"

print("\n" + "="*70)
print("Phase 5/6 Manual Debug Test")
print("="*70)

# Step 1: Login
print("\n[1] Logging in...")
response = requests.post(f"{BASE_URL}/v2/auth/login", json={
    "email": "test_phase56@example.com",
    "password": "TestPassword123!"
})

if response.status_code != 200:
    print(f"❌ Login failed: {response.status_code}")
    print(response.text)
    exit(1)

token = response.json()['tokens']['access_token']
print("✅ Login successful!")
print(f"   Token (first 50 chars): {token[:50]}...")

headers = {"Authorization": f"Bearer {token}"}

# Step 2: Test Ingestion
print("\n[2] Testing job ingestion...")
print("   ⏳ This may take 30-60 seconds (generating embeddings)...")
print("   📝 WATCH YOUR SERVER TERMINAL for detailed error output!")
print()

try:
    response = requests.post(f"{BASE_URL}/v2/jobs/ingest", headers=headers, timeout=120)
    
    if response.status_code == 200:
        data = response.json()
        print("✅ JOB INGESTION SUCCESSFUL!")
        print(f"   Total ingested: {data['total_ingested']}")
        print(f"   New jobs: {data['new_jobs']}")
        print(f"   Embeddings created: {data['embeddings_created']}")
        print(f"   Updated jobs: {data.get('updated_jobs', 0)}")
    else:
        print(f"❌ JOB INGESTION FAILED!")
        print(f"   Status Code: {response.status_code}")
        print(f"   Response: {response.text}")
        print("\n" + "="*70)
        print("🔍 CHECK YOUR SERVER TERMINAL NOW!")
        print("="*70)
        print("Look for ERROR messages and Python traceback.")
        
except requests.exceptions.Timeout:
    print("❌ Request timed out (>120s)")
    print("   This might mean embedding generation is taking too long.")
    print("   Or the server crashed - check the terminal!")
    
except Exception as e:
    print(f"❌ Exception: {e}")

print("\n" + "="*70)
print("Next Steps:")
print("="*70)
print("1. Check the server terminal for detailed Python error")
print("2. Open Swagger UI: http://localhost:8001/v2/docs")
print("3. Read MANUAL_TESTING_GUIDE.md for full instructions")
print()
