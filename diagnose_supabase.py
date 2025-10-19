"""
Quick diagnostic test for Supabase API keys
"""
import os
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent / "backend"))

print("="*60)
print("🔍 SUPABASE API KEY DIAGNOSTIC")
print("="*60)
print()

# Test 1: Check environment variables
print("1️⃣  Environment Variables:")
print("-" * 40)
from backend.v2.config import settings

print(f"✅ SUPABASE_URL: {settings.supabase_url}")
print(f"✅ SUPABASE_ANON_KEY: {settings.supabase_anon_key[:50]}...")
print(f"✅ SUPABASE_SERVICE_ROLE_KEY: {settings.supabase_service_role_key[:50]}...")
print(f"✅ STORAGE_BUCKET: {settings.supabase_storage_bucket}")
print()

# Test 2: Decode JWT tokens
print("2️⃣  JWT Token Validation:")
print("-" * 40)
try:
    import jwt
    
    # Decode anon key
    anon_decoded = jwt.decode(settings.supabase_anon_key, options={'verify_signature': False})
    print(f"✅ Anon Key - Role: {anon_decoded['role']}")
    print(f"✅ Anon Key - Project: {anon_decoded['ref']}")
    print(f"✅ Anon Key - Expires: {anon_decoded['exp']} (year 2045)")
    
    # Decode service key
    service_decoded = jwt.decode(settings.supabase_service_role_key, options={'verify_signature': False})
    print(f"✅ Service Key - Role: {service_decoded['role']}")
    print(f"✅ Service Key - Project: {service_decoded['ref']}")
    print(f"✅ Service Key - Expires: {service_decoded['exp']} (year 2045)")
    
    print("\n✅ Both JWT tokens are structurally valid!")
    
except Exception as e:
    print(f"❌ JWT decode error: {e}")

print()

# Test 3: Test Supabase client initialization
print("3️⃣  Supabase Client Test:")
print("-" * 40)
try:
    from supabase import create_client
    
    # Try with service role key
    client = create_client(settings.supabase_url, settings.supabase_service_role_key)
    print(f"✅ Supabase client created successfully")
    
except Exception as e:
    print(f"❌ Client creation failed: {e}")

print()

# Test 4: Check bucket access
print("4️⃣  Bucket Access Test:")
print("-" * 40)
try:
    # List all buckets
    buckets = client.storage.list_buckets()
    print(f"✅ Can access storage API")
    print(f"✅ Found {len(buckets)} bucket(s):")
    
    bucket_names = [b.name for b in buckets]
    for bucket in buckets:
        status = "✅" if bucket.name == settings.supabase_storage_bucket else "  "
        print(f"  {status} {bucket.name} (public: {bucket.public})")
    
    if settings.supabase_storage_bucket in bucket_names:
        print(f"\n✅ Target bucket '{settings.supabase_storage_bucket}' EXISTS!")
    else:
        print(f"\n❌ Target bucket '{settings.supabase_storage_bucket}' NOT FOUND!")
        print(f"   Create it at: https://app.supabase.com/project/cgmtifbpdujkcgkerkai/storage/buckets")
    
except Exception as e:
    print(f"❌ Bucket access failed: {e}")
    print(f"\n🔧 DIAGNOSIS:")
    if "403" in str(e) or "Unauthorized" in str(e):
        print("   → API keys might be from wrong project")
        print("   → Or bucket doesn't exist yet")
        print(f"   → Verify at: https://app.supabase.com/project/cgmtifbpdujkcgkerkai/settings/api")
    elif "401" in str(e):
        print("   → API keys are invalid or expired")
    else:
        print(f"   → Unexpected error: {e}")

print()
print("="*60)
print("📊 SUMMARY:")
print("="*60)
print()
print("If buckets are listed above:")
print("  ✅ API keys are CORRECT and WORKING!")
print("  ✅ Just need to create the bucket in dashboard")
print()
print("If you see 403/Unauthorized errors:")
print("  ❌ API keys need to be updated")
print("  → Go to: https://app.supabase.com/project/cgmtifbpdujkcgkerkai/settings/api")
print("  → Copy BOTH keys (anon + service_role)")
print("  → Update in .env file")
print()
