from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from typing import List, Optional
from datetime import date, datetime
from app.database import get_db
from app import models, schemas
from app.auth import get_current_user, require_host
from app.pricing import calculate_total_price, is_room_available

router = APIRouter()


@router.get("", response_model=List[schemas.BookingResponse])
def list_bookings(
    status: Optional[models.BookingStatus] = None,
    homestay_id: Optional[int] = None,
    room_id: Optional[int] = None,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_user)
):
    query = db.query(models.Booking)
    
    if status:
        query = query.filter(models.Booking.status == status)
    if room_id:
        query = query.filter(models.Booking.room_id == room_id)
    if homestay_id:
        query = query.join(models.Room).filter(models.Room.homestay_id == homestay_id)
    
    if current_user.role == models.UserRole.HOST:
        query = query.join(models.Room).join(models.Homestay).filter(
            models.Homestay.host_id == current_user.id
        )
    
    query = query.order_by(models.Booking.created_at.desc())
    bookings = query.all()
    
    result = []
    for booking in bookings:
        b = booking.__dict__.copy()
        b["room_name"] = booking.room.name if booking.room else None
        b["homestay_id"] = booking.room.homestay_id if booking.room else None
        b["homestay_name"] = booking.room.homestay.name if booking.room and booking.room.homestay else None
        result.append(b)
    return result


@router.get("/{booking_id}", response_model=schemas.BookingResponse)
def get_booking(
    booking_id: int,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_user)
):
    booking = db.query(models.Booking).filter(models.Booking.id == booking_id).first()
    if not booking:
        raise HTTPException(status_code=404, detail="预订不存在")
    
    if current_user.role == models.UserRole.HOST:
        if booking.room.homestay.host_id != current_user.id:
            raise HTTPException(status_code=403, detail="无权限访问")
    
    b = booking.__dict__.copy()
    b["room_name"] = booking.room.name if booking.room else None
    b["homestay_id"] = booking.room.homestay_id if booking.room else None
    b["homestay_name"] = booking.room.homestay.name if booking.room and booking.room.homestay else None
    return b


@router.post("", response_model=schemas.BookingResponse)
def create_booking(
    booking: schemas.BookingCreate,
    db: Session = Depends(get_db)
):
    room = db.query(models.Room).filter(models.Room.id == booking.room_id).first()
    if not room:
        raise HTTPException(status_code=404, detail="房间不存在")
    
    if booking.guest_count > room.max_guests:
        raise HTTPException(status_code=400, detail=f"入住人数超过房间最大容纳人数({room.max_guests}人)")
    
    if booking.check_in_date >= booking.check_out_date:
        raise HTTPException(status_code=400, detail="入住日期必须早于离开日期")
    
    if not is_room_available(booking.room_id, booking.check_in_date, booking.check_out_date, db):
        raise HTTPException(status_code=400, detail="所选日期范围内房间不可用")
    
    price_info = calculate_total_price(room, booking.check_in_date, booking.check_out_date, db)
    
    db_booking = models.Booking(
        guest_name=booking.guest_name,
        guest_phone=booking.guest_phone,
        check_in_date=booking.check_in_date,
        check_out_date=booking.check_out_date,
        room_id=booking.room_id,
        guest_count=booking.guest_count,
        special_requests=booking.special_requests,
        status=models.BookingStatus.PENDING,
        total_price=price_info["total_price"]
    )
    db.add(db_booking)
    db.commit()
    db.refresh(db_booking)
    
    b = db_booking.__dict__.copy()
    b["room_name"] = db_booking.room.name if db_booking.room else None
    b["homestay_id"] = db_booking.room.homestay_id if db_booking.room else None
    b["homestay_name"] = db_booking.room.homestay.name if db_booking.room and db_booking.room.homestay else None
    return b


@router.put("/{booking_id}/status", response_model=schemas.BookingResponse)
def update_booking_status(
    booking_id: int,
    status_update: schemas.BookingStatusUpdate,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_user)
):
    booking = db.query(models.Booking).filter(models.Booking.id == booking_id).first()
    if not booking:
        raise HTTPException(status_code=404, detail="预订不存在")
    
    if current_user.role == models.UserRole.HOST:
        if booking.room.homestay.host_id != current_user.id:
            raise HTTPException(status_code=403, detail="无权限操作")
    
    new_status = status_update.status
    
    if new_status == models.BookingStatus.CANCELLED:
        if booking.status not in [models.BookingStatus.PENDING, models.BookingStatus.CONFIRMED]:
            raise HTTPException(status_code=400, detail="当前状态无法取消")
        if status_update.reject_reason:
            booking.reject_reason = status_update.reject_reason
    
    elif new_status == models.BookingStatus.CONFIRMED:
        if booking.status != models.BookingStatus.PENDING:
            raise HTTPException(status_code=400, detail="只有待确认状态的预订可以确认")
        if not is_room_available(booking.room_id, booking.check_in_date, booking.check_out_date, db, exclude_booking_id=booking.id):
            raise HTTPException(status_code=400, detail="该日期范围已有其他预订，无法确认")
    
    elif new_status == models.BookingStatus.CHECKED_IN:
        if booking.status != models.BookingStatus.CONFIRMED:
            raise HTTPException(status_code=400, detail="只有已确认状态的预订可以办理入住")
        booking.actual_check_in = datetime.utcnow()
    
    elif new_status == models.BookingStatus.CHECKED_OUT:
        if booking.status != models.BookingStatus.CHECKED_IN:
            raise HTTPException(status_code=400, detail="只有已入住状态的预订可以办理退房")
        booking.actual_check_out = datetime.utcnow()
    
    booking.status = new_status
    db.commit()
    db.refresh(booking)
    
    b = booking.__dict__.copy()
    b["room_name"] = booking.room.name if booking.room else None
    b["homestay_id"] = booking.room.homestay_id if booking.room else None
    b["homestay_name"] = booking.room.homestay.name if booking.room and booking.room.homestay else None
    return b


@router.post("/calculate-price", response_model=schemas.PriceCalculateResponse)
def calculate_price(
    req: schemas.PriceCalculateRequest,
    db: Session = Depends(get_db)
):
    room = db.query(models.Room).filter(models.Room.id == req.room_id).first()
    if not room:
        raise HTTPException(status_code=404, detail="房间不存在")
    
    return calculate_total_price(room, req.check_in_date, req.check_out_date, db)
