import re
from typing import Dict, Tuple, List
from src.models.normalization import NormalizationCategory, NormalizationChange

def apply_dictionary_rules(
    text: str, 
    dictionary: Dict[str, str], 
    category: NormalizationCategory
) -> Tuple[str, List[NormalizationChange]]:
    """
    Applies a dictionary of corrections to the text deterministically.
    Rules:
    1. Case-insensitive matching.
    2. Longest-match-first to prevent partial word replacements.
    3. Word boundaries (\b) to prevent mid-word substring replacements.
    """
    changes = []
    
    # Sort dictionary keys by descending length for Longest-Match-First
    sorted_keys = sorted(dictionary.keys(), key=len, reverse=True)
    
    for key in sorted_keys:
        target_value = dictionary[key]
        # We use \b to ensure word boundaries.
        # re.escape ensures special characters in keys don't break the regex.
        pattern = r'\b' + re.escape(key) + r'\b'
        
        # Check if a match exists before replacing, to record the change
        if re.search(pattern, text, flags=re.IGNORECASE):
            # We record what we found. To get the EXACT original string we matched,
            # we can find all matches and record them, but for simplicity we record the key.
            # However, the user wants 'original_text' preserved. The regex replace handles that.
            
            # Find the actual matched string for the log
            matches = set(re.findall(pattern, text, flags=re.IGNORECASE))
            for match in matches:
                if match != target_value: # Don't record a change if it's identical
                    changes.append(
                        NormalizationChange(
                            category=category,
                            original=match,
                            normalized=target_value
                        )
                    )
            
            # Perform the deterministic replacement
            text = re.sub(pattern, target_value, text, flags=re.IGNORECASE)
            
    return text, changes

def normalize_whitespace(text: str) -> str:
    """Removes duplicate spaces and trims leading/trailing whitespace."""
    return re.sub(r'\s+', ' ', text).strip()
