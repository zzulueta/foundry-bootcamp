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

# Create streaming response
stream = client.responses.create(   
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
  model=deployment_name,
  stream=True
)

print("Assistant Response:")
print()

# Process streaming response
full_text = ""
total_tokens = None
input_tokens = None
output_tokens = None

for chunk in stream:
    # Handle different event types in the stream
    if hasattr(chunk, 'type'):
        # Delta events contain the actual text chunks
        if chunk.type == 'response.output_text.delta':
            if hasattr(chunk, 'delta') and chunk.delta:
                print(chunk.delta, end="", flush=True)
                full_text += chunk.delta
        # Completed event contains final metadata like usage
        elif chunk.type == 'response.completed':
            if hasattr(chunk, 'response') and hasattr(chunk.response, 'usage'):
                usage = chunk.response.usage
                total_tokens = usage.total_tokens
                input_tokens = usage.input_tokens
                output_tokens = usage.output_tokens

print("\n")

if total_tokens:
    print(f"\nToken Usage:")
    print(f"  Input tokens: {input_tokens}")
    print(f"  Output tokens: {output_tokens}")
    print(f"  Total tokens: {total_tokens}")
else:
    print("\nStreaming complete!")
