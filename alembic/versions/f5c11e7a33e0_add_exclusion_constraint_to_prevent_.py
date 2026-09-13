"""add exclusion constraint to prevent overlapping confirmed bookings

Revision ID: f5c11e7a33e0
Revises: 2b1f17bd52b8
Create Date: 2026-09-13 10:29:37.274425

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = 'f5c11e7a33e0'
down_revision: Union[str, Sequence[str], None] = '2b1f17bd52b8'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade():
    op.execute("CREATE EXTENSION IF NOT EXISTS btree_gist")
    op.execute("""
        ALTER TABLE bookings
        ADD CONSTRAINT no_overlapping_confirmed_bookings
        EXCLUDE USING gist (
            room_instance_id WITH =,
            daterange(start_date, end_date) WITH &&
        )
        WHERE (status = 'confirmed')
    """)

def downgrade():
    op.execute("ALTER TABLE bookings DROP CONSTRAINT no_overlapping_confirmed_bookings")
    op.execute("DROP EXTENSION IF EXISTS btree_gist")
