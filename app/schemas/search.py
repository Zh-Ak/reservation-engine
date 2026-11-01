import decimal
import uuid

from pydantic import BaseModel


class AvailableRoomType(BaseModel):
    room_type_id: uuid.UUID
    room_type_name: str
    property_id: uuid.UUID
    property_name: str
    city: str
    capacity: int
    price_per_night: decimal.Decimal
    nights: int
    total_price: decimal.Decimal
    available_rooms: int