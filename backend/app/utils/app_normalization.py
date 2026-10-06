"""
Utility functions for app name normalization and text processing
"""

import re
from typing import List

def normalize_app_name(name: str) -> str:
    """
    Normalize app name for comparison
    - Convert to lowercase
    - Remove punctuation
    - Normalize whitespace
    """
    if not name:
        return ""
    
    # Convert to lowercase
    name = name.lower()
    
    # Remove punctuation (keep letters, numbers, and whitespace)
    name = re.sub(r'[^\w\s]', '', name)
    
    # Normalize whitespace
    name = ' '.join(name.split())
    
    return name

def extract_keywords(text: str, min_length: int = 3) -> List[str]:
    """
    Extract meaningful keywords from text
    """
    if not text:
        return []
    
    # Normalize text
    normalized = normalize_app_name(text)
    
    # Split into words
    words = normalized.split()
    
    # Filter by minimum length and remove common words
    common_words = {'the', 'and', 'or', 'but', 'in', 'on', 'at', 'to', 'for', 'of', 'with', 'by'}
    keywords = [word for word in words if len(word) >= min_length and word not in common_words]
    
    return keywords

def calculate_string_similarity(str1: str, str2: str) -> int:
    """
    Calculate similarity between two strings (0-100)
    Uses Levenshtein distance
    """
    if not str1 and not str2:
        return 100
    if not str1 or not str2:
        return 0
    
    # Normalize strings
    s1 = normalize_app_name(str1)
    s2 = normalize_app_name(str2)
    
    if s1 == s2:
        return 100
    
    # Calculate Levenshtein distance
    distance = levenshtein_distance(s1, s2)
    max_len = max(len(s1), len(s2))
    
    if max_len == 0:
        return 100
    
    similarity = int((1 - distance / max_len) * 100)
    return max(0, similarity)

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

def is_substring_match(str1: str, str2: str) -> bool:
    """
    Check if one string is contained within another (case-insensitive)
    """
    if not str1 or not str2:
        return False
    
    s1_lower = str1.lower()
    s2_lower = str2.lower()
    
    return s1_lower in s2_lower or s2_lower in s1_lower

def get_common_prefix(str1: str, str2: str) -> str:
    """Get common prefix of two strings"""
    if not str1 or not str2:
        return ""
    
    # Find common prefix
    i = 0
    while i < len(str1) and i < len(str2) and str1[i] == str2[i]:
        i += 1
    
    return str1[:i]

def get_common_suffix(str1: str, str2: str) -> str:
    """Get common suffix of two strings"""
    if not str1 or not str2:
        return ""
    
    # Find common suffix
    i = 0
    while i < len(str1) and i < len(str2) and str1[-1-i] == str2[-1-i]:
        i += 1
    
    return str1[-i:] if i > 0 else ""