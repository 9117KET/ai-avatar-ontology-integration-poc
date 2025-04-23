"""
End-to-end tests for complete tutoring sessions.
Tests the full flow of student interactions with the tutoring system.
"""

import json
import pytest
from time import sleep

class TestTutoringSession:
    """Test suite for end-to-end tutoring session flows."""
    
    async def test_complete_tutoring_session(self, client, auth_headers):
        """Test a complete tutoring session flow."""
        session_id = "e2e_test_session"
        
        # Step 1: Initial question about Newton's Laws
        initial_response = await client.post(
            '/api/ask',
            data=json.dumps({
                "question": "Can you explain Newton's First Law?",
                "session_id": session_id
            }),
            headers=auth_headers
        )
        assert initial_response.status_code == 200
        initial_data = json.loads(initial_response.data)
        assert "Newton's First Law" in initial_data['student_model']['exposed_concepts']
        
        # Step 2: Check student model after first interaction
        model_response = client.get(
            f'/api/student_model/{session_id}',
            headers=auth_headers
        )
        assert model_response.status_code == 200
        model_data = json.loads(model_response.data)
        assert len(model_data['exposed_concepts']) > 0
        
        # Step 3: Ask follow-up question about inertia
        followup_response = await client.post(
            '/api/ask',
            data=json.dumps({
                "question": "How does inertia relate to Newton's First Law?",
                "session_id": session_id
            }),
            headers=auth_headers
        )
        assert followup_response.status_code == 200
        followup_data = json.loads(followup_response.data)
        assert "inertia" in followup_data['student_model']['exposed_concepts']
        
        # Step 4: Get learning path to advanced concept
        path_response = client.get(
            f'/api/learning_path/{session_id}/Newton\'s Second Law',
            headers=auth_headers
        )
        assert path_response.status_code == 200
        path_data = json.loads(path_response.data)
        assert isinstance(path_data['learning_path'], list)
        assert "Newton's First Law" in path_data['learning_path']
    
    async def test_error_recovery(self, client, auth_headers):
        """Test system's ability to handle errors and recover."""
        session_id = "e2e_error_test"
        
        # Step 1: Send malformed request
        error_response = await client.post(
            '/api/ask',
            data="malformed json{",
            headers=auth_headers
        )
        assert error_response.status_code in [400, 422]  # Bad request or Unprocessable Entity
        
        # Step 2: Verify system can still process valid requests
        recovery_response = await client.post(
            '/api/ask',
            data=json.dumps({
                "question": "What is force?",
                "session_id": session_id
            }),
            headers=auth_headers
        )
        assert recovery_response.status_code == 200
        
    async def test_session_persistence(self, client, auth_headers):
        """Test that session data persists across multiple requests."""
        session_id = "e2e_persistence_test"
        
        # Step 1: Initial interaction
        await client.post(
            '/api/ask',
            data=json.dumps({
                "question": "What is momentum?",
                "session_id": session_id
            }),
            headers=auth_headers
        )
        
        # Step 2: Verify data persists after delay
        sleep(1)  # Small delay to simulate time passing
        
        model_response = client.get(
            f'/api/student_model/{session_id}',
            headers=auth_headers
        )
        model_data = json.loads(model_response.data)
        assert "momentum" in model_data['exposed_concepts'] 