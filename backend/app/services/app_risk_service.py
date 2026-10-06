from typing import Tuple
from app import models_app

# Default weights for risk scoring
DEFAULT_WEIGHTS = {
    "name_similarity": 0.25,
    "logo_similarity": 0.25,
    "description_similarity": 0.15,
    "developer_mismatch": 0.15,
    "package_mismatch": 0.10,
    "developer_domain_mismatch": 0.10
}

def calculate_risk_score(
    name_sim: int,
    logo_sim: Optional[int],
    desc_sim: Optional[int],
    developer_match: models_app.DeveloperMatchType,
    developer_domain_match: Optional[bool],
    package_match: Optional[bool],
    bundle_match: Optional[bool]
) -> int:
    """
    Calculate risk score from 0 to 100 based on weighted factors
    Higher similarity = Lower risk
    Higher mismatch = Higher risk
    """
    # Initialize score
    score = 0.0
    total_weight = 0.0
    
    # Name similarity (lower similarity = higher risk)
    name_weight = DEFAULT_WEIGHTS["name_similarity"]
    name_risk = (100 - name_sim) / 100.0  # Convert similarity to risk (0-1)
    score += name_risk * name_weight
    total_weight += name_weight
    
    # Logo similarity (lower similarity = higher risk)
    if logo_sim is not None:
        logo_weight = DEFAULT_WEIGHTS["logo_similarity"]
        logo_risk = (100 - logo_sim) / 100.0  # Convert similarity to risk (0-1)
        score += logo_risk * logo_weight
        total_weight += logo_weight
    # If logo is missing, don't adjust score (treat as neutral)
    
    # Description similarity (lower similarity = higher risk)
    if desc_sim is not None:
        desc_weight = DEFAULT_WEIGHTS["description_similarity"]
        desc_risk = (100 - desc_sim) / 100.0  # Convert similarity to risk (0-1)
        score += desc_risk * desc_weight
        total_weight += desc_weight
    # If description is missing, don't adjust score (treat as neutral)
    
    # Developer mismatch (higher mismatch = higher risk)
    dev_mismatch_score = 0
    if developer_match == models_app.DeveloperMatchType.EXACT_MATCH:
        dev_mismatch_score = 0  # No risk
    elif developer_match == models_app.DeveloperMatchType.STRONG_MATCH:
        dev_mismatch_score = 0.3  # Some risk
    elif developer_match == models_app.DeveloperMatchType.POSSIBLE_MATCH:
        dev_mismatch_score = 0.5  # Moderate risk
    elif developer_match == models_app.DeveloperMatchType.MISMATCH:
        dev_mismatch_score = 0.8  # High risk
    else:  # UNKNOWN
        dev_mismatch_score = 0.5  # Moderate risk
    
    dev_weight = DEFAULT_WEIGHTS["developer_mismatch"]
    score += dev_mismatch_score * dev_weight
    total_weight += dev_weight
    
    # Package mismatch (higher mismatch = higher risk)
    if package_match is not None:
        pkg_mismatch_score = 0 if package_match else 1  # 0 if match, 1 if mismatch
        pkg_weight = DEFAULT_WEIGHTS["package_mismatch"]
        score += pkg_mismatch_score * pkg_weight
        total_weight += pkg_weight
    # If package_match is None (missing data), don't adjust score
    
    # Developer domain mismatch (higher mismatch = higher risk)
    if developer_domain_match is not None:
        domain_mismatch_score = 0 if developer_domain_match else 1  # 0 if match, 1 if mismatch
        domain_weight = DEFAULT_WEIGHTS["developer_domain_mismatch"]
        score += domain_mismatch_score * domain_weight
        total_weight += domain_weight
    # If developer_domain_match is None (missing data), don't adjust score
    
    # Normalize score based on actual weights used
    if total_weight > 0:
        final_score = (score / total_weight) * 100
    else:
        final_score = 0
    
    return min(100, max(0, int(final_score)))

def determine_classification(risk_score: int, name_sim: int, logo_sim: Optional[int], desc_sim: Optional[int]) -> Tuple[models_app.AppClassification, float]:
    """
    Determine classification and confidence based on risk score and similarities
    Returns (classification, confidence)
    """
    # Base confidence on data completeness
    confidence_factors = []
    confidence_factors.append(1.0)  # Name is always available (required field)
    
    if logo_sim is not None:
        confidence_factors.append(1.0)
    else:
        confidence_factors.append(0.5)  # Lower confidence for missing logo
    
    if desc_sim is not None:
        confidence_factors.append(1.0)
    else:
        confidence_factors.append(0.5)  # Lower confidence for missing description
    
    # Calculate base confidence
    base_confidence = sum(confidence_factors) / len(confidence_factors)
    
    # Adjust confidence based on risk score clarity
    # Very low or very high scores have higher confidence
    if risk_score < 20 or risk_score > 80:
        confidence_boost = 0.2
    elif risk_score < 40 or risk_score > 60:
        confidence_boost = 0.1
    else:
        confidence_boost = 0.0  # Middle range has lower confidence
    
    confidence = min(1.0, base_confidence + confidence_boost)
    
    # Determine classification based on risk score
    if risk_score < 30:
        classification = models_app.AppClassification.LIKELY_LEGITIMATE
    elif risk_score < 60:
        classification = models_app.AppClassification.SUSPICIOUS
    elif risk_score < 80:
        classification = models_app.AppClassification.LIKELY_IMPERSONATION
    else:
        classification = models_app.AppClassification.HIGH_RISK_IMPERSONATION
    
    # Override to LIKELY_LEGITIMATE if naming similarity is low but other factors are high
    # This helps prevent false positives
    if name_sim < 40 and risk_score > 50:
        # If name similarity is low but overall score is high, reduce classification
        if classification == models_app.AppClassification.HIGH_RISK_IMPERSONATION:
            classification = models_app.AppClassification.LIKELY_IMPERSONATION
        elif classification == models_app.AppClassification.LIKELY_IMPERSONATION:
            classification = models_app.AppClassification.SUSPICIOUS
        elif classification == models_app.AppClassification.SUSPICIOUS:
            classification = models_app.AppClassification.LIKELY_LEGITIMATE
    
    return classification, confidence