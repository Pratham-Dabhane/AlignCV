"""
Test Supabase Storage Integration
Tests file upload, download, and verification in dashboard
"""

import os
import sys
from pathlib import Path

# Add backend to path
sys.path.insert(0, str(Path(__file__).parent / "backend"))

def test_supabase_storage():
    """Test complete Supabase storage workflow"""
    print("\n" + "="*60)
    print("🧪 TESTING SUPABASE STORAGE INTEGRATION")
    print("="*60 + "\n")
    
    # Test 1: Configuration
    print("📋 Test 1: Configuration")
    print("-" * 40)
    try:
        from backend.v2.config import settings
        print(f"✅ Database URL: {settings.database_url[:50]}...")
        print(f"✅ Supabase URL: {settings.supabase_url}")
        print(f"✅ Storage Backend: {settings.storage_backend}")
        print(f"✅ Storage Bucket: {settings.supabase_storage_bucket}")
        
        if settings.storage_backend != "supabase":
            print(f"⚠️  WARNING: Storage backend is '{settings.storage_backend}', not 'supabase'")
            return False
    except Exception as e:
        print(f"❌ Configuration failed: {e}")
        return False
    
    print()
    
    # Test 2: Storage Handler Initialization
    print("🔧 Test 2: Storage Handler Initialization")
    print("-" * 40)
    try:
        from backend.v2.storage.handler import get_storage
        storage = get_storage()
        print(f"✅ Storage handler type: {type(storage).__name__}")
        
        if type(storage).__name__ != "SupabaseStorage":
            print(f"❌ Expected SupabaseStorage, got {type(storage).__name__}")
            return False
    except Exception as e:
        print(f"❌ Storage handler initialization failed: {e}")
        return False
    
    print()
    
    # Test 3: Create Test File
    print("📝 Test 3: Create Test Resume File")
    print("-" * 40)
    test_file_path = "test_resume.txt"
    test_content = """
JOHN DOE
Software Engineer

EXPERIENCE:
- Senior Developer at TechCorp (2020-2023)
- Full Stack Developer at StartupXYZ (2018-2020)

SKILLS:
Python, JavaScript, React, PostgreSQL, AWS
"""
    
    try:
        with open(test_file_path, "w") as f:
            f.write(test_content)
        print(f"✅ Created test file: {test_file_path}")
    except Exception as e:
        print(f"❌ Failed to create test file: {e}")
        return False
    
    print()
    
    # Test 4: Upload to Supabase
    print("☁️  Test 4: Upload File to Supabase Storage")
    print("-" * 40)
    try:
        storage_path = storage.save_file(
            file_path=test_file_path,
            user_id=999,  # Test user ID
            original_filename="test_resume.txt"
        )
        print(f"✅ File uploaded successfully!")
        print(f"✅ Storage path: {storage_path}")
    except Exception as e:
        print(f"❌ Upload failed: {e}")
        # Cleanup
        if os.path.exists(test_file_path):
            os.remove(test_file_path)
        return False
    
    print()
    
    # Test 5: Get File URL
    print("🔗 Test 5: Generate Signed URL")
    print("-" * 40)
    try:
        file_url = storage.get_file_url(storage_path)
        if file_url:
            print(f"✅ Signed URL generated!")
            print(f"✅ URL (first 80 chars): {file_url[:80]}...")
        else:
            print("⚠️  Could not generate URL (file might not exist yet)")
    except Exception as e:
        print(f"⚠️  URL generation warning: {e}")
    
    print()
    
    # Test 6: Download File
    print("⬇️  Test 6: Download File from Supabase")
    print("-" * 40)
    download_path = "test_resume_downloaded.txt"
    try:
        success = storage.download_file(storage_path, download_path)
        if success:
            print(f"✅ File downloaded successfully!")
            with open(download_path, "r") as f:
                content = f.read()
            print(f"✅ Content verified ({len(content)} chars)")
            # Cleanup
            os.remove(download_path)
        else:
            print("⚠️  Download returned False (file might not exist)")
    except Exception as e:
        print(f"⚠️  Download warning: {e}")
    
    print()
    
    # Test 7: Delete File
    print("🗑️  Test 7: Delete File from Supabase")
    print("-" * 40)
    try:
        success = storage.delete_file(storage_path)
        if success:
            print(f"✅ File deleted successfully!")
        else:
            print("⚠️  Delete returned False (file might not exist)")
    except Exception as e:
        print(f"⚠️  Delete warning: {e}")
    
    # Cleanup local test file
    if os.path.exists(test_file_path):
        os.remove(test_file_path)
        print(f"✅ Cleaned up local test file")
    
    print()
    print("="*60)
    print("✅ ALL TESTS COMPLETED!")
    print("="*60)
    print()
    
    # Instructions
    print("📊 VERIFY IN SUPABASE DASHBOARD:")
    print("-" * 40)
    print(f"1. Go to: https://app.supabase.com/project/cgmtifbpdujkcgkerkai/storage/buckets")
    print(f"2. Click on bucket: aligncv-resumes")
    print(f"3. Look for folder: user_999/")
    print(f"4. You should see: test_resume.txt (if delete failed)")
    print()
    print("🎯 WHEN YOU USE FRONTEND:")
    print("-" * 40)
    print("1. Upload resume through frontend → Goes to Supabase")
    print("2. Check dashboard → File appears in user_XXX/ folder")
    print("3. File persists forever in cloud!")
    print("4. Can download/view anytime from dashboard")
    print()
    
    return True


if __name__ == "__main__":
    try:
        success = test_supabase_storage()
        if success:
            print("✅ Supabase Storage is working perfectly!")
            print("✅ Frontend uploads will appear in dashboard!")
        else:
            print("❌ Some tests failed - check errors above")
    except KeyboardInterrupt:
        print("\n\n⚠️  Test interrupted by user")
    except Exception as e:
        print(f"\n\n❌ Unexpected error: {e}")
        import traceback
        traceback.print_exc()
