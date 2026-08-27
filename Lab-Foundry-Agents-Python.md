# Lab: Building Foundry Agents with Python

## Overview
In this hands-on lab, you will learn how to create intelligent AI agents using Microsoft Foundry, both through the portal and programmatically using Python. You'll create agents with tools like Web Search and Code Interpreter, and immediately use them through Python code. This lab demonstrates a streamlined approach to building production-ready AI agents.

**Estimated Time:** 60 minutes

**Prerequisites:**
- An Azure account with an active subscription
- Access to a role that allows you to create Foundry resources (e.g., Azure AI Owner)
- Basic understanding of AI agents and Python programming
- Access to Azure Cloud Shell (included with all Azure subscriptions)

---

## Lab Architecture
By the end of this lab, you will have:
- A Microsoft Foundry resource with a deployed project
- A GPT model deployment for agent responses
- An AI agent created in the Foundry Portal with custom instructions
- Python code that creates a basic agent and uses it immediately
- Python code that creates a multi-tool agent (web search + code interpreter) and demonstrates both capabilities
- Experience with streaming responses and conversation management

---

## How Agent Runtime Components Work Together

Throughout this lab, you'll follow a consistent pattern for working with agents:

1. **Create an agent** - Define an agent with instructions and optional tools
2. **Create a conversation (optional)** - Use a conversation to maintain history, or use `previous_response_id` instead
3. **Generate a response** - Send input to the agent, which processes it using the Foundry model
4. **Check response status** - Monitor the response status (especially important for streaming)
5. **Retrieve the response** - Get the generated output and display it

**You'll see this workflow demonstrated in:**
- **Step 6**: All 5 steps with `previous_response_id` approach (without conversations)
- **Step 8**: Steps 3-5 with streaming and status monitoring
- **Step 9**: All 5 steps with conversations approach (alternative to `previous_response_id`)

---

## Step 1: Setup Azure Resources

