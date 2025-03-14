# Physics Tutor POC

An ontology-driven AI tutor system for physics education using Claude 3.

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

## Usage

```python
import asyncio
from llm_integration.claude_tutor import ClaudeTutor

async def main():
    tutor = ClaudeTutor()
    response = await tutor.tutor("Can you explain Newton's First Law?")
    print(response)

if __name__ == "__main__":
    asyncio.run(main())
```

## Features

- Ontology-based knowledge representation
- Context-aware responses
- Prerequisite tracking
- Real-world examples and applications
- Integration with Claude 3 for natural language understanding
- Student model for personalized learning experiences

## Student Model

The Physics Tutor includes a student modeling system that:

- Tracks student knowledge state and learning progress
- Maintains a record of concepts the student has been exposed to
- Models the student's understanding level for each concept (0.0-1.0)
- Identifies knowledge gaps and misconceptions
- Generates personalized learning paths
- Adapts tutoring responses based on the student's knowledge

Example with the student model:

```python
import asyncio
from llm_integration.claude_tutor import ClaudeTutor

async def main():
    # Create a tutor for a specific student
    tutor = ClaudeTutor(student_id="student_123")

    # Get a response tailored to this student's knowledge
    response = await tutor.tutor("How does Newton's Second Law work?")
    print(response)

    # The student model is automatically updated with this interaction
    # and will influence future responses

if __name__ == "__main__":
    asyncio.run(main())
```

For a complete demonstration of the adaptive tutoring system, run:

```bash
python llm_integration/example_with_student_model.py
```

## Project Structure

- `ontology/` - Contains the physics knowledge base
- `llm_integration/` - Claude integration and tutoring logic
  - `claude_tutor.py` - Core tutor implementation with Claude 3
  - `student_model.py` - Student knowledge modeling
  - `example_with_student_model.py` - Demo of adaptive tutoring
- `data/` - Directory for storing student model data
- `tests/` - Test suite

## Notes

- Ensure you have sufficient API credits in your Anthropic account
- The system uses the Claude 3 Opus model for optimal performance
- All sensitive data (API keys) should be stored in `.env`
