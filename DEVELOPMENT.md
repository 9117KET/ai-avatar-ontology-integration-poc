# Development Guide

## Project Structure (Updated)

```
.
├── config/                 # Configuration management
│   ├── __init__.py
│   └── settings.py        # Centralized configuration classes
│
├── utils/                  # Utility modules
│   ├── __init__.py
│   ├── ssl_config.py      # SSL certificate configuration
│   └── error_handler.py   # Centralized error handling
│
├── llm_integration/        # LLM integration & student model
│   ├── claude_tutor.py    # Claude AI integration
│   └── student_model.py   # Student concept tracking
│
├── ontology/              # Physics ontology schemas
│   ├── app.py             # Ontology service
│   └── schemas/           # OWL files
│
├── evaluation/            # Evaluation framework
│   ├── models/            # Evaluation models
│   ├── analysis/          # Analysis tools
│   └── utils/             # Evaluation utilities
│
├── static/                # Frontend assets
│   ├── css/               # Styling
│   ├── js/                # Client-side logic
│   └── index.html         # Main application page
│
├── app.py                 # Flask application entry point
└── requirements.txt       # Project dependencies
```

## Code Quality Standards

### Type Hints
All functions should include type hints:
```python
def validate_session_id(session_id: str) -> bool:
    """Validate session ID format and content."""
    return len(session_id) <= 64
```

### Error Handling
Use centralized error handling:
```python
from utils.error_handler import ValidationError, handle_api_error

try:
    # Your code here
    pass
except Exception as e:
    return handle_api_error(e)
```

### Configuration
Use centralized configuration:
```python
from config.settings import load_config

app_config, security_config, api_config = load_config()
```

## Security Best Practices

1. **Environment Variables**: All sensitive data must be in environment variables
2. **Input Validation**: Use centralized validation functions
3. **Error Messages**: Never expose sensitive information in error messages
4. **CORS**: Specify exact allowed origins, avoid wildcards

## Development Workflow

1. **Setup Environment**:
   ```bash
   cp .env.example .env
   # Edit .env with your API keys
   pip install -r requirements.txt
   ```

2. **Run Development Server**:
   ```bash
   python app.py
   ```

3. **Testing**:
   ```bash
   pytest llm_integration/tests/
   ```

4. **Code Quality Checks**:
   ```bash
   # Type checking (if mypy is installed)
   mypy app.py
   
   # Code formatting (if black is installed)
   black .
   ```

## Environment Variables

Required variables:
- `ANTHROPIC_API_KEY`: Claude API key
- `JWT_SECRET`: Secret for JWT token encryption

Optional variables:
- `ALLOWED_ORIGINS`: Comma-separated list of allowed CORS origins
- `RATE_LIMIT`: Requests per minute (default: 100)
- `MAX_TOKENS`: Maximum tokens for API calls (default: 1024)
- `HOST`: Server host (default: 0.0.0.0)
- `PORT`: Server port (default: 5000)
- `DEBUG`: Enable debug mode (default: False)

## Common Tasks

### Adding New API Endpoints
1. Add route handler in `app.py`
2. Use centralized error handling
3. Add appropriate type hints
4. Include comprehensive docstring

### Adding New Configuration
1. Add to appropriate config class in `config/settings.py`
2. Update `load_config()` function
3. Update environment variable documentation

### Adding New Error Types
1. Create custom exception in `utils/error_handler.py`
2. Add handling logic in `handle_api_error()`
3. Update error documentation