# Lab: Deploy Hosted Agents to Microsoft Foundry

## Overview
In this hands-on lab, you will learn how to deploy containerized AI agents to Microsoft Foundry Agent Service. You'll build Docker containers with protocol libraries, deploy them using Azure Container Registry, manage secrets securely, and publish agents as production-ready applications. This lab demonstrates the complete lifecycle of hosted agent deployment from local development to production.

**Estimated Time:** 90 minutes

**Prerequisites:**
- An Azure account with an active subscription
- Access to a role that allows you to create Foundry resources and Azure Container Registry (e.g., Contributor or Owner)
- Basic understanding of Docker containers and Python programming
- Access to Azure Cloud Shell (included with all Azure subscriptions)
- Optional: Completion of Lab-Foundry-Agents-Python.md (helpful but not required)

---

## Lab Architecture
By the end of this lab, you will have:
- A Microsoft Foundry resource with a deployed GPT model
- An Azure Container Registry with pushed container images
- Hosted agents running on Microsoft-managed infrastructure
- Experience with both Responses and Invocations protocols
- A multi-protocol agent accessible through different endpoints
- Secret management via Foundry project connections
- A published Agent Application ready for production consumption

---

## Understanding Hosted Agents

**Hosted agents** are containerized applications that run on Microsoft-managed infrastructure (Foundry Agent Service). Unlike managed agents (prompt/workflow), hosted agents contain custom code packaged as Docker containers.

### Deployment Lifecycle

Throughout this lab, you'll follow this deployment pattern:

1. **Build container** - Package your agent code with protocol libraries
2. **Push to ACR** - Store the container image in Azure Container Registry
3. **Create agent version** - Register the image with Foundry Agent Service
4. **Poll for status** - Wait for infrastructure provisioning to complete
5. **Invoke agent** - Send requests to the deployed endpoint

### Key Concepts

- **Protocol Libraries**: Special libraries (`azure-ai-agentserver-responses`, `azure-ai-agentserver-invocations`) that handle communication with Foundry gateway
- **Responses Protocol**: OpenAI-compatible endpoint for conversational chatbots with streaming support
- **Invocations Protocol**: Custom webhook-style endpoint for non-conversational processing
- **Platform-Injected Variables**: Environment variables automatically provided by Foundry at runtime
- **Session State**: Hosted agents include built-in session management with persistent `$HOME` and file storage

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
   - **Resource group name:** `rg-hosted-agents`
   - **Region:** `Australia East`
5. Click **Review + Create**, then **Create**

---

## Step 2: Setup Foundry Resource and Model

### 2.1 Create a Foundry Resource
1. In the Azure Portal, click **Create a resource**
2. Search for **Microsoft Foundry** and select it
3. Click **Create**
4. Configure the resource:
   - **Subscription:** Select your subscription
   - **Resource group:** `rg-hosted-agents`
   - **Name:** `foundry-hosted-<yourname>` (must be globally unique)
   - **Region:** `Australia East`
   - **Default project name:** `hosted-agents-project`
5. Click **Review + Create**, then **Create**
6. Wait for the deployment to complete (typically 1-2 minutes)

