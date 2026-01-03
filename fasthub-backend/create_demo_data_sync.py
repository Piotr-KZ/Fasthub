"""
Create demo data for AutoFlow SaaS application (Synchronous version)
Uses psycopg2 instead of asyncpg for better compatibility with Render PostgreSQL
"""

import os
import sys
from datetime import datetime, timedelta
from uuid import uuid4

import psycopg2
from psycopg2.extras import execute_values, register_uuid

# Register UUID adapter
register_uuid()

# Demo data
DEMO_ORGANIZATIONS = [
    {"name": "TechCorp Solutions", "slug": "techcorp-solutions"},
    {"name": "Digital Innovations Ltd", "slug": "digital-innovations"},
    {"name": "CloudStart Inc", "slug": "cloudstart"},
    {"name": "DataFlow Systems", "slug": "dataflow-systems"},
]

DEMO_USERS = [
    {
        "full_name": "Alice Johnson",
        "email": "alice.johnson@techcorp.com",
        "org_index": 0,
        "role": "admin",
    },
    {
        "full_name": "Bob Smith",
        "email": "bob.smith@techcorp.com",
        "org_index": 0,
        "role": "viewer",
    },
    {
        "full_name": "Carol Williams",
        "email": "carol.williams@digitalinnovations.com",
        "org_index": 1,
        "role": "admin",
    },
    {
        "full_name": "David Brown",
        "email": "david.brown@digitalinnovations.com",
        "org_index": 1,
        "role": "viewer",
    },
    {
        "full_name": "Emma Davis",
        "email": "emma.davis@digitalinnovations.com",
        "org_index": 1,
        "role": "viewer",
    },
    {
        "full_name": "Frank Miller",
        "email": "frank.miller@cloudstart.io",
        "org_index": 2,
        "role": "admin",
    },
    {
        "full_name": "Grace Wilson",
        "email": "grace.wilson@cloudstart.io",
        "org_index": 2,
        "role": "viewer",
    },
    {
        "full_name": "Henry Moore",
        "email": "henry.moore@dataflow.systems",
        "org_index": 3,
        "role": "admin",
    },
    {
        "full_name": "Iris Taylor",
        "email": "iris.taylor@dataflow.systems",
        "org_index": 3,
        "role": "viewer",
    },
    {
        "full_name": "Jack Anderson",
        "email": "jack.anderson@dataflow.systems",
        "org_index": 3,
        "role": "viewer",
    },
]

# Default password for all demo users
DEMO_PASSWORD = "DemoPass123!"

def hash_password(password: str) -> str:
    """Hash password using bcrypt"""
    import bcrypt
    return bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt()).decode('utf-8')


def create_demo_data():
    """Create all demo data"""
    # Get DATABASE_URL from environment
    database_url = os.getenv("DATABASE_URL")
    if not database_url:
        print("❌ ERROR: DATABASE_URL environment variable not set")
        sys.exit(1)
    
    # Connect to database
    print("🔌 Connecting to database...")
    conn = psycopg2.connect(database_url)
    cursor = conn.cursor()
    
    try:
        print("🚀 Starting demo data creation...\n")
        
        # Step 1: Create organizations
        print("📦 Creating organizations...")
        organizations = []
        now = datetime.utcnow()
        created_30_days_ago = now - timedelta(days=30)
        
        for org_data in DEMO_ORGANIZATIONS:
            org_id = uuid4()
            cursor.execute("""
                INSERT INTO organizations (id, name, slug, is_complete, created_at, updated_at)
                VALUES (%s, %s, %s, %s, %s, %s)
                RETURNING id
            """, (
                org_id,
                org_data["name"],
                org_data["slug"],
                True,
                created_30_days_ago,
                now
            ))
            organizations.append({"id": org_id, **org_data})
            print(f"  ✅ {org_data['name']}")
        
        # Step 2: Create users and memberships
        print("\n👥 Creating users and memberships...")
        hashed_password = hash_password(DEMO_PASSWORD)
        created_25_days_ago = now - timedelta(days=25)
        joined_20_days_ago = now - timedelta(days=20)
        
        for user_data in DEMO_USERS:
            # Create user
            user_id = uuid4()
            cursor.execute("""
                INSERT INTO users (id, email, full_name, hashed_password, is_active, is_verified, is_superuser, created_at, updated_at)
                VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s)
                RETURNING id
            """, (
                user_id,
                user_data["email"],
                user_data["full_name"],
                hashed_password,
                True,  # is_active
                True,  # is_verified
                False,  # is_superuser
                created_25_days_ago,
                now
            ))
            
            # Create membership
            org = organizations[user_data["org_index"]]
            member_id = uuid4()
            cursor.execute("""
                INSERT INTO members (id, user_id, organization_id, role, joined_at, created_at, updated_at)
                VALUES (%s, %s, %s, %s, %s, %s, %s)
            """, (
                member_id,
                user_id,
                org["id"],
                user_data["role"],
                joined_20_days_ago,
                now,
                now
            ))
            
            print(f"  ✅ {user_data['full_name']} ({user_data['email']}) - {org['name']} [{user_data['role']}]")
        
        # Commit all changes
        conn.commit()
        
        print("\n✅ Demo data created successfully!")
        print(f"\n📊 Summary:")
        print(f"  - Organizations: {len(organizations)}")
        print(f"  - Users: {len(DEMO_USERS)}")
        print(f"  - Memberships: {len(DEMO_USERS)}")
        print(f"\n🔑 Demo credentials:")
        print(f"  - Password: {DEMO_PASSWORD}")
        print(f"\n📝 Example logins:")
        for user_data in DEMO_USERS[:3]:
            print(f"  - {user_data['email']} / {DEMO_PASSWORD}")
    
    except Exception as e:
        print(f"\n❌ Error creating demo data: {e}")
        conn.rollback()
        raise
    
    finally:
        cursor.close()
        conn.close()


if __name__ == "__main__":
    create_demo_data()
