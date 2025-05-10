"""
Text processing utilities for hallucination evaluation.
"""

import re

def extract_answer_choice(response):
    """
    Extract the letter of the selected answer from the model's response.
    
    Args:
        response: The model's response text
        
    Returns:
        The extracted answer choice letter (A-E) or None if not found
    """
    # Check if this is a fallback response due to API timeout
    if "API timeout" in response or "couldn't provide an answer" in response:
        return None
        
    # Pattern to match answer choices at the beginning of a line or after common prefixes
    pattern = r'(?:^|answer is|select|choose|option)\s*([A-E])[.\s)]'
    
    # Search case-insensitive
    match = re.search(pattern, response, re.IGNORECASE)
    if match:
        return match.group(1).upper()
    
    # If no match found, look for the options verbatim
    for option in ["A", "B", "C", "D", "E"]:
        if f"Option {option}" in response or f"option {option}" in response:
            return option
    
    # Check if response contains an error message
    if response.startswith("Error:"):
        return None
        
    return None

def keyword_match(phrase, text):
    """
    Check if a phrase or its keywords appear in the text.
    
    Args:
        phrase: The phrase to check for
        text: The text to search in
        
    Returns:
        Boolean indicating if the phrase or its key terms are found
    """
    # Direct match
    if phrase.lower() in text.lower():
        return True
    
    # Keyword matching
    keywords = [w for w in phrase.lower().split() if len(w) > 3]
    return all(keyword in text.lower() for keyword in keywords)

def parse_verification_result(verification_result):
    """
    Parse the expert verification result to extract hallucinations.
    
    Args:
        verification_result: The expert model's verification response
        
    Returns:
        List of detected hallucinations
    """
    hallucinations = []
    
    # Check if hallucinations were detected
    contains_hallucinations = False
    if "CONTAINS_HALLUCINATIONS: Yes" in verification_result:
        contains_hallucinations = True
    
    if not contains_hallucinations:
        return hallucinations
    
    # Extract hallucinations using regex
    # Looking for patterns like: "- [quote]: explanation" or "1. [quote]: explanation"
    pattern = r'[-\d+\.]\s*\[(.*?)\]:\s*(.*?)(?=$|[-\d+\.]\s*\[)'
    matches = re.finditer(pattern, verification_result, re.DOTALL)
    
    for match in matches:
        quote = match.group(1).strip()
        explanation = match.group(2).strip()
        hallucinations.append({
            "type": "expert_verification",
            "quote": quote,
            "explanation": explanation
        })
    
    return hallucinations
