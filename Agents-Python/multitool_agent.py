from azure.identity import DefaultAzureCredential
from azure.ai.projects import AIProjectClient
from azure.ai.projects.models import (
    PromptAgentDefinition, 
    WebSearchTool, 
    CodeInterpreterTool
)
from dotenv import load_dotenv
import os

# Load environment variables from .env file
load_dotenv()

# Get project endpoint from environment
PROJECT_ENDPOINT = os.getenv("PROJECT_ENDPOINT")

# Create project client
project = AIProjectClient(
    endpoint=PROJECT_ENDPOINT,
    credential=DefaultAzureCredential(),
)

print("=" * 60)
print("STEP 1: CREATE AN AGENT WITH TOOLS")
print("=" * 60)

# Step 1: Create an agent with multiple tools
agent = project.agents.create_version(
    agent_name="python-multitool-agent",
    definition=PromptAgentDefinition(
        model="gpt-4.1",
        instructions="""You are a versatile AI assistant with multiple capabilities:
        - Use web search for current information and real-time data
        - Use code interpreter for calculations, data analysis, and code execution
        - Provide clear and accurate answers
        - Cite sources when using web search""",
        tools=[WebSearchTool(), CodeInterpreterTool()],
    ),
)

print(f"✅ Agent created successfully!")
print(f"Agent Name: {agent.name}")
print(f"Agent Version: {agent.version}")
print(f"Tools: Web Search, Code Interpreter\n")

# Get OpenAI client (skipping Step 2: conversation - not needed for these tests)
openai = project.get_openai_client()

# Test 1: Web Search
print("=" * 60)
print("TEST 1: WEB SEARCH (Steps 3-5)")
print("=" * 60)

# Step 3: Generate response
response1 = openai.responses.create(
    extra_body={
        "agent_reference": {
            "name": agent.name,
            "type": "agent_reference",
        }
    },
    input="What are the latest news about Microsoft Azure AI in 2026?",
)

# Step 4: Check status & Step 5: Retrieve output
print(f"Response Status: {response1.status}")
for item in response1.output:
    if item.type == "web_search_call":
        print(f"🔍 [Web Search Tool] Status: {item.status}")
    elif item.type == "message":
        print(f"\n💬 [Assistant Response]")
        print(item.content[0].text)

# Test 2: Code Interpreter
print("\n" + "=" * 60)
print("TEST 2: CODE INTERPRETER (Steps 3-5)")
print("=" * 60)

# Step 3: Generate response
response2 = openai.responses.create(
    extra_body={
        "agent_reference": {
            "name": agent.name,
            "type": "agent_reference",
        }
    },
    input="Calculate the first 10 Fibonacci numbers and show them in a list.",
)

# Step 4: Check status & Step 5: Retrieve output
print(f"Response Status: {response2.status}")
for item in response2.output:
    if item.type == "code_interpreter_call":
        print(f"💻 [Code Interpreter Tool] Status: {item.status}")
    elif item.type == "message":
        print(f"\n💬 [Assistant Response]")
        print(item.content[0].text)

# Test 3: Combined Tools
print("\n" + "=" * 60)
print("TEST 3: COMBINED TOOLS (Steps 3-5)")
print("=" * 60)

# Step 3: Generate response
response3 = openai.responses.create(
    extra_body={
        "agent_reference": {
            "name": agent.name,
            "type": "agent_reference",
        }
    },
    input="Search for the current population of Tokyo and calculate its population density if the city area is 2,194 square kilometers.",
)

# Step 4: Check status & Step 5: Retrieve output
print(f"Response Status: {response3.status}")
for item in response3.output:
    if item.type == "web_search_call":
        print(f"🔍 [Web Search Tool] Status: {item.status}")
    elif item.type == "code_interpreter_call":
        print(f"💻 [Code Interpreter Tool] Status: {item.status}")
    elif item.type == "message":
        print(f"\n💬 [Assistant Response]")
        print(item.content[0].text)

print("=" * 60)
