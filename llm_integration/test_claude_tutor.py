import pytest
import os
from dotenv import load_dotenv
from claude_tutor import ClaudeTutor
from anthropic import BadRequestError

@pytest.fixture
def tutor():
    """Create a ClaudeTutor instance for testing."""
    load_dotenv()
    return ClaudeTutor()

def test_initialization(tutor):
    """Test that the tutor initializes correctly."""
    assert tutor.api_key is not None
    assert tutor.onto is not None
    assert tutor.system_prompt is not None

def test_get_prerequisites(tutor):
    """Test getting prerequisites for Newton's Laws."""
    # Test Newton's Third Law prerequisites
    prereqs = tutor.get_prerequisites("NewtonsThirdLaw")
    assert "Force" in prereqs
    assert "NewtonsFirstLaw" in prereqs
    assert "NewtonsSecondLaw" in prereqs

def test_get_examples(tutor):
    """Test getting examples for Newton's Laws."""
    # Test Newton's First Law examples
    examples = tutor.get_examples("NewtonsFirstLaw")
    assert len(examples) > 0
    assert "book lying on a table" in examples[0].lower()

def test_get_applications(tutor):
    """Test getting applications for physical quantities."""
    # Test Force applications
    applications = tutor.get_applications("Force")
    assert len(applications) > 0
    assert "rocket propulsion" in applications[0].lower()

def test_system_prompt_creation(tutor):
    """Test that the system prompt contains necessary information."""
    prompt = tutor.system_prompt
    assert "Topics:" in prompt
    assert "Key Laws:" in prompt
    assert "Newton's First Law" in prompt
    assert "Newton's Second Law" in prompt
    assert "Newton's Third Law" in prompt

def test_relevant_context(tutor):
    """Test getting relevant context from questions."""
    # Test with a question about Newton's First Law
    context = tutor._get_relevant_context("Can you explain Newton's First Law?")
    assert "NewtonsFirstLaw" in context
    assert "Law of Inertia" in context

@pytest.mark.asyncio
async def test_tutor_response(tutor):
    """Test getting a response from the tutor."""
    question = "What is Newton's First Law?"
    try:
        response = await tutor.tutor(question)
        assert response is not None
        assert len(response) > 0
        assert "inertia" in response.lower()
    except BadRequestError as e:
        if "credit balance is too low" in str(e):
            pytest.skip("Skipping API test due to insufficient credits")
        else:
            raise 