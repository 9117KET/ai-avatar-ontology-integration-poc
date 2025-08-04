"""  
AI Physics Tutor Application Server

This Flask application serves as the backend for the AI Physics Tutor, handling:
- API requests for the Claude AI-powered physics tutoring
- User session management with security features
- Rate limiting and input validation
- Interaction with the ontology-based knowledge system
"""

import os
import logging
import time
from datetime import datetime, timedelta
from typing import Tuple, Dict, Any, Optional
from flask import Flask, request, jsonify, send_from_directory, Response
from flask_cors import CORS
from jose import jwt
from jose.exceptions import JWTError
from llm_integration.claude_tutor import ClaudeTutor
from utils.ssl_config import configure_ssl_certificates
from config.settings import load_config
from utils.error_handler import ValidationError, handle_api_error

# Load centralized configuration
try:
    app_config, security_config, api_config = load_config()
    logger = logging.getLogger(__name__)
    logging.basicConfig(level=getattr(logging, app_config.log_level))
    logger.info("Configuration loaded successfully")
except Exception as e:
    # Fallback to basic configuration if centralized config fails
    logging.basicConfig(level=logging.INFO)
    logger = logging.getLogger(__name__)
    logger.error(f"Failed to load centralized configuration: {e}")
    logger.info("Using fallback configuration")
    
    # Fallback configuration
    class FallbackConfig:
        host = os.getenv('HOST', '0.0.0.0')
        port = int(os.getenv('PORT', '5000'))
        debug = os.getenv('DEBUG', 'False').lower() == 'true'
        
    class FallbackSecurityConfig:
        jwt_secret = os.getenv('JWT_SECRET')
        jwt_algorithm = 'HS256'
        rate_limit = int(os.getenv('RATE_LIMIT', '100'))
        rate_limit_window = int(os.getenv('RATE_LIMIT_WINDOW', '60'))
        allowed_origins = os.getenv('ALLOWED_ORIGINS', 'http://localhost:5000,http://127.0.0.1:5000').split(',')
        
    app_config = FallbackConfig()
    security_config = FallbackSecurityConfig()

# Initialize Flask app
app = Flask(__name__, static_folder='static')

# Configure SSL certificates for requests (fixes Anthropic client issues)
configure_ssl_certificates()

# Configure CORS with appropriate origins
if hasattr(security_config, 'allowed_origins'):
    allowed_origins = security_config.allowed_origins
else:
    allowed_origins = os.getenv('ALLOWED_ORIGINS', 'http://localhost:5000,http://127.0.0.1:5000').split(',')

CORS(app, resources={r"/*": {"origins": allowed_origins}})
logger.info(f"CORS configured with allowed origins: {allowed_origins}")

# Configure app for better security
app.config['JSON_SORT_KEYS'] = False  # Preserve response JSON order
app.config['SEND_FILE_MAX_AGE_DEFAULT'] = 31536000  # 1 year cache for static files

# Security configurations
if not security_config.jwt_secret:
    raise ValueError("JWT_SECRET environment variable is required for security")
JWT_SECRET = security_config.jwt_secret
JWT_ALGORITHM = security_config.jwt_algorithm
RATE_LIMIT = security_config.rate_limit
RATE_LIMIT_WINDOW = security_config.rate_limit_window

# Vercel/serverless: Use JWT for stateless session and rate limiting
# Remove in-memory dictionaries

def validate_session_id(session_id: str) -> bool:
    """Validate session ID format and content."""
    if not session_id or len(session_id) > 64:
        return False
    return True

# JWT-based stateless rate limiting and session management
def encode_session_jwt(session_id: str, count: int, window_start: float) -> str:
    payload = {
        'session_id': session_id,
        'count': count,
        'window_start': window_start,
        'exp': datetime.utcnow() + timedelta(days=7)
    }
    return jwt.encode(payload, JWT_SECRET, algorithm=JWT_ALGORITHM)

