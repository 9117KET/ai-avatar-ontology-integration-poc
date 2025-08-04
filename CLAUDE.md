# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

This is an ontology-enhanced AI Physics Tutor research project that combines structured physics knowledge (OWL ontology) with Claude 3 LLM to reduce hallucinations in educational AI systems. The system provides personalized physics tutoring through a clean chat interface with statistically proven 67% reduction in AI hallucinations.

## Development Commands

### Running the Application
```bash
python app.py
```

### Testing
```bash
# Run all tests
pytest

# Run specific test categories
pytest -m unit           # Unit tests only
pytest -m integration    # Integration tests only
pytest -m api            # API tests only

# Run with coverage
pytest --cov=. --cov-report=html
```

### Code Quality
```bash
# Format code
black .

# Lint code
flake8 .

# Type checking
mypy app.py llm_integration/ utils/ config/
```

### Evaluation Framework
```bash
# Run hallucination evaluation
python -m evaluation

# Run specific evaluation components
python evaluation/run_evaluation.py
```

## Architecture Overview

**Core Architecture Pattern**: The system follows a modular Flask-based architecture with clear separation of concerns:

- **Flask Application (`app.py`)**: Main server with JWT-based session management, CORS configuration, and comprehensive security headers
- **LLM Integration Layer (`llm_integration/`)**: Claude 3 AI integration with ontology-enhanced context and simplified student model for concept tracking  
- **Physics Ontology (`ontology/`)**: OWL/RDF knowledge representation providing structured physics domain knowledge
- **Configuration Management (`config/settings.py`)**: Centralized configuration using dataclasses with environment variable validation
- **Evaluation Framework (`evaluation/`)**: Statistical framework for measuring hallucination reduction with FCI (Force Concept Inventory) questions

**Key Integration Points**:
- Claude AI + Ontology: Physics concepts are validated against structured knowledge to reduce hallucinations
- Student Model + Tutoring: Simplified concept exposure tracking without complex learning analytics
- Security + Session Management: JWT tokens with rate limiting for stateless operation

## Key Implementation Details

### Configuration System
The application uses a centralized configuration system in `config/settings.py` with dataclasses for type safety:
- `SecurityConfig`: JWT, CORS, rate limiting
- `APIConfig`: Anthropic API key, token limits
- `AppConfig`: Flask settings, logging

### Error Handling
Centralized error handling through `utils/error_handler.py` with custom exceptions and consistent API responses.

### SSL Configuration
Custom SSL certificate configuration in `utils/ssl_config.py` to handle Anthropic API connectivity issues.

### Ontology Integration
Physics knowledge is represented using OWL ontology with owlready2 library for concept retrieval and validation.

## Environment Variables Required

**CRITICAL: The application will not function without these environment variables set:**

```env
# Required - Application will fail without these
ANTHROPIC_API_KEY=your_anthropic_api_key_here  # Must start with "sk-ant-"
JWT_SECRET=your_secure_random_string_here      # For session management

# Optional with defaults
ALLOWED_ORIGINS=http://localhost:5000,http://127.0.0.1:5000
RATE_LIMIT=100
RATE_LIMIT_WINDOW=60
HOST=0.0.0.0
PORT=5000
DEBUG=False

# Optional - Ontology path override
ONTOLOGY_PATH=/path/to/custom/physics_tutor.owl
```

**Note**: If ANTHROPIC_API_KEY is not set, you'll get a 500 Internal Server Error when trying to ask questions.

## Testing Strategy

The project uses pytest with markers for test categorization:
- **unit**: Component-level tests
- **integration**: Cross-component tests  
- **api**: API endpoint tests
- **model**: Student model tests
- **tutor**: Tutoring system tests

Test configuration in `pytest.ini` includes coverage reporting and environment setup for testing.

## Code Standards

### Type Hints
All functions should include comprehensive type hints:
```python
def validate_session_id(session_id: str) -> bool:
    """Validate session ID format and content."""
    return len(session_id) <= 64
```

### Error Handling Pattern
Use centralized error handling:
```python
from utils.error_handler import ValidationError, handle_api_error

try:
    # Your code here
    pass
except Exception as e:
    return handle_api_error(e)
```

### Configuration Access
Use centralized configuration loading:
```python
from config.settings import load_config

app_config, security_config, api_config = load_config()
```

## Security Considerations

- All sensitive data must be in environment variables
- JWT-based stateless session management for serverless compatibility
- Comprehensive security headers (CSP, X-Frame-Options, etc.)
- Input validation using centralized validation functions
- Rate limiting to prevent API abuse
- CORS with explicit allowed origins (no wildcards)

## Deployment

The application supports both traditional WSGI deployment and serverless deployment on Vercel:
- **Traditional**: Use `python app.py` or WSGI server like waitress
- **Serverless**: Vercel deployment with `api/index.py` as the handler

## Research Context

This is a thesis research project measuring the effectiveness of ontology-enhanced LLMs in reducing educational AI hallucinations. The evaluation framework provides statistical validation of the approach using physics education questions from the Force Concept Inventory (FCI).