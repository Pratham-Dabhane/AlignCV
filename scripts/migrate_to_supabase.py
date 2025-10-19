"""
Migration script to move from SQLite to Supabase PostgreSQL + Storage.

This script will:
1. Create all tables in Supabase PostgreSQL
2. Migrate data from SQLite to Supabase PostgreSQL
3. Upload local files to Supabase Storage
4. Update file paths in database

Usage:
    python scripts/migrate_to_supabase.py
"""

import asyncio
import sys
from pathlib import Path
import shutil

# Add project root to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from sqlalchemy import create_engine, text
from sqlalchemy.ext.asyncio import create_async_engine
from backend.v2.database import Base, get_db, init_db
from backend.v2.models.models import User, Document, Job, Bookmark, Application, Notification, NotificationSettings
from backend.v2.storage.handler import LocalStorage, SupabaseStorage
from backend.v2.config import settings
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


async def migrate_database():
    """Migrate all data from SQLite to Supabase PostgreSQL."""
    
    print("=" * 70)
    print("AlignCV Migration: SQLite → Supabase PostgreSQL + Storage")
    print("=" * 70)
    print()
    
    # Step 1: Backup SQLite database
    print("📦 Step 1: Backing up SQLite database...")
    sqlite_path = Path("aligncv.db")
    if sqlite_path.exists():
        backup_path = Path(f"aligncv_backup_{int(__import__('time').time())}.db")
        shutil.copy2(sqlite_path, backup_path)
        print(f"✅ Backup created: {backup_path}")
    else:
        print("⚠️  No SQLite database found (aligncv.db)")
        print("   This might be a fresh install or database is in different location")
    
    print()
    
    # Step 2: Connect to Supabase PostgreSQL
    print("🔌 Step 2: Connecting to Supabase PostgreSQL...")
    try:
        # Create async engine for Supabase
        supabase_engine = create_async_engine(settings.database_url, echo=False)
        
        # Create all tables
        async with supabase_engine.begin() as conn:
            await conn.run_sync(Base.metadata.create_all)
        
        print(f"✅ Connected to Supabase: {settings.database_url.split('@')[1].split('/')[0]}")
        print("✅ All tables created in Supabase PostgreSQL")
    except Exception as e:
        print(f"❌ Failed to connect to Supabase PostgreSQL: {e}")
        print("\n💡 Tips:")
        print("   1. Check DATABASE_URL in .env file")
        print("   2. Verify Supabase project is active")
        print("   3. Check database password is correct")
        return
    
    print()
    
    # Step 3: Migrate data from SQLite
    print("📊 Step 3: Migrating data from SQLite to Supabase...")
    
    if not sqlite_path.exists():
        print("⚠️  No SQLite database to migrate from")
        print("   Skipping data migration...")
        print()
    else:
        try:
            # Connect to SQLite
            sqlite_engine = create_engine(f"sqlite:///{sqlite_path}", echo=False)
            
            # Initialize Supabase database
            await init_db()
            
            # Migrate each table
            tables_to_migrate = [
                ("users", User),
                ("documents", Document),
                ("jobs", Job),
                ("bookmarks", Bookmark),
                ("applications", Application),
                ("notifications", Notification),
                ("notification_settings", NotificationSettings)
            ]
            
            migrated_counts = {}
            
            for table_name, model_class in tables_to_migrate:
                try:
                    # Read from SQLite
                    with sqlite_engine.connect() as sqlite_conn:
                        result = sqlite_conn.execute(text(f"SELECT * FROM {table_name}"))
                        rows = result.fetchall()
                        column_names = result.keys()
                    
                    if not rows:
                        print(f"  ⏭️  {table_name}: No data to migrate")
                        continue
                    
                    # Insert into Supabase
                    async for db in get_db():
                        for row in rows:
                            row_dict = dict(zip(column_names, row))
                            instance = model_class(**row_dict)
                            db.add(instance)
                        
                        await db.commit()
                        migrated_counts[table_name] = len(rows)
                        print(f"  ✅ {table_name}: Migrated {len(rows)} records")
                        break  # Only need one db session
                        
                except Exception as e:
                    print(f"  ⚠️  {table_name}: Migration failed - {e}")
            
            print()
            print("📊 Migration Summary:")
            for table, count in migrated_counts.items():
                print(f"   • {table}: {count} records")
                
        except Exception as e:
            print(f"❌ Data migration failed: {e}")
    
    print()
    
    # Step 4: Migrate files to Supabase Storage
    print("📤 Step 4: Migrating files to Supabase Storage...")
    
    try:
        local_storage = LocalStorage()
        supabase_storage = SupabaseStorage()
        
        local_uploads_path = Path(settings.local_storage_path)
        
        if not local_uploads_path.exists():
            print("⚠️  No local uploads directory found")
            print("   Skipping file migration...")
        else:
            # Find all files
            files = list(local_uploads_path.rglob("*.*"))
            
            if not files:
                print("⏭️  No files to migrate")
            else:
                print(f"📁 Found {len(files)} files to migrate")
                print()
                
                migrated_files = 0
                failed_files = 0
                
                for file_path in files:
                    try:
                        # Extract user_id from path (e.g., user_1/file.pdf)
                        relative_path = file_path.relative_to(local_uploads_path)
                        parts = str(relative_path).split(os.sep)
                        
                        if parts[0].startswith("user_"):
                            user_id = int(parts[0].replace("user_", ""))
                            filename = parts[-1]
                            
                            print(f"  📤 Uploading: {filename}...", end=" ")
                            
                            # Upload to Supabase
                            storage_path = supabase_storage.save_file(
                                str(file_path),
                                user_id,
                                filename
                            )
                            
                            # Update database record
                            async for db in get_db():
                                result = await db.execute(
                                    text("UPDATE documents SET storage_path = :new_path, storage_backend = 'supabase' WHERE file_name = :filename")
                                    .bindparams(new_path=storage_path, filename=filename)
                                )
                                await db.commit()
                                break
                            
                            print("✅")
                            migrated_files += 1
                        
                    except Exception as e:
                        print(f"❌ {e}")
                        failed_files += 1
                
                print()
                print(f"✅ Files migrated: {migrated_files}")
                if failed_files > 0:
                    print(f"⚠️  Files failed: {failed_files}")
        
    except Exception as e:
        print(f"❌ File migration failed: {e}")
        print("\n💡 Tips:")
        print("   1. Check SUPABASE_URL in .env")
        print("   2. Check SUPABASE_SERVICE_ROLE_KEY in .env")
        print("   3. Verify storage bucket exists in Supabase")
    
    print()
    print("=" * 70)
    print("🎉 Migration Complete!")
    print("=" * 70)
    print()
    print("✅ Next Steps:")
    print("   1. Verify data in Supabase Dashboard:")
    print("      https://app.supabase.com/project/cgmtifbpdujkcgkerkai/editor")
    print()
    print("   2. Verify files in Supabase Storage:")
    print("      https://app.supabase.com/project/cgmtifbpdujkcgkerkai/storage/buckets")
    print()
    print("   3. Update .env file:")
    print("      STORAGE_BACKEND=supabase")
    print()
    print("   4. Restart backend server:")
    print("      python -m uvicorn backend.v2.app_v2:app_v2 --port 8001")
    print()
    print("   5. Test the application!")
    print()


if __name__ == "__main__":
    import os
    
    print()
    print("⚠️  WARNING: This will migrate your data to Supabase.")
    print()
    print("Prerequisites:")
    print("   ✅ Supabase project created")
    print("   ✅ .env file updated with Supabase credentials")
    print("   ✅ Storage bucket created: aligncv-resumes")
    print()
    
    response = input("Continue with migration? (yes/no): ")
    
    if response.lower() in ['yes', 'y']:
        print()
        asyncio.run(migrate_database())
    else:
        print("Migration cancelled.")
