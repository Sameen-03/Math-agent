import requests
from datasets import load_dataset
import re

# The API endpoint of your running Math Agent
AGENT_API_URL = "http://localhost:8000/query"

def parse_final_answer(text: str) -> str:
    """
    Extracts the final numerical option (1, 2, 3, or 4) from the agent's text,
    looking for the specific pattern from our prompt.
    """
    if not text:
        return ""
    # Look for the specific pattern "The correct option is: [number]"
    match = re.search(r'The correct option is:\s*(\d)', text, re.IGNORECASE)
    if match:
        return match.group(1)
    
    # As a fallback, look for a single digit 1, 2, 3, or 4 at the very end of the string
    fallback_match = re.search(r'\b[1-4]\b$', text.strip())
    if fallback_match:
        return fallback_match.group(0)
        
    return "" # Return empty if no clear answer is found

def run_benchmark():
    """
    Loads the JEE Mains dataset, queries the agent, and computes accuracy.
    """
    print("Loading CK0607/2025-Jee-Mains-Question dataset from Hugging Face...")
    try:
        # Load the dataset and select a sample of questions for the test run.
        # Remove .select(range(50)) to run the full benchmark.
        dataset = load_dataset("CK0607/2025-Jee-Mains-Question", split="train").select(range(50))
    except Exception as e:
        print(f"Failed to load dataset. You may need to log in to Hugging Face CLI. Error: {e}")
        print("Try running 'huggingface-cli login' in your terminal.")
        return

    correct_answers = 0
    total_questions = len(dataset)
    
    if total_questions == 0:
        print("Dataset is empty.")
        return

    print(f"Starting benchmark with {total_questions} questions...")

    # Iterate over each example in the dataset
    for index, item in enumerate(dataset):
        # Use the column names from your screenshot
        question = item['Question Text']
        ground_truth = str(item['Correct Option'])

        print(f"\n--- Question #{index + 1}/{total_questions} ---")
        print(f"Query: {question}")

        try:
            # Send the request to your agent's API with a longer timeout for complex problems
            response = requests.post(AGENT_API_URL, json={"question": question}, timeout=120)
            response.raise_for_status()
            
            agent_response_text = response.json().get('answer', '')
            agent_final_answer = parse_final_answer(agent_response_text)

            if agent_final_answer and ground_truth and agent_final_answer == ground_truth:
                correct_answers += 1
                print(f"Result: CORRECT ✔️")
            else:
                print(f"Result: INCORRECT ❌ (Agent: '{agent_final_answer}', Truth: '{ground_truth}')")

        except requests.exceptions.RequestException as e:
            print(f"API call failed for question {index + 1}: {e}")

    # Calculate and print the final score
    accuracy = (correct_answers / total_questions) * 100
    print("\n\n--- Benchmark Complete ---")
    print(f"Total Questions: {total_questions}")
    print(f"Correct Answers: {correct_answers}")
    print(f"Accuracy: {accuracy:.2f}%")

if __name__ == "__main__":
    run_benchmark()