#!/usr/bin/env python3
"""
Test script to verify database connection with SSL configuration
"""
import os
import sys

sys.path.append(".")

from app.models.database import init_db, get_db


def test_connection():
    """Test database connection"""
    print("Testing database connection...")
    print(f"DATABASE_URL: {os.getenv('DATABASE_URL', 'Not set')}")

    try:
        # Test database initialization
        init_db()
        print("✅ Database initialization successful")

        # Test connection health
        db = get_db()
        if db.is_connected():
            print("✅ Database connection is healthy")
        else:
            print("❌ Database connection is not healthy")

        # Test a simple query
        with db.conn.cursor() as cur:
            cur.execute("SELECT version()")
            version = cur.fetchone()
            print(f"✅ Database query successful: {version[0]}")

        return True

    except Exception as e:
        print(f"❌ Database connection failed: {e}")
        return False


if __name__ == "__main__":
    success = test_connection()
    sys.exit(0 if success else 1)
