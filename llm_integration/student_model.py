import logging
from typing import Dict, List, Set

# Set up logging
logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)

class StudentModel:
    """
    A simplified student model that tracks exposure to concepts.
    
    The StudentModel maintains:
    - Concepts the student has been exposed to
    - Concepts the student has demonstrated understanding of
    
    This model enables basic personalization of tutoring responses based on
    what concepts the student has already encountered.
    """
    
    def __init__(self, student_id: str):
        """
        Initialize a new student model.
        
        Args:
            student_id: Unique identifier for the student
        """
        self.student_id = student_id
        
        # Initialize student model attributes
        self.exposed_concepts: Set[str] = set()  # Concepts the student has seen
        self.understood_concepts: Set[str] = set()  # Concepts the student understands
        self.misconceptions: Dict[str, str] = {}  # Concept name -> description of misconception
        self.knowledge_level: Dict[str, float] = {}  # Concept name -> knowledge level (0.0 to 1.0)
        
        logger.debug(f"Initialized student model for {self.student_id}")
    
    def expose_concept(self, concept: str) -> None:
        """
        Mark a concept as exposed to the student.
        
        This is called when a concept is mentioned or explained in a
        tutoring interaction.
        
        Args:
            concept: The concept name to mark as exposed
        """
        self.exposed_concepts.add(concept)
        # Initialize knowledge level if not set
        if concept not in self.knowledge_level:
            self.knowledge_level[concept] = 0.1
    
    def mark_as_understood(self, concept: str) -> None:
        """
        Mark a concept as understood by the student.
        
        Args:
            concept: The concept name to mark as understood
        """
        self.understood_concepts.add(concept)
        # Also ensure it's in exposed concepts
        self.exposed_concepts.add(concept)
        # Set knowledge level to high for this concept
        self.knowledge_level[concept] = 1.0
        # Remove any misconceptions about this concept
        if concept in self.misconceptions:
            del self.misconceptions[concept]
    
    def get_knowledge_gaps(self) -> List[str]:
        """Returns a list of concepts the student has been exposed to but not yet understood."""
        return list(self.exposed_concepts - self.understood_concepts)
        
    def get_ready_concepts(self, concept_prerequisites: Dict[str, List[str]]) -> List[str]:
        """Identifies concepts that the student is ready to learn based on their prerequisites.
        
        Args:
            concept_prerequisites: Dictionary mapping concepts to their prerequisites
            
        Returns:
            List of concepts that the student is ready to learn
        """
        ready_concepts = []
        
        for concept, prerequisites in concept_prerequisites.items():
            # Skip concepts the student already understands
            if concept in self.understood_concepts:
                continue
                
            # Check if all prerequisites are understood
            if all(prereq in self.understood_concepts for prereq in prerequisites):
                ready_concepts.append(concept)
                
        return ready_concepts