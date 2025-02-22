"""Update payment models with transaction ID and enum status

Revision ID: 1fd2439a52e5
Revises: cf5d6c3f9f89
Create Date: 2024-05-08 12:34:56.789012

"""
from alembic import op
import sqlalchemy as sa

# revision identifiers, used by Alembic.
revision = '1fd2439a52e5'
down_revision = 'cf5d6c3f9f89'
branch_labels = None
depends_on = None


def upgrade():
    # Add transaction_id column to FeaturedPayments
    op.add_column('featured_payments', sa.Column('transaction_id', sa.String(255), nullable=True))

    # Add transaction_id column to BuyerPayments
    op.add_column('buyer_payments', sa.Column('transaction_id', sa.String(255), nullable=True))

    # Add the ENUM if it doesn't exist.
    try:
        op.execute("CREATE TYPE paymentstatus AS ENUM ('pending_payment', 'payment_failed', 'payment_successful', 'payment_refunded')")
    except Exception as e:
        print(f"Enum 'paymentstatus' already exists or other error: {e}")

    #If the ENUM doesn't exist we are creating one and so we update the payment statuses.
    try:
        op.alter_column('featured_payments', 'payment_status', type_=sa.Enum('pending_payment', 'payment_failed', 'payment_successful', 'payment_refunded', name='paymentstatus'), postgresql_using='payment_status::text::paymentstatus')
        op.alter_column('buyer_payments', 'payment_status', type_=sa.Enum('pending_payment', 'payment_failed', 'payment_successful', 'payment_refunded', name='paymentstatus'), postgresql_using='payment_status::text::paymentstatus')
    except Exception as e:
        print(f"Columns ENUM update fails: {e}")


def downgrade():
    # Try to reverse the ENUM changes
    try:
        op.drop_column('featured_payments', 'payment_status')
        op.drop_column('buyer_payments', 'payment_status')
        op.execute("DROP TYPE paymentstatus")
    except Exception as e:
        print(f"Error during downgrade of enums: {e}")

    # Always try to drop transaction id
    op.drop_column('featured_payments', 'transaction_id')
    op.drop_column('buyer_payments', 'transaction_id')