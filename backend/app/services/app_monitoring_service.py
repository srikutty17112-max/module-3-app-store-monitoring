from sqlalchemy.orm import Session
from typing import List
from app import models_app, schemas_app
from app.services.app_source_adapters import get_source_adapter
from app.services.app_detection_service import analyze_app_candidate
import json

def start_app_scan(db: Session, brand_id: int, source_type: str) -> int:
    """
    Start an app scan for a brand
    Returns the scan job ID
    """
    # Get brand information
    brand = db.query(models_app.Brand).filter(models_app.Brand.id == brand_id).first()
    if not brand:
        raise ValueError(f"Brand with ID {brand_id} not found")
    
    # Create scan job record
    scan_job = models_app.AppScanJob(
        brand_id=brand_id,
        source_type=source_type,
        status="COLLECTING"
    )
    db.add(scan_job)
    db.commit()
    db.refresh(scan_job)
    
    try:
        # Get official apps for this brand
        official_apps = db.query(models_app.OfficialMobileApp).filter(
            models_app.OfficialMobileApp.brand_id == brand_id
        ).all()
        
        official_apps_dict = [
            {
                "id": app.id,
                "name": app.name,
                "package_id": app.package_id,
                "bundle_id": app.bundle_id,
                "store_url": app.store_url,
                "developer_name": app.developer_name,
                "developer_website": app.developer_website,
                "developer_email": app.developer_email,
                "platform": app.platform.value if app.platform else "unknown",
                "store": app.store.value if app.store else "DEMO",
                "icon_url": app.icon_url,
                "description": app.description
            }
            for app in official_apps
        ]
        
        # Get source adapter
        adapter = get_source_adapter(source_type)
        
        # Collect candidates
        raw_candidates = adapter.collect_candidates(
            brand_name=brand.name,
            keywords=brand.keywords if isinstance(brand.keywords, list) else [],
            official_apps=official_apps_dict
        )
        
        # Normalize and save candidates
        candidates = []
        for raw_candidate in raw_candidates:
            candidate_create = adapter.normalize_candidate(raw_candidate, brand_id, scan_job.id)
            # Convert external_links list to JSON string for storage
            import json
            external_links_json = json.dumps(candidate_create.external_links)
            candidate_dict = candidate_create.dict()
            candidate_dict['external_links'] = external_links_json
            candidate = models_app.AppCandidate(**candidate_dict)
            db.add(candidate)
            candidates.append(candidate)
        
        # Update scan job with collection status
        scan_job.status = "ANALYZING"
        scan_job.total_candidates = len(candidates)
        db.commit()
        
        # Analyze each candidate
        for candidate in candidates:
            analyze_app_candidate(db, candidate.id)
        
        # Update scan job completion
        scan_job.status = "COMPLETED"
        from datetime import datetime
        scan_job.completed_at = datetime.utcnow()
        db.commit()
        
        return scan_job.id
        
    except Exception as e:
        scan_job.status = "FAILED"
        scan_job.error_message = str(e)
        db.commit()
        raise e