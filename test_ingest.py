"""Quick test of job ingestion endpoint"""
import requests

BASE_URL = "http://localhost:8001"

# Login
response = requests.post(f"{BASE_URL}/v2/auth/login", json={
    "email": "test_phase56@example.com",
    "password": "TestPassword123!"
})

if response.status_code == 200:
    token = response.json()['tokens']['access_token']
    headers = {"Authorization": f"Bearer {token}"}
    
    print("Testing job ingestion...")
    response = requests.post(f"{BASE_URL}/v2/jobs/ingest", headers=headers)
    
    print(f"Status: {response.status_code}")
    print(f"Response: {response.text}")
else:
    print(f"Login failed: {response.status_code}")
    print(response.text)
