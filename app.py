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
from flask import Flask, request, jsonify, send_from_directory
from flask_cors import CORS
from jose import jwt
from jose.exceptions import JWTError
from llm_integration.claude_tutor import ClaudeTutor

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Initialize Flask app
app = Flask(__name__, static_folder='static')

# Configure SSL certificates for requests (fixes Anthropic client issues)
import certifi
os.environ['SSL_CERT_FILE'] = certifi.where()
os.environ['REQUESTS_CA_BUNDLE'] = certifi.where()
os.environ['CURL_CA_BUNDLE'] = certifi.where()
logger.debug(f"SSL certificate path set to: {certifi.where()}")

# Configure CORS with appropriate origins
allowed_origins = os.getenv('ALLOWED_ORIGINS', '*').split(',')
CORS(app, resources={r"/*": {"origins": allowed_origins}})
logger.info(f"CORS configured with allowed origins: {allowed_origins}")

# Configure app for better security
app.config['JSON_SORT_KEYS'] = False  # Preserve response JSON order
app.config['SEND_FILE_MAX_AGE_DEFAULT'] = 31536000  # 1 year cache for static files

# Security configurations
JWT_SECRET = os.getenv('JWT_SECRET', 'your-secret-key')  # Should be set in production
JWT_ALGORITHM = 'HS256'
RATE_LIMIT = int(os.getenv('RATE_LIMIT', 100))  # requests per minute
RATE_LIMIT_WINDOW = int(os.getenv('RATE_LIMIT_WINDOW', 60))  # seconds

# Dictionary to store tutor instances and rate limiting data
tutor_instances = {}
rate_limits = {}

def validate_session_id(session_id):
    """Validate session ID format and content."""
    if not session_id or len(session_id) > 64:
        return False
    return True

def check_rate_limit(session_id):
    """Implement rate limiting per session."""
    current_time = time.time()
    if session_id not in rate_limits:
        rate_limits[session_id] = {'count': 1, 'window_start': current_time}
        return True
    
    if current_time - rate_limits[session_id]['window_start'] > RATE_LIMIT_WINDOW:
        rate_limits[session_id] = {'count': 1, 'window_start': current_time}
        return True
    
    if rate_limits[session_id]['count'] >= RATE_LIMIT:
        return False
    
    rate_limits[session_id]['count'] += 1
    return True

def get_tutor(session_id):
    """Get or create a tutor instance for a session with security checks.
    
    Args:
        session_id: A string identifier for the user session
        
    Returns:
        ClaudeTutor: An instance of the tutor for this session
        
    Raises:
        ValueError: If the session ID is invalid
        RuntimeError: If the tutor cannot be initialized (e.g., ontology cannot be loaded)
    """
    if not validate_session_id(session_id):
        raise ValueError("Invalid session ID")
    
    if session_id not in tutor_instances:
        logger.info(f"Creating new tutor instance for session {session_id}")
        try:
            tutor_instances[session_id] = ClaudeTutor(student_id=session_id)
            logger.info(f"Successfully created tutor for session {session_id}")
        except Exception as e:
            logger.error(f"Failed to initialize tutor: {str(e)}")
            if "ontology" in str(e).lower():
                raise RuntimeError("Could not load physics knowledge base. Please try again later.")
            raise
    
    return tutor_instances[session_id]

@app.before_request
def before_request():
    """Security middleware for all requests."""
    # Rate limiting
    session_id = request.args.get('session_id', 'default_session')
    if not check_rate_limit(session_id):
        return jsonify({'error': 'Rate limit exceeded'}), 429
    
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
    response.headers['Content-Security-Policy'] = "default-src 'self'; script-src 'self' 'unsafe-inline' cdn.tailwindcss.com *.vercel.live vercel.live; style-src 'self' 'unsafe-inline' fonts.googleapis.com; font-src fonts.gstatic.com; img-src 'self' data:; connect-src 'self' *.vercel.app"  # CSP
    response.headers['Referrer-Policy'] = 'strict-origin-when-cross-origin'  # Limits referrer information
    
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
            return jsonify({'error': str(ve)}), 400
        except RuntimeError as re:
            return jsonify({'error': str(re)}), 503  # Service Unavailable
        
        # Get the tutor's response
        try:
            response = tutor.tutor_sync(question)
            
            # Return the response with some metadata
            return jsonify({
                'response': response,
                'session_id': session_id,
                'timestamp': datetime.now().isoformat()
            })
            
        except ValueError as ve:
            # Handle specific validation errors
            logger.warning(f"Validation error: {ve}")
            return jsonify({'error': str(ve)}), 400
            
        except Exception as e:
            # Handle API or processing errors
            error_message = str(e)
            if "api_key" in error_message.lower() or "authentication" in error_message.lower():
                logger.error(f"API authentication error: {e}")
                return jsonify({'error': 'AI service authentication error'}), 503
            elif "timeout" in error_message.lower() or "timed out" in error_message.lower():
                logger.error(f"Request timeout: {e}")
                return jsonify({'error': 'Request timed out. Please try again.'}), 504
            else:
                logger.error(f"Error generating response: {e}")
                return jsonify({'error': 'Failed to generate response'}), 500
    
    except Exception as e:
        logger.error(f"Unexpected error processing question: {e}")
        return jsonify({'error': 'Internal server error'}), 500

if __name__ == '__main__':
    # Print startup banner
    print("\n" + "=" * 80)
    print("AI Physics Tutor - Ontology-Enhanced Learning System")
    print("Version 1.0.0 | Flask WSGI Server")
    print("=" * 80)
    
    # Get configuration from environment variables
    host = os.getenv('HOST', '0.0.0.0')
    port = int(os.getenv('PORT', '5000'))
    debug = os.getenv('DEBUG', 'False').lower() == 'true'
    
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