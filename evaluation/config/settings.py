"""
Configuration settings for the hallucination evaluation module.

This module centralizes configuration settings and securely handles API keys.
"""

import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# API Configuration
BASE_API_URL = os.getenv("BASE_API_URL", "https://ai-avatar-ontology-integration-poc.vercel.app/api")

# Output configuration
DEFAULT_OUTPUT_DIR = os.path.join(os.path.dirname(os.path.dirname(__file__)), "results")
OUTPUT_DIR = os.getenv("OUTPUT_DIR", DEFAULT_OUTPUT_DIR)

# Ensure output directory exists
os.makedirs(OUTPUT_DIR, exist_ok=True)

# Logging configuration
LOG_FILE = os.path.join(OUTPUT_DIR, "evaluation.log")

class APIConfig:
    """Secure API configuration handler."""
    
    @staticmethod
    def get_anthropic_headers():
        """
        Get Anthropic API headers without exposing the API key in code.
        
        Returns:
            dict: Headers for Anthropic API requests
        """
        api_key = os.getenv("ANTHROPIC_API_KEY")
        if not api_key:
            raise ValueError("ANTHROPIC_API_KEY environment variable is required")
            
        return {
            "x-api-key": api_key,
            "anthropic-version": "2023-06-01",
            "content-type": "application/json"
        }
    
    @staticmethod
    def get_auth_token():
        """
        Get authentication token for the API.
        
        Returns:
            str: Authentication token
        """
        return os.getenv("AUTH_TOKEN", "")
