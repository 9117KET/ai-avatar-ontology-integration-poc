# LLM Integration for Physics Tutor

This module handles the integration between the physics knowledge ontology and the Claude 3 LLM to create an enhanced physics tutoring experience.

## Components

### ClaudeTutor

The `ClaudeTutor` class is the main component that:

- Loads the physics ontology for structured knowledge
- Communicates with Claude 3 through the Anthropic API
- Provides accurate physics explanations with reduced hallucinations
- Enhances responses with proper physics terminology and formula formatting

### StudentModel

The `StudentModel` class provides a simplified tracking of student interactions. It maintains:

- **Exposed Concepts**: Physics topics the student has encountered during tutoring sessions
- **Simple Session History**: Basic tracking of conversation context

This streamlined model focuses on the core functionality needed for effective physics tutoring without the overhead of complex progress tracking. The system:

1. **Tracks Concept Exposure**: Records which physics concepts a student has been exposed to
2. **Identifies Ready Concepts**: Determines which concepts a student is ready to learn based on prerequisites
3. **Provides Context**: Gives the tutor awareness of previously discussed topics

## Usage

### Basic Tutoring

```python
from llm_integration.claude_tutor import ClaudeTutor

# Create a tutor for a specific student
tutor = ClaudeTutor(student_id="student_123")

# Ask a question using the synchronous interface
response = tutor.tutor_sync("Can you explain Newton's First Law?")
print(response)
```

### Integration with Flask Application

```python
from llm_integration.claude_tutor import ClaudeTutor, get_tutor

# In a Flask route handler
def ask_question():
    # Get or create a tutor instance for this session
    session_id = "user_session_123"
    tutor = get_tutor(session_id)
    
    # Process the user's question
    question = "What is conservation of momentum?"
    response = tutor.tutor_sync(question)
    
    # The student model automatically tracks exposed physics concepts
    exposed_concepts = tutor.student_model.exposed_concepts
    
    # Find concepts the student is ready to learn
    ready_concepts = tutor.student_model.get_ready_concepts(tutor.concept_prerequisites)
    
    return response
```

## Testing

Run the simplified test suite with Python's unittest framework:

```
python -m unittest discover llm_integration/tests
```

## Technical Notes

### Synchronous Implementation

The tutoring system was migrated from an asynchronous implementation to a synchronous one for improved stability and simplicity. The `ClaudeTutor` class now provides:

- `tutor_sync()` - A synchronous method for direct use in Flask routes
- Static `get_tutor()` method to retrieve or create a tutor instance for a session

### SSL Certificate Handling

To resolve potential SSL certificate issues with the Anthropic API, the system now automatically configures SSL certificate paths using environment variables:

```python
import os
import certifi

os.environ['SSL_CERT_FILE'] = certifi.where()
os.environ['REQUESTS_CA_BUNDLE'] = certifi.where()
```

### Integration with AI Avatar

This module provides the core AI tutoring capabilities that can be enhanced with an avatar interface for more engaging educational experiences.
