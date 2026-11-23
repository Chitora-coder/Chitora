import os
import sys
import time
import itertools
import google.generativeai as genai
from dotenv import load_dotenv

# Robustly find .env file whether running as script or frozen exe
if getattr(sys, 'frozen', False):
    application_path = os.path.dirname(sys.executable)
else:
    application_path = os.path.dirname(os.path.abspath(__file__))

dotenv_path = os.path.join(application_path, '.env')
if not os.path.exists(dotenv_path):
    dotenv_path = os.path.join(os.getcwd(), '.env')

load_dotenv(dotenv_path)

# --- HTTP Proxy support ---
# Set HTTP_PROXY in .env to route all Gemini requests through a different IP.
# e.g: HTTP_PROXY=http://127.0.0.1:7890  (your VPN/proxy local port)
_proxy = os.getenv("HTTP_PROXY") or os.getenv("HTTPS_PROXY")
if _proxy:
    os.environ["HTTP_PROXY"] = _proxy
    os.environ["HTTPS_PROXY"] = _proxy
    print(f"Routing API requests via proxy: {_proxy}")

# --- Multi-key rotation support ---
# Add GEMINI_API_KEY_2, GEMINI_API_KEY_3 etc. in .env for parallel key pools
def _load_api_keys():
    keys = []
    primary = os.getenv("GEMINI_API_KEY")
    if primary:
        keys.append(primary)
    for i in range(2, 10):
        k = os.getenv(f"GEMINI_API_KEY_{i}")
        if k:
            keys.append(k)
    return keys

API_KEYS = _load_api_keys()
_current_key_index = 0

if not API_KEYS:
    print(f"CRITICAL ERROR: No GEMINI_API_KEY found in: {dotenv_path}")
else:
    print(f"Loaded {len(API_KEYS)} API key(s). Proxy: {'YES' if _proxy else 'NO (direct IP)'}")

def _next_key():
    global _current_key_index
    if not API_KEYS:
        return None
    key = API_KEYS[_current_key_index % len(API_KEYS)]
    _current_key_index += 1
    return key

MODELS = [
    "gemini-2.5-flash",
    "gemini-2.5-pro",
    "gemini-flash-latest",
]

# Backoff schedule for IP-level rate limits (seconds):
# First hit → wait 15s, second → 30s, third → 60s, then cap at 60s
BACKOFF_SCHEDULE = [15, 30, 60, 60]
_rate_limit_hit_count = 0

def get_answer_from_image(image):
    """
    Sends the image to Gemini. On IP-level rate limit (429), uses
    exponential backoff and retries automatically.
    """
    import re
    global _rate_limit_hit_count

    def clean_response(text):
        t = text.strip().upper()
        t = re.sub(r'^(QUES|ANS|ANSWER|OPTION|THE CORRECT OPTION IS|OUTPUT|RESULT)[:\s]*', '', t)
        matches = re.findall(r'\b([A-D])\b', t)
        if matches:
            unique = list(dict.fromkeys(matches))
            return ", ".join(unique)
        if len(t) < 30:
            return t
        return "NO_QUESTION"

    prompt = """
    You are an ELITE Multi-Domain Expert.

    TASK: Look at the screenshot. You will see a RED CIRCLE drawn on the image.
    Identify and solve ONLY the specific question that is located immediately next to or inside that red circle. Ignore all other questions on the screen.

    CRITICAL OUTPUT RULES:
    - Single-answer MCQ (radio buttons) → Return ONLY the letter (A, B, C, or D)
    - Multi-correct MCQ (checkboxes / "select all that apply") → Return ALL correct letters comma-separated (e.g. A, C, D)
    - Calculation/Problem → Return ONLY the final answer
    - True/False → Return ONLY "True" or "False"
    - Fill in the blank → Return ONLY the answer word/number
    - NEVER include explanations, reasoning, or context
    - NEVER include "QUES:", "Ans:", etc.

    Return NO_QUESTION if no question exists near the red circle.
    """

    tried_models = set()
    for model_name in MODELS:
        if model_name in tried_models:
            continue

        for key_attempt in range(max(1, len(API_KEYS))):
            api_key = _next_key()
            try:
                print(f"Trying: {model_name} | key ...{api_key[-6:] if api_key else 'N/A'}")
                genai.configure(api_key=api_key)
                model = genai.GenerativeModel(model_name)
                response = model.generate_content(
                    [prompt, image],
                    request_options={'timeout': 110}
                )
                answer = clean_response(response.text)
                _rate_limit_hit_count = 0  # reset on success
                print(f"Final Answer: {answer}")
                return answer

            except Exception as e:
                err_str = str(e)
                if "429" in err_str or "quota" in err_str.lower() or "rate" in err_str.lower():
                    wait = BACKOFF_SCHEDULE[min(_rate_limit_hit_count, len(BACKOFF_SCHEDULE) - 1)]
                    _rate_limit_hit_count += 1
                    print(f"IP rate-limited (hit #{_rate_limit_hit_count}). Waiting {wait}s before retry...")
                    time.sleep(wait)
                    # After waiting, retry same model — IP block should lift
                    try:
                        genai.configure(api_key=api_key)
                        model = genai.GenerativeModel(model_name)
                        response = model.generate_content(
                            [prompt, image],
                            request_options={'timeout': 110}
                        )
                        answer = clean_response(response.text)
                        _rate_limit_hit_count = 0
                        print(f"Retry succeeded. Final Answer: {answer}")
                        return answer
                    except Exception as retry_e:
                        print(f"Retry also failed: {retry_e}")
                        return "RATE_LIMIT"
                elif "404" in err_str or "not found" in err_str.lower():
                    print(f"Model {model_name} unavailable, skipping.")
                    tried_models.add(model_name)
                    break
                else:
                    print(f"{model_name} error: {e}")

    return "RATE_LIMIT" if _rate_limit_hit_count > 0 else "ERROR"

if __name__ == "__main__":
    pass

if __name__ == "__main__":
    pass
