
# Ontology-Enhanced Contextual Reasoning for Large Language Models in STEM Education

A research project investigating the integration of ontology-driven knowledge models with Large Language Models (LLMs) to enhance STEM education through more reliable AI-powered tutoring.

## Research Overview

This project addresses the critical challenge of AI hallucination in educational applications by combining:

- Domain-specific ontologies (OWL, RDF, SPARQL) for structured knowledge representation
- Claude 3 LLM for natural language understanding and generation
- Student modeling for personalized learning experiences
- Avatar-based interface for enhanced engagement

## Project Structure

```
.
├── api/                    # API implementation
│   ├── routes/            # Route definitions and handlers
│   ├── utils/             # Utility functions
│   ├── index.py           # Main API application
│   └── vercel.py          # Vercel serverless handler
│
├── docs/                  # Documentation (abstract, roadmap, UML, system design)
├── llm_integration/       # LLM integration & student model ([see README](llm_integration/README.md))
├── ontology/              # Physics ontology schemas & validation
├── static/                # Frontend assets (HTML, CSS, JS)
├── app.py                 # Main application entry point
├── requirements.txt       # Production dependencies
├── dev-requirements.txt   # Development dependencies
└── tests/                 # Test suite
```

## System Architecture

- **Backend:** Quart (async Flask-compatible) server, modular API endpoints, JWT session management, integration with Claude 3 LLM and ontology modules.
- **LLM Integration:** Adaptive tutoring logic, student model, context-aware answers ([see llm_integration/README.md](llm_integration/README.md)).
- **Ontology:** Physics domain concepts, prerequisites, validation tests.
- **Frontend:** Avatar-based web UI for interactive tutoring.
- **Documentation:** Full docs and system architecture in `docs/`.

## Requirements

- Python 3.9+
- [Anthropic Claude API key](https://console.anthropic.com/)
- See `requirements.txt` and `dev-requirements.txt` for dependencies

## Installation & Setup

1. **Clone the repository**
2. **Install dependencies:**
   ```bash
   pip install -r requirements.txt
   # For development and testing
   pip install -r dev-requirements.txt
   ```
3. **Set up environment variables:**
   ```bash
   cp .env.example .env
   # Edit .env and provide:
   # - ANTHROPIC_API_KEY
   # - JWT_SECRET
   # - ALLOWED_ORIGINS
   # (see .env.example for all options)
   ```
4. **Run the development server:**
   ```bash
   python app.py
   ```
   The app will be available at http://localhost:5000

## Deployment

### Vercel (Serverless)
1. Install Vercel CLI:
   ```bash
   npm install -g vercel
   ```
2. Deploy:
   ```bash
   vercel
   ```
   See `vercel.json` for configuration.

## Testing & Development
- Run all tests:
  ```bash
  pytest
  ```
- Format code:
  ```bash
  black .
  ```
- Lint code:
  ```bash
  flake8 .
  ```
- Type checking:
  ```bash
  mypy .
  ```

## Key Directories & Files
- `api/` — Backend API implementation
- `llm_integration/` — LLM and student model logic ([see README](llm_integration/README.md))
- `ontology/` — OWL schemas and validation
- `static/` — Frontend assets
- `tests/` — Test suite
- `.env.example` — Example environment config
- `requirements.txt` — Main dependencies
- `dev-requirements.txt` — Dev/test dependencies

## Environment Variables
- `ANTHROPIC_API_KEY` — Claude API authentication
- `JWT_SECRET` — Session security
- `ALLOWED_ORIGINS` — CORS configuration
- `HOST`, `PORT`, `DEBUG` — Server config
- See `.env.example` for all options

## Research Contributions
1. **Reduced Hallucination:** Integrates structured domain knowledge to reduce AI inaccuracies
2. **Personalized Tutoring:** Adaptive responses based on student model
3. **Scalable:** One-on-one tutoring at scale
4. **Interactive:** Avatar-based interface for engagement
5. **Knowledge Verification:** AI responses validated against ontology

## Implementation Status
- Core ontology integration and validation
- Claude 3 API integration
- Student model with learning path generation
- API endpoints and avatar interface
- Session management and interaction history
- Voice synthesis integration

## Getting Started (Quick Reference)
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
   - Examples and real-world applications
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
