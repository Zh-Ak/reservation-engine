"""fix schema for booking flow

Revision ID: 2194d2ed4b11
Revises: 35376c225648
Create Date: 2026-10-31 19:54:20.987018

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '2194d2ed4b11'
down_revision: Union[str, Sequence[str], None] = '35376c225648'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # properties: an owner can have many properties, a city can have many hotels
    op.drop_constraint("properties_owner_id_key", "properties", type_="unique")
    op.drop_constraint("properties_city_key", "properties", type_="unique")
    op.create_index("ix_properties_owner_id", "properties", ["owner_id"])
    op.create_index("ix_properties_city_lower", "properties", [sa.text("lower(city)")])

    # room_types: no free or negative rooms, no zero-capacity rooms
    op.create_check_constraint("ck_room_types_price_positive", "room_types", "price > 0")
    op.create_check_constraint("ck_room_types_capacity_positive", "room_types", "capacity > 0")

    # bookings: price snapshot, idempotency, cancellation time, sanity checks
    op.add_column(
        "bookings",
        sa.Column("total_price", sa.Numeric(10, 2), nullable=False, server_default="0"),
    )
    op.alter_column("bookings", "total_price", server_default=None)
    op.add_column("bookings", sa.Column("idempotency_key", sa.String(), nullable=True))
    op.add_column("bookings", sa.Column("cancelled_at", sa.DateTime(), nullable=True))
    op.create_check_constraint("ck_bookings_dates_order", "bookings", "end_date > start_date")
    op.create_check_constraint("ck_bookings_guest_count_positive", "bookings", "guest_count > 0")
    op.create_unique_constraint(
        "uq_bookings_user_idempotency_key", "bookings", ["user_id", "idempotency_key"]
    )


def downgrade() -> None:
    op.drop_constraint("uq_bookings_user_idempotency_key", "bookings", type_="unique")
    op.drop_constraint("ck_bookings_guest_count_positive", "bookings", type_="check")
    op.drop_constraint("ck_bookings_dates_order", "bookings", type_="check")
    op.drop_column("bookings", "cancelled_at")
    op.drop_column("bookings", "idempotency_key")
    op.drop_column("bookings", "total_price")

    op.drop_constraint("ck_room_types_capacity_positive", "room_types", type_="check")
    op.drop_constraint("ck_room_types_price_positive", "room_types", type_="check")

    op.drop_index("ix_properties_city_lower", table_name="properties")
    op.drop_index("ix_properties_owner_id", table_name="properties")
    op.create_unique_constraint("properties_city_key", "properties", ["city"])
    op.create_unique_constraint("properties_owner_id_key", "properties", ["owner_id"])