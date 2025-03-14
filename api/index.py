import os
import sys
import json

# Add the project root to the path so we can import our modules
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# Initialize NLTK data
import nltk
nltk_data_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'nltk_data')
os.makedirs(nltk_data_dir, exist_ok=True)
nltk.data.path.append(nltk_data_dir)
try:
    nltk.data.find('tokenizers/punkt')
except LookupError:
    nltk.download('punkt', download_dir=nltk_data_dir)

from flask import Flask, request, jsonify, send_from_directory
from flask_cors import CORS
import asyncio

try:
    from llm_integration.claude_tutor import ClaudeTutor
except ImportError:
    # For Vercel deployment
    sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
    from llm_integration.claude_tutor import ClaudeTutor

# Initialize Flask app
app = Flask(__name__, static_folder='../static')
CORS(app)  # Enable CORS for all routes

# Dictionary to store tutor instances for each session
tutor_instances = {}

def get_tutor(session_id):
    """Get or create a tutor instance for a session"""
    if session_id not in tutor_instances:
        tutor_instances[session_id] = ClaudeTutor(student_id=session_id)
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

# This is necessary for Vercel serverless functions
app.debug = False

# Handler for Vercel serverless function
def handler(event, context):
    return app(event, context)

# For local development
if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=int(os.environ.get('PORT', 5000))) 