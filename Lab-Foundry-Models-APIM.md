# Lab: Running Foundry Models using Azure API Management Service

## Overview
In this hands-on lab, you will learn how to deploy and manage Microsoft Foundry Models through Azure API Management (APIM). This integration enables you to leverage APIM's gateway capabilities to monitor, secure, and control access to your AI models. In addition, you will use Log Analytics for monitoring and Azure Cloud Shell to test your API endpoints.

**Estimated Time:** 90 minutes

**Prerequisites:**
- An Azure account with an active subscription 
- Access to a role that allows you to create Foundry resources (e.g., Azure AI Owner)
- Azure CLI installed (optional, for command-line approach)
- Basic understanding of REST APIs

---

## Lab Architecture
By the end of this lab, you will have:
- A Microsoft Foundry resource with a deployed model
- An Azure API Management instance configured to route requests to your model
- A Log Analytics workspace for monitoring API usage and performance
- The ability to call your model via REST API using curl

---

## Step 1: Setup an Azure API Management Resource and Log Analytics Workspace

### 1.1 Sign in to Azure Portal
1. Navigate to the [Azure Portal](https://portal.azure.com/)
2. Sign in with your Azure account credentials

### 1.2 Create a Resource Group
1. In the Azure Portal, click **Create a resource**
2. Search for **Resource Group** and select it
3. Click **Create**
4. Configure the resource group:
   - **Subscription:** Select your subscription
   - **Resource group name:** `rg-foundry-lab`
   - **Region:** `Australia East`
5. Click **Review + Create**, then **Create**

### 1.3 Create an API Management Instance
1. In the Azure Portal, click **Create a resource**
2. Search for **API Management** and select it
3. Click **Create**
4. Configure the API Management service:
   - **Subscription:** Select your subscription
   - **Resource group:** `rg-foundry-lab`
   - **Region:** `Australia East` (same as your Foundry resource)
   - **Resource name:** `apim<yourname>` (must be globally unique)
   - **Organization name:** Your organization name (can be your name or company name)
   - **Administrator email:** Your email address (any valid email for notifications)
   - **Pricing tier:** Select **Basic**
5. Click **Review + Create**, then **Create**
6. Do not wait for deployment to complete. **Proceed to next step**.

### 1.4 Create a Log Analytics Workspace
1. In the Azure Portal, click **Create a resource**
2. Search for **Log Analytics Workspaces** and select it
3. Click **Create**
4. Configure the Log Analytics Workspace:
   - **Subscription:** Select your subscription
   - **Resource group:** `rg-foundry-lab`
   - **Name:** `law-foundry-lab`
   - **Region:** `Australia East`
5. Click **Review + Create**, then **Create**
6. Wait for deployment to complete (typically 1-2 minutes)
---

## Step 2: Setup a Foundry Resource

### 2.1 Create a Foundry Resource
1. In the Azure Portal, click **Create a resource**
2. Search for **Microsoft Foundry** and select it.
3. Under Use with Foundry select **Foundry**.
4. Click **Create**
5. Configure the resource:
   - **Subscription:** Select your subscription
   - **Resource group:** `rg-foundry-lab`  
   - **Name:** `foundry<yourname>` (must be globally unique)
   - **Region:** `Australia East`
   - **Default project name:** `project01`
6. Click **Review + Create**, then **Create**
7. Wait for the deployment to complete (typically 1-2 minutes)

### 2.2 Access Microsoft Foundry Portal
1. Once deployment completes, click **Go to resource**
2. In the resource overview, click **Go to Foundry Portal** or navigate directly to [https://ai.azure.com/](https://ai.azure.com/)
3. Sign in with your Azure credentials
4. Verify that you are in the New Foundry Portal and that your project (`project01`) is selected in the upper left corner.

---

## Step 3: Deploy a Foundry Model

### 3.1 Deploy a Model
1. In Microsoft Foundry, navigate to **Build** in the top navigation
2. Select **Models** from the left sidebar
3. Click **Deploy a base model**
4. Search for the **gpt-4.1** model
5. **Select** the model.
6. Select Deploy->Custom settings.
7. Configure the deployment:
   - **Deployment name:** `gpt-4.1`
   - **Deployment type:** Select **Global Standard** (pay-per-token, easiest for testing)
   - **Tokens per minute rate limit:** `50000`

> **Note:** Global Standard deployments provide the highest initial throughput and are ideal for variable, bursty traffic patterns.

8. Click **Deploy**
9. Wait for deployment to complete (typically 1-3 minutes)

### 3.2 Deploy another Model
1. Select Models from the left sidebar.
2. Repeat the deployment steps to deploy a DeepSeek model with the following configuration:
   - **Model:** DeepSeek-V3.2
   - **Deployment name:** `DeepSeek-V3.2`
   - **Deployment type:** Select **Global Standard**
   - **Tokens per minute rate limit:** `50000`

---

## Step 4: Test the Model in the Playground

### 4.1 Access the Playground
1. In Microsoft Foundry, navigate to **Build** > **Models**
2. Select your deployment: `gpt-4.1`
3. Select Open in playground

### 4.2 Configure the Playground
1. In the **System message** field, add context:
   ```
   You are a helpful AI assistant that provides concise and accurate answers about Azure. If you don't know the answer, say you don't know. Always provide clear and informative responses. If you are asked questions about other topics besides Azure, politely decline to answer.
   ```
2. Adjust parameters:
   - **Temperature:** `0.7` (controls randomness; 0 = deterministic, 1 = creative)
   - **Max tokens:** `800` (maximum response length)
   - **Top P:** `0.95` (nucleus sampling threshold)

### 4.3 Test the Model
1. In the **User message** field, type a test prompt:
   ```
   What are the top 3 benefits of using Azure API Management with AI models?
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

### 4.4 Verify Token Usage
1. At the bottom of the response, you'll see token usage metrics:
  - **Input:** Number of tokens in your input
  - **Output:** Number of tokens in the response

2. Go to the Monitor tab to view detailed usage metrics and trends.

> **Note:** Token usage affects your billing and is important for monitoring costs.

### 4.5 Test the Second Model
1. Go back to the Models list and open the playground for `DeepSeek-V3.2`
2. Repeat the same testing steps 4.2 to 4.3 with similar prompts to verify the second model is also working correctly.

---

## Step 5: Setup the Model to be Called via Azure API Management

### 5.1 Verify API Management is Ready
1. Return to the Azure Portal
2. Navigate to **Resource groups** > `rg-foundry-lab` > `apim<yourname>`
3. Verify the **Status** shows as **Online** (if not, wait for completion)

### 5.2 Import the Foundry Model API into APIM
1. In your API Management instance, navigate to **APIs** in the left menu
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
   - **Client compatibility:** Select **Azure OpenAI** (since we're using OpenAI-compatible models)
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

6. On the **Apply semantic caching** tab:
   - Optionally enable semantic caching to reduce costs and latency for similar requests
   - For this lab, we will disable, so leave it OFF
   - Click **Next**

7. On the **AI content safety** tab:
   - Optionally configure Azure AI Content Safety integration
   - For this lab, you will skip this step because there is a default content safety policy applied for all the models deployed in Foundry.
   - Click **Review**

8. Review the configuration and click **Create**

### 5.3 Verify API Configuration and Enable Monitoring
1. Once created, click on the **Microsoft Foundry API** in the APIs list
2. Navigate to the **Design** tab
3. Verify operations are listed (e.g., `Creates a completion for the chat message`)
4. Select All operations->Inbound processing->Policies. Review the automatically applied policies for token per minute and token quota enforcement.
5. Navigate to the **Settings** tab
6. Note the following:
   - **Base URL:** This shows your APIM gateway URL
   - **Copy this URL to your Notepad for use in calling the API.**
7. Scroll down to the **Subscriptions** section
   - Notice that Subscription required is set to Yes.
   - Notice that Header name is set to `api-key` - this is the header you will use to pass your subscription key for authentication when calling the API.
8. Scroll down to the **Diagnostics Logs** section
9. Select Azure Monitor.
10. Select Please enable Azure Monitor diagnostics here link.
11. In the Diagnostics settings page, click **+ Add diagnostic setting**
12. Configure the diagnostic setting:
    - **Diagnostic setting name:** `default`
    - Category groups: Enable allLogs and audit
    - Metrics: Enable AllMetrics
    - Destination details: Send to Log Analytics workspace
    - Log Analytics workspace: `law-foundry-lab` (the workspace you created in Step 1.4)
    - Click **Save**
13. Head back to the Settings tab of the Microsoft Foundry API and scroll down to the **Diagnostics Logs** section
14. Select Azure Monitor tab. Enable Override global.
15. Enable Log LLM messages.
16. Enable Log prompts and Log completions.
17. Click Save.

### 5.4 Test the API in APIM
1. In the **Design** tab, select the `Creates a completion for the chat message` operation
2. Click on the **Test** tab
3. Configure the test request:
    - **deployment-id:** `gpt-4.1`
    - **api-version:** `2025-03-01-preview` (or latest Azure OpenAI API version)
    - **Request body:**
    ```json
    {
        "model": "gpt-4.1",
        "messages": [
        {
            "role": "user",
            "content": "Hello! What can you tell me about Azure API Management?"
        }
        ],
        "max_tokens": 500,
        "temperature": 0.7
    }
    ```
4. Click **Send**.
5. Review the response and verify you receive a valid response from the model with token usage headers included.
6. Modify the deployment-id to `DeepSeek-V3.2` and test the second model as well.

### 5.4 Get Your API Credentials
1. In APIM, navigate to **Subscriptions** in the left menu
2. Create a new subscription:
   - Click **+ Add subscription**
   - **Name:** `foundry-test-subscription`
   - **Display name:** `Foundry Test Subscription`
   - **Scope:** Select **API** > **Azure OpenAI API**
   - Click **Create**
3. Click the **...** menu next to your subscription and select **Show/hide keys**
4. Copy the **Primary key** to your Notepad - you'll need this for authentication

---

## Step 6: Run the Model via Azure Cloud Shell

### 6.1 Open Azure Cloud Shell
1. In the Azure Portal, click the **Cloud Shell** icon in the top navigation bar (looks like `>_`)
2. Select **Bash** as your shell environment
3. Select No storage account required.
4. Select your Subscription.
5. Select Apply.
6. Wait for Cloud Shell to initialize (this may take a minute)
7. Once Cloud Shell opens, you'll see a Bash command prompt

> **Note:** Azure Cloud Shell is a browser-based shell environment with pre-installed tools including curl, which makes it perfect for testing APIs. No storage account is required for this lab.

### 6.2 Set Environment Variables

In Cloud Shell, set up your environment variables. You'll need the following information:
- **APIM Instance Name:** `apim<yourname>` (e.g., `apimjohn`)
- **Subscription Key:** From Step 5.4
- **Deployment Name:** `gpt-4.1` or `DeepSeek-V3.2`
- **API Version:** `2025-03-01-preview`

Copy and paste the following commands, replacing the placeholder values:

```bash
# Set your API Management endpoint (from Step 5.3)
APIM_ENDPOINT="YOUR_API_URL"

# Set your subscription key (from Step 5.4)
SUBSCRIPTION_KEY="YOUR_SUBSCRIPTION_KEY_HERE"

# Set the deployment name
DEPLOYMENT_NAME="gpt-4.1"

# Set the API version
API_VERSION="2025-03-01-preview"
```

### 6.3 Test the GPT-4.1 Model

Now run a curl command to test your first model deployment:

```bash
curl -X POST "${APIM_ENDPOINT}/deployments/${DEPLOYMENT_NAME}/chat/completions?api-version=${API_VERSION}" \
  -H "Content-Type: application/json" \
  -H "api-key: ${SUBSCRIPTION_KEY}" \
  -d '{
    "messages": [
      {
        "role": "user",
        "content": "What are the top 3 benefits of using Azure API Management with AI models? Keep it concise."
      }
    ],
    "max_tokens": 200,
    "temperature": 0.7
  }' | jq '.'
```

> **Note:** The `| jq '.'` at the end formats the JSON response for better readability. If jq is not available, you can remove this part.

### 6.4 Verify the Response

You should receive a response similar to:
```json
{
  "choices": [
    {
      "content_filter_results": {
        "hate": {
          "filtered": false,
          "severity": "safe"
        },
        "protected_material_code": {
          "detected": false,
          "filtered": false
        },
        "protected_material_text": {
          "detected": false,
          "filtered": false
        },
        "self_harm": {
          "filtered": false,
          "severity": "safe"
        },
        "sexual": {
          "filtered": false,
          "severity": "safe"
        },
        "violence": {
          "filtered": false,
          "severity": "safe"
        }
      },
      "finish_reason": "stop",
      "index": 0,
      "logprobs": null,
      "message": {
        "annotations": [],
        "content": "**Top 3 benefits of using Azure API Management with AI models:**\n\n1. **Secure & Scalable Access**: Protect AI endpoints with authentication, rate limiting, and scalability for external and internal users.\n2. **Centralized Monitoring & Analytics**: Track usage, performance, and errors of AI APIs with built-in logging and analytics.\n3. **Easy Integration & Versioning**: Simplify integration and manage multiple AI model versions through unified APIs and documentation.",
        "refusal": null,
        "role": "assistant"
      }
    }
  ],
  "created": 1777539621,
  "id": "chatcmpl-DaHXpPJW6vp41Ss0WI2QVBX0eICGN",
  "model": "gpt-4.1-2025-04-14",
  "object": "chat.completion",
  "prompt_filter_results": [
    {
      "prompt_index": 0,
      "content_filter_results": {
        "hate": {
          "filtered": false,
          "severity": "safe"
        },
        "jailbreak": {
          "detected": false,
          "filtered": false
        },
        "self_harm": {
          "filtered": false,
          "severity": "safe"
        },
        "sexual": {
          "filtered": false,
          "severity": "safe"
        },
        "violence": {
          "filtered": false,
          "severity": "safe"
        }
      }
    }
  ],
  "service_tier": "default",
  "system_fingerprint": "fp_7a7fd0eb44",
  "usage": {
    "completion_tokens": 95,
    "completion_tokens_details": {
      "accepted_prediction_tokens": 0,
      "audio_tokens": 0,
      "reasoning_tokens": 0,
      "rejected_prediction_tokens": 0
    },
    "prompt_tokens": 27,
    "prompt_tokens_details": {
      "audio_tokens": 0,
      "cached_tokens": 0
    },
    "total_tokens": 122
  }
}
```

Review the response and verify:
- ✅ You receive a `200 OK` status
- ✅ The response contains a `choices` array with the model's answer
- ✅ Token usage is reported
- ✅ Check response headers for token consumption tracking (if configured in Step 5.2)

### 6.5 Test the DeepSeek Model

Now test your second model deployment. Update the deployment name and run another request:

```bash
# Update deployment name for DeepSeek
DEPLOYMENT_NAME="DeepSeek-V3.2"

curl -X POST "${APIM_ENDPOINT}/deployments/${DEPLOYMENT_NAME}/chat/completions?api-version=${API_VERSION}" \
  -H "Content-Type: application/json" \
  -H "api-key: ${SUBSCRIPTION_KEY}" \
  -d '{
    "messages": [
      {
        "role": "user",
        "content": "Explain the difference between Azure OpenAI and Microsoft Foundry in one sentence."
      }
    ],
    "max_tokens": 150,
    "temperature": 0.7
  }' | jq '.'
