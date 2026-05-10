import os
import requests
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Configuration
endpoint = os.getenv("AZURE_OPENAI_ENDPOINT")
api_key = os.getenv("AZURE_OPENAI_KEY")
deployment_name = os.getenv("MODEL_DEPLOYMENT_NAME")

# Construct the full URL
url = f"{endpoint}/responses?"

# Headers
headers = {
    "Content-Type": "application/json",
    "api-key": api_key
}

# Request payload
payload = {
    "input": [
        {
            "role": "system",
            "content": "You are a helpful AI assistant."
        },
        {
            "role": "user",
            "content": "What are the top 3 benefits of using Microsoft Foundry?"
        }
    ],
    "max_output_tokens": 500,
    "temperature": 0.7,
    "model": deployment_name
}

# Make the API call
try:
    response = requests.post(url, headers=headers, json=payload)
    response.raise_for_status()  # Raise an exception for bad status codes
    
    result = response.json()
    
    # Extract and print the assistant's message
    if "output" in result and len(result["output"]) > 0:
        # Extract text from the output structure
        assistant_message = result["output"][0]["content"][0]["text"]
        print("Assistant Response:")
        print(assistant_message)
        
        # Print token usage
        if "usage" in result:
            print("\nToken Usage:")
            print(f"  Input tokens: {result['usage']['input_tokens']}")
            print(f"  Output tokens: {result['usage']['output_tokens']}")
            print(f"  Total tokens: {result['usage']['total_tokens']}")
    else:
        print("Error: Unexpected response structure.")
        print(f"Response: {result}")
    
except requests.exceptions.RequestException as e:
    print(f"Error calling Foundry API: {e}")
    if hasattr(e, 'response') and e.response is not None:
        print(f"Response content: {e.response.text}")
