"""
Unit tests for the student model component.
"""

import pytest
from llm_integration.student_model import StudentModel

def test_student_model_initialization(student_model):
    """Test student model initialization."""
    assert student_model.student_id == "test_student"
    assert student_model.knowledge_level == 0
    assert len(student_model.exposed_concepts) == 0
    assert len(student_model.understood_concepts) == 0

def test_add_exposed_concept(student_model):
    """Test adding exposed concepts."""
    concept = "Newton's First Law"
    student_model.add_exposed_concept(concept)
    assert concept in student_model.exposed_concepts
    
def test_add_understood_concept(student_model):
    """Test adding understood concepts."""
    concept = "Newton's First Law"
    student_model.add_understood_concept(concept)
    assert concept in student_model.understood_concepts
    assert concept in student_model.exposed_concepts  # Should also be in exposed

def test_get_learning_path(student_model):
    """Test learning path generation."""
    target = "Newton's Second Law"
    prerequisites = {
        "Newton's Second Law": ["Newton's First Law", "Force", "Mass", "Acceleration"],
        "Force": ["Vector Mathematics"],
        "Mass": ["Basic Units"],
        "Acceleration": ["Vector Mathematics", "Basic Units"]
    }
    
    path = student_model.get_learning_path(target, prerequisites)
    assert isinstance(path, list)
    assert target in path
    assert "Newton's First Law" in path
    assert path.index("Vector Mathematics") < path.index("Force")  # Prerequisites come first 