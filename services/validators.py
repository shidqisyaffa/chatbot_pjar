import re
from services.prompts import ALLOWED_KEYWORDS

def validate_domain_keyword(prompt: str) -> bool:
    """
    Validates if the user prompt is related to network programming
    by checking for allowed keywords (case-insensitive substring match).
    
    Returns:
        bool: True if the prompt is valid/related, False otherwise.
    """
    if not prompt:
        return False
        
    prompt_lower = prompt.lower()
    
    # We clean up punctuation to prevent false negatives (e.g., matching "select()" with "select")
    # by checking direct substring match.
    for keyword in ALLOWED_KEYWORDS:
        # Check if the keyword exists as a substring
        if keyword.lower() in prompt_lower:
            return True
            
    return False
