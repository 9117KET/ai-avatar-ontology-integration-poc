# Ontology-Enhanced Contextual Reasoning for Large Language Models in STEM Education

A research project investigating the integration of ontology-driven knowledge models with Large Language Models (LLMs) to enhance STEM education through more reliable AI-powered tutoring.

## Research Overview

This project addresses the critical challenge of AI hallucination in educational applications by combining:

- Domain-specific ontologies (OWL, RDF, SPARQL) for structured knowledge representation
- Claude 3 LLM for natural language understanding and generation
- Simplified student model for concept tracking
- Intuitive, accessible chat interface for physics tutoring

## Project Structure

```
.
├── llm_integration/       # LLM integration & simplified student model
│   ├── claude_tutor.py   # Claude AI integration
│   ├── student_model.py  # Simplified student model
│   └── tests/            # Unit tests for components
│
├── ontology/              # Physics ontology schemas & validation
│   └── physics/          # Physics domain ontology files
│
├── static/                # Frontend assets
│   ├── css/              # Styling for the chat interface
│   ├── js/               # Client-side logic
│   └── index.html        # Main application page
│
├── app.py                 # Flask application entry point
├── requirements.txt       # Project dependencies
└── .env                   # Environment variables configuration
```

## System Architecture

- **Backend:** Flask server with robust error handling, JWT session management, and integration with Claude 3 LLM and ontology modules.
- **LLM Integration:** Streamlined tutoring logic focusing on physics content, simplified student model for concept tracking.
- **Ontology:** Physics domain concepts to provide structured knowledge for more accurate responses.
- **Frontend:** Clean, accessible chat interface with support for physics formulas and suggested questions.
- **Security:** Comprehensive security headers, proper CORS configuration, and SSL certificate handling.

## Requirements

- Python 3.9+
- [Anthropic Claude API key](https://console.anthropic.com/)
- See `requirements.txt` for dependencies

## Installation & Setup

1. **Clone the repository**
2. **Install dependencies:**
   ```bash
   pip install -r requirements.txt
   ```
3. **Set up environment variables:**
   Create a `.env` file in the project root with the following variables:
   ```
   # Required configuration
   ANTHROPIC_API_KEY=your_anthropic_api_key_here
   
   # Security settings
   JWT_SECRET=your_secure_random_string
   JWT_ALGORITHM=HS256
   
   # CORS configuration (comma-separated list for multiple origins)
   ALLOWED_ORIGINS=http://localhost:5000,https://yourdomain.com
   
   # Server configuration
   HOST=0.0.0.0
   PORT=5000
   DEBUG=False
   ```

4. **Run the application:**
   ```bash
   python app.py
   ```
   The AI Physics Tutor will be available at http://localhost:5000

## Deployment

### Standard Web Server

1. Set up a Python environment on your server
2. Install dependencies with `pip install -r requirements.txt`
3. Configure environment variables (especially the `ANTHROPIC_API_KEY`)
4. Run with a WSGI server for production:
   ```bash
   # Using a production WSGI server
   python -m waitress --port=5000 app:app
   ```

## Development & Troubleshooting

- **SSL Certificate Issues**: If you encounter SSL connection errors with the Anthropic API, ensure you have the latest SSL certificate package installed:
  ```bash
  pip install --upgrade pip setuptools wheel
  pip install --upgrade requests
  ```

- **Running Tests**: You can run the simplified test suite with:
  ```bash
  pytest llm_integration/tests/
  ```

- **Debug Mode**: Set `DEBUG=True` in your `.env` file for more verbose logging and error messages

## Key Files Overview

### Backend (Python/Flask)
- `app.py` — Flask server with API endpoints and main application logic
- `llm_integration/claude_tutor.py` — Claude AI integration for physics tutoring
- `llm_integration/student_model.py` — Simplified student concept tracking

### Frontend
- `static/index.html` — Main chat interface
- `static/js/app.js` — Client-side logic for chat functionality
- `static/css/style.css` — Styling for the physics tutor interface

### Knowledge Base
- `ontology/physics/` — OWL/RDF ontology files for physics domain knowledge

## Environment Variables
- `ANTHROPIC_API_KEY` — Claude API authentication key
- `JWT_SECRET` — Secret key for JWT token encryption
- `JWT_ALGORITHM` — Algorithm used for JWT (default: HS256)
- `ALLOWED_ORIGINS` — Comma-separated list of allowed origins for CORS
- `HOST`, `PORT` — Server hosting configuration
- `DEBUG` — Enable debug mode for development

## Research Contributions
1. **Reduced Hallucination:** Integrates structured ontology-based domain knowledge to reduce AI inaccuracies
2. **Focused Physics Tutoring:** Specialized responses for physics education
3. **Scalable Chat Interface:** Simple, effective interface for physics learning
4. **Knowledge Verification:** AI responses grounded in physics ontology
5. **Formula and Concept Representation:** Enhanced display of mathematical formulas and physics concepts

## Current Implementation
- Core physics ontology integration
- Claude 3 AI integration with synchronous request handling
- Simplified student model for concept tracking
- Clean chat interface with support for physics formulas
- Enhanced message formatting for physics content
- Suggested questions for better user engagement
- Comprehensive error handling and security measures

## Technical Notes

### Migration from Async to Sync
The application was migrated from Quart (async Flask) to standard Flask for improved stability and simpler maintenance. This involved converting async route handlers to synchronous ones and implementing synchronous wrappers for asynchronous code.

### SSL Certificate Configuration
To resolve SSL certificate issues with the Anthropic client, the application uses SSL certificate management to properly set certificate paths via environment variables.

### Web Server Deployment
For production deployment, we recommend using a WSGI server like Waitress to serve the Flask application for better performance and reliability.

## Research Methodology

The project follows a phased development approach:

1. **Core Functionality**

   - Environment setup and API authentication
   - System prompt structure
   - Basic question-answering functionality
   - Logging and monitoring

2. **Knowledge Representation**

   - Physics concepts, laws, and relationships
   - Prerequisites structures
   - Context retrieval system

3. **Student Model Implementation**
   - Concept exposure tracking
   - Knowledge level monitoring
   - Quiz results and interaction history
   - Learning path generation

## Evaluation Metrics

The system is evaluated based on:

1. **System Performance**

   - Response accuracy
   - Personalization effectiveness
   - System scalability

2. **User Experience**

   - Interaction quality
   - Learning engagement
   - Knowledge retention

3. **Technical Evaluation**
   - API integration
   - Knowledge representation
   - Data management

## Getting Started

1. Clone the repository
2. Install dependencies: `pip install -r requirements.txt`
3. Set up environment variables (see `.env.example`)
4. Run the development server: `python app.py`

## Accessing your app locally
- http://127.0.0.1:5000
- http://localhost:5000

## License

This project is part of a research thesis and is not currently licensed for public use.

## Contact

For research inquiries, please contact the author.
