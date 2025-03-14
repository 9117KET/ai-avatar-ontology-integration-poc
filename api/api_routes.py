from http.server import BaseHTTPRequestHandler
import os
import sys
import json
import asyncio

# Add project root to path
root_path = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.append(root_path)

# Initialize NLTK data
import nltk
nltk_data_dir = '/tmp/nltk_data'
os.makedirs(nltk_data_dir, exist_ok=True)
nltk.data.path.append(nltk_data_dir)
try:
    nltk.data.find('tokenizers/punkt')
except LookupError:
    nltk.download('punkt', download_dir=nltk_data_dir)

# Import the ClaudeTutor
try:
    from llm_integration.claude_tutor import ClaudeTutor
except ImportError as e:
    print(f"Error importing ClaudeTutor: {e}")
    class ClaudeTutor:
        def __init__(self, student_id=None, data_dir=None):
            self.student_model = type('obj', (object,), {
                'exposed_concepts': set(),
                'understood_concepts': set(),
                'knowledge_level': 0,
                'misconceptions': []
            })
        
        async def tutor(self, question):
            return "I'm sorry, but I'm currently unavailable due to a configuration issue. Please make sure the ANTHROPIC_API_KEY environment variable is set."

# Create a dictionary to store tutor instances
tutor_instances = {}

def get_tutor(session_id):
    """Get or create a tutor instance for a session"""
    if session_id not in tutor_instances:
        # Create students directory in /tmp if it doesn't exist
        os.makedirs('/tmp/data/students', exist_ok=True)
        # Create a new tutor instance for this session
        try:
            tutor_instances[session_id] = ClaudeTutor(
                student_id=session_id, 
                data_dir='/tmp/data'
            )
        except Exception as e:
            print(f"Error creating tutor: {e}")
            return ClaudeTutor(student_id=session_id)
    return tutor_instances[session_id]

class handler(BaseHTTPRequestHandler):
    def do_POST(self):
        """Handle POST requests for the tutor API"""
        # Read the request body
        content_length = int(self.headers.get('Content-Length', 0))
        body = self.rfile.read(content_length).decode('utf-8')
        
        # Parse the JSON body
        try:
            data = json.loads(body)
        except json.JSONDecodeError:
            self.send_response(400)
            self.send_header('Content-type', 'application/json')
            self.end_headers()
            self.wfile.write(json.dumps({"error": "Invalid JSON"}).encode('utf-8'))
            return
        
        # Check for required fields
        if 'question' not in data:
            self.send_response(400)
            self.send_header('Content-type', 'application/json')
            self.end_headers()
            self.wfile.write(json.dumps({"error": "Question is required"}).encode('utf-8'))
            return
        
        # Get the session ID or use a default
        session_id = data.get('session_id', 'default_session')
        question = data['question']
        
        try:
            # Get the tutor for this session
            tutor = get_tutor(session_id)
            
            # Run the async function in a synchronous context
            loop = asyncio.new_event_loop()
            asyncio.set_event_loop(loop)
            response = loop.run_until_complete(tutor.tutor(question))
            loop.close()
            
            # Return the response
            self.send_response(200)
            self.send_header('Content-type', 'application/json')
            self.end_headers()
            
            # Create the response JSON
            response_data = {
                'response': response,
                'student_model': {
                    'exposed_concepts': list(tutor.student_model.exposed_concepts),
                    'understood_concepts': list(tutor.student_model.understood_concepts),
                    'knowledge_level': tutor.student_model.knowledge_level
                }
            }
            
            self.wfile.write(json.dumps(response_data).encode('utf-8'))
            
        except Exception as e:
            self.send_response(500)
            self.send_header('Content-type', 'application/json')
            self.end_headers()
            self.wfile.write(json.dumps({"error": str(e)}).encode('utf-8'))
    
    def do_GET(self):
        """Handle GET requests with debug info"""
        self.send_response(200)
        self.send_header('Content-type', 'application/json')
        self.end_headers()
        
        # Create debug info
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
            "PYTHON_VERSION": sys.version,
        }
        
        self.wfile.write(json.dumps(env_vars).encode('utf-8')) 