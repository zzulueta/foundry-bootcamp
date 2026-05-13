from azure.identity import DefaultAzureCredential
from azure.ai.projects import AIProjectClient
from azure.ai.projects.models import PromptAgentDefinition
from dotenv import load_dotenv
import os

# Load environment variables from .env file
load_dotenv()

# Get project endpoint from environment variable
PROJECT_ENDPOINT = os.getenv("PROJECT_ENDPOINT")

# Create project client
project = AIProjectClient(
    endpoint=PROJECT_ENDPOINT,
    credential=DefaultAzureCredential(),
)

print("=" * 60)
print("STEP 1: CREATE AN AGENT")
print("=" * 60)

# Step 1: Create a basic agent
agent = project.agents.create_version(
    agent_name="python-basic-agent",
    definition=PromptAgentDefinition(
        model="gpt-4.1",
        instructions="You are a helpful assistant that specializes in Python programming.",
    ),
)

print(f"✅ Agent created successfully!")
print(f"Agent Name: {agent.name}")
print(f"Agent Version: {agent.version}")

# Get OpenAI client to call the agent
openai = project.get_openai_client()

# Step 2: Create a conversation is OPTIONAL
# In this example, we'll use previous_response_id instead to maintain context

print("\n" + "=" * 60)
print("STEP 3: GENERATE FIRST RESPONSE")
print("=" * 60)

# Step 3: Generate a response using the agent
response1 = openai.responses.create(
    extra_body={
        "agent_reference": {
            "name": agent.name,
            "type": "agent_reference",
        }
    },
    input="What are the key features of Python as a programming language?",
)

# Step 4: Check response status
print(f"Response ID: {response1.id}")
print(f"Status: {response1.status}")

# Step 5: Retrieve the response
print("\nAGENT RESPONSE (Turn 1):")
print("=" * 60)
print(response1.output_text)

print("\n" + "=" * 60)
print("STEP 3-5: GENERATE FOLLOW-UP RESPONSE")
print("=" * 60)
print("Using previous_response_id to maintain context...\n")

# Multi-turn: Use previous_response_id to carry forward context
response2 = openai.responses.create(
    extra_body={
        "agent_reference": {
            "name": agent.name,
            "type": "agent_reference",
        }
    },
    previous_response_id=response1.id,  # Carries forward context from previous response
    input="Can you give me an example of one of those features?",
)

# Check status and retrieve response
print(f"Response ID: {response2.id}")
print(f"Status: {response2.status}")
print("\nAGENT RESPONSE (Turn 2):")
print("=" * 60)
print(response2.output_text)
print("=" * 60)
