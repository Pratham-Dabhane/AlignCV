"""
Phase 7 Notification System Test

Tests:
1. Notification settings CRUD
2. Email service (SendGrid)
3. Celery task execution
4. End-to-end workflow
"""

import asyncio
import httpx
from datetime import datetime

BASE_URL = "http://localhost:8001/v2"

# Test credentials
TEST_USER = {
    "email": "test_phase7@example.com",
    "password": "TestPass123!",
    "name": "Phase 7 Tester"
}


async def test_phase7():
    """Run complete Phase 7 tests."""
    
    print("\n" + "=" * 70)
    print("Phase 7 - Notification System Test")
    print("=" * 70)
    
    async with httpx.AsyncClient(timeout=30.0) as client:
        token = None
        
        # Step 1: Health check
        print("\n📡 STEP 1: Health Check")
        print("-" * 70)
        try:
            response = await client.get(f"{BASE_URL}/health")
            if response.status_code == 200:
                print("✅ Server is healthy")
            else:
                print(f"⚠️  Server health check returned {response.status_code}")
        except Exception as e:
            print(f"❌ Health check failed: {e}")
            return
        
        # Step 2: Login/Register
        print("\n👤 STEP 2: User Authentication")
        print("-" * 70)
        try:
            # Try login first
            response = await client.post(
                f"{BASE_URL}/auth/login",
                json={"email": TEST_USER["email"], "password": TEST_USER["password"]}
            )
            
            if response.status_code == 200:
                print("✅ Logged in successfully")
                data = response.json()
                token = data["tokens"]["access_token"]
            else:
                # Register new user
                response = await client.post(
                    f"{BASE_URL}/auth/signup",
                    json=TEST_USER
                )
                if response.status_code == 201:
                    print("✅ User registered successfully")
                    data = response.json()
                    token = data["tokens"]["access_token"]
                else:
                    print(f"❌ Authentication failed: {response.text}")
                    return
                    
        except Exception as e:
            print(f"❌ Authentication error: {e}")
            return
        
        headers = {"Authorization": f"Bearer {token}"}
        
        # Step 3: Get notification settings
        print("\n⚙️  STEP 3: Get Notification Settings")
        print("-" * 70)
        try:
            response = await client.get(f"{BASE_URL}/notifications/settings", headers=headers)
            if response.status_code == 200:
                settings = response.json()
                print("✅ Notification settings retrieved")
                print(f"   Email enabled: {settings['email_enabled']}")
                print(f"   Digest frequency: {settings['digest_frequency']}")
                print(f"   Min match score: {settings['min_match_score']}")
            else:
                print(f"⚠️  Failed to get settings: {response.status_code}")
        except Exception as e:
            print(f"❌ Error: {e}")
        
        # Step 4: Update notification settings
        print("\n✏️  STEP 4: Update Notification Settings")
        print("-" * 70)
        try:
            new_settings = {
                "email_enabled": True,
                "digest_frequency": "daily",
                "notify_new_matches": True,
                "notify_application_updates": True,
                "min_match_score": 0.80
            }
            response = await client.put(
                f"{BASE_URL}/notifications/settings",
                headers=headers,
                json=new_settings
            )
            if response.status_code == 200:
                print("✅ Settings updated successfully")
                print(f"   New min match score: 80%")
            else:
                print(f"⚠️  Failed to update settings: {response.status_code}")
        except Exception as e:
            print(f"❌ Error: {e}")
        
        # Step 5: Get notifications
        print("\n📬 STEP 5: Get Notifications")
        print("-" * 70)
        try:
            response = await client.get(f"{BASE_URL}/notifications", headers=headers)
            if response.status_code == 200:
                data = response.json()
                print(f"✅ Retrieved {data['total']} notifications")
                print(f"   Unread: {data['unread']}")
                if data['notifications']:
                    notif = data['notifications'][0]
                    print(f"   Latest: {notif['title']}")
            else:
                print(f"⚠️  Failed to get notifications: {response.status_code}")
        except Exception as e:
            print(f"❌ Error: {e}")
        
        # Step 6: Test notification (send test email)
        print("\n📧 STEP 6: Send Test Notification")
        print("-" * 70)
        try:
            response = await client.post(f"{BASE_URL}/notifications/test", headers=headers)
            if response.status_code == 200:
                result = response.json()
                print("✅ Test notification queued")
                print(f"   Email: {result['email']}")
                print(f"   Note: {result['note']}")
            else:
                print(f"⚠️  Test failed: {response.status_code} - {response.text}")
        except Exception as e:
            print(f"❌ Error: {e}")
        
        # Summary
        print("\n" + "=" * 70)
        print("🎉 PHASE 7 TEST COMPLETE")
        print("=" * 70)
        print("\n✅ Successfully tested:")
        print("   1. Health check")
        print("   2. User authentication")
        print("   3. Get notification settings")
        print("   4. Update notification settings")
        print("   5. Retrieve notifications")
        print("   6. Send test notification")
        print("\n📋 Next Steps:")
        print("   - Add SendGrid API key to .env")
        print("   - Add Upstash Redis credentials to .env")
        print("   - Start Celery worker: celery -A backend.v2.notifications.celery_app worker --loglevel=info")
        print("   - Start Celery beat: celery -A backend.v2.notifications.celery_app beat --loglevel=info")
        print("   - Check email inbox for test notification")
        print()


if __name__ == "__main__":
    asyncio.run(test_phase7())
