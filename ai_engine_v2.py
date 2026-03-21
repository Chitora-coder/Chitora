import os
import sys
import google.generativeai as genai
from dotenv import load_dotenv

# Robustly find .env file whether running as script or frozen exe
if getattr(sys, 'frozen', False):
    application_path = os.path.dirname(sys.executable)
else:
    # If imported by backend_server.py in a subfolder, we want the folder where ai_engine_v2.py lives
    application_path = os.path.dirname(os.path.abspath(__file__))

dotenv_path = os.path.join(application_path, '.env')
if not os.path.exists(dotenv_path):
    # Fallback to current working directory if not found next to script
    dotenv_path = os.path.join(os.getcwd(), '.env')

load_dotenv(dotenv_path)

API_KEY = os.getenv("GEMINI_API_KEY")

if not API_KEY:
    print(f"CRITICAL ERROR: GEMINI_API_KEY not found. Looked in: {dotenv_path}")
else:
    print(f"API Key loaded from: {dotenv_path}")

try:
    genai.configure(api_key=API_KEY)
except Exception as e:
    print(f"GenAI Configuration Error: {e}")

# Using Gemini 2.5 Pro as Primary and Gemini 3 as Fallback
PRIMARY_MODEL = "gemini-2.5-pro" 
FALLBACK_MODEL = "gemini-3-pro-preview"

def get_answer_from_image(image):
    """
    Sends the image to Gemini 3 Pro to solve C programming MCQ or coding questions.
    """
    prompt = """
    You are an Elite Academic and Industry Expert across all domains.
    
    TASK:
    1. Analyze the question (MCQ, calculation, or short answer) found in this screenshot.
    2. Solve it step-by-step mentally with absolute precision.
    
    CRITICAL OUTPUT RULE:
    - If it's an MCQ, return ONLY the correct letter(s): A, B, C, or D.
    - If it's a calculation or short answer, return ONLY the final result.
    - If multiple answers are correct, return them separated by commas (e.g., A, C).
    - Do NOT include "The answer is", "QUES:", "Ans:", or any explanations.
    - If no question is found, return "NO_QUESTION".
    """
    
    import re

    def clean_response(text):
        t = text.strip().upper()
        # Remove common prefixes
        t = re.sub(r'^(QUES|ANS|ANSWER|OPTION|THE CORRECT OPTION IS|OUTPUT|RESULT)[:\s]*', '', t)
        
        # Check for multiple letters (Multi-correct)
        letters = re.findall(r'\b([A-D])\b', t)
        if letters:
            # If we found multiple letters, join them with commas
            # Remove duplicates while preserving order
            seen = set()
            unique_letters = [x for x in letters if not (x in seen or seen.add(x))]
            return ", ".join(unique_letters)
            
        # If no letters, but the response is short (like a number or code snippet)
        if len(t) < 30: 
            return t
            
        return "NO_QUESTION"

    # Try primary model first
    try:
        print(f"Trying model: {PRIMARY_MODEL}")
        model = genai.GenerativeModel(PRIMARY_MODEL)
        response = model.generate_content(
            [prompt, image],
            request_options={'timeout': 110} # Increased to 110s as requested
        )
        answer = clean_response(response.text)
        print(f"Final Answer: {answer}")
        return answer
        
    except Exception as e:
        print(f"Primary model failed: {e}")
        
        # Fallback to stable model
        try:
            print(f"Trying fallback model: {FALLBACK_MODEL}")
            model = genai.GenerativeModel(FALLBACK_MODEL)
            response = model.generate_content(
                [prompt, image],
                request_options={'timeout': 110} # Increased to 110s as requested
            )
            answer = clean_response(response.text)
            print(f"Final Answer (Fallback): {answer}")
            return answer
            
        except Exception as e2:
            print(f"Fallback model also failed: {e2}")
            return "ERROR"

if __name__ == "__main__":
    # Mock test if needed
    pass
