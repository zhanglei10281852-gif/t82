from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from sqlalchemy import func, and_
from typing import List, Optional
from datetime import date, timedelta
from calendar import monthrange
from app.database import get_db
from app import models, schemas
from app.auth import get_current_user, require_admin

router = APIRouter()


@router.get("/revenue/homestay/{homestay_id}", response_model=schemas.RevenueStatsResponse)
def get_homestay_revenue(
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
    
    start_date = date(year, month, 1)
    days_in_month = monthrange(year, month)[1]
    end_date = date(year, month, days_in_month)
    
    bookings = db.query(models.Booking).join(models.Room).filter(
        models.Room.homestay_id == homestay_id,
        models.Booking.status == models.BookingStatus.CHECKED_OUT,
        models.Booking.check_in_date <= end_date,
        models.Booking.check_out_date > start_date
    ).all()
    
    total_revenue = 0.0
    sold_nights = 0
    room_type_stats = {}
    
    for booking in bookings:
        total_revenue += booking.total_price
        nights = (booking.check_out_date - booking.check_in_date).days
        sold_nights += nights
        
        room_type = booking.room.room_type.value
        if room_type not in room_type_stats:
            room_type_stats[room_type] = {"nights": 0, "revenue": 0}
        room_type_stats[room_type]["nights"] += nights
        room_type_stats[room_type]["revenue"] += booking.total_price
    
    rooms = db.query(models.Room).filter(models.Room.homestay_id == homestay_id).all()
    total_rooms = len(rooms)
    available_nights = total_rooms * days_in_month
    
    occupancy_rate = (sold_nights / available_nights * 100) if available_nights > 0 else 0
    avg_daily_rate = (total_revenue / sold_nights) if sold_nights > 0 else 0
    
    room_type_list = []
    for rt, data in room_type_stats.items():
        room_type_list.append({
            "room_type": rt,
            "nights": data["nights"],
            "revenue": data["revenue"],
            "percentage": (data["revenue"] / total_revenue * 100) if total_revenue > 0 else 0
        })
    room_type_list.sort(key=lambda x: x["revenue"], reverse=True)
    
    return schemas.RevenueStatsResponse(
        homestay_id=homestay_id,
        homestay_name=homestay.name,
        year_month=f"{year}-{month:02d}",
        total_revenue=round(total_revenue, 2),
        occupancy_rate=round(occupancy_rate, 2),
        avg_daily_rate=round(avg_daily_rate, 2),
        sold_nights=sold_nights,
        available_nights=available_nights,
        room_type_stats=room_type_list
    )


@router.get("/dashboard", response_model=schemas.DashboardStatsResponse)
def get_dashboard_stats(
    year: int = Query(...),
    month: int = Query(...),
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_user)
):
    start_date = date(year, month, 1)
    days_in_month = monthrange(year, month)[1]
    end_date = date(year, month, days_in_month)
    
    if current_user.role == models.UserRole.ADMIN:
        all_homestays = db.query(models.Homestay).all()
    else:
        all_homestays = db.query(models.Homestay).filter(
            models.Homestay.host_id == current_user.id
        ).all()
    
    total_revenue = 0.0
    total_sold_nights = 0
    total_available_nights = 0
    
    homestay_revenue_ranking = []
    
    for hs in all_homestays:
        hs_bookings = db.query(models.Booking).join(models.Room).filter(
            models.Room.homestay_id == hs.id,
            models.Booking.status == models.BookingStatus.CHECKED_OUT,
            models.Booking.check_in_date <= end_date,
            models.Booking.check_out_date > start_date
        ).all()
        
        hs_revenue = sum(b.total_price for b in hs_bookings)
        hs_sold_nights = sum((b.check_out_date - b.check_in_date).days for b in hs_bookings)
        hs_rooms = db.query(models.Room).filter(models.Room.homestay_id == hs.id).count()
        hs_available = hs_rooms * days_in_month
        
        total_revenue += hs_revenue
        total_sold_nights += hs_sold_nights
        total_available_nights += hs_available
        
        homestay_revenue_ranking.append({
            "homestay_id": hs.id,
            "homestay_name": hs.name,
            "revenue": round(hs_revenue, 2),
            "sold_nights": hs_sold_nights
        })
    
    homestay_revenue_ranking.sort(key=lambda x: x["revenue"], reverse=True)
    
    occupancy_rate = (total_sold_nights / total_available_nights * 100) if total_available_nights > 0 else 0
    avg_daily_rate = (total_revenue / total_sold_nights) if total_sold_nights > 0 else 0
    
    if current_user.role == models.UserRole.ADMIN:
        total_bookings = db.query(models.Booking).filter(
            models.Booking.check_in_date >= start_date,
            models.Booking.check_in_date <= end_date
        ).count()
        
        monthly_trend = []
        for m in range(1, 13):
            m_start = date(year, m, 1)
            m_days = monthrange(year, m)[1]
            m_end = date(year, m, m_days)
            
            m_bookings = db.query(models.Booking).filter(
                models.Booking.check_in_date >= m_start,
                models.Booking.check_in_date <= m_end
            ).count()
            
            m_revenue = db.query(func.sum(models.Booking.total_price)).join(models.Room).filter(
                models.Booking.status == models.BookingStatus.CHECKED_OUT,
                models.Booking.check_in_date >= m_start,
                models.Booking.check_in_date <= m_end
            ).scalar() or 0
            
            monthly_trend.append({
                "month": f"{year}-{m:02d}",
                "booking_count": m_bookings,
                "revenue": round(m_revenue, 2)
            })
    else:
        homestay_ids = [hs.id for hs in all_homestays]
        total_bookings = db.query(models.Booking).join(models.Room).filter(
            models.Room.homestay_id.in_(homestay_ids),
            models.Booking.check_in_date >= start_date,
            models.Booking.check_in_date <= end_date
        ).count()
        
        monthly_trend = []
        for m in range(1, 13):
            m_start = date(year, m, 1)
            m_days = monthrange(year, m)[1]
            m_end = date(year, m, m_days)
            
            m_bookings = db.query(models.Booking).join(models.Room).filter(
                models.Room.homestay_id.in_(homestay_ids),
                models.Booking.check_in_date >= m_start,
                models.Booking.check_in_date <= m_end
            ).count()
            
            m_revenue = db.query(func.sum(models.Booking.total_price)).join(models.Room).filter(
                models.Room.homestay_id.in_(homestay_ids),
                models.Booking.status == models.BookingStatus.CHECKED_OUT,
                models.Booking.check_in_date >= m_start,
                models.Booking.check_in_date <= m_end
            ).scalar() or 0
            
            monthly_trend.append({
                "month": f"{year}-{m:02d}",
                "booking_count": m_bookings,
                "revenue": round(m_revenue, 2)
            })
    
    return schemas.DashboardStatsResponse(
        total_revenue=round(total_revenue, 2),
        total_bookings=total_bookings,
        occupancy_rate=round(occupancy_rate, 2),
        avg_daily_rate=round(avg_daily_rate, 2),
        homestay_revenue_ranking=homestay_revenue_ranking,
        monthly_booking_trend=monthly_trend
    )


@router.get("/homestay-ranking", response_model=List[schemas.HomestayRankingResponse])
def get_homestay_ranking(
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_user)
):
    homestays = db.query(models.Homestay).all()
    
    rankings = []
    for hs in homestays:
        reviews = db.query(models.Review).join(models.Room).filter(
            models.Room.homestay_id == hs.id
        ).all()
        
        if reviews:
            avg_rating = sum(r.rating for r in reviews) / len(reviews)
        else:
            avg_rating = 0.0
        
        rankings.append(schemas.HomestayRankingResponse(
            homestay_id=hs.id,
            homestay_name=hs.name,
            avg_rating=round(avg_rating, 1),
            review_count=len(reviews)
        ))
    
    rankings.sort(key=lambda x: x.avg_rating, reverse=True)
    return rankings
