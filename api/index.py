import os
import sys
import json

# Add the project root to the path so we can import our modules
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# Initialize NLTK data - Use /tmp directory which is writable in Vercel
import nltk
# Check if running on Vercel (read-only filesystem)
is_vercel = os.environ.get('VERCEL') == '1'
if is_vercel:
    nltk_data_dir = '/tmp/nltk_data'
else:
    nltk_data_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'nltk_data')

os.makedirs(nltk_data_dir, exist_ok=True)
nltk.data.path.append(nltk_data_dir)
try:
    nltk.data.find('tokenizers/punkt')
except LookupError:
    nltk.download('punkt', download_dir=nltk_data_dir)

from flask import Flask, request, jsonify, send_from_directory, Response
from flask_cors import CORS
import asyncio

# Check for ANTHROPIC_API_KEY
if not os.getenv("ANTHROPIC_API_KEY"):
    print("WARNING: ANTHROPIC_API_KEY environment variable is not set. Tutor functionality will be limited.")

try:
    from llm_integration.claude_tutor import ClaudeTutor
except ImportError:
    # For Vercel deployment
    sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
    try:
        from llm_integration.claude_tutor import ClaudeTutor
    except Exception as e:
        print(f"Error importing ClaudeTutor: {e}")
        # Create a placeholder if import fails
        class ClaudeTutor:
            def __init__(self, student_id=None):
                self.student_model = type('obj', (object,), {
                    'exposed_concepts': set(),
                    'understood_concepts': set(),
                    'knowledge_level': 0,
                    'misconceptions': []
                })
            
            async def tutor(self, question):
                return "I'm sorry, but I'm currently unavailable due to a configuration issue. Please make sure the ANTHROPIC_API_KEY environment variable is set."

# Initialize Flask app
app = Flask(__name__, static_folder='../static')
CORS(app)  # Enable CORS for all routes

# Dictionary to store tutor instances for each session
tutor_instances = {}

def get_tutor(session_id):
    """Get or create a tutor instance for a session"""
    if session_id not in tutor_instances:
        try:
            # For Vercel, tell the tutor to use the /tmp directory for student data
            if os.environ.get('VERCEL') == '1':
                # Create students directory in /tmp if it doesn't exist
                os.makedirs('/tmp/data/students', exist_ok=True)
                # Pass the temporary directory to the tutor
                tutor_instances[session_id] = ClaudeTutor(
                    student_id=session_id, 
                    data_dir='/tmp/data'
                )
            else:
                tutor_instances[session_id] = ClaudeTutor(student_id=session_id)
        except Exception as e:
            print(f"Error creating tutor: {e}")
            # Return a placeholder tutor that explains the error
            return ClaudeTutor(student_id=session_id)
    return tutor_instances[session_id]

@app.route('/')
def index():
    """Serve the main HTML page"""
    return send_from_directory('../static', 'index.html')

@app.route('/static/<path:path>')
def serve_static(path):
    """Serve static files"""
    return send_from_directory('../static', path)

@app.route('/api/ask', methods=['POST'])
def ask_tutor():
    """API endpoint to ask the tutor a question"""
    data = request.json
    if not data or 'question' not in data:
        return jsonify({'error': 'Question is required'}), 400
    
    session_id = data.get('session_id', 'default_session')
    question = data['question']
    
    try:
        # Get the tutor instance for this session
        tutor = get_tutor(session_id)
        
        # Run the async function in the synchronous Flask context
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        response = loop.run_until_complete(tutor.tutor(question))
        loop.close()
        
        # Return the response
        return jsonify({
            'response': response,
            'student_model': {
                'exposed_concepts': list(tutor.student_model.exposed_concepts),
                'understood_concepts': list(tutor.student_model.understood_concepts),
                'knowledge_level': tutor.student_model.knowledge_level
            }
        })
    
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/student_model/<session_id>', methods=['GET'])
def get_student_model(session_id):
    """API endpoint to get the current student model"""
    if session_id not in tutor_instances:
        return jsonify({'error': 'Session not found'}), 404
    
    tutor = tutor_instances[session_id]
    return jsonify({
        'exposed_concepts': list(tutor.student_model.exposed_concepts),
        'understood_concepts': list(tutor.student_model.understood_concepts),
        'knowledge_level': tutor.student_model.knowledge_level,
        'misconceptions': tutor.student_model.misconceptions,
    })

