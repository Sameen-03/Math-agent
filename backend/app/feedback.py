import os
import google.generativeai as genai

# Configure the generative AI model
try:
    genai.configure(api_key=os.getenv("GOOGLE_API_KEY"))
    model = genai.GenerativeModel('gemini-1.5-flash-latest')
except Exception as e:
    print(f"Error configuring Google Generative AI: {e}")
    model = None

def refine_answer_with_feedback(question, answer, feedback):
    """Uses the Gemini model directly to refine the answer."""
    if not model:
        return "Error: Generative AI model not configured."
        
    print("-> Refining answer with google-generativeai...")

    # Create a direct prompt for the model
    prompt = f"""
    You are a helpful teaching assistant. A student was given an answer to a math problem, but they had some feedback.
    Your task is to rewrite the original answer to incorporate the student's feedback.

    Original Question:
    {question}

    Original Answer:
    {answer}

    Student's Feedback:
    "{feedback}"

    Please provide a new, refined, and complete step-by-step answer that addresses the feedback:
    """

    try:
        response = model.generate_content(prompt)
        return response.text
    except Exception as e:
        print(f"Error during content generation: {e}")
        return f"Sorry, an error occurred while refining the answer: {e}"