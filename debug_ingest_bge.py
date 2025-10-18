"""
Debug ingestion endpoint to see actual error
"""

import httpx
import asyncio


async def test_ingest():
    """Test job ingestion endpoint."""
    base_url = "http://localhost:8001/v2"
    
    # Register/Login
    print("🔐 Registering user...")
    async with httpx.AsyncClient() as client:
        # Try to register
        response = await client.post(
            f"{base_url}/auth/register",
            json={
                "email": "test_bge@example.com",
                "password": "testpass123",
                "full_name": "BGE Test User"
            }
        )
        
        if response.status_code == 400:
            print("⚠️  User exists, logging in...")
            response = await client.post(
                f"{base_url}/auth/login",
                json={
                    "email": "test_bge@example.com",
                    "password": "testpass123"
                }
            )
        elif response.status_code != 201:
            print(f"❌ Registration failed: {response.status_code}")
            print(response.text)
            return
        
        if response.status_code != 200:
            print(f"❌ Login failed: {response.status_code}")
            print(response.text)
            return
        
        token = response.json()["access_token"]
        print(f"✅ Logged in, token: {token[:20]}...")
        
        # Test ingestion
        print("\n📥 Testing job ingestion...")
        response = await client.post(
            f"{base_url}/jobs/ingest",
            headers={"Authorization": f"Bearer {token}"}
        )
        
        print(f"Status: {response.status_code}")
        print(f"Response: {response.text}")
        
        if response.status_code == 200:
            print("✅ Ingestion successful!")
        else:
            print("❌ Ingestion failed")


if __name__ == "__main__":
    asyncio.run(test_ingest())
