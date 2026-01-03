"""Convert member role from String to ENUM

Revision ID: convert_member_role_to_enum
Revises: add_performance_indexes
Create Date: 2026-01-03 14:00:00.000000

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects.postgresql import ENUM


# revision identifiers, used by Alembic.
revision = 'convert_member_role_to_enum'
down_revision = 'add_performance_indexes'
branch_labels = None
depends_on = None


def upgrade():
    print("\n" + "="*80)
    print("MIGRATION: Convert member.role from String to ENUM")
    print("="*80)
    
    # 1. Create memberrole ENUM type
    print("Step 1/4: Creating memberrole ENUM type...")
    memberrole_enum = ENUM('admin', 'viewer', name='memberrole', create_type=True)
    memberrole_enum.create(op.get_bind(), checkfirst=True)
    print("  ✓ Created memberrole ENUM")
    
    # 2. Drop existing default value
    print("Step 2/4: Dropping existing default value...")
    op.execute("ALTER TABLE members ALTER COLUMN role DROP DEFAULT")
    print("  ✓ Dropped default value")
    
    # 3. Convert column from String to ENUM using ALTER TYPE
    print("Step 3/4: Converting members.role column to ENUM...")
    op.execute("""
        ALTER TABLE members 
        ALTER COLUMN role TYPE memberrole 
        USING role::memberrole
    """)
    print("  ✓ Converted role column to ENUM")
    
    # 4. Set new default value
    print("Step 4/4: Setting new default value...")
    op.execute("ALTER TABLE members ALTER COLUMN role SET DEFAULT 'admin'::memberrole")
    print("  ✓ Set default value")
    
    print("\n" + "="*80)
    print("MIGRATION COMPLETE!")
    print("="*80 + "\n")


def downgrade():
    print("\n" + "="*80)
    print("DOWNGRADE: Convert member.role from ENUM to String")
    print("="*80)
    
    # 1. Convert column from ENUM to String
    print("Step 1/3: Converting members.role column to String...")
    op.execute("""
        ALTER TABLE members 
        ALTER COLUMN role TYPE VARCHAR(20) 
        USING role::text
    """)
    print("  ✓ Converted role column to String")
    
    # 2. Update default value
    print("Step 2/3: Setting default value...")
    op.execute("ALTER TABLE members ALTER COLUMN role SET DEFAULT 'admin'")
    print("  ✓ Set default value")
    
    # 3. Drop memberrole ENUM type
    print("Step 3/3: Dropping memberrole ENUM type...")
    op.execute("DROP TYPE IF EXISTS memberrole")
    print("  ✓ Dropped memberrole ENUM")
    
    print("\n" + "="*80)
    print("DOWNGRADE COMPLETE!")
    print("="*80 + "\n")
