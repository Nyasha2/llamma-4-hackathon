import os
import requests
import json
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

API_KEY = os.getenv("Llama_API_KEY")
API_ENDPOINT = os.getenv("Llama_API_ENDPOINT")

def call_llama_api(prompt: str, context: dict) -> str:
    """
    Sends a request to the Llama 4 API and returns the generated text.

    Args:
        prompt: The main instruction or question for the model.
        context: A dictionary containing the world knowledge and game state.

    Returns:
        The text content of the model's response, or an error message.
    """
    if not API_KEY or not API_ENDPOINT:
        return "Error: API key or endpoint not configured. Please check your .env file."

    headers = {
        "Authorization": f"Bearer {API_KEY}",
        "Content-Type": "application/json",
    }

    # Llama 4 models often use a structured message format.
    # The 'system' message sets the context, and the 'user' message provides the prompt.
    payload = {
        "model": "llama-4-turbo", # Or whichever specific model you are using
        "messages": [
            {
                "role": "system",
                "content": f"You are a master storyteller and game master. Use the provided knowledge graph and game state to continue the story. Here is the context: {json.dumps(context)}"
            },
            {
                "role": "user",
                "content": prompt
            }
        ],
        "max_tokens": 500, # Adjust as needed
        "temperature": 0.7 # Adjust for creativity vs. coherence
    }

    try:
        response = requests.post(API_ENDPOINT, headers=headers, json=payload)
        response.raise_for_status()  # Raise an exception for bad status codes (4xx or 5xx)
        
        data = response.json()
        # The exact path to the content might vary based on the API provider's response structure
        return data['choices'][0]['message']['content'].strip()

    except requests.exceptions.RequestException as e:
        print(f"Error calling Llama 4 API: {e}")
        return f"Error: Could not connect to the Llama 4 API. Details: {e}"
    except (KeyError, IndexError) as e:
        print(f"Error parsing API response: {e}")
        return f"Error: Unexpected response format from the API. Details: {e}" 