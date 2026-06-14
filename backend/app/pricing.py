from datetime import date, timedelta
from sqlalchemy.orm import Session
from app import models


def is_weekend(d: date) -> bool:
    return d.weekday() >= 4


def is_holiday(d: date, db: Session) -> bool:
    holiday = db.query(models.Holiday).filter(models.Holiday.date == d).first()
    return holiday is not None


def get_nightly_price(base_price: float, d: date, db: Session) -> float:
    price = base_price
    if is_holiday(d, db):
        price *= 1.5
    elif is_weekend(d):
        price *= 1.3
    return round(price, 2)


def calculate_total_price(
    room: models.Room,
    check_in: date,
    check_out: date,
    db: Session
) -> dict:
    nights = (check_out - check_in).days
    if nights <= 0:
        return {"total_price": 0, "nightly_prices": [], "discount": 1.0, "nights": 0}

    nightly_prices = []
    total = 0.0
    current = check_in
    for _ in range(nights):
        price = get_nightly_price(room.base_price, current, db)
        nightly_prices.append({"date": current.isoformat(), "price": price})
        total += price
        current += timedelta(days=1)

    discount = 1.0
    if nights >= 3:
        discount = 0.9
        total = round(total * discount, 2)

    return {
        "total_price": total,
        "nightly_prices": nightly_prices,
        "discount": discount,
        "nights": nights
    }


def is_room_available(
    room_id: int,
    check_in: date,
    check_out: date,
    db: Session,
    exclude_booking_id: int = None
) -> bool:
    query = db.query(models.Booking).filter(
        models.Booking.room_id == room_id,
        models.Booking.status.in_([
            models.BookingStatus.PENDING,
            models.BookingStatus.CONFIRMED,
            models.BookingStatus.CHECKED_IN
        ]),
        models.Booking.check_in_date < check_out,
        models.Booking.check_out_date > check_in
    )
    if exclude_booking_id:
        query = query.filter(models.Booking.id != exclude_booking_id)
    conflicting_bookings = query.all()
    if conflicting_bookings:
        return False

    maintenances = db.query(models.Maintenance).filter(
        models.Maintenance.room_id == room_id,
        models.Maintenance.start_date < check_out,
        models.Maintenance.end_date > check_in
    ).all()
    if maintenances:
        return False

    return True
