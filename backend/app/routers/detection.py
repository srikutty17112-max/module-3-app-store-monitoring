from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List
from app.database import get_db
from app import models_app, schemas_app

router = APIRouter()

@router.get("/", response_model=List[schemas_app.AppDetectionResultOut])
def get_detection_results(skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
    results = db.query(models_app.AppDetectionResult).offset(skip).limit(limit).all()
    return results

@router.get("/{result_id}", response_model=schemas_app.AppDetectionResultOut)
def get_detection_result(result_id: int, db: Session = Depends(get_db)):
    result = db.query(models_app.AppDetectionResult).filter(models_app.AppDetectionResult.id == result_id).first()
    if result is None:
        raise HTTPException(status_code=404, detail="Detection result not found")
    return result

@router.put("/{result_id}/status")
def update_detection_result_status(result_id: int, status: str, db: Session = Depends(get_db)):
    result = db.query(models_app.AppDetectionResult).filter(models_app.AppDetectionResult.id == result_id).first()
    if result is None:
        raise HTTPException(status_code=404, detail="Detection result not found")
    
    # Validate status
    try:
        threat_status = models_app.ThreatStatus(status)
        result.status = threat_status
    except ValueError:
        raise HTTPException(status_code=400, detail=f"Invalid status: {status}")
    
    db.commit()
    db.refresh(result)
    return {"message": "Detection result status updated successfully"}

@router.get("/brands/{brand_id}/app-candidates", response_model=List[schemas_app.AppCandidateOut])
def get_brand_candidates(brand_id: int, skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
    # Verify brand exists
    brand = db.query(models_app.Brand).filter(models_app.Brand.id == brand_id).first()
    if brand is None:
        raise HTTPException(status_code=404, detail="Brand not found")
    
    candidates = db.query(models_app.AppCandidate).filter(
        models_app.AppCandidate.brand_id == brand_id
    ).offset(skip).limit(limit).all()
    return candidates

@router.post("/brands/{brand_id}/app-candidates", response_model=schemas_app.AppCandidateOut)
def create_app_candidate(brand_id: int, candidate: schemas_app.AppCandidateCreate, db: Session = Depends(get_db)):
    # Verify brand exists
    brand = db.query(models_app.Brand).filter(models_app.Brand.id == brand_id).first()
    if brand is None:
        raise HTTPException(status_code=404, detail="Brand not found")
    
    # Verify brand_id matches
    if candidate.brand_id != brand_id:
        raise HTTPException(status_code=400, detail="Brand ID mismatch")
    
    db_candidate = models_app.AppCandidate(**candidate.dict())
    db.add(db_candidate)
    db.commit()
    db.refresh(db_candidate)
    return db_candidate