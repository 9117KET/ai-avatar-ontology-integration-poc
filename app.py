import os
import asyncio
import logging
from quart import Quart, request, jsonify, send_from_directory
from quart_cors import cors
from llm_integration.claude_tutor import ClaudeTutor

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Initialize Quart app
app = Quart(__name__, static_folder='static')
app = cors(app)  # Enable CORS for all routes

# Dictionary to store tutor instances for each session
tutor_instances = {}

def get_tutor(session_id):
    """Get or create a tutor instance for a session"""
    if session_id not in tutor_instances:
        logger.info(f"Creating new tutor instance for session {session_id}")
        tutor_instances[session_id] = ClaudeTutor(student_id=session_id)
    return tutor_instances[session_id]

@app.route('/')
async def index():
    """Serve the main HTML page"""
    return await send_from_directory('static', 'index.html')

@app.route('/api/ask', methods=['POST'])
async def ask_tutor():
    """API endpoint to ask the tutor a question"""
    data = await request.get_json()
    if not data or 'question' not in data:
        return jsonify({'error': 'Question is required'}), 400
    
    session_id = data.get('session_id', 'default_session')
    question = data['question']
    
    try:
        # Get the tutor instance for this session
        tutor = get_tutor(session_id)
        
        # Get the tutor's response
        response = await tutor.tutor(question)
        
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
        logger.error(f"Error processing question: {e}")
        return jsonify({'error': str(e)}), 500

@app.route('/api/student_model/<session_id>', methods=['GET'])
async def get_student_model(session_id):
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
async def get_learning_path(session_id, target):
    """API endpoint to get a learning path to a target concept"""
    if session_id not in tutor_instances:
        return jsonify({'error': 'Session not found'}), 404
    
    tutor = tutor_instances[session_id]
    try:
        learning_path = tutor.student_model.get_learning_path(target, tutor.concept_prerequisites)
        return jsonify({'learning_path': learning_path})
    except Exception as e:
        logger.error(f"Error generating learning path: {e}")
        return jsonify({'error': str(e)}), 500

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=int(os.environ.get('PORT', 5000))) 