from typing import Optional
from app import models_app

def calculate_name_similarity(candidate: models_app.AppCandidate, brand: models_app.Brand) -> int:
    """
    Calculate name similarity from 0 to 100
    Uses a combination of exact match, Levenshtein distance, and token matching
    """
    if not candidate.app_name or not brand.name:
        return 0
    
    # Normalize names
    candidate_norm = normalize_text(candidate.app_name)
    brand_norm = normalize_text(brand.name)
    
    # Exact match
    if candidate_norm == brand_norm:
        return 100
    
    # Check if brand name is in candidate name or vice versa
    if brand_norm in candidate_norm or candidate_norm in brand_norm:
        # Calculate based on length ratio
        len_ratio = min(len(candidate_norm), len(brand_norm)) / max(len(candidate_norm), len(brand_norm))
        return int(80 + (len_ratio * 20))  # 80-100 range
    
    # Check against aliases, product names, service names
    all_brand_names = [brand_norm]
    
    # Add aliases
    if isinstance(brand.aliases, list):
        all_brand_names.extend([normalize_text(alias) for alias in brand.aliases if alias])
    elif brand.aliases:
        try:
            import json
            aliases = json.loads(brand.aliases)
            all_brand_names.extend([normalize_text(alias) for alias in aliases if alias])
        except:
            pass
    
    # Add product names
    if isinstance(brand.product_names, list):
        all_brand_names.extend([normalize_text(name) for name in brand.product_names if name])
    elif brand.product_names:
        try:
            import json
            products = json.loads(brand.product_names)
            all_brand_names.extend([normalize_text(name) for name in products if name])
        except:
            pass
    
    # Add service names
    if isinstance(brand.service_names, list):
        all_brand_names.extend([normalize_text(name) for name in brand.service_names if name])
    elif brand.service_names:
        try:
            import json
            services = json.loads(brand.service_names)
            all_brand_names.extend([normalize_text(name) for name in services if name])
        except:
            pass
    
    # Check for matches against all brand names
    for brand_name in all_brand_names:
        if brand_name == candidate_norm:
            return 100
        if brand_name in candidate_norm or candidate_norm in brand_name:
            len_ratio = min(len(candidate_norm), len(brand_name)) / max(len(candidate_norm), len(brand_name))
            return int(70 + (len_ratio * 30))  # 70-100 range for aliases/products/services
    
    # Calculate Levenshtein distance-based similarity
    distance = levenshtein_distance(candidate_norm, brand_norm)
    max_len = max(len(candidate_norm), len(brand_norm))
    if max_len == 0:
        return 100
    similarity = int((1 - distance / max_len) * 100)
    
    return max(0, similarity)

def calculate_logo_similarity(candidate: models_app.AppCandidate, brand: models_app.Brand) -> Optional[int]:
    """
    Calculate logo/icon similarity from 0 to 100
    Returns None if either icon is missing
    """
    if not candidate.app_icon_url or not brand.logo_url:
        return None
    
    # In a real implementation, we would download and compare images
    # For this implementation, we'll simulate based on URL similarity
    # This is a placeholder - in production you'd use perceptual hashing or similar
    
    candidate_icon = candidate.app_icon_url.lower()
    brand_icon = brand.logo_url.lower()
    
    # Exact match
    if candidate_icon == brand_icon:
        return 100
    
    # Check if they're from the same domain
    cand_domain = extract_domain_from_url(candidate_icon)
    brand_domain = extract_domain_from_url(brand_icon)
    
    if cand_domain and brand_domain and cand_domain == brand_domain:
        return 80  # Same domain but different path
    
    # Check for similar filenames
    cand_filename = candidate_icon.split("/")[-1].split("?")[0]
    brand_filename = brand_icon.split("/")[-1].split("?")[0]
    
    if cand_filename == brand_filename:
        return 90  # Same filename
    
    # Calculate string similarity as fallback
    distance = levenshtein_distance(cand_filename, brand_filename)
    max_len = max(len(cand_filename), len(brand_filename))
    if max_len == 0:
        return 100
    similarity = int((1 - distance / max_len) * 100)
    
    return max(0, similarity)

def calculate_description_similarity(candidate: models_app.AppCandidate, brand: models_app.Brand) -> Optional[int]:
    """
    Calculate description similarity from 0 to 100
    Returns None if either description is missing
    """
    if not candidate.app_description:
        return None
    
    # Brand doesn't have a description field in the current model
    # We could use website or other fields, but for now return None to skip this signal
    # In a more complete implementation, we might compare with brand website or 
    # aggregated product/service descriptions
    return None
    
    # The following code is kept for reference if we decide to implement brand description later
    # if not brand.description:
    #     return None
    # 
    # # Normalize descriptions
    # candidate_desc = normalize_text(candidate.app_description)
    # brand_desc = normalize_text(brand.description)
    # 
    # # Exact match
    # if candidate_desc == brand_desc:
    #     return 100
    # 
    # # Calculate simple word overlap similarity
    # candidate_words = set(candidate_desc.split())
    # brand_words = set(brand_desc.split())
    # 
    # if not candidate_words and not brand_words:
    #     return 100
    # if not candidate_words or not brand_words:
    #     return 0
    # 
    # # Jaccard similarity
    # intersection = len(candidate_words.intersection(brand_words))
    # union = len(candidate_words.union(brand_words))
    # 
    # if union == 0:
    #     return 100
    # 
    # similarity = int((intersection / union) * 100)
    # return similarity

