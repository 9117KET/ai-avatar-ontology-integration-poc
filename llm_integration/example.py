import asyncio
from claude_tutor import ClaudeTutor

async def main():
    # Initialize the tutor
    tutor = ClaudeTutor()
    
    # Example questions to test the tutor
    questions = [
        "Can you explain Newton's First Law?",
        "What are some real-world applications of Newton's Third Law?",
        "How does mass affect acceleration according to Newton's Second Law?"
    ]
    
    # Get responses for each question
    for question in questions:
        print(f"\nQuestion: {question}")
        print("-" * 50)
        response = await tutor.tutor(question)
        print(f"Response: {response}")
        print("-" * 50)

if __name__ == "__main__":
    asyncio.run(main()) 