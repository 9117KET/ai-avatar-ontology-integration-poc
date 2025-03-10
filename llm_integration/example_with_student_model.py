import asyncio
import logging
import os
from claude_tutor import ClaudeTutor

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

async def demonstrate_adaptive_tutoring():
    """
    Demonstrate how the tutor adapts to a student's learning progress
    across multiple interactions.
    """
    # Create a student ID - in a real app, this would be linked to a user account
    student_id = "demo_student_001"
    
    # Initialize the tutor with this student ID
    tutor = ClaudeTutor(student_id=student_id)
    logger.info(f"Created tutor for student: {student_id}")
    
    # Example questions in order of increasing complexity
    questions = [
        # First, ask about a basic concept
        "What is force in physics?",
        
        # Then, ask about a more complex concept that builds on the first
        "How is force related to acceleration?",
        
        # Finally, ask about a law that requires understanding of both concepts
        "Can you explain Newton's Second Law?"
    ]
    
    # Simulate a tutoring session with progressive questions
    for i, question in enumerate(questions, 1):
        logger.info(f"\n--- Question {i}: {question} ---")
        
        # Get the tutor's response
        response = await tutor.tutor(question)
        
        # Display the response
        print(f"\nStudent: {question}")
        print(f"\nTutor: {response}")
        
        # Show the current state of the student model
        logger.info("\nCurrent student model state:")
        logger.info(f"Exposed concepts: {tutor.student_model.exposed_concepts}")
        logger.info(f"Knowledge levels: {tutor.student_model.knowledge_level}")
        
        # Simulate the student's understanding by updating quiz results
        # In a real app, this would come from actual student interactions/quizzes
        if i == 1:
            # After first question, simulate partial understanding of force
            tutor.student_model.update_quiz_result("Force", correct=True, confidence=0.7)
            logger.info("Added quiz result: Force concept understood")
        
        elif i == 2:
            # After second question, simulate confusion about acceleration
            tutor.student_model.update_quiz_result("Acceleration", correct=False, confidence=0.5)
            logger.info("Added quiz result: Acceleration concept not fully understood")
            
            # Also record a potential misconception
            tutor.student_model.record_misconception(
                "Acceleration", 
                "Student may be confusing acceleration with velocity"
            )
            logger.info("Recorded misconception about acceleration")
        
        # Wait between questions to simulate a real conversation
        if i < len(questions):
            logger.info("\nWaiting for next question...\n")
            await asyncio.sleep(1)
    
    # At the end, show learning recommendations
    ready_concepts = tutor.student_model.get_ready_concepts(tutor.concept_prerequisites)
    knowledge_gaps = tutor.student_model.get_knowledge_gaps()
    
    logger.info("\n--- Tutoring Session Summary ---")
    logger.info(f"Concepts the student has been exposed to: {tutor.student_model.exposed_concepts}")
    logger.info(f"Concepts the student understands: {tutor.student_model.understood_concepts}")
    logger.info(f"Knowledge gaps to address: {knowledge_gaps}")
    logger.info(f"Concepts ready to learn next: {ready_concepts}")
    
    # Show personalized learning path to a target concept
    target = "NewtonsThirdLaw"
    learning_path = tutor.student_model.get_learning_path(target, tutor.concept_prerequisites)
    logger.info(f"\nPersonalized learning path to understand {target}:")
    for i, concept in enumerate(learning_path, 1):
        logger.info(f"{i}. {concept}")

async def main():
    """Run the demonstration."""
    try:
        await demonstrate_adaptive_tutoring()
    except Exception as e:
        logger.error(f"Error during demonstration: {e}")

if __name__ == "__main__":
    asyncio.run(main()) 