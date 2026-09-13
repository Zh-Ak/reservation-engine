"""fix userrole enum values to lowercase

Revision ID: d3997ee084f1
Revises: f5c11e7a33e0
Create Date: 2026-09-13 11:09:33.108836

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = 'd3997ee084f1'
down_revision: Union[str, Sequence[str], None] = 'f5c11e7a33e0'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade():
    op.execute("ALTER TYPE userrole RENAME VALUE 'CLIENT' TO 'client'")
    op.execute("ALTER TYPE userrole RENAME VALUE 'PROVIDER' TO 'provider'")
    op.execute("ALTER TYPE userrole RENAME VALUE 'MODERATOR' TO 'moderator'")

def downgrade():
    op.execute("ALTER TYPE userrole RENAME VALUE 'client' TO 'CLIENT'")
    op.execute("ALTER TYPE userrole RENAME VALUE 'provider' TO 'PROVIDER'")
    op.execute("ALTER TYPE userrole RENAME VALUE 'moderator' TO 'MODERATOR'")
