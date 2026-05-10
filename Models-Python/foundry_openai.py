import os
from openai import OpenAI
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Configuration
endpoint = os.getenv("AZURE_OPENAI_ENDPOINT")
api_key = os.getenv("AZURE_OPENAI_KEY")
deployment_name = os.getenv("MODEL_DEPLOYMENT_NAME")

client = OpenAI(
    api_key=api_key,
    base_url=endpoint
)

response = client.responses.create(   
  input=[
      {
          "role": "system",
          "content": "You are a helpful AI assistant."
      },
      {
          "role": "user",
          "content": "What are the top 3 benefits of using Microsoft Foundry?"
      }
  ],
  max_output_tokens=500,
  temperature=0.7,
  model=deployment_name
)

# Extract and print the assistant's message
if response.output and len(response.output) > 0:
    assistant_message = response.output[0].content[0].text
    print("Assistant Response:")
    print(assistant_message)
    
    # Print token usage
    if response.usage:
        print("\nToken Usage:")
        print(f"  Input tokens: {response.usage.input_tokens}")
        print(f"  Output tokens: {response.usage.output_tokens}")
        print(f"  Total tokens: {response.usage.total_tokens}")
else:
    print("Error: Unexpected response structure.")
    print(response.model_dump_json(indent=2))