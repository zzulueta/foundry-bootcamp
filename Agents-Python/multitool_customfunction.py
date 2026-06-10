from azure.identity import DefaultAzureCredential
from azure.ai.projects import AIProjectClient
from azure.ai.projects.models import (
    PromptAgentDefinition, 
    WebSearchTool, 
    CodeInterpreterTool,
    FunctionTool,
    Tool
)
from openai.types.responses.response_input_param import FunctionCallOutput, ResponseInputParam
from dotenv import load_dotenv
import os
import json

# Load environment variables from .env file
load_dotenv()

# Get project endpoint from environment
PROJECT_ENDPOINT = os.getenv("PROJECT_ENDPOINT")

# Create project client
project = AIProjectClient(
    endpoint=PROJECT_ENDPOINT,
    credential=DefaultAzureCredential(),
)

# ============================================================
# CUSTOM FUNCTION DEFINITION
# ============================================================

def get_weather(location: str) -> str:
    """
    Gets weather information for a specified location.
    This is the actual Python function that will be called.
    """
    weather_data = {
        "seattle": "Cloudy, 62°F (17°C), Humidity: 75%, Wind: 8 mph",
        "new york": "Sunny, 75°F (24°C), Humidity: 55%, Wind: 12 mph",
        "london": "Rainy, 58°F (14°C), Humidity: 85%, Wind: 15 mph",
        "tokyo": "Clear, 72°F (22°C), Humidity: 60%, Wind: 5 mph",
        "paris": "Partly Cloudy, 68°F (20°C), Humidity: 65%, Wind: 10 mph"
    }
    
    location_lower = location.lower()
    if location_lower in weather_data:
        return f"Weather in {location}: {weather_data[location_lower]}"
    else:
        return f"Weather in {location}: Sunny, 70°F (21°C), Humidity: 60%, Wind: 10 mph"


# Define the function tool schema for the agent
get_weather_tool = FunctionTool(
    name="get_weather",
    description="Get current weather information for a specified location.",
    parameters={
        "type": "object",
        "properties": {
            "location": {
                "type": "string",
                "description": "The city or location to get weather for (e.g., 'Seattle', 'Tokyo')"
            }
        },
        "required": ["location"],
        "additionalProperties": False
    },
    strict=True
)

print("=" * 60)
print("STEP 1: CREATE AN AGENT WITH TOOLS")
print("=" * 60)

# Step 1: Create an agent with multiple tools
tools: list[Tool] = [WebSearchTool(), CodeInterpreterTool(), get_weather_tool]

agent = project.agents.create_version(
    agent_name="python-multitool-agent",
    definition=PromptAgentDefinition(
        model="gpt-4.1",
        instructions="""You are a versatile AI assistant with multiple capabilities:
        - Use web search for current information and real-time data
        - Use code interpreter for calculations, data analysis, and code execution
        - Use get_weather to provide weather information for any location
        - Provide clear and accurate answers
        - Cite sources when using web search""",
        tools=tools,
    ),
)

print(f"✅ Agent created successfully!")
print(f"Agent Name: {agent.name}")
print(f"Agent Version: {agent.version}")
print(f"Tools: Web Search, Code Interpreter, Custom Function (get_weather)\n")

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

# Test 4: Custom Function
print("\n" + "=" * 60)
print("TEST 4: CUSTOM FUNCTION - GET WEATHER")
print("=" * 60)

# Create a conversation for this test
conversation = openai.conversations.create()

# Step 3: Generate response
response4 = openai.responses.create(
    input="What's the weather like in Seattle?",
    conversation=conversation.id,
    extra_body={
        "agent_reference": {
            "name": agent.name,
            "type": "agent_reference",
        }
    },
)

# Step 4: Process function calls if any
input_list: ResponseInputParam = []
for item in response4.output:
    if item.type == "function_call":
        print(f"🔧 [Custom Function] Calling: {item.name}({item.arguments})")
        if item.name == "get_weather":
            # Execute the actual Python function
            weather = get_weather(**json.loads(item.arguments))
            
            # Provide function call results to the agent
            input_list.append(
                FunctionCallOutput(
                    type="function_call_output",
                    call_id=item.call_id,
                    output=json.dumps({"weather": weather}),
                )
            )

# Step 5: Submit function results and get final response
if input_list:
    response4 = openai.responses.create(
        input=input_list,
        conversation=conversation.id,
        extra_body={
            "agent_reference": {
                "name": agent.name,
                "type": "agent_reference",
            }
        },
    )

# Display final response
print(f"\nResponse Status: {response4.status}")
for item in response4.output:
    if item.type == "message":
        print(f"\n💬 [Assistant Response]")
        print(item.content[0].text)

# Clean up
openai.conversations.delete(conversation_id=conversation.id)

print("=" * 60)
