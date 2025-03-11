import os
import logging
from typing import List, Dict, Optional, Set
from dotenv import load_dotenv
from anthropic import AsyncAnthropic
from owlready2 import get_ontology, World

# Import the StudentModel
from llm_integration.student_model import StudentModel

# Set up logging
logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)

class ClaudeTutor:
    def __init__(self, student_id: Optional[str] = None):
        """
        Initialize the Claude Tutor with API key, ontology, and student model.
        
        Args:
            student_id: Optional identifier for the student. If not provided, a generic model is used.
        """
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
        
        # Initialize student model
        self.student_id = student_id or "anonymous"
        self.student_model = StudentModel(self.student_id)
        logger.debug(f"Student model initialized for student ID: {self.student_id}")
        
        # Pre-compute concept relationships
        self.concept_prerequisites = self._build_prerequisite_graph()
        self.all_concepts = self._get_all_concepts()
        
        # Initialize the system prompt with ontology context
        self.system_prompt = self._create_system_prompt()
        logger.debug("System prompt created")
    
    def _build_prerequisite_graph(self) -> Dict[str, List[str]]:
        """Build a graph of concept prerequisites from the ontology."""
        prereq_graph = {}
        
        for concept in self.onto.search(type=self.onto.Concept):
            if hasattr(concept, 'hasPrerequisite'):
                prereq_graph[concept.name] = [prereq.name for prereq in concept.hasPrerequisite]
            else:
                prereq_graph[concept.name] = []
                
        return prereq_graph
    
    def _get_all_concepts(self) -> List[str]:
        """Get a list of all concepts in the ontology."""
        return [concept.name for concept in self.onto.search(type=self.onto.Concept)]
    
    def _create_system_prompt(self) -> str:
        """Create a system prompt that includes relevant ontology information and student model data."""
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
        
        # Add student model information if available
        if self.student_model and self.student_model.exposed_concepts:
            prompt += "\nStudent Knowledge State:\n"
            
            # Add concepts the student understands
            if self.student_model.understood_concepts:
                prompt += "Concepts understood by the student:\n"
                for concept in self.student_model.understood_concepts:
                    prompt += f"- {concept}\n"
            
            # Add knowledge gaps
            knowledge_gaps = self.student_model.get_knowledge_gaps()
            if knowledge_gaps:
                prompt += "Concepts the student needs to review:\n"
                for concept in knowledge_gaps:
                    prompt += f"- {concept}\n"
            
            # Add misconceptions
            if self.student_model.misconceptions:
                prompt += "Student misconceptions to address:\n"
                for concept, misconception in self.student_model.misconceptions.items():
                    prompt += f"- {concept}: {misconception}\n"
        
        prompt += "\nWhen tutoring:\n"
        prompt += "1. Use the knowledge base to ensure accuracy\n"
        prompt += "2. Consider prerequisites when explaining concepts\n"
        prompt += "3. Provide relevant examples from the knowledge base\n"
        prompt += "4. Connect concepts to real-world applications\n"
        prompt += "5. Be clear and concise in your explanations\n"
        
        # Add adaptive tutoring guidelines based on student model
        if self.student_model and self.student_model.exposed_concepts:
            prompt += "\nAdaptive tutoring guidelines:\n"
            prompt += "1. Build on concepts the student already understands\n"
            prompt += "2. Address knowledge gaps and misconceptions\n"
            prompt += "3. Introduce new concepts when prerequisites are understood\n"
            prompt += "4. Adjust explanation depth based on student knowledge level\n"
            prompt += "5. Reinforce concepts that need strengthening\n"
        
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
        """
        Main tutoring method that processes user questions and provides adaptive responses.
        Updates the student model based on the interaction.
        """
        logger.debug(f"Processing question: {user_question}")
        
        # Get relevant context from the ontology
        context, concepts_covered = self._get_relevant_context(user_question)
        logger.debug(f"Retrieved context: {context}")
        logger.debug(f"Concepts covered: {concepts_covered}")
        
        # Adapt context based on student model
        adapted_context = self._adapt_context_to_student(context, concepts_covered)
        logger.debug(f"Adapted context: {adapted_context}")
        
        # Create the message for Claude
        message = f"""Context from knowledge base:
{adapted_context}

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
            
            response_text = response.content[0].text
            
            # Update student model with this interaction
            self.student_model.add_interaction(
                question=user_question,
                response=response_text,
                concepts=concepts_covered
            )
            logger.debug(f"Updated student model with interaction covering concepts: {concepts_covered}")
            
            return response_text
        except Exception as e:
            logger.error(f"Error calling Claude API: {type(e).__name__}: {str(e)}")
            logger.error(f"Error details: {e.__dict__}")
            raise
    
    def _get_relevant_context(self, question: str) -> tuple[str, List[str]]:
        """
        Extract relevant context from the ontology based on the user's question.
        
        Returns:
            tuple: (context_text, list_of_concepts_covered)
        """
        logger.debug(f"Getting context for question: {question}")
        context = []
        concepts_covered = []
        
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
                    concepts_covered.append(ontology_law)
                    context.append(f"Law: {ontology_law}")
                    if hasattr(law_obj, 'hasDefinition'):
                        context.append(f"Definition: {law_obj.hasDefinition[0]}")
                    if hasattr(law_obj, 'hasPrerequisite'):
                        context.append("Prerequisites:")
                        for prereq in law_obj.hasPrerequisite:
                            concepts_covered.append(prereq.name)
                            context.append(f"- {prereq.name}")
                    if hasattr(law_obj, 'hasExample'):
                        context.append("Examples:")
                        for example in law_obj.hasExample:
                            context.append(f"- {example.hasExplanation[0]}")
                    if hasattr(law_obj, 'hasApplication'):
                        context.append("Applications:")
                        for app in law_obj.hasApplication:
                            context.append(f"- {app.hasDescription[0]}")
                    return "\n".join(context), concepts_covered
        
        # Then check for other concepts
        for keyword in keywords:
            if keyword in question_lower:
                # Search for related concepts
                for concept in self.onto.search(type=self.onto.Concept):
                    if keyword in concept.name.lower():
                        concepts_covered.append(concept.name)
                        context.append(f"Concept: {concept.name}")
                        if hasattr(concept, 'hasDefinition'):
                            context.append(f"Definition: {concept.hasDefinition[0]}")
                        if hasattr(concept, 'hasPrerequisite'):
                            context.append("Prerequisites:")
                            for prereq in concept.hasPrerequisite:
                                concepts_covered.append(prereq.name)
                                context.append(f"- {prereq.name}")
                        if hasattr(concept, 'hasExample'):
                            context.append("Examples:")
                            for example in concept.hasExample:
                                context.append(f"- {example.hasExplanation[0]}")
                        if hasattr(concept, 'hasApplication'):
                            context.append("Applications:")
                            for app in concept.hasApplication:
                                context.append(f"- {app.hasDescription[0]}")
        
        return "\n".join(context) if context else "No specific context found for this question.", list(set(concepts_covered))
    
    def _adapt_context_to_student(self, context: str, concepts: List[str]) -> str:
        """
        Adapt the context based on the student's knowledge level.
        
        Args:
            context: The original context from the ontology
            concepts: List of concepts covered in the context
            
        Returns:
            Adapted context for the student
        """
        # If no student model or empty context, return as is
        if not self.student_model or not context or context == "No specific context found for this question.":
            return context
        
        adapted_lines = []
        original_lines = context.split('\n')
        
        # Identify knowledge gaps
        knowledge_gaps = self.student_model.get_knowledge_gaps()
        
        # Add a note about adapting to the student's knowledge
        adapted_lines.append("Adapted context for student knowledge level:")
        
        # Process each line and adapt based on student knowledge
        for line in original_lines:
            # Always include definitions and basic information
            if line.startswith("Law:") or line.startswith("Concept:") or line.startswith("Definition:"):
                adapted_lines.append(line)
                continue
                
            # For prerequisites, examples, and applications, adapt based on student knowledge
            if line.startswith("Prerequisites:"):
                adapted_lines.append(line)
                continue
                
            if line.startswith("- "):
                # If this is a concept and student needs to review it, highlight it
                for gap in knowledge_gaps:
                    if gap in line:
                        line = f"{line} [KNOWLEDGE GAP - NEEDS REVIEW]"
                        break
                
                # If this is a concept and student already understands it, note it
                for understood in self.student_model.understood_concepts:
                    if understood in line:
                        line = f"{line} [ALREADY UNDERSTOOD]"
                        break
                        
                adapted_lines.append(line)
                continue
                
            # Include other sections (examples, applications)
            adapted_lines.append(line)
        
        # Add learning recommendations based on this context
        ready_concepts = self.student_model.get_ready_concepts(self.concept_prerequisites)
        if ready_concepts:
            adapted_lines.append("\nRecommended next concepts to learn:")
            for concept in ready_concepts:
                if concept in concepts:  # Only recommend concepts related to current context
                    adapted_lines.append(f"- {concept} [READY TO LEARN]")
        
        # If there are misconceptions related to these concepts, add them
        if self.student_model.misconceptions:
            misconceptions_to_address = []
            for concept in concepts:
                if concept in self.student_model.misconceptions:
                    misconceptions_to_address.append(
                        f"- {concept}: {self.student_model.misconceptions[concept]}"
                    )
            
            if misconceptions_to_address:
                adapted_lines.append("\nMisconceptions to address:")
                adapted_lines.extend(misconceptions_to_address)
        
        return "\n".join(adapted_lines) 