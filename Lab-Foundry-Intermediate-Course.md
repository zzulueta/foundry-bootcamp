# Lab: Building & Grounding Foundry Agents (Intermediate Course)

## Overview
In this intermediate, hands-on course you will build a complete picture of working with Microsoft Foundry agents — from calling a raw model, to building agents in the portal and with Python, to publishing an agent as an API, and finally grounding an agent in your own data using Retrieval-Augmented Generation (RAG).

You will work through five modules that build on a **single shared Foundry resource**, so you deploy your model once and reuse it throughout.

**Estimated Time:** ~3 hours (~185 minutes)

**Level:** Intermediate

**Prerequisites:**
- An Azure account with an active subscription
- Access to a role that allows you to create Foundry resources (e.g., Azure AI Owner)
- Basic understanding of AI agents, Python, and REST APIs
- Access to Azure Cloud Shell (included with all Azure subscriptions)
- Sample documents to upload to your knowledge base (provided in the Product Data folder)

---

## Course Architecture
By the end of this course, you will have:
- A Microsoft Foundry resource with a deployed project (used across all modules)
- A `gpt-4.1` model and a `text-embedding-3-large` embedding model deployed in Foundry
- Experience calling the **model** directly via curl (API key auth)
- An AI agent built in the Foundry Portal with Web Search + Code Interpreter
- Python scripts that create and call agents (basic, multi-tool, streaming, conversations)
- A **published agent** exposed as an OpenAI-compatible API, called via SDK and curl (bearer token auth)
- An Azure Storage account + Azure AI Search service powering a Foundry IQ knowledge base
- A RAG-grounded agent that answers questions from your documents with citations

### Shared Resource Naming
Use these names consistently throughout the course (replace `<yourname>` with your initials or alias):

| Resource | Name |
|---|---|
| Resource group | `rg-foundry-intermediate` |
| Region | `Australia East or France Central` |
| Foundry resource | `foundry-int-<yourname>` |
| Default project | `intermediate-project` |
| Chat model deployment | `gpt-4.1` |
| Embedding model deployment | `text-embedding-3-large` |
| Storage account | `stfoundryint<yourname>` |
| Azure AI Search service | `search-foundry-int-<yourname>` |

---

## How Agent Runtime Components Work Together
Throughout the Python modules, you'll follow a consistent pattern for working with agents:

1. **Create an agent** — Define an agent with instructions and optional tools
2. **Create a conversation (optional)** — Use a conversation to maintain history, or use `previous_response_id` instead
3. **Generate a response** — Send input to the agent, which processes it using the Foundry model
4. **Check response status** — Monitor the response status (especially important for streaming)
5. **Retrieve the response** — Get the generated output and display it

You'll see this workflow demonstrated in Modules 3 and 4.

---
---

# Module 1 — Foundation & Model Basics
**Estimated time:** ~25 minutes

In this module you create the shared Foundry resource, deploy your chat model, and confirm it responds to a raw REST call via curl. This raw model call becomes a useful baseline for understanding what an agent adds on top later.

