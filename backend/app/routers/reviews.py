from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List
from app.database import get_db
from app import models, schemas
from app.auth import get_current_user

router = APIRouter()


@router.get("", response_model=List[schemas.ReviewResponse])
def list_reviews(
    homestay_id: int = None,
    room_id: int = None,
    db: Session = Depends(get_db)
):
    query = db.query(models.Review)
    if room_id:
        query = query.filter(models.Review.room_id == room_id)
    if homestay_id:
        query = query.join(models.Room).filter(models.Room.homestay_id == homestay_id)
    
    reviews = query.order_by(models.Review.created_at.desc()).all()
    
    result = []
    for r in reviews:
        rd = r.__dict__.copy()
        rd["room_name"] = r.room.name if r.room else None
        rd["homestay_id"] = r.room.homestay_id if r.room else None
        rd["homestay_name"] = r.room.homestay.name if r.room and r.room.homestay else None
        result.append(rd)
    return result


@router.post("", response_model=schemas.ReviewResponse)
def create_review(
    review: schemas.ReviewCreate,
    db: Session = Depends(get_db)
):
    booking = db.query(models.Booking).filter(models.Booking.id == review.booking_id).first()
    if not booking:
        raise HTTPException(status_code=404, detail="预订不存在")
    
    if booking.status != models.BookingStatus.CHECKED_OUT:
        raise HTTPException(status_code=400, detail="只有已退房的订单可以评价")
    
    existing = db.query(models.Review).filter(models.Review.booking_id == review.booking_id).first()
    if existing:
        raise HTTPException(status_code=400, detail="该订单已评价过")
    
    db_review = models.Review(
        booking_id=review.booking_id,
        room_id=booking.room_id,
        rating=review.rating,
        content=review.content,
        guest_name=booking.guest_name
    )
    db.add(db_review)
    db.commit()
    db.refresh(db_review)
    
    rd = db_review.__dict__.copy()
    rd["room_name"] = db_review.room.name if db_review.room else None
    rd["homestay_id"] = db_review.room.homestay_id if db_review.room else None
    rd["homestay_name"] = db_review.room.homestay.name if db_review.room and db_review.room.homestay else None
    return rd


@router.get("/{review_id}", response_model=schemas.ReviewResponse)
def get_review(
    review_id: int,
    db: Session = Depends(get_db)
):
    review = db.query(models.Review).filter(models.Review.id == review_id).first()
    if not review:
        raise HTTPException(status_code=404, detail="评价不存在")
    
    rd = review.__dict__.copy()
    rd["room_name"] = review.room.name if review.room else None
    rd["homestay_id"] = review.room.homestay_id if review.room else None
    rd["homestay_name"] = review.room.homestay.name if review.room and review.room.homestay else None
    return rd