@app.route('/api/learning_path/<session_id>/<target>', methods=['GET'])
def get_learning_path(session_id, target):
    """API endpoint to get a learning path to a target concept"""
    if session_id not in tutor_instances:
        return jsonify({'error': 'Session not found'}), 404
    
    tutor = tutor_instances[session_id]
    try:
        learning_path = tutor.student_model.get_learning_path(target, tutor.concept_prerequisites)
        return jsonify({'learning_path': learning_path})
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/debug', methods=['GET'])
def debug_info():
    """API endpoint to check configuration and environment"""
    try:
        # Test writable directories
        tmp_test_file = '/tmp/test_write.txt'
        with open(tmp_test_file, 'w') as f:
            f.write('Test write access')
        tmp_writable = True
        os.remove(tmp_test_file)
    except Exception as e:
        tmp_writable = str(e)
    
    env_vars = {
        "ANTHROPIC_API_KEY": "Present" if os.getenv("ANTHROPIC_API_KEY") else "Missing",
        "NLTK_DATA": nltk_data_dir,
        "NLTK_DATA_EXISTS": os.path.exists(nltk_data_dir),
        "TMP_WRITABLE": tmp_writable,
        "VERCEL_ENV": os.environ.get('VERCEL'),
        "VERCEL_REGION": os.environ.get('VERCEL_REGION'),
        "PWD": os.environ.get('PWD'),
        "PROJECT_ROOT": os.path.dirname(os.path.dirname(os.path.abspath(__file__))),
        "PYTHON_VERSION": sys.version,
        "MODULES_LOADED": list(sys.modules.keys())
    }
    return jsonify(env_vars)

# This is necessary for Vercel serverless functions
app.debug = False

# For Vercel serverless functions
def handler(request):
    """Vercel serverless function handler."""
    if request.method == 'OPTIONS':
        # Handle CORS preflight request
        response = Response()
        response.headers['Access-Control-Allow-Origin'] = '*'
        response.headers['Access-Control-Allow-Methods'] = 'GET, POST, OPTIONS'
        response.headers['Access-Control-Allow-Headers'] = 'Content-Type'
        return response

    # Convert Vercel request to WSGI environ
    environ = {
        'REQUEST_METHOD': request.method,
        'SCRIPT_NAME': '',
        'PATH_INFO': request.path,
        'QUERY_STRING': request.query_string.decode('utf-8') if request.query_string else '',
        'SERVER_PROTOCOL': 'HTTP/1.1',
        'wsgi.version': (1, 0),
        'wsgi.url_scheme': 'https',
        'wsgi.input': request.stream,
        'wsgi.errors': sys.stderr,
        'wsgi.multithread': False,
        'wsgi.multiprocess': False,
        'wsgi.run_once': False,
        'HTTP_HOST': request.headers.get('host', ''),
        'CONTENT_TYPE': request.headers.get('content-type', ''),
        'CONTENT_LENGTH': request.headers.get('content-length', ''),
    }

    # Add HTTP headers
    for key, value in request.headers.items():
        key = key.upper().replace('-', '_')
        if key not in ('CONTENT_TYPE', 'CONTENT_LENGTH'):
            environ[f'HTTP_{key}'] = value

    def start_response(status, headers, exc_info=None):
        return Response('', status=status, headers=headers)

    return app(environ, start_response)

# For local development
if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=int(os.environ.get('PORT', 5000)))