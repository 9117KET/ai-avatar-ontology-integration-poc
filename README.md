# Ontology-Enhanced Contextual Reasoning for Large Language Models in STEM Education

A research project investigating the integration of ontology-driven knowledge models with Large Language Models (LLMs) to enhance STEM education through more reliable AI-powered tutoring.

## Research Overview

This project addresses the critical challenge of AI hallucination in educational applications by combining:

- **Domain-specific ontologies** (OWL, RDF, SPARQL) for structured knowledge representation
- **Claude 3 LLM** for natural language understanding and generation
- **Simplified student model** for concept tracking and personalized learning
- **Intuitive chat interface** for accessible physics tutoring
- **Comprehensive evaluation framework** to measure hallucination reduction

## Key Research Contributions

1. **67% Reduction in Hallucinations**: Demonstrated significant improvement in factual accuracy
2. **Ontology-Grounded Responses**: AI responses validated against structured physics knowledge
3. **Adaptive Learning System**: Personalized tutoring based on student knowledge state
4. **Statistical Validation**: Rigorous evaluation with Cohen's d = 0.77 effect size

## Project Structure

```
.
├── config/                # Configuration management
│   └── settings.py       # Centralized app, security, and API settings
│
├── utils/                 # Utility modules
│   ├── ssl_config.py     # SSL certificate configuration
│   └── error_handler.py  # Centralized error handling
│
├── llm_integration/       # LLM integration & student model
│   ├── claude_tutor.py   # Claude AI integration with ontology
│   ├── student_model.py  # Simplified student progress tracking
│   └── README.md         # LLM integration documentation
│
├── ontology/              # Physics ontology schemas & validation
│   ├── app.py            # Ontology service
│   └── schemas/          # OWL files for physics domain knowledge
│
├── evaluation/            # Evaluation framework for hallucination analysis
│   ├── models/           # Evaluation models and API clients
│   ├── analysis/         # Statistical analysis and visualization
│   ├── utils/            # Text processing and logging utilities
│   └── results_final/    # Final evaluation results and analysis
│
├── static/                # Frontend assets
│   ├── css/              # Styling for the chat interface
│   ├── js/               # Client-side logic for chat functionality
│   └── index.html        # Main application page
│
├── api/                   # API implementation (serverless deployment)
│   └── index.py          # Vercel serverless handler
│
├── app.py                 # Flask application entry point
├── requirements.txt       # Production dependencies
├── dev-requirements.txt   # Development and testing dependencies
├── pytest.ini           # Test configuration
└── vercel.json           # Serverless deployment configuration
```

## System Architecture

- **Backend:** Flask server with robust error handling, JWT session management, and integration with Claude 3 LLM and ontology modules
- **LLM Integration:** Streamlined tutoring logic focusing on physics content with ontology-enhanced context
- **Ontology:** Physics domain concepts providing structured knowledge for accurate, validated responses
- **Student Model:** Simplified tracking of concept exposure and learning progress
- **Frontend:** Clean, accessible chat interface with support for physics formulas and interactive learning
- **Security:** Comprehensive security headers, proper CORS configuration, and SSL certificate handling
- **Evaluation:** Statistical framework for measuring hallucination reduction and system effectiveness

## Requirements

