from flask import Flask, render_template, request, jsonify
import os
from dotenv import load_dotenv
from owlready2 import get_ontology
import anthropic
import json

# Load environment variables
load_dotenv()

app = Flask(__name__)

# Load the ontology
current_dir = os.path.dirname(os.path.abspath(__file__))
ontology_path = os.path.join(current_dir, 'schemas', 'physics_tutor.owl')
onto = get_ontology(f"file://{ontology_path}").load()

# Initialize Anthropic client
client = anthropic.Anthropic(api_key=os.getenv("ANTHROPIC_API_KEY"))

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/query', methods=['POST'])
def query():
    data = request.json
    user_query = data.get('query', '')
    
    # Query the ontology for relevant context
    ontology_context = get_ontology_context(user_query)
    
    # Combine ontology context with the user query for Claude
    response = get_claude_response(user_query, ontology_context)
    
    return jsonify({"response": response})

def get_ontology_context(query):
    """Extract relevant context from the ontology based on the query"""
    context = []
    
    # Keywords to look for in the query
    physics_concepts = [
        "Newton", "force", "motion", "inertia", "acceleration", "mass",
        "velocity", "kinematics", "law", "physics"
    ]
    
    # Check if any physics keywords are in the query
    query_terms = set(word.lower() for word in query.split())
    matched_terms = []
    
    for concept in physics_concepts:
        if concept.lower() in query.lower():
            matched_terms.append(concept)
    
    # If no specific matches, return empty context
    if not matched_terms:
        return ""
    
    # Search for relevant concepts in the ontology
    context_parts = []
    
    # Look for Newton's Laws
    if any(term in ["newton", "law", "force", "motion"] for term in query_terms):
        for law in ["NewtonsFirstLaw", "NewtonsSecondLaw", "NewtonsThirdLaw"]:
            law_obj = onto.search_one(iri=f"*{law}")
            if law_obj:
                context_parts.append(f"{law}: {law_obj.hasDefinition[0]}")
                
                # Add prerequisites
                prerequisites = list(law_obj.hasPrerequisite)
                if prerequisites:
                    prereq_text = ", ".join([prereq.name for prereq in prerequisites])
                    context_parts.append(f"{law} prerequisites: {prereq_text}")
                
                # Add formulas if available
                formulas = list(law_obj.hasFormula)
                for formula in formulas:
                    context_parts.append(f"{law} formula: {formula.hasDefinition[0]}")
    
    # Look for physical quantities
    for quantity in ["Force", "Mass", "Acceleration", "Velocity", "Position", "Time"]:
        if quantity.lower() in query.lower():
            quantity_obj = onto.search_one(iri=f"*{quantity}")
            if quantity_obj:
                definition = getattr(quantity_obj, "hasDefinition", [""])[0]
                context_parts.append(f"{quantity}: {definition}")
                
                # Add units
                units = list(quantity_obj.hasUnit)
                for unit in units:
                    context_parts.append(f"{quantity} unit: {unit.name}")
    
    return "\n".join(context_parts)

def get_claude_response(query, ontology_context):
    """Get a response from Claude with ontology-enhanced context"""
    
    system_prompt = """You are an AI physics tutor that provides accurate, educational responses based on established physics principles.
    When responding to questions, use the provided ontology context to ensure accuracy and factual correctness.
    Your responses should be clear, concise, and educational - suitable for a student learning physics.
    Avoid hallucinations or making up information not supported by the ontology context or standard physics knowledge.
    If you're not sure about something, acknowledge the limits of your knowledge rather than guessing."""
    
    # Add ontology context if available
    if ontology_context:
        system_prompt += "\n\nHere is relevant information from the physics ontology to help you answer accurately:\n" + ontology_context
    
    try:
        response = client.messages.create(
            model="claude-3-opus-20240229",
            max_tokens=1000,
            system=system_prompt,
            messages=[
                {"role": "user", "content": query}
            ]
        )
        return response.content[0].text
    except Exception as e:
        return f"Error getting response from Claude: {str(e)}"

if __name__ == '__main__':
    app.run(debug=True, port=5000)
