"""Test database connection with asyncpg."""
import asyncio
import asyncpg
import os
from dotenv import load_dotenv

load_dotenv()

async def test_connection():
    try:
        # Get connection details
        conn = await asyncpg.connect(
            host='db.cgmtifbpdujkcgkerkai.supabase.co',
            port=5432,
            user='postgres',
            password='$n9nS?LEUjrVaax',
            database='postgres',
            ssl='require'
        )
        
        # Test query
        version = await conn.fetchval('SELECT version()')
        print(f"✅ Connected successfully!")
        print(f"PostgreSQL version: {version}")
        
        await conn.close()
        return True
        
    except Exception as e:
        print(f"❌ Connection failed: {e}")
        return False

if __name__ == "__main__":
    asyncio.run(test_connection())
