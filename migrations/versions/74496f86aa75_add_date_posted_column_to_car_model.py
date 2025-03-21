"""Add date_posted column to Car model

Revision ID: 74496f86aa75
Revises: e7a471e757c9
Create Date: 2025-02-15 01:26:41.614359

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '74496f86aa75'
down_revision = 'e7a471e757c9'
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    with op.batch_alter_table('car', schema=None) as batch_op:
        batch_op.add_column(sa.Column('date_posted', sa.DateTime(), nullable=True))

    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    with op.batch_alter_table('car', schema=None) as batch_op:
        batch_op.drop_column('date_posted')

    # ### end Alembic commands ###
