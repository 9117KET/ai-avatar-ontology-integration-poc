"""Centralized error handling utilities for the AI Physics Tutor application."""

import logging
from typing import Tuple, Dict, Any
from flask import jsonify, Response
from anthropic import APIError, RateLimitError, APIConnectionError

logger = logging.getLogger(__name__)


class TutorError(Exception):
    """Base exception for tutor-related errors."""
    pass


class ValidationError(TutorError):
    """Raised when input validation fails."""
    pass


class APIServiceError(TutorError):
    """Raised when external API services fail."""
    pass


class OntologyError(TutorError):
    """Raised when ontology operations fail."""
    pass


def handle_api_error(error: Exception) -> Tuple[Response, int]:
    """Handle API-related errors and return appropriate responses."""
    error_message = str(error)
    
    if isinstance(error, APIError):
        if "api_key" in error_message.lower() or "authentication" in error_message.lower():
            logger.error(f"API authentication error: {error}")
            return jsonify({'error': 'AI service authentication error'}), 503
        elif isinstance(error, RateLimitError):
            logger.warning(f"API rate limit exceeded: {error}")
            return jsonify({'error': 'AI service rate limit exceeded. Please try again later.'}), 429
        elif isinstance(error, APIConnectionError):
            logger.error(f"API connection error: {error}")
            return jsonify({'error': 'AI service connection error. Please try again.'}), 503
        else:
            logger.error(f"API error: {error}")
            return jsonify({'error': 'AI service error. Please try again.'}), 500
    
    elif isinstance(error, ValidationError):
        logger.warning(f"Validation error: {error}")
        return jsonify({'error': str(error)}), 400
    
    elif isinstance(error, OntologyError):
        logger.error(f"Ontology error: {error}")
        return jsonify({'error': 'Knowledge base error. Please try again later.'}), 503
    
    elif isinstance(error, APIServiceError):
        logger.error(f"API service error: {error}")
        return jsonify({'error': 'AI service error. Please try again.'}), 503
    
    else:
        # Generic error handling
        if "timeout" in error_message.lower() or "timed out" in error_message.lower():
            logger.error(f"Request timeout: {error}")
            return jsonify({'error': 'Request timed out. Please try again.'}), 504
        elif "ontology" in error_message.lower():
            logger.error(f"Ontology error: {error}")
            return jsonify({'error': 'Could not load physics knowledge base. Please try again later.'}), 503
        else:
            logger.error(f"Unexpected error: {error}")
            return jsonify({'error': 'Internal server error'}), 500


def validate_question(question: str) -> None:
    """Validate user question input."""
    if not isinstance(question, str):
        raise ValidationError('Question must be a text string')
    
    if len(question) < 3:
        raise ValidationError('Question is too short')
    
    if len(question) > 1000:
        raise ValidationError('Question exceeds maximum length of 1000 characters')


def validate_session_id(session_id: str) -> None:
    """Validate session ID format and content."""
    if not session_id or len(session_id) > 64:
        raise ValidationError('Invalid session ID')