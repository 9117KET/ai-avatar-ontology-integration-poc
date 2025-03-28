# Physics Tutor POC

An ontology-driven AI tutor system with an embodied avatar interface for physics education using Claude 3.

## Overview

This project implements an intelligent tutoring system that combines:

- Domain ontology for structured knowledge representation
- Claude 3 LLM for natural language understanding and generation
- DeepPavlov for dialogue management
- Embodied avatar interface for enhanced engagement

## Current Implementation Status

✓ Completed:

- Basic ontology integration with physics concepts
- Claude 3 API integration for natural dialogue
- Student model with knowledge tracking
- Web API endpoints with avatar interface
- Session management and learning path generation
- Basic avatar framework with expressions and gestures
- Voice synthesis integration

## Code Structure

The codebase is organized into the following main components:

### Backend Components

- `app.py` - Main application entry point and API server (Quart-based)
- `llm_integration/` - Core tutoring system logic
  - `claude_tutor.py` - Integration with Claude API and prompt management
  - `student_model.py` - Student knowledge state tracking and adaptation
  - `example*.py` - Example implementations and test scripts

### Knowledge Management

- `ontology/` - Semantic knowledge representation
  - `schemas/` - OWL ontology definitions for physics domain
  - `data/` - Instances and relationships
  - `tests/` - Ontology validation tests

### Frontend

- `static/` - Web interface
  - `index.html` - Main web interface
  - `js/app.js` - Frontend logic and API communication
  - `css/` - Styling for the web interface

### Data

- `data/` - Persistent storage
  - `students/` - Student model data stored as JSON

## Setup

1. Clone the repository
2. Install dependencies:

   ```bash
   pip install -r requirements.txt
   ```

3. Set up your environment:

   - Copy `.env.example` to `.env`
   - Get your API key from [Anthropic Console](https://console.anthropic.com/)
   - Add your API key to `.env`

4. Run tests:
   ```bash
   pytest llm_integration/test_claude_tutor.py -v
   pytest llm_integration/test_student_model.py -v
   ```

## System Architecture

The system follows a modular architecture:

1. Domain Ontology (Owlready2) - Knowledge representation
2. LLM Integration (Claude 3) - Natural language processing
3. Dialog Manager (DeepPavlov) - Conversation control
4. Avatar Interface - User interaction
5. Student Model - Learning progress tracking

## Usage

### Local Development

```python
import asyncio
from llm_integration.claude_tutor import ClaudeTutor
from avatar.avatar_manager import AvatarManager

async def main():
    # Initialize the avatar manager
    avatar = AvatarManager()

    # Create tutor with avatar integration
    tutor = ClaudeTutor(avatar_manager=avatar)

    # The response will be delivered through the avatar
    response = await tutor.tutor("Can you explain Newton's First Law?")
    print(response)

if __name__ == "__main__":
    asyncio.run(main())
```

### Web API

The system provides a web API with an embodied avatar interface that can be accessed locally or deployed to Vercel. Start the local server:

```bash
python app.py
```

API Endpoints:

- `POST /api/ask` - Ask a question to the tutor (delivered through avatar)
  ```json
  {
    "question": "What is Newton's First Law?",
    "session_id": "student_123",
    "avatar_settings": {
      "expression": "friendly",
      "gesture": "teaching",
      "voice_style": "encouraging"
    }
  }
  ```
- `GET /api/student_model/<session_id>` - Get the current student model
- `GET /api/learning_path/<session_id>/<target>` - Get a learning path to a target concept
- `GET /api/avatar/settings` - Get available avatar customization options
- `POST /api/avatar/customize` - Update avatar settings for a session

### Avatar Interface

The system features an embodied pedagogical avatar that:

- Provides visual representation of the AI tutor
- Uses appropriate gestures and expressions while teaching
- Delivers responses with synchronized speech and animation
- Adapts behavior based on student's emotional state and engagement
- Supports customization of appearance and behavior

Avatar customization options include:

- Visual appearance (character style, clothing, accessories)
- Voice characteristics (tone, pace, accent)
- Behavioral traits (gesture frequency, expression intensity)
- Teaching style (formal/informal, serious/playful)

### Knowledge Retention Features

The system includes several features to enhance knowledge retention:

- Active recall through interactive questioning
- Spaced repetition of concepts
- Progress tracking and knowledge gap identification
- Adaptive difficulty based on student performance
- Pre/post session assessments
- Immediate feedback and corrections

## Project Structure

- `ontology/` - Contains the physics knowledge base
- `llm_integration/` - Claude integration and tutoring logic
  - `claude_tutor.py` - Core tutor implementation with Claude 3
  - `student_model.py` - Student knowledge modeling
  - `example_with_student_model.py` - Demo of adaptive tutoring
- `avatar/` - Avatar integration and management
  - `avatar_manager.py` - Core avatar control system
  - `expressions.py` - Expression and gesture definitions
  - `voice_synthesis.py` - Text-to-speech integration
  - `behavior_controller.py` - Avatar behavior adaptation
- `api/` - Serverless API functions for Vercel deployment
- `static/` - Web interface and avatar assets
  - `models/` - 3D avatar models and animations
  - `textures/` - Avatar textures and materials
  - `audio/` - Voice and sound effects
- `data/` - Directory for storing student model data
- `tests/` - Test suite
- `vercel.json` - Vercel deployment configuration

## Development Progress

See `ROADMAP.md` for detailed implementation phases and future plans.

## Notes

- Ensure you have sufficient API credits in your Anthropic account
- The system uses the Claude 3 Opus model for optimal performance
- All sensitive data (API keys) should be stored in `.env`
- For production deployment, consider implementing rate limiting and authentication
- Session data is stored in memory; for production, use a persistent database
- Avatar assets may require significant storage and CDN setup
- Voice synthesis may require additional API credentials
