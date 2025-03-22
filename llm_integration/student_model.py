import os
import json
import logging
from typing import Dict, List, Set, Optional
from datetime import datetime

# Set up logging
logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)

class StudentModel:
    """
    Tracks a student's knowledge state, interaction history, and learning progress.
    
    The StudentModel is a core component that maintains:
    - Concepts the student has been exposed to
    - Concepts the student has demonstrated understanding of
    - Quiz/assessment results
    - Interaction history
    
    This model enables personalized tutoring by adapting content based on
    the student's current knowledge state.
    """
    
    def __init__(self, student_id: str, data_path: Optional[str] = None):
        """
        Initialize a new student model or load an existing one.
        
        Persists student data between sessions using JSON storage.
        
        Args:
            student_id: Unique identifier for the student
            data_path: Optional path to store student data
        """
        self.student_id = student_id
        self.data_path = data_path or os.path.join(
            os.path.dirname(os.path.dirname(os.path.abspath(__file__))), 
            'data', 
            'students'
        )
        
        # Create data directory if it doesn't exist
        os.makedirs(self.data_path, exist_ok=True)
        
        # Initialize student model attributes
        self.exposed_concepts: Set[str] = set()  # Concepts the student has seen
        self.understood_concepts: Set[str] = set()  # Concepts the student understands
        self.misconceptions: Dict[str, str] = {}  # Concept name -> description of misconception
        self.quiz_results: List[Dict] = []  # List of quiz results
        self.interaction_history: List[Dict] = []  # List of interactions
        self.knowledge_level: Dict[str, float] = {}  # Concept name -> knowledge level (0.0 to 1.0)
        self.last_interaction: Optional[datetime] = None
        
        # Try to load existing data
        self._load_data()
        
    def _load_data(self) -> None:
        """
        Load student data from disk if it exists.
        
        Restores the student's previous state from JSON storage to enable
        continuous learning across sessions.
        """
        file_path = os.path.join(self.data_path, f"{self.student_id}.json")
        if os.path.exists(file_path):
            try:
                with open(file_path, 'r') as f:
                    data = json.load(f)
                
                self.exposed_concepts = set(data.get('exposed_concepts', []))
                self.understood_concepts = set(data.get('understood_concepts', []))
                self.misconceptions = data.get('misconceptions', {})
                self.quiz_results = data.get('quiz_results', [])
                self.interaction_history = data.get('interaction_history', [])
                self.knowledge_level = data.get('knowledge_level', {})
                
                last_interaction = data.get('last_interaction')
                if last_interaction:
                    self.last_interaction = datetime.fromisoformat(last_interaction)
                
                logger.debug(f"Loaded student data for {self.student_id}")
            except Exception as e:
                logger.error(f"Error loading student data: {e}")
    
    def save(self) -> None:
        """
        Save student data to disk.
        
        Persists the current state of the student model to enable
        continuous learning across sessions.
        """
        file_path = os.path.join(self.data_path, f"{self.student_id}.json")
        try:
            data = {
                'student_id': self.student_id,
                'exposed_concepts': list(self.exposed_concepts),
                'understood_concepts': list(self.understood_concepts),
                'misconceptions': self.misconceptions,
                'quiz_results': self.quiz_results,
                'interaction_history': self.interaction_history,
                'knowledge_level': self.knowledge_level,
                'last_interaction': self.last_interaction.isoformat() if self.last_interaction else None
            }
            
            with open(file_path, 'w') as f:
                json.dump(data, f, indent=2)
            
            logger.debug(f"Saved student data for {self.student_id}")
        except Exception as e:
            logger.error(f"Error saving student data: {e}")
    
    def add_interaction(self, question: str, response: str, concepts: List[str]) -> None:
        """
        Record a new interaction with the student.
        
        Updates the student model with information from the current tutoring
        interaction, including concepts covered.
        
        Args:
            question: The student's question
            response: The tutor's response
            concepts: List of concepts covered in the interaction
        """
        # Update last interaction time
        self.last_interaction = datetime.now()
        
        # Add concepts to exposed concepts
        self.exposed_concepts.update(concepts)
        
        # Record the interaction
        interaction = {
            'timestamp': self.last_interaction.isoformat(),
            'question': question,
            'response': response,
            'concepts': concepts
        }
        self.interaction_history.append(interaction)
        
        # Save the updated model
        self.save()
    
    def update_quiz_result(self, concept: str, correct: bool, confidence: float) -> None:
        """
        Update the student model with a quiz result.
        
        Refines the knowledge model based on assessment results, adjusting
        the estimated knowledge level for concepts and detecting possible misconceptions.
        
        Args:
            concept: The concept being tested
            correct: Whether the student answered correctly
            confidence: Student's confidence (0.0 to 1.0)
        """
        # Record the quiz result
        quiz_result = {
            'timestamp': datetime.now().isoformat(),
            'concept': concept,
            'correct': correct,
            'confidence': confidence
        }
        self.quiz_results.append(quiz_result)
        
        # Update knowledge level for the concept
        current_level = self.knowledge_level.get(concept, 0.0)
        
        if correct:
            # If correct, increase knowledge level, but weight by confidence
            # High confidence correct answers increase knowledge level more
            self.knowledge_level[concept] = min(1.0, current_level + (0.2 * confidence))
            
            # If knowledge level is high enough, add to understood concepts
            if self.knowledge_level[concept] >= 0.7:
                self.understood_concepts.add(concept)
                # Remove any misconceptions about this concept
                if concept in self.misconceptions:
                    del self.misconceptions[concept]
        else:
            # If incorrect, decrease knowledge level, but less for low confidence
            # (student was uncertain, so less negative impact)
            self.knowledge_level[concept] = max(0.0, current_level - (0.1 * confidence))
            
            # If they were very confident but wrong, might be a misconception
            if confidence > 0.7:
                # We'd need more logic to identify the specific misconception
                pass
        
        # Save the updated model
        self.save()
    
    def record_misconception(self, concept: str, misconception: str) -> None:
        """
        Record a student misconception about a concept.
        
        Enables the tutoring system to address and correct specific
        misunderstandings in future interactions.
        
        Args:
            concept: The concept name
            misconception: Description of the misconception
        """
        self.misconceptions[concept] = misconception
        self.save()
    
    def get_knowledge_gaps(self) -> List[str]:
        """
        Return concepts that should be reinforced based on low knowledge levels.
        
        Helps the tutoring system identify areas where additional practice or
        explanation is needed.
        """
        return [
            concept for concept, level in self.knowledge_level.items()
            if level < 0.5 and concept in self.exposed_concepts
        ]
    
    def get_ready_concepts(self, all_prereqs: Dict[str, List[str]]) -> List[str]:
        """
        Identify concepts the student is ready to learn next.
        
        Uses the prerequisite graph to determine which new concepts can be
        introduced based on the student's current understanding.
        
        Args:
            all_prereqs: Dictionary mapping concept names to their prerequisites
            
        Returns:
            List of concepts the student is ready to learn
        """
        ready_concepts = []
        
        for concept, prereqs in all_prereqs.items():
            # Skip concepts the student already understands
            if concept in self.understood_concepts:
                continue
                
            # Check if all prerequisites are understood
            if all(prereq in self.understood_concepts for prereq in prereqs):
                ready_concepts.append(concept)
                
        return ready_concepts
    
    def get_recommended_content(self, all_concepts: List[str]) -> Dict[str, str]:
        """
        Generate content recommendations based on the student's knowledge state.
        
        Categorizes concepts into different recommendation types to create
        a balanced learning experience (review, reinforce, new, challenge).
        
        Args:
            all_concepts: List of all available concepts
            
        Returns:
            Dictionary of recommendations by type
        """
        recommendations = {
            'review': [],      # Concepts to review
            'reinforce': [],   # Concepts that need reinforcement
            'new': [],         # New concepts to introduce
            'challenge': []    # Advanced concepts for challenge
        }
        
        # Find concepts to review (exposed but low knowledge)
        for concept in self.exposed_concepts:
            knowledge = self.knowledge_level.get(concept, 0.0)
            if knowledge < 0.4:
                recommendations['review'].append(concept)
            elif 0.4 <= knowledge < 0.7:
                recommendations['reinforce'].append(concept)
        
        # Find new concepts (not exposed yet)
        new_concepts = [c for c in all_concepts if c not in self.exposed_concepts]
        recommendations['new'] = new_concepts[:3]  # Limit to 3 new concepts
        
        # Find challenge concepts (high knowledge level)
        challenge_concepts = [
            concept for concept in self.understood_concepts
            if self.knowledge_level.get(concept, 0.0) > 0.9
        ]
        recommendations['challenge'] = challenge_concepts
        
        return recommendations
    
    def get_learning_path(self, target_concept: str, concept_graph: Dict[str, List[str]]) -> List[str]:
        """
        Generate a personalized learning path to reach a target concept.
        
        Creates an optimized sequence of concepts to learn based on prerequisites
        and the student's current knowledge state.
        
        Args:
            target_concept: The concept the student wants to learn
            concept_graph: Dictionary mapping concepts to their prerequisites
            
        Returns:
            Ordered list of concepts to learn
        """
        # Simple implementation - can be enhanced with graph algorithms
        learning_path = []
        
        def add_prerequisites(concept):
            """Recursively add prerequisites to the learning path."""
            if concept in concept_graph:
                for prereq in concept_graph[concept]:
                    if prereq not in self.understood_concepts and prereq not in learning_path:
                        add_prerequisites(prereq)
                        learning_path.append(prereq)
        
        # Add all prerequisites first
        add_prerequisites(target_concept)
        
        # Add the target concept if not already understood
        if target_concept not in self.understood_concepts and target_concept not in learning_path:
            learning_path.append(target_concept)
            
        return learning_path 