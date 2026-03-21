from flask import Flask, request, jsonify
from flask_cors import CORS
import sys
import os

# Add parent directory to path to import modules
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

import capture
import ai_engine_v2 as ai_engine

app = Flask(__name__)
CORS(app)

@app.route('/process', methods=['POST'])
def process():
    try:
        # Capture screen
        img = capture.capture_screen()
        
        # Get AI answer
        answer = ai_engine.get_answer_from_image(img)
        
        print(f"Answer: {answer}")
        
        return jsonify({'answer': answer})
        
    except Exception as e:
        import traceback
        print("Backend Error Details:")
        traceback.print_exc()
        return jsonify({'answer': 'ERR', 'details': str(e)}), 500

if __name__ == '__main__':
    print("Backend server starting on port 5555...")
    app.run(host='127.0.0.1', port=5555, debug=False)