### 1.1 Sign in to Azure Portal
1. Navigate to the [Azure Portal](https://portal.azure.com/)
2. Sign in with your Azure account credentials

### 1.2 Create a Resource Group
1. In the Azure Portal, click **Create a resource**
2. Search for **Resource Group** and select it
3. Click **Create**
4. Configure the resource group:
   - **Subscription:** Select your subscription
   - **Resource group name:** `rg-agent-python`
   - **Region:** `Australia East`
5. Click **Review + Create**, then **Create**

---

## Step 2: Setup a Foundry Resource

### 2.1 Create a Foundry Resource
1. In the Azure Portal, click **Create a resource**
2. Search for **Microsoft Foundry** and select it
3. Click **Create**
4. Configure the resource:
   - **Subscription:** Select your subscription
   - **Resource group:** `rg-agent-python`
   - **Name:** `foundry-python-<yourname>` (must be globally unique)
   - **Region:** `Australia East`
   - **Default project name:** `python-agents-project`
5. Click **Review + Create**, then **Create**
6. Wait for the deployment to complete (typically 1-2 minutes)

### 2.2 Access Microsoft Foundry Portal
1. Once deployment completes, click **Go to resource**
2. In the resource overview, click **Go to Foundry Portal** or navigate directly to [https://ai.azure.com/](https://ai.azure.com/)
3. Sign in with your Azure credentials
4. Verify that you are in the **New** Foundry Portal and that your project (`python-agents-project`) is selected in the upper left corner
> Note: If you are in the Old Foundry Portal, you may need to switch to the New Portal using the toggle at the top of the page

### 2.3 Deploy a Model for Your Agent
1. In Microsoft Foundry, navigate to **Build** in the top navigation
2. Select **Models** from the left sidebar
> Note: The Models option may be replaced by the  **Deployments** option in the left sidebar for newer versions of Foundry. If you see Deployments instead of Models, click on Deployments. 
3. Click **Deploy a base model**
4. Search for the **gpt-5.4** model
5. **Select** the model
6. Select **Deploy** > **Custom settings**
7. Configure the deployment:
   - **Deployment name:** `gpt-5.4`
   - **Deployment type:** Select **Global Standard** (pay-per-token, easiest for testing)
   - **Tokens per minute rate limit:** `100000`
8. Click **Deploy**
9. Wait for deployment to complete (typically 1-3 minutes)

### 2.4 Verify Model Deployment
1. Once deployment completes, you should be sent to the Playground with the `gpt-5.4` model selected
2. In the input box, enter a test prompt:
   ```
   What is Microsoft Foundry?
   ```
3. Click **Submit**
4. Verify you receive a coherent response describing Microsoft Foundry

---

## Step 3: Create an AI Agent in Foundry Portal

### 3.1 Navigate to Agent Builder
1. In Microsoft Foundry Portal, navigate to **Build** > **Agents** in the left sidebar
2. Click **New agent** > **Build an agent**

### 3.2 Configure Agent Basics
1. On the **Create an agent** page:
   - **Agent name:** `pythonassistant`
2. Click **Create and open playground**

### 3.3 Configure Agent Instructions
1. In the agent configuration page, navigate to the **Instructions** tab
2. In the **Instructions** field, add detailed instructions:
   ```
   You are a helpful AI assistant specializing in Python programming and general knowledge.

   Guidelines:
   - Provide clear, concise, and accurate answers
   - When asked about current events or web information, use web search
   - When asked to write or execute code, use the code interpreter tool
   - Maintain a professional and friendly tone
   - If a question is ambiguous, ask for clarification
   - Explain your reasoning when appropriate

   When providing answers:
   1. Use web search for current information and real-time data
   2. Use code interpreter for calculations, data analysis, or code execution
   3. Provide clear, actionable answers
   4. Cite sources when using web search
   ```

### 3.4 Verify Tools
1. Navigate to the **Tools** section of the agent configuration
2. Verify that **Web search** is available. Web search should be enabled by default for new agents. If not, click **Add** and enable Web search.
3. Click **Add** to enable the **Code interpreter** tool.
4. Verify that both tools are listed under the agent's tools.

### 3.5 Save Your Agent
1. Click **Save** in the upper right corner

---

## Step 4: Test Your Agent in the Playground

### 4.1 Verify Agent Setup
1. In your agent configuration, you'll see a chat interface on the right side
2. Start with a greeting:
   ```
   Hello! Can you tell me what you can help me with?
   ```
3. Verify the agent responds appropriately and describes its capabilities

### 4.2 Test Web Search
1. Ask a question that requires current information:
   ```
   Give me 3 latest developments in AI technology this week.
   ```
2. Verify the response:
   - ✅ Agent performs a web search
   - ✅ Agent provides current information
   - ✅ Agent cites sources

### 4.3 Test Code Interpreter
1. Ask a question that requires code execution:
   ```
   Simulate rolling two dice 100 times and visualize the results in a chart.
   ```
2. Verify the agent executes code and provides the result

### 4.4 Review Agent Logs
1. Click on the **Traces** at the bottom
2. Review the tool calls performed (web search and code interpreter)

---

## Step 5: Setup Azure Cloud Shell Environment

### 5.1 Open Azure Cloud Shell
1. In the Azure Portal, click the **Cloud Shell** icon in the top navigation bar (looks like `>_`)
2. Select **Bash** as your shell environment
3. Select **No storage account required**
4. Select your **Subscription**
5. Select **Apply**
6. Wait for Cloud Shell to initialize (this may take a minute)
7. Once Cloud Shell opens, you'll see a Bash command prompt

> **Note:** Azure Cloud Shell is a browser-based shell environment with pre-installed tools including Python 3 and pip, which makes it perfect for developing and testing AI agents. No storage account is required for this lab.

### 5.2 Create a Working Directory
1. In Cloud Shell, create a new directory for your Python scripts:
   ```bash
   mkdir ~/foundry-agents-lab
   cd ~/foundry-agents-lab
   ```

### 5.3 Create a Virtual Environment
1. Create a Python virtual environment:
   ```bash
   python -m venv agentenv
   ```
2. Activate the virtual environment:
   ```bash
   source agentenv/bin/activate
   ```
3. Verify the virtual environment is activated (you should see `(agentenv)` in your prompt)

**Why use a virtual environment?**
- ✅ Isolates project dependencies
- ✅ Prevents package conflicts
- ✅ Makes your environment reproducible
- ✅ Allows different Python package versions per project

### 5.4 Install Required Packages
1. Install the Azure AI Projects SDK (with virtual environment activated):
   ```bash
   pip install "azure-ai-projects==2.1.0"
   pip install azure-identity
   pip install openai
   pip install python-dotenv
   ```

### 5.5 Get Your Project Endpoint
1. In the Foundry Portal, select Home from the top navigation bar.
2. Locate and copy the **Project Endpoint**
   - Format: `https://foundry-python-<yourname>.services.ai.azure.com/api/projects/python-agents-project`
3. Save this endpoint for use in your Python code

### 5.6 Create your Environment File
1. In Cloud Shell, create a new file to store environment variables:
   ```bash
   code .env
   ```
2. Add the following to the `.env` file, replacing the URL with your actual project endpoint:
   ```
   PROJECT_ENDPOINT="https://foundry-python-<yourname>.services.ai.azure.com/api/projects/python-agents-project"
   ```
3. Save the file with `Ctrl+S` and close the editor `Ctrl+Q`

### 5.7 Login to Azure from Cloud Shell
1. In Cloud Shell, run the following command to login:
   ```bash
   az login
   ```
2. Follow the instructions to complete the login process (you may need to open a browser and enter a code)
3. Once logged in, select the correct subscription in the terminal then press Enter.

---

## Step 6: Create and Use a Basic Agent

In this step, you'll create a simple agent programmatically and demonstrate the complete workflow: create agent, generate response, check status, and retrieve output. You'll also see how to maintain context across turns without using conversations.

### 6.1 Create and Call a Basic Agent with Multi-Turn Context
1. In Cloud Shell, create a new Python file:
   ```bash
   code basic_agent.py
   ```
2. Add the following code:

```python
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
        model="gpt-5.4",
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
```
> Note: You may copy the code from the basic_agent.py file found in the Agents-Python folder if you want to skip typing it out manually.

3. Run the script:
   ```bash
   python basic_agent.py
   ```
4. Observe the complete workflow: create agent → generate response → check status → retrieve output


**Key Concepts:**
- ✅ **Step 1**: Agent creation returns an agent object with `name` and `version`
- ✅ **Step 2**: Conversations are optional - you can use `previous_response_id` instead
- ✅ **Step 3**: Generate responses by passing agent reference in `extra_body`
- ✅ **Step 4**: Check response status with `response.status` and `response.id`
- ✅ **Step 5**: Retrieve output with `response.output_text`
- ✅ Use `previous_response_id` to maintain context across turns without conversations

---

## Step 7: Create and Use an Agent with Tools

In this step, you'll create an agent with both Web Search and Code Interpreter tools, then demonstrate both capabilities.

### 7.1 Create an Agent with Multiple Tools
1. In Cloud Shell, create a new Python file:
   ```bash
   code multitool_agent.py
   ```
2. Add the following code:

```python
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
        model="gpt-5.4",
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
```
> Note: You may copy the code from the multitool_agent.py file found in the Agents-Python folder if you want to skip typing it out manually.
3. Save the file with `Ctrl+S`
4. Ensure your `.env` file has the correct `PROJECT_ENDPOINT` configured
5. Run the script:
   ```bash
   python multitool_agent.py
   ```
6. Observe the agent using different tools for different tasks

**Key Concepts:**
- ✅ **Step 1**: Create agent with multiple tools: `WebSearchTool()` and `CodeInterpreterTool()`
- ✅ **Steps 3-5**: Generate → Check Status → Retrieve pattern repeated for each test
- ✅ The agent automatically selects the appropriate tool based on the query
- ✅ Tool calls are visible in `response.output` with type indicators
- ✅ Check tool status with `item.status` for web search and code interpreter
- ✅ Web search provides current information with citations
- ✅ Code interpreter executes Python code for calculations
- ✅ Both tools can be used together in a single query

---

## Step 8: Streaming Responses

In this step, you'll learn how to stream responses in real-time and monitor response status during streaming.

### 8.1 Stream a Response with Status Monitoring
1. In Cloud Shell, create a new Python file:
   ```bash
   code streaming_agent.py
   ```
2. Add the following code:

```python
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
```
> Note: You may copy the code from the streaming_agent.py file found in the Agents-Python folder if you want to skip typing it out manually.
3. Save the file with `Ctrl+S`
4. Make sure you've run `multitool_agent.py` from Step 7 first to create the agent
5. Run the script:
   ```bash
   python streaming_agent.py
   ```
6. Observe the response streaming in real-time with status updates

**Key Concepts:**
- ✅ Used an existing agent with tools for streaming demonstration
- ✅ Set `stream=True` to enable streaming responses
- ✅ Monitor event types: `response.started`, `response.done`, etc.
- ✅ Check response status throughout the streaming process
- ✅ Iterate through the stream to get incremental deltas
- ✅ Use `flush=True` to display text immediately
- ✅ Streaming is ideal for long responses and real-time user feedback
- ✅ Streaming provides better user experience for long responses

---

## Step 9: Using Conversations for Multi-Turn Context

In this step, you'll learn how to use conversations (Step 2 of the agent workflow) to maintain context across multiple turns. This is an alternative to using `previous_response_id` as shown in Step 6.

### 9.1 Create and Use a Conversation
1. In Cloud Shell, create a new Python file:
   ```bash
   code conversation_agent.py
   ```
2. Add the following code:

```python
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
```
> Note: You may copy the code from the conversation_agent.py file found in the Agents-Python folder if you want to skip typing it out manually.
3. Save the file with `Ctrl+S`
4. Make sure you've run `multitool_agent.py` from Step 7 first to create the agent
5. Run the script:
   ```bash
   python conversation_agent.py
   ```

**Key Concepts:**
- ✅ **Step 2**: Use `conversations.create()` to create a conversation thread
- ✅ **Step 3-5**: Pass `conversation=conversation.id` to maintain context automatically
- ✅ No need to use `previous_response_id` - conversation manages history
- ✅ All previous turns are automatically available to the agent
- ✅ Agent remembers previous turns automatically
- ✅ Useful for chatbot and multi-turn scenarios
- ✅ Agent can use tools (web search, code interpreter) across turns

---

## Step 10: Call Published Agent via OpenAI SDK

### 10.1 Publish Your Agent
1. In the Foundry Portal, select **Build**.
2. Select **Agents** and navigate to your agent (`python-multitool-agent`)
3. Select **Publish** in the upper right.
4. Copy the **Endpoint (Responses)** endpoint URL
   - Format: `https://foundry-python-<yourname>.services.ai.azure.com/api/projects/python-agents-project/agents/python-multitool-agent/endpoint/protocols/openai/v1/responses`
5. Update your `.env` file to add the BASE_URL:
   ```bash
   code .env
   ```
6. Add this line to your `.env` file with your actual endpoint:
   ```
   BASE_URL="https://foundry-python-<yourname>.services.ai.azure.com/api/projects/python-agents-project/agents/python-multitool-agent/endpoint/protocols/openai"
   ```
   > **Important:** The `BASE_URL` should stop before `/v1/responses` because the OpenAI SDK will append that path internally when making requests.
7. Save with `Ctrl+S`

### 10.2 Call Published Agent (Streaming)
1. In Cloud Shell, create a new Python file:
   ```bash
   code call_published_agent.py
   ```
2. Add the following code:

```python
from openai import OpenAI
from azure.identity import DefaultAzureCredential
import os
from dotenv import load_dotenv
load_dotenv()  # Load environment variables from .env file if needed

# 1) Get Entra ID token (same audience as az account get-access-token --resource https://ai.azure.com)
credential = DefaultAzureCredential()
token = credential.get_token("https://ai.azure.com/.default")  # aligns with Foundry data-plane audience [2](https://github.com/MicrosoftDocs/azure-ai-docs/blob/main/articles/foundry/agents/how-to/manage-hosted-agent.md)
BASE_URL = os.getenv("BASE_URL") 
# 2) IMPORTANT: base_url must stop BEFORE "/v1/responses"
#    Because the SDK will call POST {base_url}/v1/responses internally.

client = OpenAI(
    api_key=token.token,  # sent as "Authorization: Bearer <token>"
    base_url=BASE_URL,
    default_query={"api-version": "2025-11-15-preview"},
    default_headers={"Foundry-Features": "AgentEndpoints=V1Preview"},
)

# 3) Invoke the agent
stream = client.responses.create(
    input="Give me 5 benefits of Microsoft Foundry in bullet points.",
    stream=True
)


print("\n" + "=" * 60)
print("CALLING PUBLISHED AGENT:")
print("=" * 60)

# Should iterate through streaming events and print the response as it comes in
for event in stream:
    if event.type == "response.output_text.delta":
        print(event.delta, end="", flush=True)

print()  # newline at end

```
> Note: You may copy the code from the call_published_agent.py file found in the Agents-Python folder if you want to skip typing it out manually.
3. Save the file with `Ctrl+S`
4. Run the script:
   ```bash
   python call_published_agent.py
   ```

### 10.3 Calling the Published Agent via CURL
You can also call the published agent using CURL from the Cloud Shell. Here's how:
1. First, get an access token using Azure CLI:
```bash
TOKEN=$(az account get-access-token --resource https://ai.azure.com --query accessToken -o tsv)
echo "${#TOKEN}"   # should print a non-zero length
```
> Note: You must be logged in to Azure CLI (via az login) and have the appropriate permissions (Azure AI User) to get an access token. The token will be used for authentication when calling the published agent.
2. Use the following CURL command to call the published agent, replacing `<BASE_URL>` with your actual values:
```bash
curl -i --fail-with-body -X POST \
"<BASE_URL>/responses?api-version=2025-11-15-preview" \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -H "Foundry-Features: AgentEndpoints=V1Preview" \
  -d '{"input": "What are the benefits of using Microsoft Foundry?"}'
```
> Note: Remove `/v1/responses` from the BASE_URL when using it in the CURL command, as the path is included in the command itself.

Sample:
```bash
curl -i --fail-with-body -X POST \
"https://foundry-python-ziggy.services.ai.azure.com/api/projects/python-agents-project/agents/python-multitool-agent/endpoint/protocols/openai/responses?api-version=2025-11-15-preview" \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -H "Foundry-Features: AgentEndpoints=V1Preview" \
  -d '{"input":"What are the benefits of using Microsoft Foundry?"}'
```  
3. You should receive a response from the agent with a full JSON payload containing the agent's answer to the question.

### 10.4 Understanding Published Agents
Published agents expose an OpenAI-compatible API endpoint that:
- ✅ Requires Azure RBAC authentication (Azure AI User role)
- ✅ Requires client-side conversation history management
- ✅ Can be consumed from any application with proper credentials
- ✅ Provides a managed, scalable API endpoint

> **Note:** Published agents are ideal for production scenarios where you need a managed API endpoint without maintaining server infrastructure.

---

## Verification Checklist

**Portal Setup:**
- [ ] Foundry resource created successfully
- [ ] GPT model deployed in Foundry
- [ ] Agent created in Portal with instructions configured
- [ ] Agent tested successfully in playground with web search
- [ ] Agent tested successfully in playground with code interpreter
- [ ] Azure Cloud Shell opened and packages installed

**Agent Workflow Pattern (Steps 1-5):**
- [ ] Step 1: Created agents programmatically with Python
- [ ] Step 2: Used both `previous_response_id` and `conversations` approaches
- [ ] Step 3: Generated responses using agent references
- [ ] Step 4: Checked response status during processing
- [ ] Step 5: Retrieved and displayed agent output

**Tool Capabilities:**
- [ ] Multi-tool agent (web search + code interpreter) created and used successfully
- [ ] Web search tool demonstrated successfully
- [ ] Code interpreter tool demonstrated successfully

**Advanced Features:**
- [ ] Successfully streamed responses with status monitoring
- [ ] Successfully used conversations for context management
- [ ] Successfully published and called agent via OpenAI SDK

---

## Clean Up Resources

To avoid incurring charges, delete the resources when you're finished with the lab:

1. In the Azure Portal, navigate to **Resource groups**
2. Select `rg-agent-python`
3. Click **Delete resource group**
4. Type the resource group name to confirm
5. Click **Delete**

> **Note:** This will delete all resources including Foundry and deployed models.

---

## Summary and Key Takeaways

In this lab, you successfully:

1. ✅ Created a Foundry resource and deployed a GPT model
2. ✅ Created an AI agent in the Foundry Portal with custom instructions
3. ✅ Tested the agent with web search and code interpreter tools
4. ✅ Setup Azure Cloud Shell with required Azure SDK packages
5. ✅ **Mastered the 5-step agent workflow pattern:**
   - Step 1: Create an agent
   - Step 2: Create a conversation (optional)
   - Step 3: Generate a response
   - Step 4: Check response status
   - Step 5: Retrieve the response
6. ✅ Created and used agents programmatically with Python
7. ✅ Demonstrated both context management approaches (`previous_response_id` and `conversations`)
8. ✅ Created multi-tool agents with Web Search and Code Interpreter
9. ✅ Monitored tool execution status and inspected outputs
10. ✅ Implemented streaming responses with status monitoring
11. ✅ Published agent and consumed it via OpenAI SDK

### Key Concepts

**Agent Runtime Workflow:**
- **Step 1**: Create agents with instructions and tools
- **Step 2**: Use conversations OR `previous_response_id` for context
- **Steps 3-5**: Generate → Check Status → Retrieve pattern for all interactions
- **Streaming**: Monitor event types and status throughout the stream

**Agent Creation Patterns:**
- **Portal-based:** Quick visual creation with UI configuration
- **SDK-based:** Programmatic creation with version control and automation
- **Published:** Managed API endpoints for production consumption

**Tool Integration:**
- **Web Search:** Enables agents to access current information
- **Code Interpreter:** Enables agents to execute Python code
- **Multi-tool:** Agents can use multiple tools based on context

**Response Patterns:**
- **Synchronous:** Wait for complete response before continuing
- **Streaming:** Receive partial results in real-time
- **Background:** Long-running tasks executed asynchronously

**Conversation Management:**
- **Server-side:** Use conversations for managed history
- **Client-side:** Manage context manually for full control
- **Published agents:** Always client-side with `store=False`

### Best Practices

1. **Authentication:** Cloud Shell automatically authenticates with `DefaultAzureCredential()`
2. **Tool Selection:** Choose tools based on agent purpose (web search for current info, code interpreter for calculations)
3. **Streaming:** Use streaming for better user experience with long responses
4. **Conversations:** Use conversations for multi-turn context when server-side storage is acceptable
5. **Published Agents:** Use for production APIs with RBAC security
6. **Cloud Shell:** Use the built-in `code` editor command for a full-featured editing experience

### Production Considerations

**When to Use Published Agents:**
- ✅ Need a managed, scalable API endpoint
- ✅ Want to integrate with non-Azure applications
- ✅ Require RBAC-based security
- ✅ Need OpenAI-compatible protocol

**When to Use SDK Directly:**
- ✅ Building Azure-native applications
- ✅ Need full control over conversation storage
- ✅ Want to use all SDK features (not just responses)
- ✅ Developing in Python, C#, or JavaScript

---

## Additional Resources

- [Microsoft Foundry Agents Documentation](https://learn.microsoft.com/en-us/azure/foundry/agents/)
- [Azure AI Projects SDK for Python](https://learn.microsoft.com/en-us/python/api/overview/azure/ai-projects-readme)
- [Foundry Tools Catalog](https://learn.microsoft.com/en-us/azure/foundry/agents/concepts/tool-catalog)
- [Responses API Documentation](https://learn.microsoft.com/en-us/azure/foundry/openai/how-to/responses)

---

## Lab Completion Badge

Congratulations! 🎉 You have completed the **Microsoft Foundry Agents with Python** lab.

You now have hands-on experience with:
- Creating and configuring AI agents in Microsoft Foundry Portal
- Building agents programmatically with the Azure AI Projects Python SDK
- Integrating tools (Web Search, Code Interpreter) into agents
- Calling agents programmatically with various patterns
- Implementing streaming responses and conversation management
- Publishing and consuming agents via OpenAI-compatible APIs

---

**End of Lab**
