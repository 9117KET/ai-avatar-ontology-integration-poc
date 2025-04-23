"""
Integration tests for API endpoints.
Tests the interaction between components through the API layer.
"""

import json
import pytest
from flask import url_for

async def test_ask_endpoint(client, auth_headers, mock_tutor):
    """Test the /api/ask endpoint with a mock tutor."""
    data = {
        "question": "What is Newton's First Law?",
        "session_id": "test_session"
    }
    
    response = await client.post(
        '/api/ask',
        data=json.dumps(data),
        headers=auth_headers
    )
    
    assert response.status_code == 200
    result = json.loads(response.data)
    assert 'response' in result
    assert 'student_model' in result
    assert isinstance(result['student_model'], dict)

def test_student_model_endpoint(client, auth_headers, student_model):
    """Test the /api/student_model endpoint."""
    session_id = "test_session"
    response = client.get(
        f'/api/student_model/{session_id}',
        headers=auth_headers
    )
    
    assert response.status_code == 200
    result = json.loads(response.data)
    assert 'exposed_concepts' in result
    assert 'understood_concepts' in result
    assert 'knowledge_level' in result
    assert isinstance(result['exposed_concepts'], list)

def test_learning_path_endpoint(client, auth_headers, student_model):
    """Test the /api/learning_path endpoint."""
    session_id = "test_session"
    target_concept = "Newton's Second Law"
    
    response = client.get(
        f'/api/learning_path/{session_id}/{target_concept}',
        headers=auth_headers
    )
    
    assert response.status_code == 200
    result = json.loads(response.data)
    assert 'learning_path' in result
    assert isinstance(result['learning_path'], list)
    assert target_concept in result['learning_path']

def test_unauthorized_access(client):
    """Test endpoints without proper authentication."""
    endpoints = [
        '/api/ask',
        '/api/student_model/test_session',
        '/api/learning_path/test_session/concept'
    ]
    
    for endpoint in endpoints:
        response = client.get(endpoint)
        assert response.status_code in [401, 403]  # Unauthorized or Forbidden 