## Step 1.1: Sign in to Azure Portal
1. Navigate to the [Azure Portal](https://portal.azure.com/)
2. Sign in with your Azure account credentials

## Step 1.2: Create a Resource Group
1. In the Azure Portal, click **Create a resource**
2. Search for **Resource Group** and select it
3. Click **Create**
4. Configure the resource group:
   - **Subscription:** Select your subscription
   - **Resource group name:** `rg-foundry-intermediate`
   - **Region:** `Australia East or France Central`
5. Click **Review + Create**, then **Create**

## Step 1.3: Create a Foundry Resource
1. In the Azure Portal, click **Create a resource**
2. Search for **Microsoft Foundry** and select it
3. Click **Create**
4. Configure the resource:
   - **Subscription:** Select your subscription
   - **Resource group:** `rg-foundry-intermediate`
   - **Name:** `foundry-int-<yourname>` (must be globally unique)
   - **Region:** `Australia East or France Central`
   - **Default project name:** `intermediate-project`
5. Click **Review + Create**, then **Create**
6. Wait for the deployment to complete (typically 1-2 minutes)

## Step 1.4: Access Microsoft Foundry Portal
1. Once deployment completes, click **Go to resource**
2. In the resource overview, click **Go to Foundry Portal** or navigate directly to [https://ai.azure.com/](https://ai.azure.com/)
3. Sign in with your Azure credentials
4. Verify that you are in the **New** Foundry Portal and that your project (`intermediate-project`) is selected in the upper left corner
   > **Note:** If you are in the Old Foundry Portal, switch to the New Portal using the toggle at the top of the page.

## Step 1.5: Deploy the gpt-4.1 Model
1. In Microsoft Foundry, navigate to **Build** in the top navigation
2. Select **Models** from the left sidebar. **Note:** Some user may see "Deployments" instead of "Models" — this is the same place, just different naming based on your Foundry version.
3. Click **Deploy a base model**
4. Search for the **gpt-4.1** model
5. **Select** the model
6. Select **Deploy** > **Custom settings**
7. Configure the deployment:
   - **Deployment name:** `gpt-4.1`
   - **Deployment type:** Select **Global Standard** (pay-per-token, easiest for testing)
   - **Tokens per minute rate limit:** `50000`
8. Click **Deploy**
9. Wait for deployment to complete (typically 1-3 minutes)

## Step 1.6: Verify the Model in the Playground
1. Once deployment completes, you should be sent to the Playground with the `gpt-4.1` model selected
2. In the input box, enter a test prompt:
   ```
   What is Microsoft Foundry?
   ```
3. Click **Submit**
4. Verify you receive a coherent response describing Microsoft Foundry

## Step 1.7: Deploy the DeepSeek-V3.1 Model
To experience working with more than one model family, deploy a second model — DeepSeek-V3.1 — into the same Foundry resource. You'll reuse this later to compare model responses from Python.
1. In Microsoft Foundry, navigate to **Build** > **Models**
2. Click **Deploy a base model**
3. Search for the **DeepSeek-V3.1** model
4. **Select** the model
5. Select **Deploy** > **Custom settings**
> Note: If a dialog box appears asking you to accepts terms of use, select **Agree and proceed** to continue with the deployment
6. Configure the deployment:
   - **Deployment name:** `DeepSeek-V3.1`
   - **Deployment type:** Select **Global Standard**
   - **Tokens per minute rate limit:** `50000`
7. Click **Deploy**
8. Wait for deployment to complete (typically 1-3 minutes)
9. Once deployment completes, you should be sent to the Playground with the `DeepSeek-V3.1` model selected
10. In the input box, enter a test prompt:
    ```
    What is Microsoft Foundry?
    ```
11. Click **Submit**
12. Verify you receive a coherent response describing Microsoft Foundry


## Step 1.8: Call the Model Directly via curl (Warm-Up)
Before working with agents, confirm the deployed model responds to a raw REST call. This calls the **model** directly (no agent, no SDK) using the Foundry Azure OpenAI endpoint with an **API key** — a useful baseline you'll contrast against the agent call in Module 4.

### 1.7.1 Get the Model Endpoint and Key
1. In the Foundry Portal, select **Home** from the top navigation
2. Copy your **Azure OpenAI endpoint** — it looks like:
   ```
   https://foundry-int-<yourname>.openai.azure.com/openai/v1
   ```
3. In the same location, copy the **API Key**
4. Keep both handy for the next step

> **Note:** Keep your API key secure and never commit it to version control. In production, use Azure Key Vault or environment variables.

### 1.7.2 Open Cloud Shell and Set Variables
1. In the Azure Portal, click the **Cloud Shell** icon (`>_`) in the top navigation bar
2. Select **Bash**, choose **No storage account required**, select your subscription, and click **Apply**
3. Once Cloud Shell opens, set up your values (replace the placeholders):
   ```bash
   # From Step 1.7.1
   MODEL_ENDPOINT="https://foundry-int-<yourname>.openai.azure.com/openai/v1"
   MODEL_KEY="YOUR_API_KEY_HERE"
   DEPLOYMENT_NAME="gpt-4.1"
   ```

### 1.7.3 Call the Model
Run the following curl command to send a prompt directly to the model:
```bash
curl -X POST "${MODEL_ENDPOINT}/responses" \
  -H "Content-Type: application/json" \
  -H "api-key: ${MODEL_KEY}" \
  -d '{
    "model": "'"${DEPLOYMENT_NAME}"'",
    "input": "What are the top 3 benefits of using Microsoft Foundry? Keep it concise.",
    "max_output_tokens": 300
  }' | jq '.'
```

> **Note:** The `| jq '.'` formats the JSON response for readability. If `jq` is unavailable, remove it.

### 1.7.4 Verify the Response
Confirm that:
- ✅ You receive a `200 OK` response
- ✅ The JSON contains an `output` array with the model's answer text
- ✅ A `usage` block reports input/output/total tokens

**Key takeaway:** This curl hits the **model** endpoint directly using an **API key**. In Module 4, you'll call a **published agent** at a different endpoint using an **Entra ID bearer token** — notice how the auth method and URL differ between a raw model and an agent.

---
---

# Module 2 — Build an Agent in the Portal
**Estimated time:** ~20 minutes

Now you'll build your first agent visually in the Foundry Portal and give it two built-in tools: Web Search and Code Interpreter.

## Step 2.1: Navigate to Agent Builder
1. In Microsoft Foundry Portal, navigate to **Build** > **Agents** in the left sidebar
2. Click **Create agent**

## Step 2.2: Configure Agent Basics
1. On the **Create an agent** page:
   - **Agent name:** `pythonassistant`
2. Click **Create and open playground**

## Step 2.3: Configure Agent Instructions
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

## Step 2.4: Verify Tools
1. Navigate to the **Tools** section of the agent configuration
2. Verify that **Web search** is available. Web search should be enabled by default for new agents. If not, click **Add** and enable Web search.
3. Click **Add** to enable the **Code interpreter** tool.
4. Verify that both tools are listed under the agent's tools.

## Step 2.5: Save Your Agent
1. Click **Save** in the upper right corner

## Step 2.6: Test Your Agent in the Playground
1. In your agent configuration, you'll see a chat interface on the right side
2. Start with a greeting:
   ```
   Hello! Can you tell me what you can help me with?
   ```
3. Verify the agent responds appropriately and describes its capabilities

### Test Web Search
1. Ask a question that requires current information:
   ```
   What are the latest developments in AI technology this week?
   ```
2. Verify the response:
   - ✅ Agent performs a web search
   - ✅ Agent provides current information
   - ✅ Agent cites sources

### Test Code Interpreter
1. Ask a question that requires code execution:
   ```
   Calculate the factorial of 10 and show me the Python code
   ```
2. Verify the agent executes code and provides the result

### Test Both Tools Together
1. Ask a question that requires both web search and code execution in a single query:
   ```
   Search for the current population of Tokyo and calculate its population density if the city area is 2,194 square kilometers.
   ```
2. Verify the response:
   - ✅ Agent performs a web search to find the current population
   - ✅ Agent uses the code interpreter to calculate the population density
   - ✅ Agent combines both results into a single answer with sources cited

## Step 2.7: Review Agent Logs
1. Click on the **Logs** at the bottom
2. Review the tool calls performed (web search and code interpreter)

---
---

# Module 3 — Build Agents Programmatically with Python
**Estimated time:** ~35 minutes

In this module you'll create and call agents from code using the Azure AI Projects SDK — covering basic agents, multi-tool agents, streaming, and conversations.

## Step 3.1: Setup Azure Cloud Shell Environment
1. In the Azure Portal, click the **Cloud Shell** icon (`>_`) in the top navigation bar
2. Select **Bash** as your shell environment
3. Select **No storage account required**
4. Select your **Subscription** and click **Apply**
5. Wait for Cloud Shell to initialize

### 3.1.1 Create a Working Directory
```bash
mkdir ~/foundry-agents-lab
cd ~/foundry-agents-lab
```

### 3.1.2 Create and Activate a Virtual Environment
```bash
python -m venv agentenv
source agentenv/bin/activate
```
Verify the virtual environment is activated (you should see `(agentenv)` in your prompt).

**Why use a virtual environment?**
- ✅ Isolates project dependencies
- ✅ Prevents package conflicts
- ✅ Makes your environment reproducible
- ✅ Allows different Python package versions per project

### 3.1.3 Install Required Packages
```bash
pip install "azure-ai-projects==2.1.0"
pip install azure-identity
pip install openai
pip install python-dotenv
```

### 3.1.4 Get Your Project Endpoint
1. In the Foundry Portal, select **Home** from the top navigation bar
2. Locate and copy the **Project Endpoint**
   - Format: `https://foundry-int-<yourname>.services.ai.azure.com/api/projects/intermediate-project`
3. Save this endpoint for use in your Python code

### 3.1.5 Create your Environment File
1. In Cloud Shell, create a new file:
   ```bash
   code .env
   ```
2. Add the following to the `.env` file, replacing the URL with your actual project endpoint:
   ```
   PROJECT_ENDPOINT="https://foundry-int-<yourname>.services.ai.azure.com/api/projects/intermediate-project"
   ```
3. Save the file with `Ctrl+S` and close the editor with `Ctrl+Q`

### 3.1.6 Login to Azure from Cloud Shell
1. Run:
   ```bash
   az login
   ```
2. Follow the instructions to complete login (you may need to open a browser and enter a code)
3. Once logged in, select the correct subscription in the terminal then press Enter

## Step 3.2: Create and Use a Basic Agent
You'll create a simple agent and demonstrate the complete workflow: create agent, generate response, check status, retrieve output — maintaining context across turns without using conversations.

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
```

3. Run the script:
   ```bash
   python basic_agent.py
   ```
4. Observe the complete workflow: create agent → generate response → check status → retrieve output

**Key Concepts:**
- ✅ **Step 1**: Agent creation returns an agent object with `name` and `version`
- ✅ **Step 2**: Conversations are optional — you can use `previous_response_id` instead
- ✅ **Step 3**: Generate responses by passing agent reference in `extra_body`
- ✅ **Step 4**: Check response status with `response.status` and `response.id`
- ✅ **Step 5**: Retrieve output with `response.output_text`

## Step 3.3: Create and Use an Agent with Multiple Tools
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
```

3. Save the file with `Ctrl+S`
4. Ensure your `.env` file has the correct `PROJECT_ENDPOINT` configured
5. Run the script:
   ```bash
   python multitool_agent.py
   ```
6. Observe the agent using different tools for different tasks

**Key Concepts:**
- ✅ **Step 1**: Create agent with multiple tools: `WebSearchTool()` and `CodeInterpreterTool()`
- ✅ The agent automatically selects the appropriate tool based on the query
- ✅ Tool calls are visible in `response.output` with type indicators
- ✅ Both tools can be used together in a single query

## Step 3.4: Streaming Responses
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

# Use the agent created in Step 3.3
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

3. Save the file with `Ctrl+S`
4. Run the script:
   ```bash
   python streaming_agent.py
   ```
5. Observe the response streaming in real-time with status updates

**Key Concepts:**
- ✅ Set `stream=True` to enable streaming responses
- ✅ Monitor event types: `response.started`, `response.done`, etc.
- ✅ Iterate through the stream to get incremental deltas
- ✅ Use `flush=True` to display text immediately

## Step 3.5: Using Conversations for Multi-Turn Context
This is an alternative to `previous_response_id` (used in Step 3.2). Conversations maintain history automatically.

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

# Use the agent created in Step 3.3
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

3. Save the file with `Ctrl+S`
4. Run the script:
   ```bash
   python conversation_agent.py
   ```

**Key Concepts:**
- ✅ **Step 2**: Use `conversations.create()` to create a conversation thread
- ✅ Pass `conversation=conversation.id` to maintain context automatically
- ✅ All previous turns are automatically available to the agent
- ✅ Useful for chatbot and multi-turn scenarios

---
---

# Module 4 — Publish & Call the Agent via curl
**Estimated time:** ~15 minutes

In this module you'll publish your multi-tool agent as a managed, OpenAI-compatible API endpoint, then call it via both the OpenAI SDK and curl. Note the auth difference from Module 1: the **agent** endpoint requires an **Entra ID bearer token**, not an API key.

## Step 4.1: Publish Your Agent
1. In the Foundry Portal, select **Build**
2. Select **Agents** and navigate to your agent (`python-multitool-agent`)
3. Select **Publish** in the upper right
4. Copy the **Endpoint (Responses)** endpoint URL
   - Format: `https://foundry-int-<yourname>.services.ai.azure.com/api/projects/intermediate-project/agents/python-multitool-agent/endpoint/protocols/openai/v1/responses`
5. Update your `.env` file to add the BASE_URL:
   ```bash
   code .env
   ```
6. Add this line to your `.env` file with your actual endpoint:
   ```
   BASE_URL="https://foundry-int-<yourname>.services.ai.azure.com/api/projects/intermediate-project/agents/python-multitool-agent/endpoint/protocols/openai"
   ```
   > **Important:** The `BASE_URL` should stop before `/v1/responses` because the OpenAI SDK will append that path internally when making requests.
7. Save with `Ctrl+S`

## Step 4.2: Call the Published Agent via OpenAI SDK (Streaming)
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
token = credential.get_token("https://ai.azure.com/.default")  # aligns with Foundry data-plane audience
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

3. Save the file with `Ctrl+S`
4. Run the script:
   ```bash
   python call_published_agent.py
   ```

## Step 4.3: Call the Published Agent via curl
You can also call the published agent using curl from Cloud Shell.

1. First, get an access token using Azure CLI:
   ```bash
   TOKEN=$(az account get-access-token --resource https://ai.azure.com --query accessToken -o tsv)
   echo "${#TOKEN}"   # should print a non-zero length
   ```
   > **Note:** You must be logged in to Azure CLI (via `az login`) and have the appropriate permissions (Azure AI User) to get an access token.

2. Use the following curl command to call the published agent, replacing `<BASE_URL>` with your actual value:
   ```bash
   curl -i --fail-with-body -X POST \
   "<BASE_URL>/responses?api-version=2025-11-15-preview" \
     -H "Authorization: Bearer $TOKEN" \
     -H "Content-Type: application/json" \
     -H "Foundry-Features: AgentEndpoints=V1Preview" \
     -d '{"input": "What are the benefits of using Microsoft Foundry?"}'
   ```
   > **Note:** Remove `/v1/responses` from the BASE_URL when using it in the curl command, as the path is included in the command itself.

   Sample:
   ```bash
   curl -i --fail-with-body -X POST \
   "https://foundry-int-<yourname>.services.ai.azure.com/api/projects/intermediate-project/agents/python-multitool-agent/endpoint/protocols/openai/responses?api-version=2025-11-15-preview" \
     -H "Authorization: Bearer $TOKEN" \
     -H "Content-Type: application/json" \
     -H "Foundry-Features: AgentEndpoints=V1Preview" \
     -d '{"input":"What are the benefits of using Microsoft Foundry?"}'
   ```
3. You should receive a response from the agent with a full JSON payload containing the agent's answer

## Step 4.4: Compare Model vs Agent Invocation
Reflect on the contrast between Module 1 and Module 4:

| | **Model call (Step 1.7)** | **Agent call (Step 4.3)** |
|---|---|---|
| Endpoint | Azure OpenAI model endpoint | Published agent (Responses) endpoint |
| Auth | `api-key` header (API key) | `Authorization: Bearer` (Entra ID token) |
| What runs | Just the model | Agent instructions + tools + model |
| Identity | Resource key | Azure RBAC (Azure AI User role) |

**Understanding Published Agents:** A published agent exposes an OpenAI-compatible API endpoint that requires Azure RBAC authentication, supports client-side conversation history management, can be consumed from any application with proper credentials, and provides a managed, scalable endpoint — ideal for production.

---
---

# Module 5 — Ground an Agent in Your Data (RAG)
**Estimated time:** ~55 minutes

In this final module you'll build a knowledge base from your own documents using Azure Storage, Azure AI Search, and Foundry IQ — then connect it to an agent so it answers questions with citations (Retrieval-Augmented Generation).

## Step 5.1: Create an Azure Storage Account
1. In the Azure Portal, click **Create a resource**
2. Search for **Storage Account** and select it
3. Click **Create**
4. Configure the storage account:
   - **Subscription:** Select your subscription
   - **Resource group:** `rg-foundry-intermediate`
   - **Storage account name:** `stfoundryint<yourname>` (must be globally unique, lowercase, no hyphens)
   - **Region:** `Australia East or France Central`
   - **Preferred storage type:** `Azure Blob Storage or Azure Data Lake Storage Gen2`
   - **Performance:** Standard
   - **Redundancy:** Locally-redundant storage (LRS)
5. Click **Review + Create**, then **Create**
6. Wait for deployment to complete, then click **Go to resource**

## Step 5.2: Create Containers and Upload Sample Documents
1. In your storage account, navigate to **Data storage** > **Containers** in the left menu
2. Click **+ Container**
3. Configure the container:
   - **Name:** `manuals`
   - **Public access level:** Private (no anonymous access)
4. Click **Create**
5. Click on the **manuals** container
6. Click **Upload**
7. Upload manuals data from the Product Data folder of this repository
8. Click **Upload** and wait for completion
9. Repeat steps 2-8 to create another container named `reviews` and upload reviews data from the Product Data folder

## Step 5.3: Create an Azure AI Search Service
1. In the Azure Portal, click **Create a resource**
2. Search for **Azure AI Search** and select it
3. Click **Create**
4. Configure the AI Search service:
   - **Subscription:** Select your subscription
   - **Resource group:** `rg-foundry-intermediate`
   - **Service name:** `search-foundry-int-<yourname>` (must be globally unique)
   - **Location:** `Australia East or France Central`
   - **Pricing tier:** Basic (sufficient for this lab)
5. Click **Review + Create**, then **Create**
6. Wait for deployment to complete (typically 3-5 minutes)

## Step 5.4: Deploy an Embedding Model
1. In Microsoft Foundry, navigate to **Build** > **Models**
2. Click **Deploy a base model**
3. Search for the **text-embedding-3-large** model
4. Select the model and click **Deploy** > **Custom settings**
5. Configure the deployment:
   - **Deployment name:** `text-embedding-3-large`
   - **Deployment type:** Select **Global Standard**
   - **Tokens per minute rate limit:** `50000`
6. Click **Deploy**

## Step 5.5: Create an Azure AI Search Index
1. In the Azure Portal, navigate to your Azure AI Search service (`search-foundry-int-<yourname>`)
2. In the AI Search service Overview, click **Import data**
3. Select **Azure Blob Storage** as the data source
4. Select **RAG**
5. Connect to your data:
   - **Subscription:** Select your subscription
   - **Storage account:** Select `stfoundryint<yourname>`
   - **Container:** Select `manuals`
   - Click **Next**
6. Vectorize your text:
   - **Kind:** Select `Microsoft Foundry`
   - **Subscription:** Select your subscription
   - **Microsoft Foundry project:** Select `intermediate-project`
   - **Model deployment:** Select `text-embedding-3-large`
   - **Authentication type:** Select `API Key`
   - Enable Acknowledgement of additional costs
   - Click **Next**
7. Leave default settings for Vectorize and enrich your images
8. Advanced Settings:
   - Enable semantic ranker
   - **Schedule:** Once
   - Click **Next**
9. Set Objects name prefix to `manuals`
10. Click **Create**

## Step 5.6: Verify Indexing
1. In your Azure AI Search service, navigate to **Search Management** > **Indexes** in the left menu
2. Select the `manuals` index
3. Click **Search**
4. Verify in the results that your documents are indexed:
   - ✅ Chunks of text from your documents are returned
   - ✅ Title of the document is displayed
   - ✅ Text vectors are created

## Step 5.7: Access Foundry IQ and Connect AI Search
1. In Microsoft Foundry Portal, navigate to **Build** > **Knowledge** in the left sidebar
2. If this is your first time accessing Foundry IQ, you may see an introduction screen
3. Select your Azure AI Search resource:
   - Click **Select a resource**
   - Choose `search-foundry-int-<yourname>` from the list
   - Under Auth Type, choose **API Key**
   - Click **Connect**

## Step 5.8: Create a New Knowledge Base
1. In the Knowledge section, click **Create a knowledge base**
2. Select **Azure AI Search** under Configure a knowledge base
3. Click **Connect**
4. Create a knowledge source configuration:
   - **Name:** `productmanuals`
   - **Description:** `Knowledge base for product manuals`
   - **Select search index:** `manuals`
5. Click **Create**

## Step 5.9: Configure Knowledge Base Settings
1. Under Basic configuration:
   - **Name:** `productkb`
   - **Description:** `Knowledge base for product manuals and other information`
   - **Chat completions model:** Select `gpt-4.1`
   - **Retrieval reasoning effort:** Select **Low**
   - **Output mode:** Extractive
   - **Retrieval instructions:**
     ```
     Use 'productmanuals' to get product information and specifications. Use 'productreviews' for customer reviews.
     ```

## Step 5.10: Add Azure Blob as a Second Knowledge Source
1. In your knowledge base, scroll down to the **Knowledge sources** section
2. Click **Create new**
3. Select **Azure Blob Storage**
4. Configure knowledge source:
   - **Name:** `productreviews`
   - **Description:** `Contains customer product reviews`
   - **Storage account:** Select `stfoundryint<yourname>`
   - **Container:** Select `reviews`
   - **Authentication:** Select **API Key**
   - **Context extraction mode:** Select **Minimal**
   - **Embedding model:** Select `text-embedding-3-large`
   - **Chat completions model:** Select `gpt-4.1`
5. Click **Create**

**Notes:**
- Foundry IQ can have multiple knowledge sources such as existing Azure AI Search indexes, Azure Blob Storage containers, and other data sources. This lets you combine different types of data in a single knowledge base.
- Unlike the manuals data which we pre-indexed in Azure AI Search, we're adding reviews as a direct blob storage source. Foundry IQ will automatically extract and embed the content using the specified embedding model.

## Step 5.11: Save the Knowledge Base
1. In the upper right select **Save knowledge base**
2. Refresh the page and wait for the product reviews knowledge source to be **Active** in status (this may take a few minutes)

## Step 5.12: Create the RAG Agent
1. In Microsoft Foundry Portal, navigate to **Build** > **Agents** in the left sidebar
2. Click **Create agent**
3. On the **Create an agent** page:
   - **Agent name:** `productassistant`
4. Click **Create and open playground**
5. Navigate to the **Instructions** tab and add:
   ```
   You are a helpful AI assistant. Your role is to answer questions based on the product knowledge base.

   Guidelines:
   - Always search the knowledge base before answering questions
   - If you find relevant information, cite the source document
   - If the information is not in the knowledge base, clearly state "I don't have information about that in my current knowledge base"
   - Be concise but thorough in your responses
   - Maintain a professional and friendly tone
   - If a question is ambiguous, ask for clarification
   - Never make up information that isn't in the knowledge base

   When providing answers:
   1. Search the knowledge base for relevant information
   2. Synthesize information from multiple sources if needed
   3. Cite your sources with document names
   4. Provide clear, actionable answers
   ```

## Step 5.13: Connect the Knowledge Base
1. Navigate to the **Knowledge** section of the agent configuration
2. Click **Add** then **Connect to Foundry IQ**
3. Connect to Foundry IQ:
   - **Connection:** Select `search-foundry-int-<yourname>`
   - **Knowledge base:** Select **productkb**
4. Click **Connect**

## Step 5.14: Remove Web Search and Save
1. Navigate to the **Tools** section of the agent configuration
2. Under Web search select the three dots and select **Remove**
3. Click **Save** in the upper right corner

## Step 5.15: Test Your RAG Agent
### Verify Agent Setup
1. Start with a greeting:
   ```
   Hello! Can you tell me what you can help me with?
   ```
2. Verify the agent responds appropriately and describes its capabilities

### Test Knowledge Base Queries
1. Ask a question answerable from your documents:
   ```
   What are the features of the Adventure Seeker Sling Bag and what is its cost?
   ```
2. Verify the response:
   - ✅ Agent provides relevant information
   - ✅ Agent cites source documents
   - ✅ Response is accurate based on your documents

3. Try a question with no answer in the knowledge base:
   ```
   What is the weather forecast for tomorrow?
   ```
4. Verify the agent correctly states it doesn't have that information

### Test Multi-Turn and Multi-Source
1. Ask a follow-up question:
   ```
   Can you provide more details about its warranty?
   ```
2. Verify the agent maintains context from the previous response

3. Ask a question requiring multiple knowledge sources:
   ```
   What are its main features and what do people say about them in customer reviews?
   ```
4. Verify the agent synthesizes information from both the manuals and reviews sources

### Review Agent Logs
1. Click on the **Logs** at the bottom
2. Review the knowledge base searches performed

---
---

# Wrap-Up

## Verification Checklist

**Module 1 — Foundation & Model Basics**
- [ ] Resource group `rg-foundry-intermediate` created
- [ ] Foundry resource created successfully
- [ ] GPT-4.1 model deployed in Foundry
- [ ] Model verified in the playground
- [ ] Model called successfully via curl (API key auth)

**Module 2 — Portal Agent**
- [ ] Agent `pythonassistant` created with instructions
- [ ] Web Search and Code Interpreter tools enabled
- [ ] Agent tested in playground (web search + code interpreter)

**Module 3 — Python Agents**
- [ ] Cloud Shell environment set up with SDK packages
- [ ] Basic agent created and called (with `previous_response_id`)
- [ ] Multi-tool agent created and called
- [ ] Streaming response demonstrated
- [ ] Conversation-based multi-turn context demonstrated

**Module 4 — Published Agent**
- [ ] Agent published with Responses endpoint
- [ ] Published agent called via OpenAI SDK (streaming)
- [ ] Published agent called via curl (bearer token auth)
- [ ] Understood model vs agent auth differences

**Module 5 — RAG Agent**
- [ ] Storage account created with manuals and reviews uploaded
- [ ] Azure AI Search service provisioned
- [ ] Embedding model deployed
- [ ] AI Search index created and documents indexed
- [ ] Knowledge base created in Foundry IQ with two knowledge sources
- [ ] Agent `productassistant` created and connected to the knowledge base
- [ ] Agent tested successfully with relevant, cited responses

---

## Clean Up Resources
All course resources live in a single resource group, so cleanup is one step.

1. In the Azure Portal, navigate to **Resource groups**
2. Select `rg-foundry-intermediate`
3. Click **Delete resource group**
4. Type the resource group name to confirm
5. Click **Delete**

> **Note:** This deletes all resources created in this course, including Foundry, Storage, and AI Search.

---

## Summary and Key Takeaways

In this course, you successfully:

1. ✅ Created a single shared Foundry resource and deployed a GPT-4.1 model
2. ✅ Called the model directly via curl using API key authentication
3. ✅ Built an agent in the Foundry Portal with Web Search and Code Interpreter
4. ✅ Created and called agents programmatically with the Azure AI Projects Python SDK
5. ✅ Demonstrated both context approaches (`previous_response_id` and conversations)
6. ✅ Implemented streaming responses with status monitoring
7. ✅ Published an agent and called it via SDK and curl using bearer token authentication
8. ✅ Built a knowledge base in Foundry IQ with multiple data sources
9. ✅ Created a RAG-grounded agent that answers from your documents with citations

### The Big Picture: Model → Agent → Grounded Agent
- **Raw model** (Module 1): the model alone, called with an API key
- **Agent** (Modules 2-4): instructions + tools wrapped around the model, called with RBAC/bearer token once published
- **Grounded agent** (Module 5): an agent that retrieves from your own data (RAG) before answering

### Why RAG over Fine-Tuning
- ✅ Easier to update (just add/modify documents)
- ✅ More transparent (you can see what data was used)
- ✅ More accurate (model sees actual content, not memorized patterns)
- ✅ Lower cost (no expensive fine-tuning compute)

---

## Course Completion Badge
Congratulations! 🎉 You have completed the **Building & Grounding Foundry Agents (Intermediate)** course.

You now have hands-on experience with:
- Deploying and calling Foundry models directly via REST
- Creating and configuring AI agents in the Foundry Portal
- Building agents programmatically with the Azure AI Projects Python SDK
- Streaming responses and managing multi-turn conversations
- Publishing agents and consuming them via OpenAI-compatible APIs
- Building knowledge bases and implementing Retrieval-Augmented Generation (RAG)

**End of Course**
