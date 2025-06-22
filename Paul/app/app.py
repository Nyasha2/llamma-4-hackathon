from flask import Flask, render_template, request, jsonify
import os
from dotenv import load_dotenv
import sys
sys.path.append(os.path.join(os.path.dirname(__file__), '..', 'src'))

from llm_interface.llama_api import LlamaAPI

# Load environment variables
load_dotenv()

app = Flask(__name__)

# Initialize Llama API
llama_api = LlamaAPI()

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/chat', methods=['POST'])
def chat():
    try:
        data = request.get_json()
        user_message = data.get('message', '')
        
        if not user_message:
            return jsonify({'error': 'Message is empty.'}), 400
        
        # Get response from Llama API
        response = llama_api.get_response(user_message)
        
        return jsonify({'response': response})
        
    except Exception as e:
        print(f"Error in chat endpoint: {e}")
        return jsonify({'error': 'Server error occurred.'}), 500

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5001) 