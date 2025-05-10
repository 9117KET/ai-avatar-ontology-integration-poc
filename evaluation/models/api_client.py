"""
API client implementations for model interactions.

This module provides secure implementations for interacting with external APIs.
"""

import requests
import logging
from evaluation.config.settings import BASE_API_URL, APIConfig

logger = logging.getLogger("hallucination_evaluator")

class AnthropicClient:
    """Secure client for interacting with Anthropic Claude API."""
    
    @staticmethod
    def query_model(prompt, model="claude-3-opus-20240229", max_tokens=1024, timeout=30):
        """
        Query the Claude model securely.
        
        Args:
            prompt: The prompt to send to the model
            model: The model identifier to use
            max_tokens: Maximum number of tokens to generate
            timeout: Request timeout in seconds
            
        Returns:
            The model's response text
        """
        logger.info(f"Querying Claude model: {model} with prompt: {prompt[:50]}...")
        
        try:
            # Get headers securely without exposing API key in code
            headers = APIConfig.get_anthropic_headers()
            
            response = requests.post(
                "https://api.anthropic.com/v1/messages",
                json={
                    "model": model,
                    "max_tokens": max_tokens,
                    "messages": [{"role": "user", "content": prompt}]
                },
                headers=headers,
                timeout=timeout
            )
            
            if response.status_code != 200:
                logger.error(f"Claude API error: {response.status_code} - {response.text}")
                return f"Error: {response.status_code} - {response.text}"
            
            return response.json()["content"][0]["text"]
            
        except Exception as e:
            logger.error(f"Error querying Claude model: {e}")
            return f"Error: {str(e)}"

class OntologyAPIClient:
    """Client for interacting with the ontology-enhanced API."""
    
    @staticmethod
    def query_model(prompt, session_id="eval_session", max_retries=1, timeout=10):
        """
        Query the ontology-enhanced model through the deployed API.
        
        Args:
            prompt: The question/prompt to send to the model
            session_id: Session ID for the API call
            max_retries: Maximum number of retry attempts for timeouts
            timeout: Request timeout in seconds
            
        Returns:
            The model's response text or None if API fails
        """
        logger.info(f"Querying ontology API with prompt: {prompt[:50]}...")
        
        for attempt in range(max_retries):
            try:
                # Get auth token securely
                auth_token = APIConfig.get_auth_token()
                
                # Prepare headers with auth token if available
                headers = {}
                if auth_token:
                    headers["Authorization"] = f"Bearer {auth_token}"
                
                response = requests.post(
                    f"{BASE_API_URL}/ask",
                    json={"question": prompt, "session_id": session_id},
                    headers=headers,
                    timeout=timeout
                )
                
                if response.status_code == 200:
                    return response.json()["response"]
                else:
                    logger.warning(f"API error: {response.status_code} - {response.text}")
                    break
                    
            except Exception as e:
                logger.warning(f"Error querying ontology model API (attempt {attempt+1}/{max_retries}): {e}")
                if attempt < max_retries - 1:
                    continue
                break
        
        return None
