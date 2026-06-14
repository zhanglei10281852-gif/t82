from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from typing import List
from app.database import get_db
from app import models, schemas
from app.auth import require_admin

router = APIRouter()


@router.get("", response_model=List[schemas.HolidayResponse])
def list_holidays(
    year: int = None,
    db: Session = Depends(get_db)
):
    query = db.query(models.Holiday)
    if year:
        query = query.filter(
            models.Holiday.date >= f"{year}-01-01",
            models.Holiday.date <= f"{year}-12-31"
        )
    return query.order_by(models.Holiday.date).all()


@router.post("", response_model=schemas.HolidayResponse)
def create_holiday(
    holiday: schemas.HolidayCreate,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(require_admin)
):
    existing = db.query(models.Holiday).filter(models.Holiday.date == holiday.date).first()
    if existing:
        raise HTTPException(status_code=400, detail="该日期已设置为节假日")
    
    db_holiday = models.Holiday(**holiday.model_dump())
    db.add(db_holiday)
    db.commit()
    db.refresh(db_holiday)
    return db_holiday


@router.delete("/{holiday_id}")
def delete_holiday(
    holiday_id: int,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(require_admin)
):
    holiday = db.query(models.Holiday).filter(models.Holiday.id == holiday_id).first()
    if not holiday:
        raise HTTPException(status_code=404, detail="节假日不存在")
    db.delete(holiday)
    db.commit()
    return {"message": "删除成功"}
