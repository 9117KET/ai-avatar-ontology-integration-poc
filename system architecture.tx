┌─────────────────────────────────────────────────────────────────────────┐
│                            CLIENT BROWSER                               │
│  ┌─────────────┐        ┌────────────────┐       ┌──────────────────┐  │
│  │ HTML/CSS    │        │ JavaScript     │       │ Avatar Renderer  │  │
│  │ (Bootstrap) │◄─────► │ (app.js)       │◄────► │ (3D Models/      │  │
│  └─────────────┘        └────────────────┘       │  Animations)     │  │
│                                │                  └──────────────────┘  │
└────────────────────────────────┼──────────────────────────────────────┘
                                  │ HTTP/AJAX
                                  ▼
┌─────────────────────────────────────────────────────────────────────────┐
│                             BACKEND SERVER                               │
│  ┌─────────────┐        ┌────────────────┐       ┌──────────────────┐  │
│  │ Quart Web   │        │ API Endpoints  │       │ Session Manager  │  │
│  │ Server      │◄─────► │ (/api/ask      │◄────► │ (tutor_instances)│  │
│  └─────────────┘        │  /api/student..)       └──────────────────┘  │
│                         └────────┬───────┘                              │
└─────────────────────────────────┼───────────────────────────────────────┘
                                  │
                                  ▼
┌─────────────────────────────────────────────────────────────────────────┐
│                        TUTORING SYSTEM CORE                              │
│                                                                          │
│  ┌─────────────────────┐      ┌─────────────────────────────────────┐   │
│  │  Claude Tutor       │      │         Student Model               │   │
│  │  ┌─────────────┐    │      │  ┌───────────────┐ ┌─────────────┐  │   │
│  │  │ Prompt      │    │      │  │ Knowledge     │ │ Interaction │  │   │
│  │  │ Management  │    │      │  │ Tracking      │ │ History     │  │   │
│  │  └─────────────┘    │◄────►│  └───────────────┘ └─────────────┘  │   │
│  │  ┌─────────────┐    │      │  ┌───────────────┐ ┌─────────────┐  │   │
│  │  │ Claude API  │    │      │  │ Misconception │ │ Learning    │  │   │
│  │  │ Integration │    │      │  │ Detection     │ │ Path Gen    │  │   │
│  │  └─────────────┘    │      │  └───────────────┘ └─────────────┘  │   │
│  └─────────────────────┘      └─────────────────────────────────────┘   │
│                │                               │                         │
│                │                               │                         │
│                ▼                               ▼                         │
│  ┌───────────────────────────────────────────────────────────────┐      │
│  │                   Domain Knowledge                             │      │
│  │  ┌─────────────────────┐      ┌─────────────────────────┐     │      │
│  │  │  Ontology (OWL)     │      │ Physics Knowledge Base  │     │      │
│  │  │  ┌─────────────┐    │      │ ┌─────────────────────┐ │     │      │
│  │  │  │ Concepts    │    │      │ │ Laws & Definitions  │ │     │      │
│  │  │  └─────────────┘    │      │ └─────────────────────┘ │     │      │
│  │  │  ┌─────────────┐    │◄────►│ ┌─────────────────────┐ │     │      │
│  │  │  │ Relationships│    │      │ │ Examples           │ │     │      │
│  │  │  └─────────────┘    │      │ └─────────────────────┘ │     │      │
│  │  │  ┌─────────────┐    │      │ ┌─────────────────────┐ │     │      │
│  │  │  │ Prerequisites│    │      │ │ Applications       │ │     │      │
│  │  │  └─────────────┘    │      │ └─────────────────────┘ │     │      │
│  │  └─────────────────────┘      └─────────────────────────┘     │      │
│  └───────────────────────────────────────────────────────────────┘      │
│                                                                          │
└─────────────────────────────────────────────────────────────────────────┘
                                  │
                                  ▼
┌─────────────────────────────────────────────────────────────────────────┐
│                        PERSISTENT STORAGE                                │
│  ┌─────────────────────┐      ┌─────────────────────────────────────┐   │
│  │  Student Data       │      │         Session Data                │   │
│  │  (JSON)             │      │         (In-memory)                 │   │
│  └─────────────────────┘      └─────────────────────────────────────┘   │
└─────────────────────────────────────────────────────────────────────────┘


# Data Flow Description

## 1. User Interaction Flow
- Student enters a question in the frontend interface
- JavaScript handles the input and sends an AJAX request to the backend API 
- The response is displayed in the chat interface and updates the student model visualization

## 2. Backend Processing Flow
- Quart server receives the API request at /api/ask
- Request is routed to the appropriate session instance via get_tutor(session_id)
- The tutor instance processes the question and returns a response
- The API formats and returns the response with the updated student model data

## 3. Tutoring System Flow 
- ClaudeTutor analyzes the question using _get_relevant_context()
- Retrieves concepts and knowledge from the ontology
- Adapts the context based on student's knowledge level using _adapt_context_to_student()
- Constructs a prompt for Claude API with system instructions and context
- Sends the prompt to Claude 3 and receives the response
- Updates the student model with add_interaction()

## 4. Knowledge Graph Flow
- Ontology provides structured knowledge about physics concepts
- ClaudeTutor retrieves prerequisite relationships, definitions, examples, and applications
- This knowledge is used to provide accurate responses and track learning progress

## 5. Student Model Flow
- Records concepts the student has been exposed to
- Tracks understanding levels for different concepts 
- Identifies knowledge gaps and misconceptions
- Generates personalized learning paths based on the concept prerequisite graph
- Persists student data between sessions using JSON storage

## 6. API Response Flow
- The tutor response is returned to the frontend
- Student model data is included for UI updates
- Frontend visualizes the student's knowledge state
- Knowledge levels are represented with progress bars of different colors

## 7. Storage Flow
- Student model data is persisted to JSON files in the data/students/ directory
- Session data is maintained in memory through the tutor_instances dictionary

## 8. Technology Stack Integration
| Component | Technology |
|-----------|------------|
| Frontend | HTML/CSS/JavaScript with Bootstrap for responsive design |
| Backend | Quart (async Python web framework) for API endpoints |
| NLP | Claude 3 API (via Anthropic client) for intelligent tutoring |
| Knowledge Representation | Owlready2 for ontology parsing and reasoning |
| Data Storage | File-based JSON storage for student models |
| Session Management | In-memory dictionary for maintaining session state |