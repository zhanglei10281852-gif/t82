from sqlalchemy import Column, Integer, String, Float, Date, DateTime, ForeignKey, Text, Enum, Boolean
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from app.database import Base
import enum


class UserRole(str, enum.Enum):
    ADMIN = "admin"
    HOST = "host"


class BookingStatus(str, enum.Enum):
    PENDING = "pending"
    CONFIRMED = "confirmed"
    CHECKED_IN = "checked_in"
    CHECKED_OUT = "checked_out"
    CANCELLED = "cancelled"


class RoomType(str, enum.Enum):
    KING = "大床房"
    TWIN = "双床房"
    FAMILY = "家庭套房"
    DELUXE = "豪华大床房"
    SUITE = "行政套房"


class RoomStatus(str, enum.Enum):
    AVAILABLE = "available"
    BOOKED = "booked"
    OCCUPIED = "occupied"
    MAINTENANCE = "maintenance"


class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    username = Column(String(50), unique=True, index=True, nullable=False)
    password_hash = Column(String(255), nullable=False)
    role = Column(Enum(UserRole), nullable=False)
    full_name = Column(String(100))
    phone = Column(String(20))
    created_at = Column(DateTime(timezone=True), server_default=func.now())

    homestays = relationship("Homestay", back_populates="host")


class Homestay(Base):
    __tablename__ = "homestays"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(100), nullable=False)
    address = Column(String(255), nullable=False)
    room_count = Column(Integer, nullable=False)
    contact_phone = Column(String(20), nullable=False)
    description = Column(Text)
    host_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now())

    host = relationship("User", back_populates="homestays")
    rooms = relationship("Room", back_populates="homestay", cascade="all, delete-orphan")


class Room(Base):
    __tablename__ = "rooms"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(50), nullable=False)
    room_type = Column(Enum(RoomType), nullable=False)
    area = Column(Float, nullable=False)
    base_price = Column(Float, nullable=False)
    max_guests = Column(Integer, nullable=False)
    homestay_id = Column(Integer, ForeignKey("homestays.id"), nullable=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now())

    homestay = relationship("Homestay", back_populates="rooms")
    bookings = relationship("Booking", back_populates="room")
    maintenances = relationship("Maintenance", back_populates="room")
    reviews = relationship("Review", back_populates="room")


class Booking(Base):
    __tablename__ = "bookings"

    id = Column(Integer, primary_key=True, index=True)
    guest_name = Column(String(50), nullable=False)
    guest_phone = Column(String(20), nullable=False)
    check_in_date = Column(Date, nullable=False)
    check_out_date = Column(Date, nullable=False)
    room_id = Column(Integer, ForeignKey("rooms.id"), nullable=False)
    guest_count = Column(Integer, nullable=False)
    special_requests = Column(Text)
    status = Column(Enum(BookingStatus), default=BookingStatus.PENDING, nullable=False)
    total_price = Column(Float, nullable=False)
    reject_reason = Column(Text)
    actual_check_in = Column(DateTime(timezone=True))
    actual_check_out = Column(DateTime(timezone=True))
    created_at = Column(DateTime(timezone=True), server_default=func.now())

    room = relationship("Room", back_populates="bookings")
    review = relationship("Review", back_populates="booking", uselist=False)


class Maintenance(Base):
    __tablename__ = "maintenances"

    id = Column(Integer, primary_key=True, index=True)
    room_id = Column(Integer, ForeignKey("rooms.id"), nullable=False)
    start_date = Column(Date, nullable=False)
    end_date = Column(Date, nullable=False)
    reason = Column(String(255))
    created_at = Column(DateTime(timezone=True), server_default=func.now())

    room = relationship("Room", back_populates="maintenances")


class Holiday(Base):
    __tablename__ = "holidays"

    id = Column(Integer, primary_key=True, index=True)
    date = Column(Date, unique=True, nullable=False)
    name = Column(String(50), nullable=False)


class Review(Base):
    __tablename__ = "reviews"

    id = Column(Integer, primary_key=True, index=True)
    booking_id = Column(Integer, ForeignKey("bookings.id"), nullable=False)
    room_id = Column(Integer, ForeignKey("rooms.id"), nullable=False)
    rating = Column(Integer, nullable=False)
    content = Column(Text)
    guest_name = Column(String(50))
    created_at = Column(DateTime(timezone=True), server_default=func.now())

    booking = relationship("Booking", back_populates="review")
    room = relationship("Room", back_populates="reviews")
