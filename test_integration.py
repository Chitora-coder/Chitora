import capture
import ai_engine
import webbrowser
import time
import os

def test_pipeline():
    # 1. Open a C programming question
    print("Opening browser...")
    url = "https://www.geeksforgeeks.org/c-programming-interview-questions/"
    webbrowser.open(url)
    
    print("Waiting 5 seconds for page to load...")
    time.sleep(5)
    
    # 2. Capture
    print("Capturing screen...")
    try:
        img = capture.capture_screen()
        print("Screen captured.")
    except Exception as e:
        print(f"Capture failed: {e}")
        return

    # 3. Process
    print("Sending to AI...")
    try:
        answer = ai_engine.get_answer_from_image(img)
        print("-" * 20)
        print("AI ANSWER:")
        print(answer)
        print("-" * 20)
    except Exception as e:
        print(f"AI processing failed: {e}")

if __name__ == "__main__":
    test_pipeline()
