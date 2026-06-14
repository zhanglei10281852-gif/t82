from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List
from app.database import get_db
from app import models, schemas
from app.auth import get_current_user, require_admin

router = APIRouter()


@router.get("", response_model=List[schemas.RoomResponse])
def list_rooms(
    homestay_id: int = None,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_user)
):
    query = db.query(models.Room)
    if homestay_id:
        query = query.filter(models.Room.homestay_id == homestay_id)
    
    if current_user.role == models.UserRole.HOST:
        query = query.join(models.Homestay).filter(models.Homestay.host_id == current_user.id)
    
    rooms = query.all()
    result = []
    for room in rooms:
        room_dict = room.__dict__.copy()
        room_dict["homestay_name"] = room.homestay.name if room.homestay else None
        
        reviews = db.query(models.Review).filter(models.Review.room_id == room.id).all()
        if reviews:
            avg_rating = sum(r.rating for r in reviews) / len(reviews)
            room_dict["avg_rating"] = round(avg_rating, 1)
        else:
            room_dict["avg_rating"] = None
        
        result.append(room_dict)
    return result


@router.get("/{room_id}", response_model=schemas.RoomResponse)
def get_room(
    room_id: int,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_user)
):
    room = db.query(models.Room).filter(models.Room.id == room_id).first()
    if not room:
        raise HTTPException(status_code=404, detail="房间不存在")
    
    if current_user.role == models.UserRole.HOST and room.homestay.host_id != current_user.id:
        raise HTTPException(status_code=403, detail="无权限访问")
    
    room_dict = room.__dict__.copy()
    room_dict["homestay_name"] = room.homestay.name if room.homestay else None
    
    reviews = db.query(models.Review).filter(models.Review.room_id == room.id).all()
    if reviews:
        avg_rating = sum(r.rating for r in reviews) / len(reviews)
        room_dict["avg_rating"] = round(avg_rating, 1)
    else:
        room_dict["avg_rating"] = None
    
    return room_dict


@router.post("", response_model=schemas.RoomResponse)
def create_room(
    room: schemas.RoomCreate,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(require_admin)
):
    homestay = db.query(models.Homestay).filter(models.Homestay.id == room.homestay_id).first()
    if not homestay:
        raise HTTPException(status_code=404, detail="民宿不存在")
    
    db_room = models.Room(**room.model_dump())
    db.add(db_room)
    db.commit()
    db.refresh(db_room)
    return db_room


@router.put("/{room_id}", response_model=schemas.RoomResponse)
def update_room(
    room_id: int,
    room_update: schemas.RoomUpdate,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_user)
):
    room = db.query(models.Room).filter(models.Room.id == room_id).first()
    if not room:
        raise HTTPException(status_code=404, detail="房间不存在")
    
    if current_user.role == models.UserRole.HOST and room.homestay.host_id != current_user.id:
        raise HTTPException(status_code=403, detail="无权限修改")
    
    update_data = room_update.model_dump(exclude_unset=True)
    for key, value in update_data.items():
        setattr(room, key, value)
    
    db.commit()
    db.refresh(room)
    return room


@router.delete("/{room_id}")
def delete_room(
    room_id: int,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(require_admin)
):
    room = db.query(models.Room).filter(models.Room.id == room_id).first()
    if not room:
        raise HTTPException(status_code=404, detail="房间不存在")
    db.delete(room)
    db.commit()
    return {"message": "删除成功"}