```

Compare the responses from both models and note any differences in:
- Response style and content
- Token consumption
- Response time

### 6.6 Test Error Handling

Test how APIM handles authentication failures by using an invalid subscription key:

```bash
curl -X POST "${APIM_ENDPOINT}/deployments/gpt-4.1/chat/completions?api-version=${API_VERSION}" \
  -H "Content-Type: application/json" \
  -H "api-key: invalid-key-12345" \
  -d '{
    "messages": [
      {
        "role": "user",
        "content": "What are Microsoft Foundry Models?"
      }
    ],
    "max_tokens": 500
  }' | jq '.'
```

Expected response:
```json
{
  "statusCode": 401,
  "message": "Access denied due to invalid subscription key. Make sure to provide a valid key for an active subscription."
}
```

### 6.7 Test Token Quota Limits

In Cloud Shell, test the token quota limits you configured in Step 5.2. Run multiple requests to exceed the hourly quota:

```bash
curl -X POST "${APIM_ENDPOINT}/deployments/${DEPLOYMENT_NAME}/chat/completions?api-version=${API_VERSION}" \
  -H "Content-Type: application/json" \
  -H "api-key: ${SUBSCRIPTION_KEY}" \
  -d '{
    "messages": [
      {
        "role": "user",
        "content": "What is Microsoft Foundry? Provide a detailed explanation covering its key features, benefits, and use cases in the context of AI model deployment and management in at least 1000 words."
      }
    ],
    "max_tokens": 1000,
    "temperature": 0.7
  }' | jq '.'
