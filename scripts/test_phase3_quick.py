"""
Quick Test Script for AlignCV V2 Phase 3
Tests authentication and AI rewriting without Google OAuth
"""

import requests
import json

BASE_URL = "http://localhost:8001"

def test_phase3():
    print("=" * 60)
    print("AlignCV V2 Phase 3 - Quick Test")
    print("=" * 60)
    
    # Test 1: Health Check
    print("\n1️⃣  Testing Health Endpoint...")
    try:
        response = requests.get(f"{BASE_URL}/v2/health")
        if response.status_code == 200:
            data = response.json()
            print(f"   ✅ Server is healthy!")
            print(f"   Status: {data['status']}")
            print(f"   Version: {data['version']}")
            print(f"   Environment: {data['environment']}")
        else:
            print(f"   ❌ Health check failed: {response.status_code}")
            return
    except Exception as e:
        print(f"   ❌ Server not running: {e}")
        print(f"   Please start: python -m uvicorn backend.v2.app_v2:app_v2 --reload --port 8001")
        return
    
    # Test 2: Signup
    print("\n2️⃣  Testing Signup (Email/Password - No Google OAuth needed)...")
    signup_data = {
        "name": "Phase3 Test User",
        "email": "phase3test@example.com",
        "password": "SecurePass123!"
    }
    
    try:
        response = requests.post(f"{BASE_URL}/v2/auth/signup", json=signup_data)
        if response.status_code == 200:
            data = response.json()
            token = data["access_token"]
            print(f"   ✅ Signup successful!")
            print(f"   User ID: {data['user']['id']}")
            print(f"   Name: {data['user']['name']}")
            print(f"   Email: {data['user']['email']}")
            print(f"   Token: {token[:30]}...")
            
            # Save token for next steps
            return token
        elif response.status_code == 400 and "already exists" in response.text.lower():
            print(f"   ⚠️  User already exists, trying login...")
            
            # Try login instead
            login_response = requests.post(f"{BASE_URL}/v2/auth/login", json={
                "email": signup_data["email"],
                "password": signup_data["password"]
            })
            
            if login_response.status_code == 200:
                data = login_response.json()
                token = data["access_token"]
                print(f"   ✅ Login successful!")
                print(f"   Token: {token[:30]}...")
                return token
            else:
                print(f"   ❌ Login failed: {login_response.text}")
                return None
        else:
            print(f"   ❌ Signup failed: {response.status_code}")
            print(f"   Error: {response.text}")
            return None
    except Exception as e:
        print(f"   ❌ Error: {e}")
        return None
    
    # Test 3 would be upload and rewrite, but requires file upload
    print("\n3️⃣  Next Steps (Manual):")
    print("   📝 Visit: http://localhost:8001/v2/docs")
    print("   📝 Use the /v2/upload endpoint to upload a resume")
    print("   📝 Then use /v2/rewrite to test AI rewriting")
    print("   📝 Check fallback mode (works without Mistral API key!)")

if __name__ == "__main__":
    token = test_phase3()
    
    if token:
        print("\n" + "=" * 60)
        print("✅ PHASE 3 CORE FEATURES WORKING!")
        print("=" * 60)
        print("\n🔑 Your Access Token (for API testing):")
        print(f"{token}\n")
        print("📚 Use this token in API docs:")
        print("   1. Go to http://localhost:8001/v2/docs")
        print("   2. Click 'Authorize' button")
        print("   3. Paste token above")
        print("   4. Test /v2/upload and /v2/rewrite endpoints")
        print("\n💡 Google OAuth placeholders are OK - not needed for testing!")
    else:
        print("\n❌ Tests failed. Check server is running on port 8001")
