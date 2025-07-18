from langchain_google_genai import ChatGoogleGenerativeAI
from .schemas import QueryRequest
import os

# Initialize the Gemini model for guardrail checks
llm = ChatGoogleGenerativeAI(model="gemini-1.5-flash-latest", google_api_key=os.getenv("GOOGLE_API_KEY"))

def is_math_question(query: QueryRequest) -> bool:
    """Checks if the question is related to math."""
    prompt = f"""
    Is the following question primarily about mathematics, science, or a related technical field?
    Answer with only 'yes' or 'no'.

    Question: "{query.question}"
    """
    response = llm.invoke(prompt).content.strip().lower()
    return "yes" in response

def moderate_output(answer: str) -> str:
    """A simple placeholder for output moderation."""
    print("Moderating output... (placeholder)")
    return answer