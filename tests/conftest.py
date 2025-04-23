"""
Test configuration and shared fixtures for the AI Tutoring System.
"""

import os
import sys
import pytest
from flask import Flask
from dotenv import load_dotenv

# Add project root to path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# Load environment variables for testing
load_dotenv('.env.test', override=True)

# Import application components
from app import app as flask_app
from llm_integration.claude_tutor import ClaudeTutor
from llm_integration.student_model import StudentModel

@pytest.fixture
def app():
    """Create and configure a test Flask application."""
    flask_app.config.update({
        'TESTING': True,
        'DEBUG': True,
        'SERVER_NAME': 'localhost.localdomain'
    })
    return flask_app

@pytest.fixture
def client(app):
    """Create a test client for the Flask application."""
    return app.test_client()

@pytest.fixture
def runner(app):
    """Create a test CLI runner for Flask commands."""
    return app.test_cli_runner()

@pytest.fixture
def mock_tutor():
    """Create a mock tutor instance for testing."""
    class MockTutor(ClaudeTutor):
        async def tutor(self, question):
            return "Mock tutor response"
    
    return MockTutor(student_id="test_student")

@pytest.fixture
def student_model():
    """Create a test student model instance."""
    return StudentModel(student_id="test_student")

@pytest.fixture
def auth_headers():
    """Create authentication headers for protected endpoints."""
    return {
        'Authorization': f'Bearer test_token',
        'Content-Type': 'application/json'
    }

@pytest.fixture(autouse=True)
def setup_test_env():
    """Set up test environment variables."""
    os.environ['TESTING'] = 'true'
    os.environ['ANTHROPIC_API_KEY'] = 'test_key'
    os.environ['JWT_SECRET'] = 'test_secret'
    yield
    # Clean up after tests
    os.environ.pop('TESTING', None) 