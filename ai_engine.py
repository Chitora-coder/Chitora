import os
import sys
import google.generativeai as genai
from dotenv import load_dotenv

# Robustly find .env file whether running as script or frozen exe
if getattr(sys, 'frozen', False):
    # Running as compiled exe
    application_path = os.path.dirname(sys.executable)
else:
    # Running as script
    application_path = os.path.dirname(os.path.abspath(__file__))

dotenv_path = os.path.join(application_path, '.env')
load_dotenv(dotenv_path)

API_KEY = os.getenv("GEMINI_API_KEY")

if not API_KEY:
    print(f"CRITICAL ERROR: GEMINI_API_KEY not found. Looked in: {dotenv_path}")
    # We don't exit here so the app doesn't just silently vanish, 
    # but requests will fail.

genai.configure(api_key=API_KEY)

# Models with fallback
MODELS = ["gemini-2.5-flash", "gemini-2.5-pro", "gemini-flash-latest"] 

def get_answer_from_image(image):
    """
    Sends the image to Gemini to detect and answer C programming questions.
    """
    import re
    
    def clean_response(text):
        t = text.strip().upper()
        # Remove common prefixes
        t = re.sub(r'^(QUES|ANS|ANSWER|OPTION|THE CORRECT OPTION IS|OUTPUT|RESULT)[:\s]*', '', t)
        
        # If it's a single letter A-D among other text, try to find it isolated
        match = re.search(r'\b([A-D])\b', t)
        if match:
            return match.group(1)
            
        # If no isolated A-D, but the whole thing is short, return it (e.g., "42")
        if len(t) < 20: 
            return t
            
        return "NO_QUESTION_FOUND"

    prompt = """
    You are an ELITE Multi-Domain Expert.
    
    TASK: Solve the question in this screenshot.
    
    CRITICAL OUTPUT RULES:
    - MCQ Question → Return ONLY the letter (A, B, C, or D)
    - Calculation/Problem → Return ONLY the final answer
    - True/False → Return ONLY "True" or "False"
    - NEVER include explanations, reasoning, or context
    - NEVER include "QUES:", "Ans:", etc.
    
    Return NO_QUESTION_FOUND if no question exists.
    """

    for model_name in MODELS:
        try:
            model = genai.GenerativeModel(model_name)
            response = model.generate_content(
                [prompt, image],
                request_options={'timeout': 110}
            )
            return clean_response(response.text)
        except Exception:
            continue
    return "NO_QUESTION_FOUND"

if __name__ == "__main__":
    # Mock test if needed
    pass