def detect_lookalike_pattern(candidate: models_app.AppCandidate, brand: models_app.Brand) -> Optional[models_app.LookalikePattern]:
    """
    Detect look-alike patterns in the app name
    Returns the pattern type or None if no pattern detected
    """
    if not candidate.app_name or not brand.name:
        return None
    
    candidate_norm = normalize_text(candidate.app_name)
    brand_norm = normalize_text(brand.name)
    
    # Case variation check - do this early so we catch it even if normalization makes them equal
    if candidate.app_name.lower() == brand.name.lower() and candidate.app_name != brand.name:
        return models_app.LookalikePattern.CASE_VARIATION
    
    # Exact match after normalization
    if candidate_norm == brand_norm:
        return None  # Not a look-alike pattern if they're identical after normalization
    
    # Character swap
    if len(candidate_norm) == len(brand_norm) and candidate_norm != brand_norm:
        diff_count = sum(1 for a, b in zip(candidate_norm, brand_norm) if a != b)
        if diff_count == 2:
            # Check if it's a swap
            chars1 = list(candidate_norm)
            chars2 = list(brand_norm)
            diff_positions = [i for i, (a, b) in enumerate(zip(chars1, chars2)) if a != b]
            if len(diff_positions) == 2:
                i, j = diff_positions
                if chars1[i] == chars2[j] and chars1[j] == chars2[i]:
                    return models_app.LookalikePattern.CHARACTER_SWAP
    
    # Spacing change
    candidate_no_space = ''.join(candidate_norm.split())
    brand_no_space = ''.join(brand_norm.split())
    if candidate_no_space == brand_no_space and candidate_norm != brand_norm:
        return models_app.LookalikePattern.SPACING_CHANGE
    
    # Removed character
    if len(candidate_norm) < len(brand_norm):
        # Check if adding one character makes them match
        # This is simplified - in reality we'd check for single char differences
        if len(brand_norm) - len(candidate_norm) == 1:
            return models_app.LookalikePattern.REMOVED_CHARACTER
    
    # Extra character
    if len(candidate_norm) > len(brand_norm):
        if len(candidate_norm) - len(brand_norm) == 1:
            return models_app.LookalikePattern.EXTRA_CHARACTER
    
    # Spacing change
    candidate_no_space = ''.join(candidate_norm.split())
    brand_no_space = ''.join(brand_norm.split())
    if candidate_no_space == brand_no_space and candidate_norm != brand_norm:
        return models_app.LookalikePattern.SPACING_CHANGE
    
    # Added word
    if len(candidate_norm) > len(brand_norm):
        # Check if removing one word makes them match
        candidate_words = candidate_norm.split()
        brand_words = brand_norm.split()
        if len(candidate_words) == len(brand_words) + 1:
            # Try removing each word from candidate
            for i in range(len(candidate_words)):
                reduced_words = candidate_words[:i] + candidate_words[i+1:]
                reduced_norm = " ".join(reduced_words)
                if reduced_norm == brand_norm:
                    return models_app.LookalikePattern.ADDED_WORD
    
    # Punctuation change
    import re
    candidate_no_punct = re.sub(r'[^\w\s]', '', candidate_norm)
    brand_no_punct = re.sub(r'[^\w\s]', '', brand_norm)
    if candidate_no_punct == brand_no_punct and candidate_norm != brand_norm:
        return models_app.LookalikePattern.PUNCTUATION_CHANGE
    
    # Character substitution
    if len(candidate_norm) == len(brand_norm):
        diff_count = sum(1 for a, b in zip(candidate_norm, brand_norm) if a != b)
        if diff_count > 0 and diff_count < len(candidate_norm) * 0.5:  # Less than 50% different
            return models_app.LookalikePattern.CHARACTER_SUBSTITUTION
    
    # Case variation
    if candidate_norm.lower() == brand_norm.lower() and candidate_norm != brand_norm:
        return models_app.LookalikePattern.CASE_VARIATION
    
    return None

def normalize_text(text: str) -> str:
    """Normalize text for comparison"""
    if not text:
        return ""
    import re
    # Convert to lowercase
    text = text.lower()
    # Remove extra whitespace
    text = " ".join(text.split())
    # Remove punctuation (keeping letters and numbers)
    text = re.sub(r'[^\w\s]', '', text)
    return text

def levenshtein_distance(s1: str, s2: str) -> int:
    """Calculate Levenshtein distance between two strings"""
    if len(s1) < len(s2):
        return levenshtein_distance(s2, s1)
    
    if len(s2) == 0:
        return len(s1)
    
    previous_row = list(range(len(s2) + 1))
    for i, c1 in enumerate(s1):
        current_row = [i + 1]
        for j, c2 in enumerate(s2):
            insertions = previous_row[j + 1] + 1
            deletions = current_row[j] + 1
            substitutions = previous_row[j] + (c1 != c2)
            current_row.append(min(insertions, deletions, substitutions))
        previous_row = current_row
    
    return previous_row[-1]

def extract_domain_from_url(url: str) -> Optional[str]:
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