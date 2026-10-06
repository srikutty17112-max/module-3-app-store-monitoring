from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List
from app.database import get_db
from app import models_app, schemas_app
from app.services.app_monitoring_service import start_app_scan

router = APIRouter()

@router.post("/brands/{brand_id}/app-scan", response_model=schemas_app.AppScanStartResponse)
def start_scan(brand_id: int, request: schemas_app.AppScanStartRequest, db: Session = Depends(get_db)):
    # Verify brand exists
    brand = db.query(models_app.Brand).filter(models_app.Brand.id == brand_id).first()
    if brand is None:
        raise HTTPException(status_code=404, detail="Brand not found")
    
    # Start the scan using the service
    scan_job_id = start_app_scan(db, brand_id, request.source_type)
    
    return schemas_app.AppScanStartResponse(
        scan_job_id=scan_job_id,
        status="STARTED",
        message=f"App scan started for brand {brand.name}"
    )

@router.get("/brands/{brand_id}/app-scan/status/{scan_job_id}", response_model=schemas_app.AppScanStatusResponse)
def get_scan_status(brand_id: int, scan_job_id: int, db: Session = Depends(get_db)):
    # Verify brand exists
    brand = db.query(models_app.Brand).filter(models_app.Brand.id == brand_id).first()
    if brand is None:
        raise HTTPException(status_code=404, detail="Brand not found")
    
    # Get scan job
    scan_job = db.query(models_app.AppScanJob).filter(
        models_app.AppScanJob.id == scan_job_id,
        models_app.AppScanJob.brand_id == brand_id
    ).first()
    
    if scan_job is None:
        raise HTTPException(status_code=404, detail="Scan job not found")
    
    return schemas_app.AppScanStatusResponse(
        scan_job_id=scan_job.id,
        status=scan_job.status,
        total_candidates=scan_job.total_candidates,
        official_count=scan_job.official_count,
        suspicious_count=scan_job.suspicious_count,
        likely_impersonation_count=scan_job.likely_impersonation_count,
        high_risk_count=scan_job.high_risk_count,
        error_message=scan_job.error_message
    )

@router.get("/brands/{brand_id}/app-threats", response_model=List[schemas_app.AppThreatOut])
def get_brand_threats(brand_id: int, skip: int = 0, limit: int = 50, db: Session = Depends(get_db)):
    # Verify brand exists
    brand = db.query(models_app.Brand).filter(models_app.Brand.id == brand_id).first()
    if brand is None:
        raise HTTPException(status_code=404, detail="Brand not found")
    
    # Get threats/detection results for this brand
    threats = db.query(models_app.AppDetectionResult).filter(
        models_app.AppDetectionResult.brand_id == brand_id
    ).offset(skip).limit(limit).all()
    
    # Convert to AppThreatOut format
    result = []
    for threat in threats:
        # Get candidate info
        candidate = db.query(models_app.AppCandidate).filter(models_app.AppCandidate.id == threat.candidate_id).first()
        official_match = db.query(models_app.OfficialMobileApp).filter(models_app.OfficialMobileApp.id == threat.official_match_id).first() if threat.official_match_id else None
        
        threat_dict = {
            "id": str(threat.id),
            "brand_id": str(threat.brand_id),
            "source_type": "DEMO",  # Default, would come from source_data in real implementation
            "store": candidate.store.value if candidate and candidate.store else "DEMO",
            "candidate": {
                "id": candidate.id if candidate else None,
                "app_name": candidate.app_name if candidate else "",
                "package_id": candidate.package_id if candidate else None,
                "bundle_id": candidate.bundle_id if candidate else None,
                "developer_name": candidate.developer_name if candidate else None,
                "developer_website": candidate.developer_website if candidate else None,
                "app_icon_url": candidate.app_icon_url if candidate else None,
                "app_description": candidate.app_description if candidate else None
            } if candidate else {},
            "signals": {},  # Would be populated from app_signals table
            "lookalike": {
                "detected": threat.lookalike_detected,
                "pattern": threat.lookalike_pattern.value if threat.lookalike_pattern else None
            },
            "official_match": {
                "id": official_match.id if official_match else None,
                "name": official_match.name if official_match else None,
                "package_id": official_match.package_id if official_match else None,
                "bundle_id": official_match.bundle_id if official_match else None
            } if official_match else {},
            "risk_score": threat.risk_score,
            "risk_level": threat.risk_level.value,
            "confidence": threat.confidence,
            "classification": threat.classification.value,
            "reasons": [],  # Would be parsed from threat.reasons
            "source": {},  # Would be populated from threat.source_data
            "status": threat.status.value
        }
        result.append(schemas_app.AppThreatOut(**threat_dict))
    
    return result