```

If you run the request twice in quick succession, you will trigger the tokens per minute limit, which will return a different error message indicating too many requests.
```json
{
  "statusCode": 429,
  "message": "Token limit is exceeded. Try again in 53 seconds."
}
```

After several requests, you should see a quota exceeded error message indicating the token limit policy is working. You will need to wait for the quota to reset before you can make successful requests again.
```json
{
  "statusCode": 403,
  "message": "Token quota is exceeded. Try again in 21 minutes and 33 seconds."
}
```

### 6.8 Monitor API Usage in Log Analytics
Note: It may take 20-30 minutes for logs to appear in Log Analytics after making API calls.
1. In the Azure Portal, navigate to **Log Analytics workspaces** > `law-foundry-lab`
2. Click on **Logs** in the left menu
3. Select KQL mode in the right side.
4. Use the following query to view API call logs and token usage:
```kusto
ApiManagementGatewayLlmLog
```
5. Observe the logs for your API calls, including request details, response status, and token usage metrics.

---

## Verification and Testing

### Verification Checklist
- [ ] Foundry resource created successfully
- [ ] API Management instance is online
- [ ] GPT-4.1 model deployed in Foundry portal
- [ ] DeepSeek-V3.2 model deployed in Foundry portal
- [ ] Both models tested successfully in playground
- [ ] Foundry API imported into APIM with token policies
- [ ] Subscription key obtained
- [ ] Azure Cloud Shell opened and configured
- [ ] Successful API calls to both models from Cloud Shell
- [ ] Responses received with model output and token usage
- [ ] Token quota policies tested and verified

### Troubleshooting Common Issues

**Issue 1: API Management still provisioning**
- **Solution:** APIM Basic tier takes 30-45 minutes to provision. Check status in Azure Portal and wait for **Status: Online** before proceeding to Step 5.

**Issue 2: 401 Unauthorized error**
- **Solution:** 
  - Verify your subscription key is correct and copied completely (no extra spaces)
  - Check that the subscription is associated with the **Azure OpenAI API** (from Step 5.4)
  - Verify the subscription is in **Active** state in APIM

**Issue 3: 404 Not Found error**
- **Solution:** 
  - Verify the deployment name matches exactly (`gpt-4.1` or `DeepSeek-V3.2`)
  - Check that the base path is `/openai/` (not `/foundry/`)
  - Ensure API version is valid (`2025-03-01-preview`)
  - Verify your APIM instance name is correct in the URL

**Issue 4: Model deployment fails**
- **Solution:** 
  - Verify you have sufficient quota in Australia East region
  - Try a different deployment type (e.g., Data Zone Standard)
  - Check Azure Service Health for any regional issues
  - Ensure the model is available in Australia East region

**Issue 5: Timeout errors**
- **Solution:** 
  - Check that your Foundry resource is in Australia East (same region as APIM)
  - Verify network connectivity between APIM and Foundry resource
  - Increase timeout settings in APIM policies if needed
  - Try a simpler prompt with lower max_tokens

**Issue 6: Token quota exceeded errors appearing immediately**
- **Solution:**
  - The hourly quota (5000 tokens) may have been reached during testing
  - Wait for the quota to reset (check Step 5.2 settings)
  - Increase the quota limit in APIM token policy if needed
  - Check APIM Analytics to see actual token consumption
  - Increase timeout settings in APIM if needed

---

## Clean Up Resources

To avoid incurring charges, delete the resources when you're finished with the lab:

### Option 1: Delete the Resource Group (Recommended)
1. In the Azure Portal, navigate to **Resource groups**
2. Select `rg-foundry-lab`
3. Click **Delete resource group**
4. Type the resource group name to confirm
5. Click **Delete**

### Option 2: Delete Individual Resources
If you want to keep some resources:
1. Delete the API Management instance (highest cost)
2. Delete the AI Services resource
3. Keep the resource group for future use

> **Note:** Deleting APIM may take several minutes to complete.

---

## Summary and Key Takeaways

In this lab, you successfully:

1. ✅ Created a Microsoft Foundry resource for hosting AI models
2. ✅ Provisioned an Azure API Management instance for API gateway capabilities
3. ✅ Deployed a GPT model in Microsoft Foundry
4. ✅ Tested the model in the Foundry playground
5. ✅ Integrated the Foundry API with API Management
6. ✅ Called the model via REST API using curl

### Benefits of Using APIM with Foundry Models

**Best Answer:** Using Azure API Management with Microsoft Foundry Models is the optimal approach because it provides:
- **Centralized management:** Single gateway for all your APIs, including AI models
- **Enhanced security:** Subscription keys, OAuth, rate limiting, and IP filtering
- **Cost control:** Token usage tracking, quotas, and monitoring to prevent unexpected costs
- **Performance optimization:** Response caching (including semantic caching for AI responses)
- **Observability:** Built-in analytics, logging, and integration with Application Insights
- **Compliance:** Policy enforcement, request/response transformation, and audit trails

### Why Other Approaches Are Less Suitable

**Direct Foundry API calls:** While calling Foundry APIs directly is simpler for testing, it lacks centralized governance, security policies, and cost management capabilities that enterprises require.

**Custom gateway implementations:** Building your own gateway adds development and maintenance overhead, and you miss out on APIM's extensive policy library and Azure ecosystem integrations.

---

## Next Steps and Further Learning

### Explore Advanced Features
1. **Token Limits:** Configure per-subscription token limits to control costs
   - Documentation: [Manage token consumption](https://learn.microsoft.com/en-us/azure/api-management/llm-token-limit-policy)

2. **Semantic Caching:** Enable caching for similar prompts to reduce costs and latency
   - Documentation: [Enable semantic caching](https://learn.microsoft.com/en-us/azure/api-management/azure-openai-enable-semantic-caching)

3. **Content Safety:** Integrate Azure AI Content Safety to filter inappropriate content
   - Documentation: [Enforce content safety checks](https://learn.microsoft.com/en-us/azure/api-management/llm-content-safety-policy)

4. **Load Balancing:** Configure multiple Foundry deployments for high availability
   - Documentation: [Backend pools in APIM](https://learn.microsoft.com/en-us/azure/api-management/backends)

5. **Developer Portal:** Customize the APIM developer portal for your API consumers
   - Documentation: [Customize developer portal](https://learn.microsoft.com/en-us/azure/api-management/api-management-howto-developer-portal-customize)

### Related Training Resources
- [Explore API Management - Microsoft Learn](https://learn.microsoft.com/en-us/training/modules/explore-api-management/)
- [Develop generative AI apps in Microsoft Foundry](https://learn.microsoft.com/en-us/training/paths/create-custom-copilots-ai-studio/)
- [Microsoft Certified: Azure AI Fundamentals](https://learn.microsoft.com/en-us/credentials/certifications/azure-ai-fundamentals/)

---

## References and Citations

This lab was created using information from the following official Microsoft Learn documentation:

1. **Microsoft Foundry Overview**
   - [What is Microsoft Foundry?](https://learn.microsoft.com/en-us/azure/foundry/)
   - Primary source for understanding Foundry architecture and capabilities

2. **Foundry Resource Setup**
   - [Quickstart: Set up Microsoft Foundry resources](https://learn.microsoft.com/en-us/azure/foundry/tutorials/quickstart-create-foundry-resources)
   - Used for Steps 1 and 3: Creating resources and deploying models

3. **Deployment Types**
   - [Deployment types for Microsoft Foundry Models](https://learn.microsoft.com/en-us/azure/foundry/foundry-models/concepts/deployment-types)
   - Referenced in Step 3 for understanding deployment type selection

4. **APIM Integration**
   - [Import a Microsoft Foundry API](https://learn.microsoft.com/en-us/azure/api-management/azure-ai-foundry-api)
   - Used for Steps 2, 5, and 6: APIM setup and API integration

5. **API Management Documentation**
   - [Azure API Management Documentation](https://learn.microsoft.com/en-us/azure/api-management/)
   - Referenced throughout for APIM concepts and best practices

---

## Lab Completion Badge

Congratulations! 🎉 You have completed the **Microsoft Foundry Models with Azure API Management** lab.

You now have hands-on experience with:
- Microsoft Foundry resource management
- AI model deployment and testing (GPT-4.1 and DeepSeek-V3.2)
- Azure API Management configuration
- REST API integration with AI models
- Token consumption policies and quota management
- Testing with Azure Cloud Shell
- Monitoring API usage and analytics

**Lab Version:** 1.1  
**Last Updated:** April 30, 2026  
**Microsoft Learn References:** Current as of April 2026

---

## Appendix: Additional Code Examples

### Python Example
```python
import requests
import json

