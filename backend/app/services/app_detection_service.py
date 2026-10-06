from sqlalchemy.orm import Session
from typing import Optional
from app import models_app
from app.services.app_similarity_service import (
    calculate_name_similarity,
    calculate_logo_similarity,
    calculate_description_similarity,
    detect_lookalike_pattern
)
from app.services.app_risk_service import calculate_risk_score, determine_classification
import json

def analyze_app_candidate(db: Session, candidate_id: int) -> Optional[int]:
    """
    Analyze an app candidate and create/update detection result
    Returns the detection result ID
    """
    # Get candidate
    candidate = db.query(models_app.AppCandidate).filter(
        models_app.AppCandidate.id == candidate_id
    ).first()
    
    if not candidate:
        return None
    
    # Get brand
    brand = db.query(models_app.Brand).filter(
        models_app.Brand.id == candidate.brand_id
    ).first()
    
    if not brand:
        return None
    
    # Check for exact official match first
    official_match = check_exact_official_match(db, candidate)
    
    if official_match:
        # This is an official app - no threat
        detection_result = models_app.AppDetectionResult(
            brand_id=candidate.brand_id,
            candidate_id=candidate.id,
            classification=models_app.AppClassification.OFFICIAL,
            threat=False,
            risk_score=0,
            risk_level=models_app.RiskLevel.LOW,
            confidence=1.0,
            name_similarity=100,
            logo_similarity=100 if candidate.app_icon_url and official_match.icon_url else None,
            description_similarity=100 if candidate.app_description and official_match.description else None,
            branding_similarity=100,
            developer_match=models_app.DeveloperMatchType.EXACT_MATCH,
            developer_domain_match=True,
            package_match=True,
            bundle_match=True,
            lookalike_detected=False,
            reasons=json.dumps(["Exact match with official app"]),
            signals=json.dumps({}),
            source_data=json.dumps({}),
            status=models_app.ThreatStatus.CONFIRMED
        )
        db.add(detection_result)
        db.commit()
        db.refresh(detection_result)
        return detection_result.id
    
    # Not an official app, proceed with analysis
    
    # Calculate similarities
    name_sim = calculate_name_similarity(candidate, brand)
    logo_sim = calculate_logo_similarity(candidate, brand)
    desc_sim = calculate_description_similarity(candidate, brand)
    lookalike_pattern = detect_lookalike_pattern(candidate, brand)
    
    # Publisher/developer analysis
    developer_match = analyze_developer_match(candidate, brand)
    developer_domain_match = analyze_developer_domain_match(candidate, brand)
    
    # Package/bundle analysis
    package_match = analyze_package_match(db, candidate, brand)
    bundle_match = analyze_bundle_match(db, candidate, brand)
    
    # Calculate branding similarity (combined score)
    branding_sim = calculate_branding_similarity(
        name_sim, logo_sim, desc_sim, 
        developer_match, developer_domain_match,
        package_match, bundle_match
    )
    
    # Calculate risk score and confidence
    risk_score = calculate_risk_score(
        name_sim, logo_sim, desc_sim,
        developer_match, developer_domain_match,
        package_match, bundle_match
    )
    
    classification, confidence = determine_classification(risk_score, name_sim, logo_sim, desc_sim)
    
    # Create detection result
    detection_result = models_app.AppDetectionResult(
        brand_id=candidate.brand_id,
        candidate_id=candidate.id,
        classification=classification,
        threat=classification in [
            models_app.AppClassification.SUSPICIOUS,
            models_app.AppClassification.LIKELY_IMPERSONATION,
            models_app.AppClassification.HIGH_RISK_IMPERSONATION
        ],
        risk_score=risk_score,
        risk_level=models_app.RiskLevel(risk_score_to_level(risk_score)),
        confidence=confidence,
        name_similarity=name_sim,
        logo_similarity=logo_sim,
        description_similarity=desc_sim,
        branding_similarity=branding_sim,
        developer_match=developer_match,
        developer_domain_match=developer_domain_match,
        package_match=package_match,
        bundle_match=bundle_match,
        lookalike_detected=lookalike_pattern is not None,
        lookalike_pattern=lookalike_pattern,
        reasons=json.dumps(generate_detection_reasons(
            name_sim, logo_sim, desc_sim,
            developer_match, developer_domain_match,
            package_match, bundle_match,
            lookalike_pattern
        )),
        signals=json.dumps({}),  # Empty signals dict
        source_data=json.dumps({}),  # Empty source data dict
        status=models_app.ThreatStatus.NEW
    )
    
    db.add(detection_result)
    db.commit()
    db.refresh(detection_result)
    
    return detection_result.id

