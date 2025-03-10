import os
import shutil
import pytest
from datetime import datetime
from student_model import StudentModel

@pytest.fixture
def temp_data_dir(tmp_path):
    """Create a temporary directory for student data."""
    test_data_dir = tmp_path / "test_student_data"
    test_data_dir.mkdir()
    yield str(test_data_dir)
    # Clean up
    if test_data_dir.exists():
        shutil.rmtree(str(test_data_dir))

@pytest.fixture
def student_model(temp_data_dir):
    """Create a StudentModel instance for testing."""
    return StudentModel("test_student", data_path=temp_data_dir)

def test_initialization(student_model):
    """Test that the student model initializes correctly."""
    assert student_model.student_id == "test_student"
    assert student_model.exposed_concepts == set()
    assert student_model.understood_concepts == set()
    assert student_model.quiz_results == []
    assert student_model.interaction_history == []
    assert student_model.knowledge_level == {}

def test_add_interaction(student_model):
    """Test adding an interaction to the student model."""
    # Add an interaction
    student_model.add_interaction(
        question="What is Newton's First Law?",
        response="Newton's First Law states that an object at rest stays at rest...",
        concepts=["NewtonsFirstLaw", "Force", "Inertia"]
    )
    
    # Check that the interaction was recorded
    assert len(student_model.interaction_history) == 1
    assert student_model.interaction_history[0]["question"] == "What is Newton's First Law?"
    assert "Newton's First Law states that" in student_model.interaction_history[0]["response"]
    assert set(student_model.interaction_history[0]["concepts"]) == {"NewtonsFirstLaw", "Force", "Inertia"}
    
    # Check that the concepts were added to exposed concepts
    assert student_model.exposed_concepts == {"NewtonsFirstLaw", "Force", "Inertia"}
    
    # Check that the last interaction time was updated
    assert isinstance(student_model.last_interaction, datetime)

def test_update_quiz_result_correct(student_model):
    """Test updating quiz results with a correct answer."""
    # Add a correct quiz result with high confidence
    student_model.update_quiz_result(
        concept="Force",
        correct=True,
        confidence=0.9
    )
    
    # Check that the quiz result was recorded
    assert len(student_model.quiz_results) == 1
    assert student_model.quiz_results[0]["concept"] == "Force"
    assert student_model.quiz_results[0]["correct"] is True
    assert student_model.quiz_results[0]["confidence"] == 0.9
    
    # Check that the knowledge level was updated
    assert "Force" in student_model.knowledge_level
    assert student_model.knowledge_level["Force"] == pytest.approx(0.18, 0.01)
    
    # Add another correct answer to push knowledge level higher
    student_model.update_quiz_result(
        concept="Force",
        correct=True,
        confidence=0.9
    )
    
    student_model.update_quiz_result(
        concept="Force",
        correct=True,
        confidence=0.9
    )
    
    student_model.update_quiz_result(
        concept="Force",
        correct=True,
        confidence=0.9
    )
    
    # Now the concept should be considered understood
    assert "Force" in student_model.understood_concepts
    assert student_model.knowledge_level["Force"] >= 0.7

def test_update_quiz_result_incorrect(student_model):
    """Test updating quiz results with an incorrect answer."""
    # Set initial knowledge level
    student_model.knowledge_level["Mass"] = 0.6
    
    # Add an incorrect quiz result with medium confidence
    student_model.update_quiz_result(
        concept="Mass",
        correct=False,
        confidence=0.5
    )
    
    # Check that the knowledge level decreased
    assert student_model.knowledge_level["Mass"] == pytest.approx(0.55, 0.01)
    
    # Add an incorrect quiz result with high confidence (potential misconception)
    student_model.update_quiz_result(
        concept="Mass",
        correct=False,
        confidence=0.9
    )
    
    # Check that the knowledge level decreased more
    assert student_model.knowledge_level["Mass"] == pytest.approx(0.46, 0.01)

