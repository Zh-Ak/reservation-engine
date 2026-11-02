import datetime
import decimal
import uuid

from pydantic import BaseModel, ConfigDict, Field, model_validator

from app.models.booking import BookingStatus


class BookingCreate(BaseModel):
    room_type_id: uuid.UUID
    start_date: datetime.date
    end_date: datetime.date
    guest_count: int = Field(gt=0, le=20)

    @model_validator(mode="after")
    def end_after_start(self) -> "BookingCreate":
        if self.end_date <= self.start_date:
            raise ValueError("end_date must be after start_date")
        return self


class BookingResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: uuid.UUID
    user_id: uuid.UUID
    room_instance_id: uuid.UUID
    start_date: datetime.date
    end_date: datetime.date
    guest_count: int
    total_price: decimal.Decimal
    status: BookingStatus
    created_at: datetime.datetime
    cancelled_at: datetime.datetime | None