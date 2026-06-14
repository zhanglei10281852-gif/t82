from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List
from app.database import get_db
from app import models, schemas
from app.auth import get_current_user

router = APIRouter()


@router.get("", response_model=List[schemas.MaintenanceResponse])
def list_maintenances(
    room_id: int = None,
    homestay_id: int = None,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_user)
):
    query = db.query(models.Maintenance)
    if room_id:
        query = query.filter(models.Maintenance.room_id == room_id)
    if homestay_id:
        query = query.join(models.Room).filter(models.Room.homestay_id == homestay_id)
    
    if current_user.role == models.UserRole.HOST:
        query = query.join(models.Room).join(models.Homestay).filter(
            models.Homestay.host_id == current_user.id
        )
    
    maintenances = query.order_by(models.Maintenance.start_date.desc()).all()
    result = []
    for m in maintenances:
        md = m.__dict__.copy()
        md["room_name"] = m.room.name if m.room else None
        result.append(md)
    return result


@router.post("", response_model=schemas.MaintenanceResponse)
def create_maintenance(
    maintenance: schemas.MaintenanceCreate,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_user)
):
    room = db.query(models.Room).filter(models.Room.id == maintenance.room_id).first()
    if not room:
        raise HTTPException(status_code=404, detail="房间不存在")
    
    if current_user.role == models.UserRole.HOST:
        if room.homestay.host_id != current_user.id:
            raise HTTPException(status_code=403, detail="无权限操作")
    
    if maintenance.start_date >= maintenance.end_date:
        raise HTTPException(status_code=400, detail="开始日期必须早于结束日期")
    
    conflicting = db.query(models.Booking).filter(
        models.Booking.room_id == maintenance.room_id,
        models.Booking.status.in_([
            models.BookingStatus.PENDING,
            models.BookingStatus.CONFIRMED,
            models.BookingStatus.CHECKED_IN
        ]),
        models.Booking.check_in_date < maintenance.end_date,
        models.Booking.check_out_date > maintenance.start_date
    ).all()
    if conflicting:
        raise HTTPException(status_code=400, detail="所选日期范围内已有预订，无法设置维护")
    
    db_maintenance = models.Maintenance(**maintenance.model_dump())
    db.add(db_maintenance)
    db.commit()
    db.refresh(db_maintenance)
    
    md = db_maintenance.__dict__.copy()
    md["room_name"] = db_maintenance.room.name if db_maintenance.room else None
    return md


@router.delete("/{maintenance_id}")
def delete_maintenance(
    maintenance_id: int,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_user)
):
    maintenance = db.query(models.Maintenance).filter(models.Maintenance.id == maintenance_id).first()
    if not maintenance:
        raise HTTPException(status_code=404, detail="维护记录不存在")
    
    if current_user.role == models.UserRole.HOST:
        if maintenance.room.homestay.host_id != current_user.id:
            raise HTTPException(status_code=403, detail="无权限操作")
    
    db.delete(maintenance)
    db.commit()
    return {"message": "删除成功"}
