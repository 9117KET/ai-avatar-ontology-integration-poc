import os
import logging
from typing import List, Dict, Optional
from dotenv import load_dotenv
from anthropic import AsyncAnthropic
from owlready2 import get_ontology, World

# Set up logging
logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)

class ClaudeTutor:
    def __init__(self):
        """Initialize the Claude Tutor with API key and ontology."""
        logger.debug("Initializing ClaudeTutor...")
        load_dotenv()
        self.api_key = os.getenv("ANTHROPIC_API_KEY")
        if not self.api_key:
            logger.error("ANTHROPIC_API_KEY environment variable is not set")
            raise ValueError("ANTHROPIC_API_KEY environment variable is not set")
        logger.debug("API key loaded successfully")
        
        try:
            self.client = AsyncAnthropic(api_key=self.api_key)
            logger.debug("Anthropic client initialized")
        except Exception as e:
            logger.error(f"Failed to initialize Anthropic client: {e}")
            raise
        
        # Load the ontology
        try:
            current_dir = os.path.dirname(os.path.abspath(__file__))
            ontology_path = os.path.join(os.path.dirname(current_dir), 'ontology', 'schemas', 'physics_tutor.owl')
            logger.debug(f"Loading ontology from: {ontology_path}")
            self.onto = get_ontology(f"file://{ontology_path}").load()
            logger.debug("Ontology loaded successfully")
        except Exception as e:
            logger.error(f"Failed to load ontology: {e}")
            raise
        
        # Initialize the system prompt with ontology context
        self.system_prompt = self._create_system_prompt()
        logger.debug("System prompt created")
    
    def _create_system_prompt(self) -> str:
        """Create a system prompt that includes relevant ontology information."""
        prompt = """You are a physics tutor that uses a structured knowledge base to provide accurate and helpful responses.
        You have access to the following key concepts and their relationships:
        
        Topics:
        """
        
        # Add topics
        for topic in self.onto.search(type=self.onto.Topic):
            prompt += f"- {topic.name}: {topic.hasDefinition[0]}\n"
        
        prompt += "\nKey Laws:\n"
        # Add Newton's Laws
        for law in ["NewtonsFirstLaw", "NewtonsSecondLaw", "NewtonsThirdLaw"]:
            law_obj = self.onto.search_one(iri=f"*{law}")
            if law_obj:
                prompt += f"- {law}: {law_obj.hasDefinition[0]}\n"
        
        prompt += "\nWhen tutoring:\n"
        prompt += "1. Use the knowledge base to ensure accuracy\n"
        prompt += "2. Consider prerequisites when explaining concepts\n"
        prompt += "3. Provide relevant examples from the knowledge base\n"
        prompt += "4. Connect concepts to real-world applications\n"
        prompt += "5. Be clear and concise in your explanations\n"
        
        return prompt
    
    def get_prerequisites(self, concept_name: str) -> List[str]:
        """Get prerequisites for a given concept from the ontology."""
        concept = self.onto.search_one(iri=f"*{concept_name}")
        if concept and hasattr(concept, 'hasPrerequisite'):
            return [prereq.name for prereq in concept.hasPrerequisite]
        return []
    
    def get_examples(self, concept_name: str) -> List[str]:
        """Get examples for a given concept from the ontology."""
        concept = self.onto.search_one(iri=f"*{concept_name}")
        if concept and hasattr(concept, 'hasExample'):
            return [example.hasExplanation[0] for example in concept.hasExample]
        return []
    
    def get_applications(self, concept_name: str) -> List[str]:
        """Get real-world applications for a given concept from the ontology."""
        concept = self.onto.search_one(iri=f"*{concept_name}")
        if concept and hasattr(concept, 'hasApplication'):
            return [app.hasDescription[0] for app in concept.hasApplication]
        return []
    
    async def tutor(self, user_question: str) -> str:
        """Main tutoring method that processes user questions and provides responses."""
        logger.debug(f"Processing question: {user_question}")
        
        # Get relevant context from the ontology
        context = self._get_relevant_context(user_question)
        logger.debug(f"Retrieved context: {context}")
        
        # Create the message for Claude
        message = f"""Context from knowledge base:
{context}

User question: {user_question}

Please provide a helpful response based on the knowledge base and your understanding of physics."""
        
        logger.debug("Preparing API call to Claude")
        try:
            # Get response from Claude
            logger.debug("Creating message with Claude API...")
            create_message = self.client.messages.create(
                model="claude-3-opus-20240229",
                max_tokens=1000,
                system=self.system_prompt,
                messages=[
                    {"role": "user", "content": message}
                ]
            )
            
            # Check if create_message is awaitable
            if hasattr(create_message, '__await__'):
                logger.debug("Message creation is awaitable, awaiting response...")
                response = await create_message
            else:
                logger.debug("Message creation is not awaitable, using synchronous response")
                response = create_message
                
            logger.debug("Successfully received response from Claude API")
            logger.debug(f"Response type: {type(response)}")
            logger.debug(f"Response content type: {type(response.content)}")
            logger.debug(f"Response content: {response.content}")
            
            return response.content[0].text
        except Exception as e:
            logger.error(f"Error calling Claude API: {type(e).__name__}: {str(e)}")
            logger.error(f"Error details: {e.__dict__}")
            raise
    
    def _get_relevant_context(self, question: str) -> str:
        """Extract relevant context from the ontology based on the user's question."""
        logger.debug(f"Getting context for question: {question}")
        context = []
        
        # Expanded keyword list with variations
        keywords = [
            "newton", "force", "mass", "acceleration", "velocity", "motion",
            "law", "laws", "inertia", "action", "reaction"
        ]
        
        # Convert question to lowercase for case-insensitive matching
        question_lower = question.lower()
        
        # First, check for Newton's Laws specifically
        law_mappings = {
            "newton's first law": "NewtonsFirstLaw",
            "newtons first law": "NewtonsFirstLaw",
            "newton's second law": "NewtonsSecondLaw",
            "newtons second law": "NewtonsSecondLaw",
            "newton's third law": "NewtonsThirdLaw",
            "newtons third law": "NewtonsThirdLaw"
        }
        
        for question_law, ontology_law in law_mappings.items():
            if question_law in question_lower:
                law_obj = self.onto.search_one(iri=f"*{ontology_law}")
                if law_obj:
                    context.append(f"Law: {ontology_law}")
                    if hasattr(law_obj, 'hasDefinition'):
                        context.append(f"Definition: {law_obj.hasDefinition[0]}")
                    if hasattr(law_obj, 'hasPrerequisite'):
                        context.append("Prerequisites:")
                        for prereq in law_obj.hasPrerequisite:
                            context.append(f"- {prereq.name}")
                    if hasattr(law_obj, 'hasExample'):
                        context.append("Examples:")
                        for example in law_obj.hasExample:
                            context.append(f"- {example.hasExplanation[0]}")
                    if hasattr(law_obj, 'hasApplication'):
                        context.append("Applications:")
                        for app in law_obj.hasApplication:
                            context.append(f"- {app.hasDescription[0]}")
                    return "\n".join(context)
        
        # Then check for other concepts
        for keyword in keywords:
            if keyword in question_lower:
                # Search for related concepts
                for concept in self.onto.search(type=self.onto.Concept):
                    if keyword in concept.name.lower():
                        context.append(f"Concept: {concept.name}")
                        if hasattr(concept, 'hasDefinition'):
                            context.append(f"Definition: {concept.hasDefinition[0]}")
                        if hasattr(concept, 'hasPrerequisite'):
                            context.append("Prerequisites:")
                            for prereq in concept.hasPrerequisite:
                                context.append(f"- {prereq.name}")
                        if hasattr(concept, 'hasExample'):
                            context.append("Examples:")
                            for example in concept.hasExample:
                                context.append(f"- {example.hasExplanation[0]}")
                        if hasattr(concept, 'hasApplication'):
                            context.append("Applications:")
                            for app in concept.hasApplication:
                                context.append(f"- {app.hasDescription[0]}")
        
        return "\n".join(context) if context else "No specific context found for this question." 