# Configuration - replace with your values
apim_name = "apim<yourname>"  # e.g., "apimjohn"
apim_endpoint = f"https://{apim_name}.azure-api.net/openai"
subscription_key = "YOUR_SUBSCRIPTION_KEY"
deployment_name = "gpt-4.1"
api_version = "2025-03-01-preview"

# Headers
headers = {
    "Content-Type": "application/json",
    "Ocp-Apim-Subscription-Key": subscription_key
}

# Request body
data = {
    "messages": [
        {
            "role": "user",
            "content": "Explain Azure API Management in simple terms."
        }
    ],
    "max_tokens": 200,
    "temperature": 0.7
}

# Make request
url = f"{apim_endpoint}/openai/deployments/{deployment_name}/chat/completions?api-version={api_version}"
response = requests.post(url, headers=headers, json=data)

# Print response
if response.status_code == 200:
    print(json.dumps(response.json(), indent=2))
    print(f"\nTokens used: {response.json()['usage']['total_tokens']}")
else:
    print(f"Error: {response.status_code}")
    print(response.text)
```

### C# Example
```csharp
using System;
using System.Net.Http;
using System.Text;
using System.Text.Json;
using System.Threading.Tasks;

class Program
{
    static async Task Main(string[] args)
    {
        // Configuration - replace with your values
        string apimName = "apim<yourname>";  // e.g., "apimjohn"
        string apimEndpoint = $"https://{apimName}.azure-api.net/openai";
        string subscriptionKey = "YOUR_SUBSCRIPTION_KEY";
        string deploymentName = "gpt-4.1";
        string apiVersion = "2025-03-01-preview";

        using var client = new HttpClient();
        client.DefaultRequestHeaders.Add("Ocp-Apim-Subscription-Key", subscriptionKey);

        var requestBody = new
        {
            messages = new[]
            {
                new { role = "user", content = "What is Microsoft Foundry?" }
            },
            max_tokens = 150,
            temperature = 0.7
        };

        string json = JsonSerializer.Serialize(requestBody);
        var content = new StringContent(json, Encoding.UTF8, "application/json");

        string url = $"{apimEndpoint}/openai/deployments/{deploymentName}/chat/completions?api-version={apiVersion}";
        var response = await client.PostAsync(url, content);
        
        string result = await response.Content.ReadAsStringAsync();
        Console.WriteLine(result);
        Console.WriteLine($"\nStatus: {response.StatusCode}");
    }
}
```

### JavaScript (Node.js) Example
```javascript
const axios = require('axios');

// Configuration - replace with your values
const apimName = 'apim<yourname>';  // e.g., 'apimjohn'
const apimEndpoint = `https://${apimName}.azure-api.net/openai`;
const subscriptionKey = 'YOUR_SUBSCRIPTION_KEY';
const deploymentName = 'gpt-4.1';
const apiVersion = '2025-03-01-preview';

// Request configuration
const config = {
    headers: {
        'Content-Type': 'application/json',
        'Ocp-Apim-Subscription-Key': subscriptionKey
    }
};

// Request body
const data = {
    messages: [
        {
            role: 'user',
            content: 'Tell me about Azure API Management benefits.'
        }
    ],
    max_tokens: 200,
    temperature: 0.7
};

// Make request
const url = `${apimEndpoint}/openai/deployments/${deploymentName}/chat/completions?api-version=${apiVersion}`;

axios.post(url, data, config)
    .then(response => {
        console.log(JSON.stringify(response.data, null, 2));
        console.log(`\nTokens used: ${response.data.usage.total_tokens}`);
    })
    .catch(error => {
        console.error('Error:', error.response ? error.response.data : error.message);
    });
```

---

**End of Lab**
