from pydantic import BaseModel, Field
from typing import Optional
from datetime import date, datetime
from app.models import UserRole, BookingStatus, RoomType, RoomStatus
from typing import List


class Token(BaseModel):
    access_token: str
    token_type: str = "bearer"


class TokenData(BaseModel):
    username: Optional[str] = None
    role: Optional[UserRole] = None


class UserBase(BaseModel):
    username: str
    full_name: Optional[str] = None
    phone: Optional[str] = None


class UserCreate(UserBase):
    password: str
    role: UserRole


class UserResponse(UserBase):
    id: int
    role: UserRole
    created_at: datetime

    class Config:
        from_attributes = True


class LoginRequest(BaseModel):
    username: str
    password: str


class HomestayBase(BaseModel):
    name: str
    address: str
    room_count: int
    contact_phone: str
    description: Optional[str] = None


class HomestayCreate(HomestayBase):
    host_id: int


class HomestayUpdate(BaseModel):
    name: Optional[str] = None
    address: Optional[str] = None
    room_count: Optional[int] = None
    contact_phone: Optional[str] = None
    description: Optional[str] = None


class HomestayResponse(HomestayBase):
    id: int
    host_id: int
    host_name: Optional[str] = None
    avg_rating: Optional[float] = None
    created_at: datetime

    class Config:
        from_attributes = True


class RoomBase(BaseModel):
    name: str
    room_type: RoomType
    area: float
    base_price: float
    max_guests: int


class RoomCreate(RoomBase):
    homestay_id: int


class RoomUpdate(BaseModel):
    name: Optional[str] = None
    room_type: Optional[RoomType] = None
    area: Optional[float] = None
    base_price: Optional[float] = None
    max_guests: Optional[int] = None


class RoomResponse(RoomBase):
    id: int
    homestay_id: int
    homestay_name: Optional[str] = None
    avg_rating: Optional[float] = None
    created_at: datetime

    class Config:
        from_attributes = True


class BookingCreate(BaseModel):
    guest_name: str
    guest_phone: str
    check_in_date: date
    check_out_date: date
    room_id: int
    guest_count: int
    special_requests: Optional[str] = None


class BookingResponse(BaseModel):
    id: int
    guest_name: str
    guest_phone: str
    check_in_date: date
    check_out_date: date
    room_id: int
    room_name: Optional[str] = None
    homestay_id: Optional[int] = None
    homestay_name: Optional[str] = None
    guest_count: int
    special_requests: Optional[str] = None
    status: BookingStatus
    total_price: float
    reject_reason: Optional[str] = None
    actual_check_in: Optional[datetime] = None
    actual_check_out: Optional[datetime] = None
    created_at: datetime

    class Config:
        from_attributes = True


class BookingStatusUpdate(BaseModel):
    status: BookingStatus
    reject_reason: Optional[str] = None


class PriceCalculateRequest(BaseModel):
    room_id: int
    check_in_date: date
    check_out_date: date


class PriceCalculateResponse(BaseModel):
    total_price: float
    nightly_prices: List[dict]
    discount: float
    nights: int


class RoomCalendarDay(BaseModel):
    date: date
    status: RoomStatus
    booking_id: Optional[int] = None


class RoomCalendarResponse(BaseModel):
    room_id: int
    room_name: str
    days: List[RoomCalendarDay]


class HomestayCalendarResponse(BaseModel):
    homestay_id: int
    homestay_name: str
    month: str
    rooms: List[RoomCalendarResponse]


class MaintenanceCreate(BaseModel):
    room_id: int
    start_date: date
    end_date: date
    reason: Optional[str] = None


class MaintenanceResponse(BaseModel):
    id: int
    room_id: int
    room_name: Optional[str] = None
    start_date: date
    end_date: date
    reason: Optional[str] = None
    created_at: datetime

    class Config:
        from_attributes = True


class HolidayCreate(BaseModel):
    date: date
    name: str


class HolidayResponse(BaseModel):
    id: int
    date: date
    name: str

    class Config:
        from_attributes = True


class RevenueStatsResponse(BaseModel):
    homestay_id: int
    homestay_name: str
    year_month: str
    total_revenue: float
    occupancy_rate: float
    avg_daily_rate: float
    sold_nights: int
    available_nights: int
    room_type_stats: List[dict]


class ReviewCreate(BaseModel):
    booking_id: int
    rating: int = Field(ge=1, le=5)
    content: Optional[str] = None


class ReviewResponse(BaseModel):
    id: int
    booking_id: int
    room_id: int
    room_name: Optional[str] = None
    homestay_id: Optional[int] = None
    homestay_name: Optional[str] = None
    rating: int
    content: Optional[str] = None
    guest_name: Optional[str] = None
    created_at: datetime

    class Config:
        from_attributes = True


class HomestayRankingResponse(BaseModel):
    homestay_id: int
    homestay_name: str
    avg_rating: float
    review_count: int


class DashboardStatsResponse(BaseModel):
    total_revenue: float
    total_bookings: int
    occupancy_rate: float
    avg_daily_rate: float
    homestay_revenue_ranking: List[dict]
    monthly_booking_trend: List[dict]
