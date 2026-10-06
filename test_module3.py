"""
Test cases for Module 3 core functionality
"""

from app.utils.app_normalization import normalize_app_name, calculate_string_similarity
from app.services.app_similarity_service import (
    levenshtein_distance,
    detect_lookalike_pattern
)
from app import models_app

def test_normalization():
    """Test app name normalization"""
    assert normalize_app_name("KampusVC") == "kampusvc"
    assert normalize_app_name("Kampus VC") == "kampus vc"
    assert normalize_app_name("Kampus.VC!") == "kampusvc"
    assert normalize_app_name("  Kampus   VC  ") == "kampus vc"
    print("✓ Normalization tests passed")

def test_string_similarity():
    """Test string similarity calculation"""
    assert calculate_string_similarity("test", "test") == 100
    assert calculate_string_similarity("test", "tent") == 75  # 1 edit distance out of 4
    assert calculate_string_similarity("kitten", "sitting") == 63  # Known example
    assert calculate_string_similarity("", "") == 100
    assert calculate_string_similarity("abc", "") == 0
    print("✓ String similarity tests passed")

def test_lookalike_detection():
    """Test look-alike pattern detection"""
    # Create mock objects
    class MockApp:
        def __init__(self, name):
            self.app_name = name
    
    class MockBrand:
        def __init__(self, name):
            self.name = name
    
    # Test character swap
    candidate = MockApp("KampussVC")
    brand = MockBrand("KampusVC")
    pattern = detect_lookalike_pattern(candidate, brand)
    assert pattern == models_app.LookalikePattern.CHARACTER_SWAP
    
    # Test added word
    candidate = MockApp("KampusVC Support")
    brand = MockBrand("KampusVC")
    pattern = detect_lookalike_pattern(candidate, brand)
    assert pattern == models_app.LookalikePattern.ADDED_WORD
    
    # Test spacing change
    candidate = MockApp("Kampus VC")
    brand = MockBrand("KampusVC")
    pattern = detect_lookalike_pattern(candidate, brand)
    assert pattern == models_app.LookalikePattern.SPACING_CHANGE
    
    # Test case variation
    candidate = MockApp("KAMPUSVC")
    brand = MockBrand("KampusVC")
    pattern = detect_lookalike_pattern(candidate, brand)
    assert pattern == models_app.LookalikePattern.CASE_VARIATION
    
    print("✓ Look-alike detection tests passed")

def test_risk_scoring():
    """Test risk scoring logic"""
    from app.services.app_risk_service import calculate_risk_score, determine_classification
    
    # Test exact match (should be low risk)
    score = calculate_risk_score(
        name_sim=100,
        logo_sim=100,
        desc_sim=100,
        developer_match=models_app.DeveloperMatchType.EXACT_MATCH,
        developer_domain_match=True,
        package_match=True,
        bundle_match=True
    )
    assert score == 0  # Should be 0 risk for exact match
    
    # Test high risk scenario
    score = calculate_risk_score(
        name_sim=90,
        logo_sim=80,
        desc_sim=70,
        developer_match=models_app.DeveloperMatchType.MISMATCH,
        developer_domain_match=False,
        package_match=False,
        bundle_match=False
    )
    assert score > 70  # Should be high risk
    
    print("✓ Risk scoring tests passed")

if __name__ == "__main__":
    test_normalization()
    test_string_similarity()
    test_lookalike_detection()
    test_risk_scoring()
    print("\n✅ All tests passed!")