def test_get_knowledge_gaps(student_model):
    """Test identifying knowledge gaps."""
    # Set up knowledge levels
    student_model.exposed_concepts = {"Force", "Mass", "Acceleration", "Velocity"}
    student_model.knowledge_level = {
        "Force": 0.8,
        "Mass": 0.3,
        "Acceleration": 0.4,
        "Velocity": 0.9
    }
    
    # Get knowledge gaps
    gaps = student_model.get_knowledge_gaps()
    
    # Check that only concepts with knowledge level < 0.5 are returned
    assert set(gaps) == {"Mass", "Acceleration"}
    assert "Force" not in gaps
    assert "Velocity" not in gaps

def test_get_ready_concepts(student_model):
    """Test identifying concepts the student is ready to learn."""
    # Set up understood concepts
    student_model.understood_concepts = {"Force", "Mass"}
    
    # Set up prerequisite graph
    prereqs = {
        "NewtonsFirstLaw": ["Force", "Inertia"],
        "NewtonsSecondLaw": ["Force", "Mass", "Acceleration"],
        "NewtonsThirdLaw": ["Force", "NewtonsFirstLaw", "NewtonsSecondLaw"],
        "Force": [],
        "Mass": [],
        "Acceleration": [],
        "Inertia": ["Mass"]
    }
    
    # Get ready concepts
    ready = student_model.get_ready_concepts(prereqs)
    
    # Check that concepts with all prerequisites understood are returned
    assert "Inertia" in ready  # Prerequisites: Mass (understood)
    assert "NewtonsFirstLaw" not in ready  # Missing Inertia
    assert "NewtonsSecondLaw" not in ready  # Missing Acceleration
    assert "NewtonsThirdLaw" not in ready  # Missing many prerequisites

def test_save_and_load(temp_data_dir):
    """Test saving and loading student model data."""
    # Create a student model with data
    model1 = StudentModel("save_test_student", data_path=temp_data_dir)
    model1.exposed_concepts = {"Force", "Mass"}
    model1.understood_concepts = {"Force"}
    model1.knowledge_level = {"Force": 0.8, "Mass": 0.4}
    model1.last_interaction = datetime.now()
    
    # Save the model
    model1.save()
    
    # Create a new model instance that should load the saved data
    model2 = StudentModel("save_test_student", data_path=temp_data_dir)
    
    # Check that the data was loaded correctly
    assert model2.exposed_concepts == {"Force", "Mass"}
    assert model2.understood_concepts == {"Force"}
    assert model2.knowledge_level["Force"] == pytest.approx(0.8)
    assert model2.knowledge_level["Mass"] == pytest.approx(0.4)
    assert model2.last_interaction is not None

def test_get_learning_path(student_model):
    """Test generating a learning path to reach a target concept."""
    # Set up understood concepts
    student_model.understood_concepts = {"Force"}
    
    # Set up concept graph
    concept_graph = {
        "NewtonsFirstLaw": ["Force", "Inertia"],
        "NewtonsSecondLaw": ["Force", "Mass", "Acceleration"],
        "NewtonsThirdLaw": ["NewtonsFirstLaw", "NewtonsSecondLaw"],
        "Force": [],
        "Mass": [],
        "Acceleration": [],
        "Inertia": []
    }
    
    # Get learning path to Newton's Third Law
    path = student_model.get_learning_path("NewtonsThirdLaw", concept_graph)
    
    # Force is already understood, so shouldn't be in the path
    assert "Force" not in path
    
    # Check that prerequisites are in the correct order
    # The exact order might vary, but this checks general correctness
    assert path.index("Inertia") < path.index("NewtonsFirstLaw")
    assert path.index("Mass") < path.index("NewtonsSecondLaw")
    assert path.index("Acceleration") < path.index("NewtonsSecondLaw")
    assert path.index("NewtonsFirstLaw") < path.index("NewtonsThirdLaw")
    assert path.index("NewtonsSecondLaw") < path.index("NewtonsThirdLaw")
    assert "NewtonsThirdLaw" in path  # The target should be in the path 