def decode_session_jwt(token: str) -> Optional[Dict[str, Any]]:
    try:
        payload = jwt.decode(token, JWT_SECRET, algorithms=[JWT_ALGORITHM])
        return payload
    except JWTError:
        return None

def check_rate_limit_jwt(token: Optional[str]) -> Tuple[str, bool]:
    payload = decode_session_jwt(token) if token else None
    current_time = time.time()
    if not payload:
        # New session
        return encode_session_jwt('default_session', 1, current_time), True
    count = payload.get('count', 0)
    window_start = payload.get('window_start', current_time)
    if current_time - window_start > RATE_LIMIT_WINDOW:
        # Reset window
        return encode_session_jwt(payload['session_id'], 1, current_time), True
    if count >= RATE_LIMIT:
        return token, False
    return encode_session_jwt(payload['session_id'], count + 1, window_start), True

def get_tutor(session_id: str) -> ClaudeTutor:
    """Always create a new tutor instance for each request (stateless)."""
    if not validate_session_id(session_id):
        raise ValueError("Invalid session ID")
    try:
        tutor = ClaudeTutor(student_id=session_id)
        logger.info(f"Created tutor for session {session_id}")
        return tutor
    except Exception as e:
        logger.error(f"Failed to initialize tutor: {str(e)}")
        if "ontology" in str(e).lower():
            raise RuntimeError("Could not load physics knowledge base. Please try again later.")
        raise

@app.before_request
def before_request():
    """Security middleware for all requests."""
    # Skip validation for static files and non-API routes
    if request.endpoint in ['index', 'favicon'] or request.path.startswith('/static'):
        return
        
    # Rate limiting
    session_id = 'default_session'
    
    # Try to get session_id from different sources
    if request.is_json and request.get_json():
        session_id = request.get_json().get('session_id', 'default_session')
    else:
        session_id = request.args.get('session_id', 'default_session')
    
    token = request.headers.get('Authorization')
    new_token, allowed = check_rate_limit_jwt(token)
    if not allowed:
        resp = jsonify({'error': 'Rate limit exceeded'})
        if new_token:
            resp.headers['Authorization'] = new_token
        return resp, 429
    # Attach the new token to the response in after_request (Flask limitation)
    request.new_token = new_token
    # Validate session ID
    if not validate_session_id(session_id):
        return jsonify({'error': 'Invalid session ID'}), 400

@app.route('/')
def index():
    """Serve the main HTML page with enhanced security headers.
    
    This route delivers the single-page application (SPA) with appropriate
    security headers to protect against common web vulnerabilities.
    
    Returns:
        Flask response with the HTML content and security headers
    """
    response = send_from_directory('static', 'index.html')
    
    # Security headers to prevent common attacks
    response.headers['X-Content-Type-Options'] = 'nosniff'  # Prevents MIME type sniffing
    response.headers['X-Frame-Options'] = 'DENY'  # Prevents clickjacking
    response.headers['X-XSS-Protection'] = '1; mode=block'  # Basic XSS protection
    # Comprehensive CSP header that allows necessary resources
    csp_directives = [
        "default-src 'self'",
        "script-src 'self' 'unsafe-inline' 'unsafe-eval' cdn.tailwindcss.com *.vercel.live vercel.live",
        "style-src 'self' 'unsafe-inline' fonts.googleapis.com cdn.tailwindcss.com",
        "font-src 'self' fonts.gstatic.com data:",
        "img-src 'self' data: blob:",
        "connect-src 'self' *.vercel.app api2.amplitude.com o4505129952280576.ingest.sentry.io",
        "frame-src 'self'",
        "base-uri 'self'"
    ]
    response.headers['Content-Security-Policy'] = "; ".join(csp_directives)  # CSP
    response.headers['Referrer-Policy'] = 'strict-origin-when-cross-origin'  # Limits referrer information
    
    return response

@app.route('/favicon.ico')
def favicon():
    """Serve the favicon directly from the static folder."""
    return send_from_directory('static', 'favicon.ico')