### 2.2 Access Microsoft Foundry Portal
1. Once deployment completes, click **Go to resource**
2. In the resource overview, click **Go to Foundry Portal** or navigate directly to [https://ai.azure.com/](https://ai.azure.com/)
3. Sign in with your Azure credentials
4. Verify that you are in the **New** Foundry Portal and that your project (`hosted-agents-project`) is selected in the upper left corner

### 2.3 Deploy a Model
1. In Microsoft Foundry, navigate to **Build** in the top navigation
2. Select **Models** from the left sidebar
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

### 2.4 Get Your Project Endpoint
1. In the Foundry Portal, select **Home** from the top navigation bar
2. Locate and copy the **Project Endpoint**
   - Format: `https://foundry-hosted-<yourname>.services.ai.azure.com/api/projects/hosted-agents-project`
3. Save this endpoint for use in your configuration

---

## Step 3: Setup Azure Container Registry

### 3.1 Create Azure Container Registry
1. In the Azure Portal, click **Create a resource**
2. Search for **Container Registry** and select it
3. Click **Create**
4. Configure the registry:
   - **Subscription:** Select your subscription
   - **Resource group:** `rg-hosted-agents`
   - **Registry name:** `acrhosted<yourname>` (must be globally unique, alphanumeric only)
   - **Location:** `Australia East`
   - **SKU:** `Standard`
5. Click **Review + Create**, then **Create**
6. Wait for deployment to complete

### 3.2 Get ACR Login Server
1. Navigate to your Azure Container Registry resource
2. In the **Overview** page, copy the **Login server** URL
   - Format: `acrhosted<yourname>.azurecr.io`
3. Save this for later use

### 3.3 Configure ACR Permissions
1. In the Foundry Portal, navigate to your project settings
2. Go to the **Identity** tab
3. Copy the **Object (principal) ID** of the system-assigned managed identity
4. Go back to your Azure Container Registry in the Azure Portal
5. Select **Access control (IAM)** from the left menu
6. Click **Add** > **Add role assignment**
7. Select the **AcrPull** role
8. Click **Next**
9. Click **Select members**
10. Paste the managed identity Object ID and select it
11. Click **Review + assign**

> **Note:** This allows the Foundry project to pull container images from ACR at runtime.

---

## Step 4: Setup Development Environment

### 4.1 Open Azure Cloud Shell
1. In the Azure Portal, click the **Cloud Shell** icon in the top navigation bar (looks like `>_`)
2. Select **Bash** as your shell environment
3. Select **No storage account required**
4. Select your **Subscription**
5. Select **Apply**
6. Wait for Cloud Shell to initialize

> **Note:** Azure Cloud Shell includes Docker CLI tools and Python 3 pre-installed, making it ideal for this lab.

### 4.2 Create Working Directory
1. In Cloud Shell, create a new directory:
   ```bash
   mkdir ~/hosted-agents-lab
   cd ~/hosted-agents-lab
   ```

### 4.3 Create Virtual Environment
1. Create a Python virtual environment:
   ```bash
   python -m venv agentenv
   ```
2. Activate the virtual environment:
   ```bash
   source agentenv/bin/activate
   ```
3. Verify activation (you should see `(agentenv)` in your prompt)

### 4.4 Install Required Packages
1. Install the Azure AI Projects SDK and protocol libraries:
   ```bash
   pip install "azure-ai-projects>=2.1.0"
   pip install azure-identity
   pip install "azure-ai-agentserver-responses"
   pip install "azure-ai-agentserver-invocations"
   pip install fastapi
   pip install uvicorn[standard]
   ```

### 4.5 Create Environment File
1. Create a `.env` file to store configuration:
   ```bash
   code .env
   ```
2. Add the following, replacing with your actual values:
   ```
   PROJECT_ENDPOINT="https://foundry-hosted-<yourname>.services.ai.azure.com/api/projects/hosted-agents-project"
   ACR_LOGIN_SERVER="acrhosted<yourname>.azurecr.io"
   MODEL_DEPLOYMENT="gpt-4.1"
   ```
3. Save with `Ctrl+S` and close with `Ctrl+Q`

### 4.6 Login to Azure
1. Login to Azure CLI:
   ```bash
   az login
   ```
2. Follow the instructions to complete authentication
3. Select your subscription when prompted

---

## Step 5: Create a Simple Hosted Agent (Responses Protocol)

In this step, you'll create a containerized agent that uses the Responses protocol - ideal for conversational chatbots with streaming support.

### 5.1 Create Agent Directory Structure
1. Create directory for the simple agent:
   ```bash
   mkdir -p ~/hosted-agents-lab/simple_agent
   cd ~/hosted-agents-lab/simple_agent
   ```

### 5.2 Create the Agent Application
1. Create the main application file:
   ```bash
   code app.py
   ```
2. Add the following code:

```python
import os
from azure.ai.agentserver.responses import ResponsesHostServer
from azure.ai.agentserver.responses.models import Response, TextContent, MessageItem
from azure.identity import DefaultAzureCredential
from azure.ai.projects import AIProjectClient

# Get environment variables (injected by platform at runtime)
project_endpoint = os.getenv("FOUNDRY_PROJECT_ENDPOINT")
model_deployment = os.getenv("MODEL_DEPLOYMENT", "gpt-4.1")

print(f"Initializing simple agent...")
print(f"Project Endpoint: {project_endpoint}")
print(f"Model: {model_deployment}")

# Create a simple response handler
def handle_request(request_input: str) -> str:
    """Simple handler that echoes back with a greeting"""
    return f"Hello! You said: '{request_input}'. I'm a hosted agent running on Foundry Agent Service!"

# Create the server
server = ResponsesHostServer(
    response_handler=handle_request,
    name="simple-agent"
)

# Run the server on port 8088
if __name__ == "__main__":
    print("Starting server on port 8088...")
    server.run(host="0.0.0.0", port=8088)
```

3. Save with `Ctrl+S` and close with `Ctrl+Q`

### 5.3 Create Dockerfile
1. Create a Dockerfile:
   ```bash
   code Dockerfile
   ```
2. Add the following:

```dockerfile
# Use Python 3.11 slim image
FROM python:3.11-slim

# Set working directory
WORKDIR /app

# Copy requirements and install
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy application code
COPY app.py .

# Expose port 8088
EXPOSE 8088

# Run the application
CMD ["python", "app.py"]
```

3. Save and close

### 5.4 Create Requirements File
1. Create requirements file:
   ```bash
   code requirements.txt
   ```
2. Add the dependencies:

```
azure-ai-agentserver-responses
azure-ai-projects>=2.1.0
azure-identity
fastapi
uvicorn[standard]
```

3. Save and close

### 5.5 Create Agent Manifest
1. Create the agent manifest:
   ```bash
   code agent.yaml
   ```
2. Add the following:

```yaml
name: simple-agent
description: A simple hosted agent using the Responses protocol
runtime:
  protocol_versions:
    - protocol: responses
      version: 1.0.0
  port: 8088
environment_variables:
  - name: MODEL_DEPLOYMENT
    value: gpt-4.1
```

3. Save and close

### 5.6 Test Locally (Optional)
1. Run the agent locally to verify it works:
   ```bash
   export FOUNDRY_PROJECT_ENDPOINT="your-project-endpoint"
   export MODEL_DEPLOYMENT="gpt-4.1"
   python app.py
   ```
2. In a new Cloud Shell tab, test with curl:
   ```bash
   curl -X POST http://localhost:8088/responses \
     -H "Content-Type: application/json" \
     -d '{"input": "Hello agent!", "stream": false}'
   ```
3. You should see a response from the agent
4. Stop the server with `Ctrl+C`

**Key Concepts:**
- ✅ **Port 8088**: Standard port for hosted agents
- ✅ **Responses Protocol**: OpenAI-compatible conversational endpoint
- ✅ **Platform Variables**: `FOUNDRY_PROJECT_ENDPOINT` is auto-injected at runtime
- ✅ **Health Endpoint**: `/readiness` is automatically exposed by the protocol library

---

## Step 6: Create an Invocations Agent

In this step, you'll create an agent using the Invocations protocol - ideal for webhook-style processing and custom workflows.

### 6.1 Create Agent Directory
1. Create directory for invocations agent:
   ```bash
   mkdir -p ~/hosted-agents-lab/invocations_agent
   cd ~/hosted-agents-lab/invocations_agent
   ```

### 6.2 Create the Application
1. Create the application file:
   ```bash
   code app.py
   ```
2. Add the following code:

```python
import os
from azure.ai.agentserver.invocations import InvocationsHostServer

# Get environment variables
project_endpoint = os.getenv("FOUNDRY_PROJECT_ENDPOINT")
agent_name = os.getenv("FOUNDRY_AGENT_NAME", "invocations-agent")

print(f"Initializing invocations agent: {agent_name}")
print(f"Project Endpoint: {project_endpoint}")

# Create a custom invocation handler
def handle_invocation(payload: dict) -> dict:
    """
    Handle custom invocation requests
    This is ideal for webhook-style processing
    """
    message = payload.get("message", "No message provided")
    action = payload.get("action", "echo")
    
    print(f"Received invocation: action={action}, message={message}")
    
    if action == "echo":
        return {
            "status": "success",
            "result": f"Echo: {message}",
            "agent": agent_name
        }
    elif action == "uppercase":
        return {
            "status": "success",
            "result": message.upper(),
            "agent": agent_name
        }
    elif action == "count":
        return {
            "status": "success",
            "result": f"Message length: {len(message)} characters",
            "agent": agent_name
        }
    else:
        return {
            "status": "error",
            "error": f"Unknown action: {action}",
            "agent": agent_name
        }

# Create the server
server = InvocationsHostServer(
    invocation_handler=handle_invocation,
    name="invocations-agent"
)

# Run the server
if __name__ == "__main__":
    print("Starting invocations server on port 8088...")
    server.run(host="0.0.0.0", port=8088)
```

3. Save and close

### 6.3 Create Dockerfile
1. Create Dockerfile:
   ```bash
   code Dockerfile
   ```
2. Add the content:

```dockerfile
FROM python:3.11-slim

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY app.py .

EXPOSE 8088

CMD ["python", "app.py"]
```

3. Save and close

### 6.4 Create Requirements File
1. Create requirements:
   ```bash
   code requirements.txt
   ```
2. Add dependencies:

```
azure-ai-agentserver-invocations
azure-ai-projects>=2.1.0
azure-identity
fastapi
uvicorn[standard]
```

3. Save and close

### 6.5 Create Agent Manifest
1. Create manifest:
   ```bash
   code agent.yaml
   ```
2. Add configuration:

```yaml
name: invocations-agent
description: A hosted agent using the Invocations protocol for custom processing
runtime:
  protocol_versions:
    - protocol: invocations
      version: 1.0.0
  port: 8088
```

3. Save and close

**Key Concepts:**
- ✅ **Invocations Protocol**: Custom request/response format for webhooks and async workflows
- ✅ **Custom Payload**: You define the request and response structure
- ✅ **Non-Conversational**: Best for task-based processing, not chatbots
- ✅ **Same Port**: Both protocols use port 8088

---

## Step 7: Build and Push Container Images

In this step, you'll build Docker images for both agents and push them to Azure Container Registry using ACR Tasks.

### 7.1 Login to Azure Container Registry
1. Login to ACR:
   ```bash
   source ~/.env
   az acr login --name ${ACR_LOGIN_SERVER%.azurecr.io}
   ```
2. Verify successful login

> **Important:** We use ACR Tasks (`az acr build`) instead of local Docker builds to ensure proper linux/amd64 platform architecture.

### 7.2 Build and Push Simple Agent
1. Navigate to simple agent directory:
   ```bash
   cd ~/hosted-agents-lab/simple_agent
   ```
2. Build and push using ACR Tasks:
   ```bash
   az acr build \
     --registry ${ACR_LOGIN_SERVER%.azurecr.io} \
     --image simple-agent:v1 \
     --platform linux/amd64 \
     --file Dockerfile \
     .
   ```
3. Wait for the build to complete (typically 2-3 minutes)
4. Verify the image was pushed:
   ```bash
   az acr repository show \
     --name ${ACR_LOGIN_SERVER%.azurecr.io} \
     --repository simple-agent
   ```

### 7.3 Build and Push Invocations Agent
1. Navigate to invocations agent directory:
   ```bash
   cd ~/hosted-agents-lab/invocations_agent
   ```
2. Build and push:
   ```bash
   az acr build \
     --registry ${ACR_LOGIN_SERVER%.azurecr.io} \
     --image invocations-agent:v1 \
     --platform linux/amd64 \
     --file Dockerfile \
     .
   ```
3. Wait for completion
4. Verify:
   ```bash
   az acr repository list \
     --name ${ACR_LOGIN_SERVER%.azurecr.io} \
     --output table
   ```

You should see both `simple-agent` and `invocations-agent` listed.

**Key Concepts:**
- ✅ **ACR Tasks**: Cloud-based image builds ensure correct platform architecture
- ✅ **linux/amd64**: Required platform for Foundry hosted agents
- ✅ **Image Tags**: Use version tags (v1, v2) instead of :latest for reproducibility
- ✅ **Verification**: Always verify images are in ACR before deployment

---

## Step 8: Deploy Hosted Agent Using Python SDK

In this step, you'll deploy the simple agent using the Azure AI Projects Python SDK.

### 8.1 Create Deployment Script
1. Navigate to the lab directory:
   ```bash
   cd ~/hosted-agents-lab
   ```
2. Create the deployment script:
   ```bash
   code deploy_simple_agent.py
   ```
3. Add the following code:

```python
from azure.identity import DefaultAzureCredential
from azure.ai.projects import AIProjectClient
from azure.ai.projects.models import (
    HostedAgentDefinition,
    ProtocolVersionRecord,
    AgentProtocol
)
from dotenv import load_dotenv
import os
import time

# Load environment variables
load_dotenv()

PROJECT_ENDPOINT = os.getenv("PROJECT_ENDPOINT")
ACR_LOGIN_SERVER = os.getenv("ACR_LOGIN_SERVER")
MODEL_DEPLOYMENT = os.getenv("MODEL_DEPLOYMENT")

print("=" * 60)
print("STEP 1: CREATE PROJECT CLIENT")
print("=" * 60)

# Create project client
credential = DefaultAzureCredential()
project = AIProjectClient(
    endpoint=PROJECT_ENDPOINT,
    credential=credential,
)

print(f"✅ Connected to project: {PROJECT_ENDPOINT}")

print("\n" + "=" * 60)
print("STEP 2: CREATE HOSTED AGENT VERSION")
print("=" * 60)

# Create the hosted agent version
agent = project.agents.create_version(
    agent_name="simple-hosted-agent",
    definition=HostedAgentDefinition(
        # Specify the Responses protocol
        container_protocol_versions=[
            ProtocolVersionRecord(
                protocol=AgentProtocol.RESPONSES,
                version="1.0.0"
            )
        ],
        # Resource allocation
        cpu="1",
        memory="2Gi",
        # Container image location
        image=f"{ACR_LOGIN_SERVER}/simple-agent:v1",
        # Environment variables for the container
        environment_variables={
            "MODEL_DEPLOYMENT": MODEL_DEPLOYMENT
        }
    )
)

print(f"✅ Agent version created!")
print(f"   Agent Name: {agent.name}")
print(f"   Version: {agent.version}")
print(f"   Image: {ACR_LOGIN_SERVER}/simple-agent:v1")

print("\n" + "=" * 60)
print("STEP 3: POLL FOR ACTIVE STATUS")
print("=" * 60)
print("Waiting for infrastructure provisioning (this may take 2-3 minutes)...\n")

# Poll until the agent is active
max_attempts = 60
attempt = 0

while attempt < max_attempts:
    version_info = project.agents.get_version(
        agent_name=agent.name,
        agent_version=agent.version
    )
    
    status = version_info.get("status", "unknown")
    print(f"⏳ Attempt {attempt + 1}/{max_attempts}: Status = {status}")
    
    if status == "active":
        print("\n✅ Agent is ACTIVE and ready to serve requests!")
        break
    elif status == "failed":
        error = version_info.get("error", "Unknown error")
        print(f"\n❌ Provisioning FAILED: {error}")
        exit(1)
    
    attempt += 1
    time.sleep(5)

if attempt >= max_attempts:
    print("\n❌ Timeout waiting for agent to become active")
    exit(1)

print("\n" + "=" * 60)
print("STEP 4: INVOKE THE AGENT")
print("=" * 60)

# Get OpenAI client bound to the agent
openai_client = project.get_openai_client(agent_name=agent.name)

# Invoke the agent
print("Sending request to hosted agent...\n")
response = openai_client.responses.create(
    input="Hello from the Python SDK!",
)

print("AGENT RESPONSE:")
print("=" * 60)
print(response.output_text)
print("=" * 60)

print("\n✅ Deployment and invocation successful!")
print(f"\nAgent Endpoint: {PROJECT_ENDPOINT}/agents/{agent.name}/endpoint")
```

4. Save and close

### 8.2 Run the Deployment
1. Ensure your virtual environment is activated and you're in the lab directory:
   ```bash
   cd ~/hosted-agents-lab
   source agentenv/bin/activate
   ```
2. Run the deployment script:
   ```bash
   python deploy_simple_agent.py
   ```
3. Watch the output as it:
   - Creates the agent version
   - Polls for active status
   - Invokes the deployed agent
4. Verify you see the agent's response

**Key Concepts:**
- ✅ **HostedAgentDefinition**: Specifies container image, resources, and protocols
- ✅ **Status Polling**: Wait for "active" status before invoking
- ✅ **Status Values**: creating → active (or failed)
- ✅ **Resource Allocation**: cpu="1", memory="2Gi" for basic agents
- ✅ **Agent Endpoint**: Each agent gets a dedicated endpoint
- ✅ **Platform Provisioning**: Creates infrastructure, Entra identity, and networking automatically

---

## Step 9: Deploy Using REST API

In this step, you'll deploy the invocations agent using direct REST API calls.

### 9.1 Create Deployment Script
1. Create a bash script:
   ```bash
   cd ~/hosted-agents-lab
   code deploy_invocations_agent.sh
   ```
2. Add the following:

```bash
#!/bin/bash

# Load environment variables
source .env

echo "======================================================================"
echo "STEP 1: SETUP VARIABLES"
echo "======================================================================"

# Get Azure access token
TOKEN=$(az account get-access-token --resource https://ai.azure.com --query accessToken -o tsv)

if [ -z "$TOKEN" ]; then
    echo "❌ Failed to get access token"
    exit 1
fi

echo "✅ Access token obtained"

# Extract base URL and project name from PROJECT_ENDPOINT
BASE_URL="${PROJECT_ENDPOINT}"
API_VERSION="v1"

echo "Base URL: $BASE_URL"
echo "ACR: $ACR_LOGIN_SERVER"

echo ""
echo "======================================================================"
echo "STEP 2: CREATE AGENT VERSION"
echo "======================================================================"

# Create the agent version
CREATE_RESPONSE=$(curl -s -X POST "${BASE_URL}/agents?api-version=${API_VERSION}" \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d "{
    \"name\": \"invocations-hosted-agent\",
    \"definition\": {
      \"kind\": \"hosted\",
      \"image\": \"${ACR_LOGIN_SERVER}/invocations-agent:v1\",
      \"cpu\": \"1\",
      \"memory\": \"2Gi\",
      \"container_protocol_versions\": [
        {
          \"protocol\": \"invocations\",
          \"version\": \"1.0.0\"
        }
      ]
    }
  }")

echo "Response: $CREATE_RESPONSE"

# Extract agent name and version
AGENT_NAME="invocations-hosted-agent"
AGENT_VERSION="1"

echo "✅ Agent version created: $AGENT_NAME version $AGENT_VERSION"

echo ""
echo "======================================================================"
echo "STEP 3: POLL FOR ACTIVE STATUS"
echo "======================================================================"
echo "Waiting for infrastructure provisioning..."
echo ""

# Poll for status
MAX_ATTEMPTS=60
ATTEMPT=0

while [ $ATTEMPT -lt $MAX_ATTEMPTS ]; do
    STATUS_RESPONSE=$(curl -s -X GET \
      "${BASE_URL}/agents/${AGENT_NAME}/versions/${AGENT_VERSION}?api-version=${API_VERSION}" \
      -H "Authorization: Bearer $TOKEN")
    
    STATUS=$(echo $STATUS_RESPONSE | grep -o '"status":"[^"]*"' | cut -d'"' -f4)
    
    echo "⏳ Attempt $((ATTEMPT + 1))/$MAX_ATTEMPTS: Status = $STATUS"
    
    if [ "$STATUS" == "active" ]; then
        echo ""
        echo "✅ Agent is ACTIVE and ready!"
        break
    elif [ "$STATUS" == "failed" ]; then
        echo ""
        echo "❌ Provisioning FAILED"
        echo "$STATUS_RESPONSE"
        exit 1
    fi
    
    ATTEMPT=$((ATTEMPT + 1))
    sleep 5
done

if [ $ATTEMPT -ge $MAX_ATTEMPTS ]; then
    echo ""
    echo "❌ Timeout waiting for agent"
    exit 1
fi

echo ""
echo "======================================================================"
echo "STEP 4: INVOKE THE AGENT"
echo "======================================================================"

# Test with different actions
echo ""
echo "Test 1: Echo action"
echo "-------------------------------------------------------------------"
curl -X POST \
  "${BASE_URL}/agents/${AGENT_NAME}/endpoint/protocols/invocations?api-version=${API_VERSION}" \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -H "Foundry-Features: HostedAgents=V1Preview" \
  -d '{
    "message": "Hello from REST API!",
    "action": "echo"
  }' | jq .

echo ""
echo "Test 2: Uppercase action"
echo "-------------------------------------------------------------------"
curl -X POST \
  "${BASE_URL}/agents/${AGENT_NAME}/endpoint/protocols/invocations?api-version=${API_VERSION}" \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -H "Foundry-Features: HostedAgents=V1Preview" \
  -d '{
    "message": "make this uppercase",
    "action": "uppercase"
  }' | jq .

echo ""
echo "Test 3: Count action"
echo "-------------------------------------------------------------------"
curl -X POST \
  "${BASE_URL}/agents/${AGENT_NAME}/endpoint/protocols/invocations?api-version=${API_VERSION}" \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -H "Foundry-Features: HostedAgents=V1Preview" \
  -d '{
    "message": "How long is this message?",
    "action": "count"
  }' | jq .

echo ""
echo "======================================================================"
echo "✅ DEPLOYMENT AND INVOCATION SUCCESSFUL"
echo "======================================================================"
```

3. Save and close

### 9.2 Run the Deployment Script
1. Make the script executable:
   ```bash
   chmod +x deploy_invocations_agent.sh
   ```
2. Run the script:
   ```bash
   ./deploy_invocations_agent.sh
   ```
3. Observe the output as it creates, polls, and invokes the agent
4. Verify all three test actions work correctly

**Key Concepts:**
- ✅ **REST API Access**: Direct HTTP API for custom integrations
- ✅ **Authentication**: Bearer token from `az account get-access-token`
- ✅ **Invocations Protocol**: Custom payload structure with actions
- ✅ **Feature Headers**: `Foundry-Features: HostedAgents=V1Preview` for preview features
- ✅ **jq Tool**: Formats JSON responses for readability

---

## Step 10: Create Multi-Protocol Agent

In this step, you'll create an agent that exposes BOTH Responses and Invocations protocols simultaneously.

### 10.1 Create Multi-Protocol Agent Directory
1. Create directory:
   ```bash
   mkdir -p ~/hosted-agents-lab/multi_protocol_agent
   cd ~/hosted-agents-lab/multi_protocol_agent
   ```

### 10.2 Create the Application
1. Create the app:
   ```bash
   code app.py
   ```
2. Add the code:

```python
import os
from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse
import uvicorn

# Create FastAPI app
app = FastAPI()

# Get environment variables
agent_name = os.getenv("FOUNDRY_AGENT_NAME", "multi-protocol-agent")
project_endpoint = os.getenv("FOUNDRY_PROJECT_ENDPOINT")

print(f"Starting multi-protocol agent: {agent_name}")
print(f"Project: {project_endpoint}")

@app.get("/readiness")
async def readiness():
    """Health check endpoint required by Foundry"""
    return {"status": "ready", "agent": agent_name}

@app.post("/responses")
async def handle_responses(request: Request):
    """
    Responses protocol endpoint
    OpenAI-compatible conversational interface
    """
    body = await request.json()
    user_input = body.get("input", "")
    
    print(f"[Responses] Received: {user_input}")
    
    response_text = f"[Multi-Protocol Agent via Responses] You said: {user_input}"
    
    return {
        "id": "resp-123",
        "status": "completed",
        "output": [
            {
                "type": "message",
                "content": [
                    {
                        "type": "text",
                        "text": response_text
                    }
                ]
            }
        ]
    }

@app.post("/invocations")
async def handle_invocations(request: Request):
    """
    Invocations protocol endpoint
    Custom webhook-style interface
    """
    body = await request.json()
    message = body.get("message", "")
    action = body.get("action", "process")
    
    print(f"[Invocations] Action: {action}, Message: {message}")
    
    if action == "analyze":
        result = f"Analysis of '{message}': {len(message)} characters, {len(message.split())} words"
    elif action == "reverse":
        result = message[::-1]
    else:
        result = f"Processed '{message}' with action '{action}'"
    
    return {
        "status": "success",
        "result": result,
        "agent": agent_name,
        "protocol": "invocations"
    }

if __name__ == "__main__":
    print("Starting server on port 8088 with both protocols...")
    print("  - Responses endpoint: POST /responses")
    print("  - Invocations endpoint: POST /invocations")
    print("  - Health check: GET /readiness")
    uvicorn.run(app, host="0.0.0.0", port=8088)
```

3. Save and close

### 10.3 Create Dockerfile
1. Create Dockerfile:
   ```bash
   code Dockerfile
   ```
2. Add content:

```dockerfile
FROM python:3.11-slim

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY app.py .

EXPOSE 8088

CMD ["python", "app.py"]
```

3. Save and close

### 10.4 Create Requirements
1. Create requirements:
   ```bash
   code requirements.txt
   ```
2. Add:

```
fastapi
uvicorn[standard]
```

3. Save and close

### 10.5 Build and Deploy
1. Build and push the image:
   ```bash
   cd ~/hosted-agents-lab/multi_protocol_agent
   source ~/.env
   
   az acr build \
     --registry ${ACR_LOGIN_SERVER%.azurecr.io} \
     --image multi-protocol-agent:v1 \
     --platform linux/amd64 \
     --file Dockerfile \
     .
   ```

2. Create deployment script:
   ```bash
   cd ~/hosted-agents-lab
   code deploy_multi_protocol.py
   ```

3. Add the code:

```python
from azure.identity import DefaultAzureCredential
from azure.ai.projects import AIProjectClient
from azure.ai.projects.models import (
    HostedAgentDefinition,
    ProtocolVersionRecord,
    AgentProtocol
)
from dotenv import load_dotenv
import os
import time

load_dotenv()

PROJECT_ENDPOINT = os.getenv("PROJECT_ENDPOINT")
ACR_LOGIN_SERVER = os.getenv("ACR_LOGIN_SERVER")

credential = DefaultAzureCredential()
project = AIProjectClient(endpoint=PROJECT_ENDPOINT, credential=credential)

print("=" * 60)
print("DEPLOYING MULTI-PROTOCOL AGENT")
print("=" * 60)

# Create agent with BOTH protocols
agent = project.agents.create_version(
    agent_name="multi-protocol-agent",
    definition=HostedAgentDefinition(
        container_protocol_versions=[
            ProtocolVersionRecord(protocol=AgentProtocol.RESPONSES, version="1.0.0"),
            ProtocolVersionRecord(protocol=AgentProtocol.INVOCATIONS, version="1.0.0")
        ],
        cpu="1",
        memory="2Gi",
        image=f"{ACR_LOGIN_SERVER}/multi-protocol-agent:v1"
    )
)

print(f"✅ Agent created: {agent.name} v{agent.version}")
print("⏳ Polling for active status...")

# Poll for status
for i in range(60):
    info = project.agents.get_version(agent.name, agent.version)
    status = info.get("status")
    print(f"   Attempt {i+1}: {status}")
    if status == "active":
        break
    time.sleep(5)

print("\n✅ Agent is ACTIVE!\n")

# Test Responses protocol
print("=" * 60)
print("TEST 1: RESPONSES PROTOCOL")
print("=" * 60)

openai_client = project.get_openai_client(agent_name=agent.name)
response = openai_client.responses.create(
    input="Hello via Responses protocol!"
)
print(f"Response: {response.output_text}\n")

# Test Invocations protocol
print("=" * 60)
print("TEST 2: INVOCATIONS PROTOCOL")
print("=" * 60)

import requests

token = credential.get_token("https://ai.azure.com/.default").token
url = f"{PROJECT_ENDPOINT}/agents/{agent.name}/endpoint/protocols/invocations"

# Test analyze action
resp = requests.post(url, headers={
    "Authorization": f"Bearer {token}",
    "Content-Type": "application/json",
    "Foundry-Features": "HostedAgents=V1Preview"
}, params={"api-version": "v1"}, json={
    "message": "This is a test message for analysis",
    "action": "analyze"
})

print(f"Analyze: {resp.json()}")

# Test reverse action
resp = requests.post(url, headers={
    "Authorization": f"Bearer {token}",
    "Content-Type": "application/json",
    "Foundry-Features": "HostedAgents=V1Preview"
}, params={"api-version": "v1"}, json={
    "message": "Foundry",
    "action": "reverse"
})

print(f"Reverse: {resp.json()}")

print("\n" + "=" * 60)
print("✅ BOTH PROTOCOLS WORKING!")
print("=" * 60)
```

4. Save and close

### 10.6 Run the Deployment
1. Run the script:
   ```bash
   python deploy_multi_protocol.py
   ```
2. Observe both protocols being tested
3. Verify both endpoints respond correctly

**Key Concepts:**
- ✅ **Protocol Flexibility**: Single container can expose multiple protocols
- ✅ **Different Use Cases**: Responses for chat, Invocations for webhooks
- ✅ **Shared Infrastructure**: Same container, different endpoints
- ✅ **FastAPI**: Custom implementation gives full control
- ✅ **Health Endpoint**: Required `/readiness` for platform monitoring

---

## Step 11: Secret Management with Project Connections

In this step, you'll learn how to securely manage secrets using Foundry project connections instead of hardcoding them.

### 11.1 Create a Project Connection
1. In the Foundry Portal, navigate to your project
2. Go to **Settings** > **Connected resources**
3. Click **New connection**
4. Select **Custom Keys** as the connection type
5. Configure the connection:
   - **Name:** `agent-secrets`
   - **Add a key:**
     - **Key name:** `api_token`
     - **Value:** `my-secret-token-12345`
6. Click **Create**

> **Note:** In production, you'd store actual API keys, tokens, or credentials here.

### 11.2 Create Agent with Secret Reference
1. Create a new agent directory:
   ```bash
   mkdir -p ~/hosted-agents-lab/secret_agent
   cd ~/hosted-agents-lab/secret_agent
   ```

2. Create app.py:
   ```bash
   code app.py
   ```

3. Add code that uses the secret:

```python
import os
from fastapi import FastAPI
import uvicorn

app = FastAPI()

# The secret will be injected as an environment variable
api_token = os.getenv("API_TOKEN")
agent_name = os.getenv("FOUNDRY_AGENT_NAME", "secret-agent")

print(f"Agent: {agent_name}")
print(f"API Token loaded: {'Yes' if api_token else 'No'}")
if api_token:
    print(f"Token (first 5 chars): {api_token[:5]}***")

@app.get("/readiness")
async def readiness():
    return {"status": "ready", "agent": agent_name}

@app.post("/responses")
async def handle_responses(request):
    body = await request.json()
    user_input = body.get("input", "")
    
    # Demonstrate that the secret is available
    response_text = f"Request processed with authenticated token (starts with {api_token[:5]}***)"
    
    return {
        "id": "resp-secret",
        "status": "completed",
        "output": [
            {
                "type": "message",
                "content": [{"type": "text", "text": response_text}]
            }
        ]
    }

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8088)
```

4. Save and close

### 11.3 Create Dockerfile and Requirements
1. Create Dockerfile:
   ```bash
   code Dockerfile
   ```

```dockerfile
FROM python:3.11-slim
WORKDIR /app
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt
COPY app.py .
EXPOSE 8088
CMD ["python", "app.py"]
```

2. Create requirements:
   ```bash
   code requirements.txt
   ```

```
fastapi
uvicorn[standard]
```

3. Save both files

### 11.4 Build and Deploy with Secret Reference
1. Build the image:
   ```bash
   source ~/.env
   az acr build \
     --registry ${ACR_LOGIN_SERVER%.azurecr.io} \
     --image secret-agent:v1 \
     --platform linux/amd64 \
     --file Dockerfile \
     .
   ```

2. Create deployment script:
   ```bash
   cd ~/hosted-agents-lab
   code deploy_secret_agent.py
   ```

3. Add code with placeholder syntax:

```python
from azure.identity import DefaultAzureCredential
from azure.ai.projects import AIProjectClient
from azure.ai.projects.models import (
    HostedAgentDefinition,
    ProtocolVersionRecord,
    AgentProtocol
)
from dotenv import load_dotenv
import os
import time

load_dotenv()

PROJECT_ENDPOINT = os.getenv("PROJECT_ENDPOINT")
ACR_LOGIN_SERVER = os.getenv("ACR_LOGIN_SERVER")

credential = DefaultAzureCredential()
project = AIProjectClient(endpoint=PROJECT_ENDPOINT, credential=credential)

print("=" * 60)
print("DEPLOYING AGENT WITH SECRET MANAGEMENT")
print("=" * 60)

# Create agent with secret reference using placeholder syntax
agent = project.agents.create_version(
    agent_name="secret-agent",
    definition=HostedAgentDefinition(
        container_protocol_versions=[
            ProtocolVersionRecord(protocol=AgentProtocol.RESPONSES, version="1.0.0")
        ],
        cpu="1",
        memory="2Gi",
        image=f"{ACR_LOGIN_SERVER}/secret-agent:v1",
        environment_variables={
            # This placeholder will be resolved to the actual secret at runtime
            "API_TOKEN": "${{connections.agent-secrets.credentials.api_token}}"
        }
    )
)

print(f"✅ Agent created with secret reference")
print(f"   Agent: {agent.name} v{agent.version}")
print(f"   Secret: ${{connections.agent-secrets.credentials.api_token}}")
print("\n⏳ Polling for active status...\n")

# Poll for status
for i in range(60):
    info = project.agents.get_version(agent.name, agent.version)
    status = info.get("status")
    print(f"   Attempt {i+1}: {status}")
    if status == "active":
        break
    elif status == "failed":
        error = info.get("error")
        print(f"❌ Failed: {error}")
        exit(1)
    time.sleep(5)

print("\n✅ Agent is ACTIVE! Secret has been resolved.\n")

# Test the agent
print("=" * 60)
print("TESTING AGENT WITH SECRET")
print("=" * 60)

openai_client = project.get_openai_client(agent_name=agent.name)
response = openai_client.responses.create(
    input="Can you confirm you have the API token?"
)

print(f"\nAgent Response:\n{response.output_text}\n")
print("=" * 60)
print("✅ Secret successfully loaded and used!")
print("=" * 60)
```

4. Save and close

### 11.5 Deploy and Verify
1. Run the deployment:
   ```bash
   python deploy_secret_agent.py
   ```
2. Verify the agent responds showing it has the token
3. Note that the actual secret value is never exposed in logs or API responses

**Key Concepts:**
- ✅ **Placeholder Syntax**: `${{connections.<name>.credentials.<field>}}`
- ✅ **Runtime Resolution**: Platform resolves placeholders before container starts
- ✅ **Security**: Secrets never appear in API responses or logs
- ✅ **Connection Types**: ApiKey, AppInsights (use `credentials.key`), CustomKeys (use field name)
- ✅ **Key Vault Integration**: Foundry manages Key Vault storage automatically
- ✅ **Best Practice**: Never hardcode secrets in images or code

---

## Step 12: Publish Hosted Agent as Application

In this step, you'll publish a hosted agent as an Agent Application - a production-ready Azure resource with its own endpoint, RBAC, and dedicated identity.

### 12.1 Publish via Foundry Portal
1. In the Foundry Portal, navigate to **Build** > **Agents**
2. Find your `simple-hosted-agent`
3. Click on the agent to open it
4. Click **Publish** in the top right
5. Configure the publication:
   - **Application name:** `simple-agent-app`
   - **Authentication:** Leave as **RBAC** (default)
   - **Deployment type:** **Hosted**
   - **Min replicas:** `1`
   - **Max replicas:** `3`
6. Click **Publish**
7. Wait for publishing to complete

### 12.2 Get Published Endpoint
1. After publishing, copy the **Published Endpoint URL**
   - Format: `https://foundry-hosted-<yourname>.services.ai.azure.com/api/projects/hosted-agents-project/applications/simple-agent-app/protocols/openai`
2. Save this URL

### 12.3 Test Published Agent
1. Create a test script:
   ```bash
   cd ~/hosted-agents-lab
   code test_published_agent.py
   ```

2. Add the code:

```python
from openai import OpenAI
from azure.identity import DefaultAzureCredential
import os
from dotenv import load_dotenv

load_dotenv()

# Get credentials
credential = DefaultAzureCredential()
token = credential.get_token("https://ai.azure.com/.default")

# Published endpoint (remove /v1/responses from the base URL)
BASE_URL = "https://foundry-hosted-<yourname>.services.ai.azure.com/api/projects/hosted-agents-project/applications/simple-agent-app/protocols/openai"

print("=" * 60)
print("TESTING PUBLISHED AGENT APPLICATION")
print("=" * 60)
print(f"Endpoint: {BASE_URL}\n")

# Create OpenAI client
client = OpenAI(
    api_key=token.token,
    base_url=BASE_URL,
    default_headers={"Foundry-Features": "AgentEndpoints=V1Preview"}
)

# Test non-streaming
print("Test 1: Non-streaming response")
print("-" * 60)
response = client.responses.create(
    input="Hello published agent!",
    stream=False
)
print(f"Response: {response.output[0].content[0].text}\n")

# Test streaming
print("Test 2: Streaming response")
print("-" * 60)
print("Streamed output: ", end="", flush=True)
stream = client.responses.create(
    input="Count from 1 to 5",
    stream=True
)

for event in stream:
    if event.type == "response.output_text.delta":
        print(event.delta, end="", flush=True)

print("\n")
print("=" * 60)
print("✅ Published Agent Application working!")
print("=" * 60)
```

3. Save and close
4. Update the BASE_URL with your actual endpoint
5. Run the test:
   ```bash
   python test_published_agent.py
   ```

### 12.4 Test with CURL
1. Test the published endpoint with curl:
   ```bash
   TOKEN=$(az account get-access-token --resource https://ai.azure.com --query accessToken -o tsv)
   
   curl -X POST \
     "https://foundry-hosted-<yourname>.services.ai.azure.com/api/projects/hosted-agents-project/applications/simple-agent-app/protocols/openai/responses?api-version=2025-11-15-preview" \
     -H "Authorization: Bearer $TOKEN" \
     -H "Content-Type: application/json" \
     -H "Foundry-Features: AgentEndpoints=V1Preview" \
     -d '{"input": "Hello from curl!"}'
   ```

**Key Concepts:**
- ✅ **Agent Application**: Production Azure ARM resource
- ✅ **Stable Endpoint**: URL doesn't change when updating agent versions
- ✅ **Dedicated Identity**: Published agent gets its own Entra identity
- ✅ **Independent RBAC**: Control access separately from project
- ✅ **Scaling**: Configure min/max replicas for hosted agents
- ✅ **Authentication**: Requires Azure RBAC (Foundry User role)
- ✅ **Stateless**: Published agents currently use stateless responses only
- ✅ **Production Ready**: Managed infrastructure, monitoring, and governance

---

## Step 13: Compare Deployment Methods

Now that you've deployed agents using multiple methods, let's compare them.

### 13.1 Deployment Method Comparison

| Method | Best For | Pros | Cons |
|--------|----------|------|------|
| **Azure Developer CLI (azd)** | First-time deployment, full automation | Handles everything (build, push, RBAC, deploy) | Less granular control, requires azd installation |
| **Python SDK** | Python applications, programmatic control | Type-safe, great for automation, Python-native | Requires Azure AI Projects SDK |
| **REST API** | Language-agnostic, custom integrations | Works from any language/tool, maximum flexibility | Manual token management, more verbose |

### 13.2 When to Use Each Protocol

| Protocol | Use Case | Characteristics |
|----------|----------|-----------------|
| **Responses** | Chatbots, conversational AI, streaming | OpenAI-compatible, multi-turn support, SSE streaming |
| **Invocations** | Webhooks, task processing, async workflows | Custom payloads, non-conversational, flexible structure |
| **Both** | Dual-purpose agents | Maximum flexibility, single deployment, multiple interfaces |

### 13.3 Hosted vs Managed Agents

| Aspect | Hosted Agents | Managed Agents (from Python lab) |
|--------|---------------|----------------------------------|
| **Code** | Custom containerized code | Prompt + tools only |
| **Deployment** | Docker + ACR + Foundry | SDK create_version() |
| **Complexity** | Higher (containers required) | Lower (no containers) |
| **Flexibility** | Maximum (any code) | Limited to supported tools |
| **Use Case** | Custom logic, integrations | Standard chat/search/code |
| **Infrastructure** | Microsoft-managed containers | Microsoft-managed compute |
| **State** | Session state (files, $HOME) | Conversations (when not published) |
| **Scaling** | Configure min/max replicas | Automatic |

### 13.4 Development to Production Path

```
Local Development
    ↓
Test in Cloud Shell (port 8088)
    ↓
Build & Push to ACR
    ↓
Deploy as Agent Version
    ↓
Test with project endpoint
    ↓
Publish as Agent Application
    ↓
Production Consumption
```

### 13.5 Production Considerations

**When to Use Hosted Agents:**
- ✅ Need custom business logic beyond standard tools
- ✅ Integrate with proprietary systems or APIs
- ✅ Complex data processing workflows
- ✅ Require specific Python packages or libraries
- ✅ Need session state management

**When to Use Managed Agents (Prompt-based):**
- ✅ Standard conversational chatbots
- ✅ Using built-in tools (web search, code interpreter)
- ✅ Rapid prototyping
- ✅ No container expertise required
- ✅ Simple use cases

**Cost Considerations:**
- Hosted agents incur costs while deployed
- Auto-deprovision after 15 minutes of inactivity (no cost when idle)
- Publisher-pays model (you pay for infrastructure, not end users)
- Scale replicas based on expected load

---

## Verification Checklist

**Azure Resources:**
- [ ] Resource group `rg-hosted-agents` created
- [ ] Foundry resource created with GPT-4.1 model deployed
- [ ] Azure Container Registry created with proper RBAC
- [ ] Project managed identity has AcrPull role on ACR

**Container Images:**
- [ ] simple-agent:v1 built and pushed to ACR
- [ ] invocations-agent:v1 built and pushed to ACR
- [ ] multi-protocol-agent:v1 built and pushed to ACR
- [ ] secret-agent:v1 built and pushed to ACR
- [ ] All images verified in ACR repository list

**Agent Deployments:**
- [ ] simple-hosted-agent deployed via Python SDK
- [ ] Agent version status reached "active"
- [ ] Responses protocol endpoint accessible
- [ ] invocations-hosted-agent deployed via REST API
- [ ] Invocations protocol endpoint accessible with custom actions
- [ ] multi-protocol-agent accessible on both protocols
- [ ] secret-agent successfully loads secrets from project connections

**Publishing:**
- [ ] simple-agent-app published as Agent Application
- [ ] Published endpoint accessible with Azure RBAC auth
- [ ] OpenAI SDK can invoke published agent
- [ ] CURL commands work against published endpoint

**Advanced Features:**
- [ ] Multi-protocol agent tested on /responses and /invocations
- [ ] Secret management verified with project connections
- [ ] Placeholder syntax resolves correctly at runtime
- [ ] Replica scaling configured for published agents

---

## Clean Up Resources

To avoid incurring charges, delete the resources when you're finished with the lab:

### Option 1: Delete Resource Group (Fastest)
1. In the Azure Portal, navigate to **Resource groups**
2. Select `rg-hosted-agents`
3. Click **Delete resource group**
4. Type the resource group name to confirm
5. Click **Delete**

> **Note:** This deletes ALL resources including Foundry, ACR, models, and agent deployments.

### Option 2: Delete Individual Agents
If you want to keep the infrastructure but remove agents:

1. Delete agent versions via Python:
   ```python
   project.agents.delete_version(agent_name="simple-hosted-agent", agent_version="1")
   project.agents.delete_version(agent_name="invocations-hosted-agent", agent_version="1")
   ```

2. Delete ACR images:
   ```bash
   az acr repository delete --name acrhosted<yourname> --repository simple-agent --yes
   az acr repository delete --name acrhosted<yourname> --repository invocations-agent --yes
   ```

---

## Summary and Key Takeaways

In this lab, you successfully:

1. ✅ Created Azure infrastructure for hosted agents (Foundry, ACR, models)
2. ✅ Built containerized agents with protocol libraries
3. ✅ Deployed agents using multiple methods (Python SDK, REST API)
4. ✅ Implemented both Responses and Invocations protocols
5. ✅ Created a multi-protocol agent with dual endpoints
6. ✅ Managed secrets securely using project connections
7. ✅ Published hosted agents as production Agent Applications
8. ✅ Tested agents with OpenAI SDK and CURL

### Key Concepts

**Hosted Agent Architecture:**
- **Containerization**: Package custom code with protocol libraries
- **ACR Integration**: Store images in Azure Container Registry
- **Platform Provisioning**: Foundry creates infrastructure, identity, and networking
- **Protocol Libraries**: Handle communication with Foundry gateway
- **State Management**: Built-in session persistence for files and $HOME

**Deployment Lifecycle:**
1. **Build** → Package code into Docker image (linux/amd64)
2. **Push** → Store in ACR with proper tagging
3. **Create** → Register agent version with Foundry
4. **Poll** → Wait for "active" status (infrastructure provisioning)
5. **Invoke** → Send requests to dedicated endpoint

**Protocol Selection:**
- **Responses**: OpenAI-compatible, conversational, streaming (port 8088)
- **Invocations**: Custom webhooks, task processing, flexible payloads (port 8088)
- **Both**: Maximum flexibility, single container, multiple interfaces

**Secret Management:**
- **Project Connections**: Store secrets in CustomKeys connections
- **Placeholder Syntax**: `${{connections.<name>.credentials.<field>}}`
- **Runtime Resolution**: Platform injects secrets before container starts
- **Security**: Secrets never exposed in API responses or logs

**Publishing:**
- **Agent Application**: Production Azure ARM resource
- **Stable Endpoint**: URL persists across version updates
- **Dedicated Identity**: Separate Entra identity for security
- **RBAC Control**: Independent access management
- **Scaling**: Configure min/max replicas for load handling

### Best Practices

1. **Container Images:**
   - Use ACR Tasks for cloud-based builds (ensures correct platform)
   - Tag images with versions (v1, v2) not :latest
   - Keep images small (use slim base images)
   - Verify images in ACR before deployment

2. **Deployment:**
   - Always poll for "active" status before invoking
   - Handle "failed" status with error checking
   - Test locally before pushing to ACR
   - Use environment variables for configuration

3. **Security:**
   - Never hardcode secrets in images or code
   - Use project connections for all sensitive data
   - Assign minimal RBAC permissions
   - Use system-assigned managed identities

4. **Protocols:**
   - Use Responses for conversational agents
   - Use Invocations for webhook/task processing
   - Expose both protocols only when needed
   - Implement /readiness for health checks

5. **Production:**
   - Publish as Agent Applications for stable endpoints
   - Configure appropriate replica scaling
   - Monitor agent performance and costs
   - Clean up unused versions regularly

### Production Considerations

**Cost Management:**
- Hosted agents incur costs while deployed
- Auto-deprovision after 15 minutes idle (no cost)
- Publisher-pays model (you pay, not end users)
- Delete unused agents and images

**Performance:**
- Start with cpu="1", memory="2Gi" for testing
- Scale resources based on agent complexity
- Configure min/max replicas for traffic patterns
- Monitor response times and adjust

**Security:**
- Use RBAC for all access control
- Rotate secrets regularly via project connections
- Audit agent access logs
- Follow principle of least privilege

**Monitoring:**
- Application Insights connection string auto-injected
- Monitor container health via /readiness
- Track invocation counts and latencies
- Set up alerts for failures

---

## Additional Resources

- [Deploy a hosted agent - Microsoft Learn](https://learn.microsoft.com/en-us/azure/foundry/agents/how-to/deploy-hosted-agent)
- [Foundry Hosted Agents Concepts](https://learn.microsoft.com/azure/foundry/agents/concepts/hosted-agents)
- [Agent Applications Documentation](https://learn.microsoft.com/azure/foundry/agents/how-to/agent-applications)
- [Azure Container Registry Documentation](https://learn.microsoft.com/en-us/azure/container-registry/)
- [Responses Protocol Specification](https://github.com/Azure/azure-sdk-for-net/tree/main/sdk/agentserver/Azure.AI.AgentServer.Responses)
- [Lab: Building Foundry Agents with Python](Lab-Foundry-Agents-Python.md) - Companion lab

---

## Lab Completion Badge

Congratulations! 🎉 You have completed the **Deploy Hosted Agents to Microsoft Foundry** lab.

You now have hands-on experience with:
- Building containerized AI agents with protocol libraries
- Deploying to Microsoft-managed infrastructure
- Using Azure Container Registry for image management
- Implementing both Responses and Invocations protocols
- Managing secrets securely with project connections
- Publishing agents as production-ready applications
- Comparing deployment methods and choosing the right approach

You're ready to deploy custom containerized agents to production on Azure Foundry! 🚀

---

**End of Lab**
