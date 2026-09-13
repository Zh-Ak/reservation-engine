"""fix bookingstatus enum values to lowercase

Revision ID: 2b1f17bd52b8
Revises: f85a1f9d58fe
Create Date: 2026-09-12 11:51:51.500624

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '2b1f17bd52b8'
down_revision: Union[str, Sequence[str], None] = 'f85a1f9d58fe'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade():
    op.execute("ALTER TYPE bookingstatus RENAME VALUE 'CONFIRMED' TO 'confirmed'")
    op.execute("ALTER TYPE bookingstatus RENAME VALUE 'CANCELLED' TO 'cancelled'")

def downgrade():
    op.execute("ALTER TYPE bookingstatus RENAME VALUE 'confirmed' TO 'CONFIRMED'")
    op.execute("ALTER TYPE bookingstatus RENAME VALUE 'cancelled' TO 'CANCELLED'")
