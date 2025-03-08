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

## Project Structure

- `ontology/` - Contains the physics knowledge base
- `llm_integration/` - Claude integration and tutoring logic
- `tests/` - Test suite

## Notes

- Ensure you have sufficient API credits in your Anthropic account
- The system uses the Claude 3 Opus model for optimal performance
- All sensitive data (API keys) should be stored in `.env`
