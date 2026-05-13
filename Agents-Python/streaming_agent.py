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

print("\n" + "=" * 60)
print("STEP 3: GENERATE RESPONSE (STREAMING MODE)")
print("=" * 60)

# Stream a response using the agent
stream = openai.responses.create(
    extra_body={
        "agent_reference": {
            "name": AGENT_NAME,
            "type": "agent_reference",
        }
    },
    input="Explain how agents work in Microsoft Foundry in one paragraph.",
    stream=True,
)

print("\nSTEP 4: CHECK RESPONSE STATUS & STEP 5: RETRIEVE OUTPUT")
print("-" * 60)

# Monitor streaming events and status
response_started = False
for event in stream:
    # Check event type and status
    if hasattr(event, "type"):
        if event.type == "response.started":
            response_started = True
            print(f"[Status: Started] Response ID: {event.id if hasattr(event, 'id') else 'N/A'}")
            print("\n[Streaming Output]:")
        elif event.type == "response.done":
            print(f"\n[Status: Done] Response completed successfully")
    
    # Retrieve and display streaming output
    if hasattr(event, "delta") and event.delta:
        print(event.delta, end="", flush=True)

print("\n" + "=" * 60)