def check_exact_official_match(db: Session, candidate: models_app.AppCandidate) -> Optional[models_app.OfficialMobileApp]:
    """Check if candidate exactly matches an official app"""
    query = db.query(models_app.OfficialMobileApp).filter(
        models_app.OfficialMobileApp.brand_id == candidate.brand_id
    )
    
    # Check package ID match
    if candidate.package_id:
        match = query.filter(
            models_app.OfficialMobileApp.package_id == candidate.package_id
        ).first()
        if match:
            return match
    
    # Check bundle ID match
    if candidate.bundle_id:
        match = query.filter(
            models_app.OfficialMobileApp.bundle_id == candidate.bundle_id
        ).first()
        if match:
            return match
    
    # Check store + URL match
    if candidate.app_url:
        match = query.filter(
            models_app.OfficialMobileApp.store_url == candidate.app_url
        ).first()
        if match:
            return match
    
    return None

def analyze_developer_match(candidate: models_app.AppCandidate, brand: models_app.Brand) -> models_app.DeveloperMatchType:
    """Analyze developer/publisher match"""
    if not candidate.developer_name:
        return models_app.DeveloperMatchType.UNKNOWN
    
    # Get official developer names
    official_dev_names = []
    if isinstance(brand.official_developer_names, list):
        official_dev_names = brand.official_developer_names
    elif brand.official_developer_names:
        # Try to parse as JSON/list if it's stored as text
        import json
        try:
            official_dev_names = json.loads(brand.official_developer_names)
        except:
            official_dev_names = [brand.official_developer_names] if brand.official_developer_names else []
    
    # Check for exact match
    if candidate.developer_name in official_dev_names:
        return models_app.DeveloperMatchType.EXACT_MATCH
    
    # Check for strong match (similarity > 80%)
    # This would use string similarity in a real implementation
    # For now, we'll return POSSIBLE_MATCH if there's any overlap
    for official_name in official_dev_names:
        if official_name.lower() in candidate.developer_name.lower() or \
           candidate.developer_name.lower() in official_name.lower():
            return models_app.DeveloperMatchType.POSSIBLE_MATCH
    
    return models_app.DeveloperMatchType.MISMATCH

def analyze_developer_domain_match(candidate: models_app.AppCandidate, brand: models_app.Brand) -> bool:
    """Analyze developer domain match"""
    if not candidate.developer_website or not brand.website:
        return None  # Unknown
    
    # Extract domains
    candidate_domain = extract_domain(candidate.developer_website)
    brand_domain = extract_domain(brand.website)
    
    if not candidate_domain or not brand_domain:
        return None
    
    return candidate_domain == brand_domain

def extract_domain(url: str) -> Optional[str]:
    """Extract domain from URL"""
    if not url:
        return None
    
    # Remove protocol
    url = url.split("://")[-1] if "://" in url else url
    
    # Remove path and params
    domain = url.split("/")[0].split("?")[0].split("#")[0]
    
    # Remove www.
    if domain.startswith("www."):
        domain = domain[4:]
    
    return domain.lower() if domain else None

def analyze_package_match(db: Session, candidate: models_app.AppCandidate, brand: models_app.Brand) -> bool:
    """Analyze package ID match"""
    if not candidate.package_id:
        return None
    
    # Check against official apps
    official_apps = db.query(models_app.OfficialMobileApp).filter(
        models_app.OfficialMobileApp.brand_id == brand.id
    ).all()
    
    for app in official_apps:
        if app.package_id == candidate.package_id:
            return True
    
    return False

def analyze_bundle_match(db: Session, candidate: models_app.AppCandidate, brand: models_app.Brand) -> bool:
    """Analyze bundle ID match"""
    if not candidate.bundle_id:
        return None
    
    # Check against official apps
    official_apps = db.query(models_app.OfficialMobileApp).filter(
        models_app.OfficialMobileApp.brand_id == brand.id
    ).all()
    
    for app in official_apps:
        if app.bundle_id == candidate.bundle_id:
            return True
    
    return False

