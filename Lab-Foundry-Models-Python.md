# Lab: Running Foundry Models using Python

## Overview
In this hands-on lab, you will learn how to deploy and interact with Microsoft Foundry Models using Python. You will deploy AI models in Microsoft Foundry, test them in the playground, and then use Python code to call the models via REST API. This approach is ideal for developers who want to integrate Foundry models directly into their Python applications.

**Estimated Time:** 90 minutes

**Prerequisites:**
- An Azure account with an active subscription 
- Access to a role that allows you to create Foundry resources (e.g., Azure AI Owner)
- Basic understanding of Python and REST APIs
- Access to Azure Cloud Shell (or Python 3.8+ locally with command line experience)


---

## Lab Architecture
By the end of this lab, you will have:
- A Microsoft Foundry resource with deployed models (GPT-4.1 and DeepSeek-V3.1)
- Tested models in the Foundry playground
- Python scripts that call your models via REST API
- Understanding of authentication and API integration with Foundry models

---

## Step 1: Setup a Foundry Resource

### 1.1 Sign in to Azure Portal
1. Navigate to the [Azure Portal](https://portal.azure.com/)
2. Sign in with your Azure account credentials

### 1.2 Create a Resource Group
1. In the Azure Portal, click **Create a resource**
2. Search for **Resource Group** and select it
3. Click **Create**
4. Configure the resource group:
   - **Subscription:** Select your subscription
   - **Resource group name:** `rg-foundry-python-lab`
   - **Region:** `Australia East`
5. Click **Review + Create**, then **Create**

### 1.3 Create an API Management Instance
1. In the Azure Portal, click **Create a resource**
2. Search for **API Management** and select it
3. Click **Create**
4. Configure the API Management service:
   - **Subscription:** Select your subscription
   - **Resource group:** `rg-foundry-python-lab`
   - **Region:** `Australia East` (same as your Foundry resource)
   - **Resource name:** `apim<yourname>` (must be globally unique)
   - **Organization name:** Your organization name (can be your name or company name)
   - **Administrator email:** Your email address (any valid email for notifications)
   - **Pricing tier:** Select **Basic**
5. Click **Review + Create**, then **Create**
6. Do not wait for deployment to complete. **Proceed to next step**.

### 1.4 Create a Foundry Resource
1. In the Azure Portal, click **Create a resource**
2. Search for **Microsoft Foundry** and select it
3. Click **Create**
4. Configure the resource:
   - **Subscription:** Select your subscription
   - **Resource group:** `rg-foundry-python-lab`  
   - **Name:** `foundry<yourname>` (must be globally unique)
   - **Region:** `Australia East`
   - **Default project name:** `project01`
5. Click **Review + Create**, then **Create**
6. Wait for the deployment to complete (typically 1-2 minutes)

### 1.5 Access Microsoft Foundry Portal
1. Once deployment completes, click **Go to resource**
2. In the resource overview, click **Go to Foundry Portal** or navigate directly to [https://ai.azure.com/](https://ai.azure.com/)
3. Sign in with your Azure credentials
4. Verify that you are in the New Foundry Portal and that your project (`project01`) is selected in the upper left corner.

---

## Step 2: Deploy Foundry Models

### 2.1 Deploy a GPT-4.1 Model
1. In Microsoft Foundry, navigate to **Build** in the top navigation
2. Select **Models** from the left sidebar
3. Click **Deploy a base model**
4. Search for the **gpt-4.1** model
5. **Select** the model
6. Select Deploy > Custom settings
7. Configure the deployment:
   - **Deployment name:** `gpt-4.1`
   - **Deployment type:** Select **Global Standard** (pay-per-token, easiest for testing)
   - **Tokens per minute rate limit:** `50000`
8. Click **Deploy**
9. Wait for deployment to complete (typically 1-3 minutes)

### 2.2 Deploy a DeepSeek Model
1. Select Models from the left sidebar.
2. Repeat the deployment steps to deploy a DeepSeek model with the following configuration:
   - **Model:** DeepSeek-V3.1
   - **Deployment name:** `DeepSeek-V3.1`
   - **Deployment type:** Select **Global Standard**
   - **Tokens per minute rate limit:** `50000`

---

## Step 3: Test the Models in the Playground

### 3.1 Access the Playground
1. In Microsoft Foundry, navigate to **Build** > **Models**
2. Select your deployment: `gpt-4.1`
3. Select Open in playground

### 3.2 Configure the Playground
1. In the **System message** field, add context:
   ```
   You are a helpful AI assistant that provides concise and accurate answers about Azure. If you don't know the answer, say you don't know. Always provide clear and informative responses. If you are asked questions about other topics besides Azure, politely decline to answer.
   ```
2. Adjust parameters:
   - **Temperature:** `0.7` (controls randomness; 0 = deterministic, 1 = creative)
   - **Max tokens:** `800` (maximum response length)
   - **Top P:** `0.95` (nucleus sampling threshold)

### 3.3 Test the GPT-4.1 Model
1. In the **User message** field, type a test prompt:
   ```
   What are the top 3 benefits of using Microsoft Foundry for AI model deployment?
   ```
2. Click **Send** or press Enter
3. Review the model's response
4. Try additional prompts to verify the model is working correctly:
   ```
   Explain what Microsoft Foundry is in 2 sentences.
   ```
5. Test a non-Azure related question to verify the system message is working:
   ```
   What is the capital of France?
   ```

### 3.4 Test the DeepSeek Model
1. Go back to the Models list and open the playground for `DeepSeek-V3.1`
2. Repeat the same testing steps 3.2 to 3.3 with similar prompts to verify the second model is also working correctly.

---

## Step 4: Get API Credentials for Python Integration

### 4.1 Retrieve the Endpoint URL
1. In Microsoft Foundry, navigate to **Home**.
2. Copy your `Azure OpenAI endpoint` endpoint
   It should look like:
   ```
   https://foundry<yourname>.openai.azure.com/openai/v1
   ```
3. Save this endpoint to your Notepad

### 4.2 Retrieve the API Key
1. In the same location, look for the **API Key**
2. Copy the key
3. Save this key securely to your Notepad

> **Note:** Keep your API key secure and never commit it to version control. In production, use Azure Key Vault or environment variables.

---

## Step 5: Setup Python Environment

### 5.1 Verify Python Installation
1. Open Cloud Shell in Azure Portal. 
2. Go to Classic Version of Cloud Shell (Bash)
3. Check your Python version:
   ```bash
   python --version
   ```
4. Ensure you have Python 3.8 or higher installed

### 5.2 Install Required Libraries
1. Create a new directory for your lab project:
   ```bash
   mkdir foundry-python-lab
   cd foundry-python-lab
   ```
2. Create a virtual environment:
   ```bash
   python -m venv venv
   source venv/bin/activate
   ```
3. Install the required libraries:
   ```bash
   pip install openai requests python-dotenv
   ```

> **Note:** We're using the `openai` library because Foundry models support Azure OpenAI compatible APIs.

### 5.3 Create Environment Configuration File
1. In your project directory, create a file named `.env`:
   ```bash
   code .env
   ```
2. Open the `.env` file in your text editor and add your credentials:
   ```
   AZURE_OPENAI_ENDPOINT=your_endpoint_here
   AZURE_OPENAI_KEY=your_api_key_here
   MODEL_DEPLOYMENT_NAME=gpt-4.1
   ```
3. Replace the placeholder values with your actual endpoint and API key
4. Save the `.env` file by pressing `Ctrl + S` then close it by pressing `Ctrl + Q`
---

## Step 6: Call Models Using Python

### 6.1 Create a Basic Python Script (Using Requests Library)

1. Create a file named `foundry_basic.py`.
```
code foundry_basic.py
```
2. Open the file and add the following code to call the Foundry model using the `requests` library:
```python
import os
import requests
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Configuration
endpoint = os.getenv("AZURE_OPENAI_ENDPOINT")
api_key = os.getenv("AZURE_OPENAI_KEY")
deployment_name = os.getenv("MODEL_DEPLOYMENT_NAME")

# Construct the full URL
url = f"{endpoint}/responses"

# Headers
headers = {
    "Content-Type": "application/json",
    "api-key": api_key
}

# Request payload
payload = {
    "input": [
        {
            "role": "system",
            "content": "You are a helpful AI assistant."
        },
        {
            "role": "user",
            "content": "What are the top 3 benefits of using Microsoft Foundry?"
        }
    ],
    "max_output_tokens": 500,
    "temperature": 0.7,
    "model": deployment_name
}

# Make the API call
try:
    response = requests.post(url, headers=headers, json=payload)
    response.raise_for_status()  # Raise an exception for bad status codes
    
    result = response.json()
    
    # Extract and print the assistant's message
    if "output" in result and len(result["output"]) > 0:
        # Extract text from the output structure
        assistant_message = result["output"][0]["content"][0]["text"]
        print("Assistant Response:")
        print(assistant_message)
        
        # Print token usage
        if "usage" in result:
            print("\nToken Usage:")
            print(f"  Input tokens: {result['usage']['input_tokens']}")
            print(f"  Output tokens: {result['usage']['output_tokens']}")
            print(f"  Total tokens: {result['usage']['total_tokens']}")
    else:
        print("Error: Unexpected response structure.")
        print(f"Response: {result}")
    
except requests.exceptions.RequestException as e:
    print(f"Error calling Foundry API: {e}")
    if hasattr(e, 'response') and e.response is not None:
        print(f"Response content: {e.response.text}")
```
3. You may copy the contents of the foundry_basic.py file found in the Models-Python folder of the repository and paste it into your `foundry_basic.py` file.

### 6.2 Run the Basic Script

1. Save the file and run it:
```bash
python foundry_basic.py
```

2. You should see output similar to:
```
Assistant Response:
**Top 3 Benefits of Using Microsoft Foundry:**

1. **Unified AI Platform**: Foundry provides a centralized environment for building, deploying, and managing AI models...
2. **Enterprise-Grade Security**: Built on Azure, it offers robust security features...
3. **Seamless Integration**: Easy integration with Azure services and tools...

Token Usage:
    Input tokens: 28
    Output tokens: 150
    Total tokens: 178
```

### 6.3 Create an Advanced Script with OpenAI Library

1. Create a file named `foundry_openai.py`.
```
code foundry_openai.py
```
2. Open the file and add the following code to call the Foundry model using the `openai` library:
```python
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

response = client.responses.create(   
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
  model=deployment_name
)

# Extract and print the assistant's message
if response.output and len(response.output) > 0:
    assistant_message = response.output[0].content[0].text
    print("Assistant Response:")
    print(assistant_message)
    
    # Print token usage
    if response.usage:
        print("\nToken Usage:")
        print(f"  Input tokens: {response.usage.input_tokens}")
        print(f"  Output tokens: {response.usage.output_tokens}")
        print(f"  Total tokens: {response.usage.total_tokens}")
else:
    print("Error: Unexpected response structure.")
    print(response.model_dump_json(indent=2))
```
3. You may copy the contents of the foundry_openai.py file found in the Models-Python folder of the repository and paste it into your `foundry_openai.py` file.

### 6.4 Run the Advanced Script

1. Save the file and run it:
```bash
python foundry_openai.py
```
2. You should see a similar response as the basic script, but this time using the `openai` library which provides a more streamlined interface for working with Foundry models.

### 6.5 Create a Streaming Response Script

1. Create a file named `foundry_streaming.py`.
```
code foundry_streaming.py
```
2. Open the file and add the following code to demonstrate how to handle streaming responses from Foundry models:
```python
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

```
3. You may copy the contents of the foundry_streaming.py file found in the Models-Python folder of the repository and paste it into your `foundry_streaming.py` file.

### 6.6 Run the Streaming Script

1. Save and run:
```bash
python foundry_streaming.py
```

2. Observe how the response streams in real-time, similar to ChatGPT's interface

### 6.7 Create an Interactive Chat Script

1. Create a file named `foundry_chat.py`.
```
code foundry_chat.py
```
2. Open the file and add the following code to create an interactive chat interface with the Foundry model:
```python
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

```
3. You may copy the contents of the foundry_chat.py file found in the Models-Python folder of the repository and paste it into your `foundry_chat.py` file.

### 6.8 Run the Interactive Chat

1. Save and run:
```bash
python foundry_chat.py
```

2. Have a conversation with the model:
```
You: What is Microsoft Foundry?
Assistant: [Response...]
   
You: How do I deploy models in Foundry?
Assistant: [Response...]
   
You: quit
```
### 6.9 Run with another model
1. To test with the second model, update the `MODEL_DEPLOYMENT_NAME` in your `.env` file to `DeepSeek-V3.1`
2. Run any of the scripts again to see how the response differs with the different model.

---
## Step 7: Setup the Model to be Called via Azure API Management

### 7.1 Verify API Management is Ready
1. Return to the Azure Portal
2. Navigate to **Resource groups** > `rg-foundry-python-lab` > `apim<yourname>`
3. Verify the **Status** shows as **Online** (if not, wait for completion)

### 7.2 Import the Foundry Model API into APIM
1. In your API Management instance, navigate to **APIs** in the left menu and select **+ Add API** at the top
2. Under **Create an AI API**, click **Microsoft Foundry**
3. On the **Select AI Service** tab:
   - **Subscription:** Select your subscription
   - **AI Service:** Select `foundry<yourname>` (the Foundry resource you created)
   - Review deployments by clicking the deployments link
   - Click **Next**

4. On the **Configure Model Route** tab:
   - **Display name:** `Microsoft Foundry API`
   - **Name:** `microsoft-foundry-api`
   - **Base path:** `foundry` (this will be part of your API URL)
   - **Description:** `API for accessing Microsoft Foundry deployed models`
   - **Products:** Select **Unlimited** 
   - **Client compatibility:** Select **Azure OpenAI v1**
   - Click **Next**

5. On the **Manage token consumption** tab:
   - Enable Manage token consumption
   - Tokens per minute (TPM): 1000
   - Token quota: 5000
   - Token quota period: Hourly 
   - Enable the following options:
     - **Estimate prompt tokens**: ON
     - **Add consumed tokens header**: ON
     - **Add remaining tokens header**: ON
   - Click **Next**
> Note: We're setting a lower token limit in APIM (1000 TPM) than the model's capacity (50000 TPM) to easily demonstrate rate limiting. In production, set APIM limits based on your budget and expected usage patterns.

6. On the **Apply semantic caching** tab:
   - Optionally enable semantic caching to reduce costs and latency for similar requests
   - For this lab, we will disable, so leave it OFF
   - Click **Next**

7. On the **AI content safety** tab:
   - Optionally configure Azure AI Content Safety integration
   - For this lab, you will skip this step because there is a default content safety policy applied for all the models deployed in Foundry.
   - Click **Review**

8. Review the configuration and click **Create**

### 7.3 Verify API Configuration
1. Once created, click on the **Microsoft Foundry API** in the APIs list
2. Navigate to the **Design** tab
3. Verify operations are listed (e.g., `Creates a completion for the chat message`)
4. Click **All operations**, then under **Inbound processing**, click the **</>** (code icon) to view **Policies**. Review the automatically applied policies for token per minute and token quota enforcement.
5. Navigate to the **Settings** tab
6. Note the following:
   - **Base URL:** This shows your APIM gateway URL
   - **Copy this URL to your Notepad for use in calling the API.**
7. Scroll down to the **Subscriptions** section
   - Notice that Subscription required is set to Yes.
   - Notice that Header name is set to `api-key` - this is the header you will use to pass your subscription key for authentication when calling the API.

### 7.4 Test the API in APIM
1. In the **Design** tab, select the `Creates a model response` operation
2. Click on the **Test** tab
3. Configure the test request:
    - **api-version:** `v1`
    - **Request body:**
    ```json
    {"model":"gpt-4.1","input":"What is Azure?","stream":false}
    ```
4. Click **Send**.
5. Review the response and verify you receive a valid response from the model with token usage headers included.
6. Modify the model to `DeepSeek-V3.1` in the request body and test the second model as well.

### 7.5 Get Your API Credentials
1. In APIM, navigate to **Subscriptions** in the left menu
2. Create a new subscription:
   - Click **+ Add subscription**
   - **Name:** `foundry-test-subscription`
   - **Display name:** `Foundry Test Subscription`
   - **Scope:** Select **API** > **Microsoft Foundry API**
   - Click **Create**
3. Click the **...** menu next to your subscription and select **Show/hide keys**
4. Copy the **Primary key** to your Notepad - you'll need this for authentication

---
## Step 8: Call the APIM Endpoint from Python

### 8.1 Create a Script

1. Open your existing .env file and **add** these new lines (keep the existing ones):
```
GENAI_GATEWAY_ENDPOINT=your_apim_gateway_url_here
GENAI_GATEWAY_API_KEY=your_subscription_key_here
```
2. Create a file named `foundry_apim.py`.
```
code foundry_apim.py
```
3. Open the file and add the following code to demonstrate how to handle responses from the Foundry model via the APIM endpoint with proper error handling for rate limits and API errors:
```python
import os
from openai import OpenAI, RateLimitError, APIError
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Configuration
gateway_endpoint = os.getenv("GENAI_GATEWAY_ENDPOINT")
gateway_api_key = os.getenv("GENAI_GATEWAY_API_KEY")
deployment_name = os.getenv("MODEL_DEPLOYMENT_NAME")

def get_client_from_gateway() -> OpenAI:
    client = OpenAI(
        api_key="fakevalueshouldnotbeused", # dummy value to satisfy the required parameter, actual key is passed in headers
        base_url=gateway_endpoint,
        default_headers={"api-key": gateway_api_key},
        timeout=30.0,  # Set timeout to 30 seconds
        max_retries=0  # Disable automatic retries
    )
    return client

client = get_client_from_gateway()

try:
    response = client.responses.create(   
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
      max_output_tokens=1000,
      temperature=0.7,
      model=deployment_name
    )

    # Extract and print the assistant's message
    if response.output and len(response.output) > 0:
        assistant_message = response.output[0].content[0].text
        print("Assistant Response:")
        print(assistant_message)
        
        # Print token usage
        if response.usage:
            print("\nToken Usage:")
            print(f"  Input tokens: {response.usage.input_tokens}")
            print(f"  Output tokens: {response.usage.output_tokens}")
            print(f"  Total tokens: {response.usage.total_tokens}")
    else:
        print("Error: Unexpected response structure.")
        print(response.model_dump_json(indent=2))

except RateLimitError as e:
    print(f"\n⚠️  Rate limit exceeded!")
    print(f"Status Code: {e.status_code}")
    print(f"Error Message: {e.message}")
    print(f"Response Body: {e.body}")

except APIError as e:
    # Check if this is a rate limit error (can be 403 or 429)
    is_rate_limit = False
    if e.status_code in [403, 429]:
        error_msg = str(e.message).lower()
        if any(keyword in error_msg for keyword in ['quota', 'limit', 'rate', 'exceeded', 'try again']):
            is_rate_limit = True
    
    if is_rate_limit:
        print(f"\n⚠️  Rate limit/Quota exceeded!")
        print(f"Status Code: {e.status_code}")
        print(f"Error Message: {e.message}")
        print(f"Response Body: {e.body}")
    else:
        print(f"\n❌ API Error occurred!")
        print(f"Status Code: {e.status_code}")
        print(f"Error Message: {e.message}")
        print(f"Response Body: {e.body}")

except Exception as e:
    print(f"\n❌ Unexpected error: {type(e).__name__}")
    print(f"Details: {str(e)}")
```
4. You may copy the contents of the foundry_apim.py file found in the Models-Python folder of the repository and paste it into your `foundry_apim.py` file.

### 8.2 Run the APIM Script

1. Save and run:
```bash
python foundry_apim.py
```
2. Observe the response from the Foundry model via the APIM endpoint. 
3. **Expected behavior:** The first call should succeed. Running it multiple times rapidly will trigger the rate limit (1000 TPM). You should see the rate limit error after consuming your quota.


---

## Clean Up Resources

To avoid incurring charges, delete the resources when you're finished with the lab:

### Delete the Resource Group
1. In the Azure Portal, navigate to **Resource groups**
2. Select `rg-foundry-python-lab`
3. Click **Delete resource group**
4. Type the resource group name to confirm
5. Click **Delete**

---

## Summary and Key Takeaways

In this lab, you successfully:

1. ✅ Created a Microsoft Foundry resource for hosting AI models
2. ✅ Deployed GPT-4.1 and DeepSeek-V3.1 models in Microsoft Foundry
3. ✅ Tested models in the Foundry playground
4. ✅ Retrieved API credentials for programmatic access
5. ✅ Set up a Python development environment
6. ✅ Created Python scripts using the `requests` library
7. ✅ Implemented advanced features using the `openai` library
8. ✅ Built streaming and interactive chat interfaces
9. ✅ Tested APIM rate limits and subscription key authentication

---

## Lab Completion Badge

Congratulations! 🎉 You have completed the **Microsoft Foundry Models with Python** lab.

You now have hands-on experience with:
- Azure API Management for AI models
- Microsoft Foundry resource and model deployment
- Testing AI models in the playground
- Python integration with Foundry APIs
- Using both `requests` and `openai` libraries
- Implementing streaming responses
- Building interactive chat interfaces
- Testing APIM rate limits and subscription key authentication
---

**End of Lab**
