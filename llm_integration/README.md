# LLM Integration for Physics Tutor

This module handles the integration between the physics knowledge ontology and the Claude 3 LLM to create an adaptive tutoring experience.

## Components

### ClaudeTutor

The `ClaudeTutor` class is the main component that:

- Loads the physics ontology
- Communicates with Claude 3 through the Anthropic API
- Extracts relevant context based on student questions
- Adapts responses based on the student's knowledge level

### StudentModel

The `StudentModel` class tracks a student's knowledge state and learning progress over time. It maintains:

- **Exposed Concepts**: Topics the student has encountered during tutoring sessions
- **Understood Concepts**: Concepts the student has demonstrated understanding of
- **Knowledge Levels**: Numerical scores (0.0-1.0) representing mastery level for each concept
- **Misconceptions**: Specific misunderstandings the student has shown about concepts
- **Interaction History**: Record of all questions and responses
- **Quiz Results**: Results of assessments to gauge understanding

The student model is used to adapt tutoring in several ways:

1. **Personalized Context**: The tutor enhances responses with information about which concepts the student already knows and which need review
2. **Knowledge Gap Identification**: Highlights areas that require reinforcement
3. **Prerequisite Tracking**: Ensures new concepts are introduced only when prerequisites are understood
4. **Learning Path Generation**: Creates customized learning sequences to reach target concepts

## Usage

### Basic Tutoring

```python
import asyncio
from claude_tutor import ClaudeTutor

async def main():
    # Create a tutor for a specific student
    tutor = ClaudeTutor(student_id="student_123")

    # Ask a question
    response = await tutor.tutor("Can you explain Newton's First Law?")
    print(response)

if __name__ == "__main__":
    asyncio.run(main())
```

### Advanced Usage with Student Model

```python
import asyncio
from claude_tutor import ClaudeTutor

async def main():
    # Create a tutor for a specific student
    tutor = ClaudeTutor(student_id="student_123")

    # Get a physics explanation
    response = await tutor.tutor("Can you explain Newton's First Law?")
    print(response)

    # Record quiz results to update the student model
    tutor.student_model.update_quiz_result(
        concept="NewtonsFirstLaw",
        correct=True,
        confidence=0.8
    )

    # Record a misconception if detected
    tutor.student_model.record_misconception(
        concept="Acceleration",
        misconception="Confuses acceleration with velocity"
    )

    # Get learning recommendations
    knowledge_gaps = tutor.student_model.get_knowledge_gaps()
    ready_concepts = tutor.student_model.get_ready_concepts(tutor.concept_prerequisites)

    # Generate a personalized learning path
    learning_path = tutor.student_model.get_learning_path(
        target_concept="NewtonsThirdLaw",
        concept_graph=tutor.concept_prerequisites
    )

if __name__ == "__main__":
    asyncio.run(main())
```

## Testing

Run the tests with pytest:

```
python -m pytest llm_integration/test_claude_tutor.py -v
python -m pytest llm_integration/test_student_model.py -v
python -m pytest llm_integration/test_claude_student_integration.py -v
```

## Example

To see a full demonstration of the adaptive tutoring functionality, run:

```
python llm_integration/example_with_student_model.py
```

This example simulates a tutoring session where the student's knowledge is tracked and the tutor adapts its responses accordingly.
