from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from typing import List
from datetime import date, timedelta
from calendar import monthrange
from app.database import get_db
from app import models, schemas
from app.auth import get_current_user

router = APIRouter()


def get_room_status_for_date(room_id: int, d: date, db: Session) -> tuple:
    maintenances = db.query(models.Maintenance).filter(
        models.Maintenance.room_id == room_id,
        models.Maintenance.start_date <= d,
        models.Maintenance.end_date > d
    ).all()
    if maintenances:
        return models.RoomStatus.MAINTENANCE, None
    
    bookings = db.query(models.Booking).filter(
        models.Booking.room_id == room_id,
        models.Booking.check_in_date <= d,
        models.Booking.check_out_date > d,
        models.Booking.status.in_([
            models.BookingStatus.PENDING,
            models.BookingStatus.CONFIRMED,
            models.BookingStatus.CHECKED_IN,
            models.BookingStatus.CHECKED_OUT
        ])
    ).all()
    
    for booking in bookings:
        if booking.status == models.BookingStatus.CHECKED_IN:
            return models.RoomStatus.OCCUPIED, booking.id
        elif booking.status in [models.BookingStatus.CONFIRMED, models.BookingStatus.PENDING]:
            return models.RoomStatus.BOOKED, booking.id
    
    return models.RoomStatus.AVAILABLE, None


@router.get("/homestay/{homestay_id}", response_model=schemas.HomestayCalendarResponse)
def get_homestay_calendar(
    homestay_id: int,
    year: int = Query(...),
    month: int = Query(...),
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_user)
):
    homestay = db.query(models.Homestay).filter(models.Homestay.id == homestay_id).first()
    if not homestay:
        raise HTTPException(status_code=404, detail="民宿不存在")
    
    if current_user.role == models.UserRole.HOST and homestay.host_id != current_user.id:
        raise HTTPException(status_code=403, detail="无权限访问")
    
    days_in_month = monthrange(year, month)[1]
    start_date = date(year, month, 1)
    end_date = date(year, month, days_in_month)
    
    rooms = db.query(models.Room).filter(models.Room.homestay_id == homestay_id).order_by(models.Room.id).all()
    
    room_calendars = []
    for room in rooms:
        days = []
        current = start_date
        while current <= end_date:
            status, booking_id = get_room_status_for_date(room.id, current, db)
            days.append(schemas.RoomCalendarDay(
                date=current,
                status=status,
                booking_id=booking_id
            ))
            current += timedelta(days=1)
        
        room_calendars.append(schemas.RoomCalendarResponse(
            room_id=room.id,
            room_name=room.name,
            days=days
        ))
    
    return schemas.HomestayCalendarResponse(
        homestay_id=homestay_id,
        homestay_name=homestay.name,
        month=f"{year}-{month:02d}",
        rooms=room_calendars
    )