@app.after_request
def after_request(response):
    # Attach new JWT token for stateless rate limiting
    new_token = getattr(request, 'new_token', None)
    if new_token:
        response.headers['Authorization'] = new_token
    return response

@app.route('/api/ask', methods=['POST'])
def ask_tutor():
    """API endpoint to ask the tutor a question with input validation.
    
    Processes user questions and returns tutoring responses leveraging
    the Claude AI and physics ontology. Includes comprehensive validation
    and error handling for a robust user experience.
    
    Returns:
        JSON response with tutor's answer or error details
    """
    try:
        # Parse and validate input data
        data = request.get_json()
        if not data or 'question' not in data:
            return jsonify({'error': 'Question is required'}), 400
        
        session_id = data.get('session_id', 'default_session')
        question = data['question']
        
        # Input validation
        if not isinstance(question, str):
            return jsonify({'error': 'Question must be a text string'}), 400
        
        if len(question) < 3:
            return jsonify({'error': 'Question is too short'}), 400
            
        if len(question) > 1000:
            return jsonify({'error': 'Question exceeds maximum length of 1000 characters'}), 400
        
        logger.info(f"Processing question for session {session_id}: {question[:50]}...")
        
        # Get the tutor instance for this session
        try:
            tutor = get_tutor(session_id)
        except ValueError as ve:
            logger.error(f"Validation error creating tutor: {ve}")
            if "API" in str(ve) or "api_key" in str(ve).lower():
                return jsonify({'error': 'AI service configuration error. Please contact support.'}), 503
            return jsonify({'error': str(ve)}), 400
        except RuntimeError as re:
            logger.error(f"Runtime error creating tutor: {re}")
            return jsonify({'error': str(re)}), 503  # Service Unavailable
        except Exception as e:
            logger.error(f"Unexpected error creating tutor: {e}")
            return jsonify({'error': 'Failed to initialize AI tutor. Please try again.'}), 500
        
        # Get the tutor's response
        try:
            response = tutor.tutor_sync(question)
            
            # Return the response with some metadata
            return jsonify({
                'response': response,
                'session_id': session_id,
                'timestamp': datetime.now().isoformat()
            })
            
        except Exception as e:
            # Use centralized error handling
            return handle_api_error(e)
    
    except Exception as e:
        # Use centralized error handling for unexpected errors
        logger.error(f"Unexpected error processing question: {e}")
        return handle_api_error(e)

if __name__ == '__main__':
    # Print startup banner
    print("\n" + "=" * 80)
    print("AI Physics Tutor - Ontology-Enhanced Learning System")
    print("Version 1.0.0 | Flask WSGI Server")
    print("=" * 80)
    
    # Use centralized configuration
    host = app_config.host
    port = app_config.port
    debug = app_config.debug
    
    # Log startup information
    logger.info(f"Starting AI Physics Tutor server at http://{host}:{port}")
    logger.info(f"Debug mode: {debug}")
    
    # Check for API key
    if not os.getenv('ANTHROPIC_API_KEY'):
        logger.warning("ANTHROPIC_API_KEY environment variable not set! The tutor will not function properly.")
        print("\nWARNING: ANTHROPIC_API_KEY environment variable not set!")
        print("The AI tutor requires a valid Claude API key to function.")
        print("Please set this in your .env file or environment variables.\n")
    
    # SSL configuration if needed
    ssl_context = None
    if os.getenv('USE_SSL', 'False').lower() == 'true':
        ssl_cert = os.getenv('SSL_CERT_FILE')
        ssl_key = os.getenv('SSL_KEY_FILE')
        if ssl_cert and ssl_key:
            ssl_context = (ssl_cert, ssl_key)
            logger.info("SSL enabled with provided certificate and key")
        else:
            logger.warning("SSL_CERT_FILE or SSL_KEY_FILE not set. Disabling SSL.")
    
    print("\nServer starting...")
    if debug:
        print("Debug mode is ON - do not use in production!\n")
    
    # Run the Flask server (WSGI)
    app.run(host=host, port=port, debug=debug, ssl_context=ssl_context)