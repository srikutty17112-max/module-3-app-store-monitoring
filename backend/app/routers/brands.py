from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List
from app.database import get_db
from app import models_app, schemas_app

router = APIRouter()

@router.get("/", response_model=List[schemas_app.BrandOut])
def get_brands(skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
    brands = db.query(models_app.Brand).offset(skip).limit(limit).all()
    return brands

@router.get("/{brand_id}", response_model=schemas_app.BrandOut)
def get_brand(brand_id: int, db: Session = Depends(get_db)):
    brand = db.query(models_app.Brand).filter(models_app.Brand.id == brand_id).first()
    if brand is None:
        raise HTTPException(status_code=404, detail="Brand not found")
    return brand

@router.post("/", response_model=schemas_app.BrandOut)
def create_brand(brand: schemas_app.BrandCreate, db: Session = Depends(get_db)):
    db_brand = models_app.Brand(**brand.dict())
    db.add(db_brand)
    db.commit()
    db.refresh(db_brand)
    return db_brand

@router.put("/{brand_id}", response_model=schemas_app.BrandOut)
def update_brand(brand_id: int, brand: schemas_app.BrandUpdate, db: Session = Depends(get_db)):
    db_brand = db.query(models_app.Brand).filter(models_app.Brand.id == brand_id).first()
    if db_brand is None:
        raise HTTPException(status_code=404, detail="Brand not found")
    
    update_data = brand.dict(exclude_unset=True)
    for key, value in update_data.items():
        setattr(db_brand, key, value)
    
    db.commit()
    db.refresh(db_brand)
    return db_brand

@router.delete("/{brand_id}")
def delete_brand(brand_id: int, db: Session = Depends(get_db)):
    db_brand = db.query(models_app.Brand).filter(models_app.Brand.id == brand_id).first()
    if db_brand is None:
        raise HTTPException(status_code=404, detail="Brand not found")
    
    db.delete(db_brand)
    db.commit()
    return {"message": "Brand deleted successfully"}