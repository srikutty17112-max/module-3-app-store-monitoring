from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List
from app.database import get_db
from app import models_app, schemas_app

router = APIRouter()

@router.get("/", response_model=List[schemas_app.OfficialMobileAppOut])
def get_official_apps(skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
    apps = db.query(models_app.OfficialMobileApp).offset(skip).limit(limit).all()
    return apps

@router.get("/{app_id}", response_model=schemas_app.OfficialMobileAppOut)
def get_official_app(app_id: int, db: Session = Depends(get_db)):
    app = db.query(models_app.OfficialMobileApp).filter(models_app.OfficialMobileApp.id == app_id).first()
    if app is None:
        raise HTTPException(status_code=404, detail="Official app not found")
    return app

@router.post("/", response_model=schemas_app.OfficialMobileAppOut)
def create_official_app(app: schemas_app.OfficialMobileAppCreate, db: Session = Depends(get_db)):
    db_app = models_app.OfficialMobileApp(**app.dict())
    db.add(db_app)
    db.commit()
    db.refresh(db_app)
    return db_app

@router.put("/{app_id}", response_model=schemas_app.OfficialMobileAppOut)
def update_official_app(app_id: int, app: schemas_app.OfficialMobileAppUpdate, db: Session = Depends(get_db)):
    db_app = db.query(models_app.OfficialMobileApp).filter(models_app.OfficialMobileApp.id == app_id).first()
    if db_app is None:
        raise HTTPException(status_code=404, detail="Official app not found")
    
    update_data = app.dict(exclude_unset=True)
    for key, value in update_data.items():
        setattr(db_app, key, value)
    
    db.commit()
    db.refresh(db_app)
    return db_app

@router.delete("/{app_id}")
def delete_official_app(app_id: int, db: Session = Depends(get_db)):
    db_app = db.query(models_app.OfficialMobileApp).filter(models_app.OfficialMobileApp.id == app_id).first()
    if db_app is None:
        raise HTTPException(status_code=404, detail="Official app not found")
    
    db.delete(db_app)
    db.commit()
    return {"message": "Official app deleted successfully"}