from azure.identity import DefaultAzureCredential
from azure.ai.projects import AIProjectClient
from dotenv import load_dotenv
import os

# Load environment variables from .env file
load_dotenv()

# Get configuration from environment
PROJECT_ENDPOINT = os.getenv("PROJECT_ENDPOINT")

# Use the agent created in Step 7
AGENT_NAME = "python-multitool-agent"

# Create clients to call Foundry API
project = AIProjectClient(
    endpoint=PROJECT_ENDPOINT,
    credential=DefaultAzureCredential(),
)
openai = project.get_openai_client()

print("=" * 60)
print("STEP 2: CREATE A CONVERSATION (OPTIONAL)")
print("=" * 60)

# Step 2: Create a conversation for multi-turn chat
conversation = openai.conversations.create()
print(f"✅ Conversation created with ID: {conversation.id}")
print("This maintains history across all turns automatically.\n")

# First turn
print("=" * 60)
print("STEP 3-5: TURN 1 (Generate & Retrieve)")
print("=" * 60)
response = openai.responses.create(
    conversation=conversation.id,  # Pass conversation ID
    extra_body={
        "agent_reference": {
            "name": AGENT_NAME,
            "type": "agent_reference",
        }
    },
    input="What is the capital of France?",
)
print(f"Status: {response.status}")
print(f"User: What is the capital of France?")
print(f"Assistant: {response.output_text}\n")

# Follow-up turn in the same conversation
print("=" * 60)
print("STEP 3-5: TURN 2 (Generate & Retrieve)")
print("=" * 60)
follow_up = openai.responses.create(
    conversation=conversation.id,  # Same conversation ID maintains context
    extra_body={
        "agent_reference": {
            "name": AGENT_NAME,
            "type": "agent_reference",
        }
    },
    input="What is the population of that city?",
)
print(f"Status: {follow_up.status}")
print(f"User: What is the population of that city?")
print(f"Assistant: {follow_up.output_text}\n")

# Third turn with a calculation request
print("=" * 60)
print("STEP 3-5: TURN 3 (Generate & Retrieve - with tool use)")
print("=" * 60)
calculation = openai.responses.create(
    conversation=conversation.id,  # Context from all previous turns
    extra_body={
        "agent_reference": {
            "name": AGENT_NAME,
            "type": "agent_reference",
        }
    },
    input="Calculate the population density if the city area is 105 square kilometers.",
)
print(f"Status: {calculation.status}")
print(f"User: Calculate the population density if the city area is 105 square kilometers.")
print(f"Assistant: {calculation.output_text}")
print("=" * 60)
