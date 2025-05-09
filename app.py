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
CORS(app, resources={r"/*": {"origins": os.getenv('ALLOWED_ORIGINS', '*')}})  # Configure CORS

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
    """Get or create a tutor instance for a session with security checks."""
    if not validate_session_id(session_id):
        raise ValueError("Invalid session ID")
    
    if session_id not in tutor_instances:
        logger.info(f"Creating new tutor instance for session {session_id}")
        tutor_instances[session_id] = ClaudeTutor(student_id=session_id)
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
    """Serve the main HTML page with security headers."""
    response = send_from_directory('static', 'index.html')
    response.headers['X-Content-Type-Options'] = 'nosniff'
    response.headers['X-Frame-Options'] = 'DENY'
    response.headers['X-XSS-Protection'] = '1; mode=block'
    return response

@app.route('/api/ask', methods=['POST'])
def ask_tutor():
    """API endpoint to ask the tutor a question with input validation."""
    try:
        data = request.get_json()
        if not data or 'question' not in data:
            return jsonify({'error': 'Question is required'}), 400
        
        session_id = data.get('session_id', 'default_session')
        question = data['question']
        
        # Input validation
        if not isinstance(question, str) or len(question) > 1000:
            return jsonify({'error': 'Invalid question format'}), 400
        
        # Get the tutor instance for this session
        tutor = get_tutor(session_id)
        
        # Get the tutor's response
        response = tutor.tutor_sync(question)
        
        # Return the response
        return jsonify({
            'response': response
        })
    
    except Exception as e:
        logger.error(f"Error processing question: {e}")
        return jsonify({'error': 'Internal server error'}), 500

if __name__ == '__main__':
    # Get configuration from environment variables
    host = os.getenv('HOST', '0.0.0.0')
    port = int(os.getenv('PORT', '5000'))
    debug = os.getenv('DEBUG', 'False').lower() == 'true'
    
    # SSL configuration if needed
    ssl_context = None
    if os.getenv('USE_SSL', 'False').lower() == 'true':
        ssl_context = (os.getenv('SSL_CERT_FILE'), os.getenv('SSL_KEY_FILE'))
    
    # Run the Flask server
    app.run(host=host, port=port, debug=debug, ssl_context=ssl_context)