def calculate_branding_similarity(
    name_sim: int, logo_sim: Optional[int], desc_sim: Optional[int],
    developer_match: models_app.DeveloperMatchType,
    developer_domain_match: Optional[bool],
    package_match: Optional[bool],
    bundle_match: Optional[bool]
) -> int:
    """Calculate combined branding similarity score"""
    # Weight different factors
    score = name_sim * 0.4  # Name is most important
    
    if logo_sim is not None:
        score += logo_sim * 0.3
    else:
        score += 50 * 0.3  # Neutral score for missing logo
    
    if desc_sim is not None:
        score += desc_sim * 0.2
    else:
        score += 50 * 0.2  # Neutral score for missing description
    
    # Developer/publisher factors
    dev_score = 0
    if developer_match == models_app.DeveloperMatchType.EXACT_MATCH:
        dev_score = 100
    elif developer_match == models_app.DeveloperMatchType.STRONG_MATCH:
        dev_score = 80
    elif developer_match == models_app.DeveloperMatchType.POSSIBLE_MATCH:
        dev_score = 60
    elif developer_match == models_app.DeveloperMatchType.MISMATCH:
        dev_score = 20
    else:  # UNKNOWN
        dev_score = 50
    
    score += dev_score * 0.1
    
    # Package/bundle factors
    pkg_score = 100 if package_match else 0 if package_match is False else 50
    score += pkg_score * 0.05
    
    bun_score = 100 if bundle_match else 0 if bundle_match is False else 50
    score += bun_score * 0.05
    
    return min(100, max(0, int(score)))

def generate_detection_reasons(
    name_sim: int, logo_sim: Optional[int], desc_sim: Optional[int],
    developer_match: models_app.DeveloperMatchType,
    developer_domain_match: Optional[bool],
    package_match: Optional[bool],
    bundle_match: Optional[bool],
    lookalike_pattern: Optional[models_app.LookalikePattern]
) -> List[str]:
    """Generate human-readable reasons for detection"""
    reasons = []
    
    if name_sim >= 90:
        reasons.append("Very high name similarity")
    elif name_sim >= 70:
        reasons.append("High name similarity")
    elif name_sim >= 50:
        reasons.append("Moderate name similarity")
    
    if logo_sim is not None:
        if logo_sim >= 90:
            reasons.append("Very high icon similarity")
        elif logo_sim >= 70:
            reasons.append("High icon similarity")
        elif logo_sim >= 50:
            reasons.append("Moderate icon similarity")
    
    if desc_sim is not None:
        if desc_sim >= 90:
            reasons.append("Very high description similarity")
        elif desc_sim >= 70:
            reasons.append("High description similarity")
        elif desc_sim >= 50:
            reasons.append("Moderate description similarity")
    
    if developer_match == models_app.DeveloperMatchType.MISMATCH:
        reasons.append("Publisher mismatch")
    elif developer_match == models_app.DeveloperMatchType.POSSIBLE_MATCH:
        reasons.append("Publisher similarity detected")
    
    if developer_domain_match is False:
        reasons.append("Developer domain mismatch")
    elif developer_domain_match is True:
        reasons.append("Developer domain match")
    
    if package_match is False:
        reasons.append("Package ID mismatch")
    elif package_match is True:
        reasons.append("Package ID match")
    
    if bundle_match is False:
        reasons.append("Bundle ID mismatch")
    elif bundle_match is True:
        reasons.append("Bundle ID match")
    
    if lookalike_pattern:
        reasons.append(f"Look-alike pattern detected: {lookalike_pattern.value.replace('_', ' ').title()}")
    
    if not reasons:
        reasons.append("Some similarity detected but insufficient evidence for impersonation")
    
    return reasons

def risk_score_to_level(risk_score: int) -> str:
    """Convert risk score to risk level"""
    if risk_score < 30:
        return "LOW"
    elif risk_score < 60:
        return "MEDIUM"
    elif risk_score < 80:
        return "HIGH"
    else:
        return "CRITICAL"