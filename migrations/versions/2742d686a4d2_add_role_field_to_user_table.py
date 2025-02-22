"""Add role field to user table

Revision ID: 2742d686a4d2
Revises: b22713a9a90c
Create Date: 2025-02-18 00:56:37.199514

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '2742d686a4d2'
down_revision = 'b22713a9a90c'
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    with op.batch_alter_table('user', schema=None) as batch_op:
        batch_op.add_column(sa.Column('role', sa.Enum('BUYER', 'SELLER', 'AGENT', name='userrole'), nullable=True))
        batch_op.drop_column('is_seller')

    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    with op.batch_alter_table('user', schema=None) as batch_op:
        batch_op.add_column(sa.Column('is_seller', sa.BOOLEAN(), autoincrement=False, nullable=True))
        batch_op.drop_column('role')

    # ### end Alembic commands ###
