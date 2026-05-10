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

# Initialize conversation history with system message
conversation_history = [
    {
        "role": "system",
        "content": "You are a helpful AI assistant."
    }
]

print("Chat with Microsoft Foundry AI Assistant")
print("Type 'quit' or 'exit' to end the conversation.\n")

while True:
    # Get user input
    user_input = input("You: ").strip()
    
    # Check for exit commands
    if user_input.lower() in ['quit', 'exit']:
        print("Goodbye!")
        break
    
    # Skip empty inputs
    if not user_input:
        continue
    
    # Add user message to conversation history
    conversation_history.append({
        "role": "user",
        "content": user_input
    })
    
    try:
        # Send request to the model
        response = client.responses.create(   
            input=conversation_history,
            max_output_tokens=500,
            temperature=0.7,
            model=deployment_name
        )
        
        # Extract the assistant's message
        if response.output and len(response.output) > 0:
            assistant_message = response.output[0].content[0].text
            print(f"\nAssistant: {assistant_message}\n")
            
            # Add assistant response to conversation history
            conversation_history.append({
                "role": "assistant",
                "content": assistant_message
            })
            
            # Print token usage
            if response.usage:
                print(f"[Tokens - Input: {response.usage.input_tokens}, Output: {response.usage.output_tokens}, Total: {response.usage.total_tokens}]\n")
        else:
            print("Error: Unexpected response structure.")
            print(response.model_dump_json(indent=2))
            
    except Exception as e:
        print(f"Error: {str(e)}\n")
