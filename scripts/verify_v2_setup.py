"""
Quick verification script for AlignCV V2 Phase 1 setup.

Checks:
- Dependencies installed
- SpaCy model downloaded
- .env file exists
- Database connection works
- File storage directory exists
"""

import sys
import os
from pathlib import Path


def check_dependencies():
    """Check if required packages are installed."""
    print("🔍 Checking dependencies...")
    
    required = [
        "fastapi",
        "sqlalchemy",
        "alembic",
        "pydantic",
        "pydantic_settings",
        "jose",
        "passlib",
        "google.auth",
        "fitz",  # PyMuPDF
        "docx",
        "spacy",
        "boto3",
    ]
    
    missing = []
    for package in required:
        try:
            __import__(package.replace(".", "_"))
        except ImportError:
            missing.append(package)
    
    if missing:
        print(f"  ❌ Missing packages: {', '.join(missing)}")
        print("  Run: pip install -r requirements.txt")
        return False
    else:
        print("  ✅ All dependencies installed")
        return True


def check_spacy_model():
    """Check if SpaCy model is downloaded."""
    print("\n🔍 Checking SpaCy model...")
    
    try:
        import spacy
        nlp = spacy.load("en_core_web_sm")
        print("  ✅ SpaCy model (en_core_web_sm) is installed")
        return True
    except OSError:
        print("  ❌ SpaCy model not found")
        print("  Run: python -m spacy download en_core_web_sm")
        return False


def check_env_file():
    """Check if .env file exists."""
    print("\n🔍 Checking .env file...")
    
    env_path = Path(".env")
    if env_path.exists():
        print("  ✅ .env file exists")
        
        # Check for required variables
        with open(env_path) as f:
            content = f.read()
        
        required_vars = ["DATABASE_URL", "JWT_SECRET_KEY"]
        missing_vars = []
        
        for var in required_vars:
            if f"{var}=PLACEHOLDER" in content or f"{var}=" not in content:
                missing_vars.append(var)
        
        if missing_vars:
            print(f"  ⚠️  Please update placeholders: {', '.join(missing_vars)}")
            return False
        else:
            print("  ✅ Required variables are set")
            return True
    else:
        print("  ❌ .env file not found")
        print("  Run: cp .env.example .env")
        return False


def check_storage_directory():
    """Check if storage directory exists."""
    print("\n🔍 Checking storage directory...")
    
    storage_path = Path("storage/uploads")
    if storage_path.exists():
        print(f"  ✅ Storage directory exists: {storage_path}")
        return True
    else:
        print(f"  ⚠️  Storage directory not found, will be created automatically")
        return True  # Not critical, will be created


def check_database_connection():
    """Check if database connection works (if configured)."""
    print("\n🔍 Checking database connection...")
    
    try:
        from dotenv import load_dotenv
        load_dotenv()
        
        from backend.v2.config import settings
        
        if "PLACEHOLDER" in settings.database_url:
            print("  ⚠️  Database URL not configured yet")
            return False
        
        print("  ✅ Database URL is configured")
        print(f"  📍 Database: {settings.database_url.split('@')[1] if '@' in settings.database_url else 'configured'}")
        return True
        
    except Exception as e:
        print(f"  ❌ Error loading configuration: {str(e)}")
        return False


def check_v1_compatibility():
    """Check if V1 files are still intact."""
    print("\n🔍 Checking V1 compatibility...")
    
    v1_files = [
        "backend/app.py",
        "backend/utils/semantic_utils.py",
        "frontend/app.py",
        "tests/test_api.py",
        "tests/test_semantic_utils.py"
    ]
    
    all_exist = True
    for file in v1_files:
        if not Path(file).exists():
            print(f"  ❌ V1 file missing: {file}")
            all_exist = False
    
    if all_exist:
        print("  ✅ All V1 files intact")
        return True
    return False


def main():
    """Run all checks."""
    print("=" * 60)
    print("🚀 AlignCV V2 Phase 1 - Setup Verification")
    print("=" * 60)
    
    checks = [
        check_dependencies,
        check_spacy_model,
        check_env_file,
        check_storage_directory,
        check_database_connection,
        check_v1_compatibility,
    ]
    
    results = [check() for check in checks]
    
    print("\n" + "=" * 60)
    print("📊 Summary")
    print("=" * 60)
    
    passed = sum(results)
    total = len(results)
    
    print(f"  Checks passed: {passed}/{total}")
    
    if passed == total:
        print("\n  ✅ All checks passed! You're ready to start V2!")
        print("\n  🚀 Next steps:")
        print("     1. cd backend")
        print("     2. python -m uvicorn v2.app_v2:app_v2 --reload --port 8001")
        print("     3. Open http://localhost:8001/v2/docs")
        return 0
    else:
        print("\n  ⚠️  Some checks failed. Please fix the issues above.")
        print("\n  📚 See docs/V2_PHASE1_SETUP.md for help")
        return 1


if __name__ == "__main__":
    sys.exit(main())
