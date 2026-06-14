from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List, Optional
from app.database import get_db
from app import models, schemas
from app.auth import get_current_user, require_admin, require_host

router = APIRouter()


@router.get("", response_model=List[schemas.HomestayResponse])
def list_homestays(
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_user)
):
    query = db.query(models.Homestay)
    if current_user.role == models.UserRole.HOST:
        query = query.filter(models.Homestay.host_id == current_user.id)
    homestays = query.all()
    
    result = []
    for hs in homestays:
        hs_dict = hs.__dict__.copy()
        hs_dict["host_name"] = hs.host.full_name if hs.host else None
        
        reviews = db.query(models.Review).join(models.Room).filter(
            models.Room.homestay_id == hs.id
        ).all()
        if reviews:
            avg_rating = sum(r.rating for r in reviews) / len(reviews)
            hs_dict["avg_rating"] = round(avg_rating, 1)
        else:
            hs_dict["avg_rating"] = None
        
        result.append(hs_dict)
    return result


@router.get("/{homestay_id}", response_model=schemas.HomestayResponse)
def get_homestay(
    homestay_id: int,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_user)
):
    homestay = db.query(models.Homestay).filter(models.Homestay.id == homestay_id).first()
    if not homestay:
        raise HTTPException(status_code=404, detail="民宿不存在")
    
    if current_user.role == models.UserRole.HOST and homestay.host_id != current_user.id:
        raise HTTPException(status_code=403, detail="无权限访问")
    
    hs_dict = homestay.__dict__.copy()
    hs_dict["host_name"] = homestay.host.full_name if homestay.host else None
    
    reviews = db.query(models.Review).join(models.Room).filter(
        models.Room.homestay_id == homestay.id
    ).all()
    if reviews:
        avg_rating = sum(r.rating for r in reviews) / len(reviews)
        hs_dict["avg_rating"] = round(avg_rating, 1)
    else:
        hs_dict["avg_rating"] = None
    
    return hs_dict


@router.post("", response_model=schemas.HomestayResponse)
def create_homestay(
    homestay: schemas.HomestayCreate,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(require_admin)
):
    db_homestay = models.Homestay(**homestay.model_dump())
    db.add(db_homestay)
    db.commit()
    db.refresh(db_homestay)
    return db_homestay


@router.put("/{homestay_id}", response_model=schemas.HomestayResponse)
def update_homestay(
    homestay_id: int,
    homestay_update: schemas.HomestayUpdate,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_user)
):
    homestay = db.query(models.Homestay).filter(models.Homestay.id == homestay_id).first()
    if not homestay:
        raise HTTPException(status_code=404, detail="民宿不存在")
    
    if current_user.role == models.UserRole.HOST and homestay.host_id != current_user.id:
        raise HTTPException(status_code=403, detail="无权限修改")
    
    update_data = homestay_update.model_dump(exclude_unset=True)
    for key, value in update_data.items():
        setattr(homestay, key, value)
    
    db.commit()
    db.refresh(homestay)
    return homestay


@router.delete("/{homestay_id}")
def delete_homestay(
    homestay_id: int,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(require_admin)
):
    homestay = db.query(models.Homestay).filter(models.Homestay.id == homestay_id).first()
    if not homestay:
        raise HTTPException(status_code=404, detail="民宿不存在")
    db.delete(homestay)
    db.commit()
    return {"message": "删除成功"}
