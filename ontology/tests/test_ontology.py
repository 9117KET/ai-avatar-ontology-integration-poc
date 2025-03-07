from owlready2 import get_ontology
import os

def test_ontology():
    # Get the absolute path to the ontology file
    current_dir = os.path.dirname(os.path.abspath(__file__))
    ontology_path = os.path.join(os.path.dirname(current_dir), 'schemas', 'physics_tutor.owl')
    
    # Load the ontology
    onto = get_ontology(f"file://{ontology_path}").load()
    
    # Test 1: List all classes
    print("\n=== Classes in the ontology ===")
    for cls in onto.classes():
        print(f"- {cls.name}")
    
    # Test 2: List all properties
    print("\n=== Properties in the ontology ===")
    for prop in onto.object_properties():
        print(f"- {prop.name}")
    for prop in onto.data_properties():
        print(f"- {prop.name}")
    
    # Test 3: Query prerequisites for Newton's Laws
    print("\n=== Prerequisites for Newton's Laws ===")
    for law in ["NewtonsFirstLaw", "NewtonsSecondLaw", "NewtonsThirdLaw"]:
        law_obj = onto.search_one(iri=f"*{law}")
        if law_obj:
            print(f"\n{law}:")
            prerequisites = list(law_obj.hasPrerequisite)
            for prereq in prerequisites:
                print(f"- {prereq.name}")
    
    # Test 4: Query units for physical quantities
    print("\n=== Units for Physical Quantities ===")
    for quantity in onto.search(type=onto.PhysicalQuantity):
        print(f"\n{quantity.name}:")
        units = list(quantity.hasUnit)
        for unit in units:
            print(f"- {unit.name}")
    
    # Test 5: Query examples for Newton's Laws
    print("\n=== Examples for Newton's Laws ===")
    for law in ["NewtonsFirstLaw", "NewtonsSecondLaw", "NewtonsThirdLaw"]:
        law_obj = onto.search_one(iri=f"*{law}")
        if law_obj:
            print(f"\n{law}:")
            examples = list(law_obj.hasExample)
            for example in examples:
                print(f"- {example.hasExplanation[0]}")
    
    # Test 6: Query formulas for Newton's Laws
    print("\n=== Formulas for Newton's Laws ===")
    for law in ["NewtonsFirstLaw", "NewtonsSecondLaw", "NewtonsThirdLaw"]:
        law_obj = onto.search_one(iri=f"*{law}")
        if law_obj:
            print(f"\n{law}:")
            formulas = list(law_obj.hasFormula)
            for formula in formulas:
                print(f"- {formula.hasDefinition[0]}")
    
    # Test 7: Query topics and their concepts
    print("\n=== Topics and Their Concepts ===")
    for topic in onto.search(type=onto.Topic):
        print(f"\n{topic.name}:")
        print(f"Definition: {topic.hasDefinition[0]}")
        concepts = [c for c in onto.search(type=onto.Concept) if topic in c.isPartOf]
        print("Concepts:")
        for concept in concepts:
            print(f"- {concept.name}")
    
    # Test 8: Query applications and their concepts
    print("\n=== Applications and Their Concepts ===")
    for app in onto.search(type=onto.Application):
        print(f"\n{app.name}:")
        print(f"Description: {app.hasDescription[0]}")
        concepts = [c for c in onto.search(type=onto.Concept) if app in c.hasApplication]
        print("Related Concepts:")
        for concept in concepts:
            print(f"- {concept.name}")
    
    # Test 9: Query related concepts
    print("\n=== Related Concepts ===")
    for concept in onto.search(type=onto.Concept):
        related = list(concept.relatesTo)
        if related:
            print(f"\n{concept.name} relates to:")
            for rel in related:
                print(f"- {rel.name}")
    
    # Test 10: Query formulas and their quantities
    print("\n=== Formulas and Their Quantities ===")
    for formula in onto.search(type=onto.Formula):
        print(f"\n{formula.name}:")
        print(f"Definition: {formula.hasDefinition[0]}")
        quantities = [q for q in onto.search(type=onto.PhysicalQuantity) if formula in q.isUsedIn]
        print("Used Quantities:")
        for quantity in quantities:
            print(f"- {quantity.name}")

if __name__ == "__main__":
    test_ontology() 