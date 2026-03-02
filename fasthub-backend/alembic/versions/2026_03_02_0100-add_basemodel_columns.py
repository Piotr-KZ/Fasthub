"""Add missing BaseModel columns to RBAC and Audit tables

After unifying all models to inherit from BaseModel, some tables
need updated_at columns that BaseModel provides automatically.

Revision ID: add_basemodel_columns
Revises: sync_models_with_core
Create Date: 2026-03-02 01:00:00.000000

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = 'add_basemodel_columns'
down_revision = 'sync_models_with_core'
branch_labels = None
depends_on = None


def upgrade():
    conn = op.get_bind()
    inspector = sa.inspect(conn)

    # audit_logs: add updated_at (BaseModel provides it, old model didn't have it)
    audit_cols = [col['name'] for col in inspector.get_columns('audit_logs')]
    if 'updated_at' not in audit_cols:
        op.add_column('audit_logs',
            sa.Column('updated_at', sa.DateTime(), nullable=False, server_default=sa.func.now())
        )

    # permissions: add updated_at
    perm_cols = [col['name'] for col in inspector.get_columns('permissions')]
    if 'updated_at' not in perm_cols:
        op.add_column('permissions',
            sa.Column('updated_at', sa.DateTime(), nullable=False, server_default=sa.func.now())
        )

    # role_permissions: add created_at, updated_at
    rp_cols = [col['name'] for col in inspector.get_columns('role_permissions')]
    if 'created_at' not in rp_cols:
        op.add_column('role_permissions',
            sa.Column('created_at', sa.DateTime(), nullable=False, server_default=sa.func.now())
        )
    if 'updated_at' not in rp_cols:
        op.add_column('role_permissions',
            sa.Column('updated_at', sa.DateTime(), nullable=False, server_default=sa.func.now())
        )

    # user_roles: add created_at, updated_at
    ur_cols = [col['name'] for col in inspector.get_columns('user_roles')]
    if 'created_at' not in ur_cols:
        op.add_column('user_roles',
            sa.Column('created_at', sa.DateTime(), nullable=False, server_default=sa.func.now())
        )
    if 'updated_at' not in ur_cols:
        op.add_column('user_roles',
            sa.Column('updated_at', sa.DateTime(), nullable=False, server_default=sa.func.now())
        )


def downgrade():
    op.drop_column('user_roles', 'updated_at')
    op.drop_column('user_roles', 'created_at')
    op.drop_column('role_permissions', 'updated_at')
    op.drop_column('role_permissions', 'created_at')
    op.drop_column('permissions', 'updated_at')
    op.drop_column('audit_logs', 'updated_at')