- Python 3.9+
- [Anthropic Claude API key](https://console.anthropic.com/)
- See `requirements.txt` for dependencies

## Installation & Setup

### Prerequisites
- Python 3.9+
- [Anthropic Claude API key](https://console.anthropic.com/)

### Quick Start
1. **Clone the repository**
   ```bash
   git clone <repository-url>
   cd poc
   ```

2. **Install dependencies:**
   ```bash
   # Production dependencies
   pip install -r requirements.txt
   
   # For development and testing
   pip install -r dev-requirements.txt
   ```

3. **Set up environment variables:**
   Create a `.env` file in the project root:
   ```env
   # Required configuration
   ANTHROPIC_API_KEY=your_anthropic_api_key_here
   
   # Security settings
   JWT_SECRET=your_secure_random_string_here
   JWT_ALGORITHM=HS256
   
   # CORS configuration
   ALLOWED_ORIGINS=http://localhost:5000,http://127.0.0.1:5000
   
   # Server configuration
   HOST=0.0.0.0
   PORT=5000
   DEBUG=False
   
   # Optional: Rate limiting
   RATE_LIMIT=100
   RATE_LIMIT_WINDOW=60
   ```

4. **Run the application:**
   ```bash
   python app.py
   ```
   
   The AI Physics Tutor will be available at:
   - http://localhost:5000
   - http://127.0.0.1:5000

## Testing & Development

### Running Tests
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

### Development Mode
Set `DEBUG=True` in your `.env` file for:
- Verbose logging and error messages
- Hot reloading during development
- Enhanced debugging information

## Deployment

### Local/Standard Web Server
1. Set up a Python environment on your server
2. Install dependencies: `pip install -r requirements.txt`
3. Configure environment variables
4. Run with a WSGI server for production:
   ```bash
   python -m waitress --port=5000 app:app
   ```

### Vercel (Serverless)
1. Install Vercel CLI: `npm install -g vercel`
2. Deploy: `vercel`
3. Configure environment variables in Vercel dashboard

## Troubleshooting

### SSL Certificate Issues
If you encounter SSL connection errors with the Anthropic API:
```bash
pip install --upgrade pip setuptools wheel
pip install --upgrade requests certifi
```

### API Authentication
- Ensure your `ANTHROPIC_API_KEY` starts with `sk-ant-`
- Check API key permissions in the Anthropic console
- Verify the key hasn't expired

### Rate Limiting
- Default: 100 requests per 60 seconds
- Adjust `RATE_LIMIT` and `RATE_LIMIT_WINDOW` in `.env`
- Monitor usage in application logs

## Key Components

### Core Application
- **`app.py`** — Flask server with API endpoints, security, and session management
- **`config/settings.py`** — Centralized configuration management with validation
- **`utils/error_handler.py`** — Comprehensive error handling and custom exceptions
- **`utils/ssl_config.py`** — SSL certificate configuration for API calls

### LLM Integration
- **`llm_integration/claude_tutor.py`** — Ontology-enhanced Claude AI integration
- **`llm_integration/student_model.py`** — Student progress tracking and concept exposure

### Knowledge Base
- **`ontology/schemas/physics_tutor.owl`** — OWL ontology with physics concepts, laws, and relationships
- **`ontology/app.py`** — Ontology service for knowledge retrieval and validation

### Evaluation Framework
- **`evaluation/models/hallucination_evaluator.py`** — Core evaluation engine
- **`evaluation/analysis/`** — Statistical analysis and visualization tools
- **`evaluation/results_final/`** — Final research results and analysis

### Frontend
- **`static/index.html`** — Main chat interface with physics formula support
- **`static/js/app.js`** — Client-side logic for interactive tutoring
- **`static/css/style.css`** — Modern, accessible styling

## Research Methodology & Results

### Evaluation Framework
The system was evaluated using the Force Concept Inventory (FCI) with:
- **Baseline Model**: Standard Claude-3-Opus responses
- **Enhanced Model**: Ontology-grounded responses with structured knowledge
- **Hybrid Detection**: Keyword matching + expert verification for hallucination detection

### Key Findings
- **67% Hallucination Reduction**: From 60% (baseline) to 20% (enhanced)
- **Statistical Significance**: p < 0.05 with Cohen's d = 0.77 (medium-large effect)
- **Trade-off Analysis**: Reduced hallucinations with maintained educational effectiveness
- **Validation**: Expert verification confirms improvement in factual accuracy

### Technical Achievements
- **Synchronous Architecture**: Migrated from async to sync for improved stability
- **Comprehensive Security**: JWT authentication, CORS configuration, input validation
- **Error Resilience**: Centralized error handling with graceful fallbacks
- **SSL Compatibility**: Automated certificate configuration for API reliability

## Documentation
- **[Development Guide](DEVELOPMENT.md)** — Code standards, workflow, and best practices
- **[LLM Integration](llm_integration/README.md)** — Detailed integration documentation
- **[Evaluation Details](evaluation/eval_README.md)** — Complete evaluation methodology and results
- **[Changelog](CHANGELOG.md)** — Version history and improvements

## License

This project is part of a research thesis investigating ontology-enhanced contextual reasoning for educational AI systems.

## Citation

If you use this work in your research, please cite:
```
[Author]. "Ontology-Enhanced Contextual Reasoning for Large Language Models in STEM Education." 
[Institution], 2025. Research Thesis.
```

## Contact

For research inquiries, collaboration opportunities, or technical questions, please contact the project maintainer.
