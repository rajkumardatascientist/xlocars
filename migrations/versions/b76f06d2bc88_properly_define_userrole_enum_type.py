"""Properly define UserRole enum type

Revision ID: b76f06d2bc88
Revises: 2742d686a4d2
Create Date: 2025-02-18 01:42:38.123456

"""
from alembic import op
import sqlalchemy as sa

# Import UserRoleType from where it is defined
from models.user import UserRoleType # ADD THIS LINE


# revision identifiers, used by Alembic.
revision = 'b76f06d2bc88'
down_revision = '2742d686a4d2'
branch_labels = None
depends_on = None


def upgrade():
    op.alter_column('user', 'role',
                    existing_type=sa.VARCHAR(length=20), # Existing type
                    type_=UserRoleType(), # Use UserRoleType
                    existing_nullable=True)


def downgrade():
    op.alter_column('user', 'role',
                    existing_type=UserRoleType(),  # Existing type
                    type_=sa.VARCHAR(length=20),  # Revert back
                    existing_nullable=True)