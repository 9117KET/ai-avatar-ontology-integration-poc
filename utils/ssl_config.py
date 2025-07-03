"""SSL configuration utilities for the AI Physics Tutor application."""

import os
import certifi
import logging

logger = logging.getLogger(__name__)

def configure_ssl_certificates():
    """Configure SSL certificates for all HTTP requests.
    
    This function sets up the necessary environment variables for SSL certificate
    verification, fixing common issues with the Anthropic client and other HTTPS requests.
    """
    cert_path = certifi.where()
    
    # Set SSL certificate path environment variables
    os.environ['SSL_CERT_FILE'] = cert_path
    os.environ['REQUESTS_CA_BUNDLE'] = cert_path
    os.environ['CURL_CA_BUNDLE'] = cert_path
    
    logger.debug(f"SSL certificate path configured: {cert_path}")
    return cert_path