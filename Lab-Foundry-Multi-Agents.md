# Lab: Build Multi-Agent Systems using Workflows and Orchestrations in Microsoft Foundry and the Microsoft Agent Framework

## Overview
In this hands-on lab, you will use the Microsoft Foundry portal to build a workflow for automating customer support ticket processing. You will create AI agents to classify tickets, handle low-confidence cases, and generate recommended responses, applying conditional logic for routing and escalation. You then connect the workflow to Python code via the Azure AI Projects SDK to run and validate automated support ticket handling programmatically.

In the final section, you will explore advanced multi-agent collaboration using Group Chat orchestration, where multiple agents work together iteratively to solve problems through collaborative refinement.

**Estimated Time:** 90 minutes

**Prerequisites:**
- An Azure account with an active subscription
- Access to a Microsoft Foundry resource with a deployed project
- Basic understanding of AI agents and workflows
- Familiarity with Python programming
- Azure Cloud Shell access

---

## Lab Architecture
By the end of this lab, you will have:
- An Azure resource group for organizing all lab resources
- A Microsoft Foundry resource with a deployed project
- A GPT-4.1 model deployment for agent capabilities
- A workflow in Microsoft Foundry for customer support ticket processing
- A Triage Agent that classifies support tickets with confidence scores
- A Resolution Agent that generates recommended responses
- Conditional logic for handling low-confidence classifications and routing
- A Python application that invokes the workflow programmatically via Azure AI Projects SDK
- A Group Chat orchestration with multiple agents collaborating iteratively
- Experience with agent-based orchestrators for intelligent speaker coordination

### Workflow Overview
- **Collect incoming support tickets:** The workflow starts with a predefined array of customer support issues
- **Process tickets one at a time:** A for-each loop iterates over the array, ensuring each support ticket is handled independently
- **Classify each ticket with an AI agent:** The workflow invokes a Triage Agent to classify the issue as Billing, Technical, or General, along with a confidence score
- **Handle uncertainty with conditional logic:** If the confidence score is below a defined threshold, the workflow recommends additional information
- **Route based on issue category:** Billing issues are flagged for escalation. Technical and General issues continue through automated handling
- **Generate a recommended response:** For non-billing tickets, the workflow invokes a Resolution Agent to draft a category-appropriate support response

### Group Chat Orchestration Overview
- **Multi-agent collaboration:** Multiple specialized agents work together iteratively
- **Centralized coordination:** An orchestrator manages speaker selection and conversation flow
- **Iterative refinement:** Agents review and build upon each other's responses
- **Shared context:** All agents see the full conversation history for collaborative problem-solving

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
   - **Resource group name:** `rg-foundry-workflows`
   - **Region:** `Australia East`
5. Click **Review + Create**, then **Create**

### 1.3 Create a Foundry Resource
1. In the Azure Portal, click **Create a resource**
2. Search for **Microsoft Foundry** and select it
3. Click **Create**
4. Configure the resource:
   - **Subscription:** Select your subscription
   - **Resource group:** `rg-foundry-workflows`
   - **Name:** `foundry-workflows-<yourname>` (must be globally unique)
   - **Region:** `Australia East`
   - **Default project name:** `workflows-project`
5. Click **Review + Create**, then **Create**
6. Wait for the deployment to complete (typically 1-2 minutes)

### 1.4 Access Microsoft Foundry Portal
1. Once deployment completes, click **Go to resource**
2. In the resource overview, click **Go to Foundry Portal** or navigate directly to [https://ai.azure.com/](https://ai.azure.com/)
3. Sign in with your Azure credentials
4. Verify that you are in the Foundry Portal and that your project (`workflows-project`) is selected in the upper left corner

### 1.5 Deploy a Model for Your Agents
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

### 1.6 Verify Model Deployment
1. Once deployment completes, you should be sent to the Playground with the `gpt-4.1` model selected
2. In the input box, enter a test prompt:
   ```
   What is Microsoft Foundry?
   ```
3. Click **Submit**
4. Verify you receive a coherent response describing Microsoft Foundry

---

## Step 2: Create a Customer Support Triage Workflow

### 2.1 Create a Blank Workflow
1. Navigate to the Foundry portal home page
2. Select **Build** from the toolbar menu
3. On the left-hand menu, select **Agents > Workflows**
4. In the upper right corner, select **Create** > **Blank workflow** to create a new blank workflow
5. Select **Save** in the visualizer found in the upper right to save your new workflow
6. In the dialog box, enter a name for your workflow: `ContosoPay-Customer-Support-Triage`
7. Select **Save**

### 2.2 Create a Ticket Array Variable
In this task, you will initialize a support ticket array variable in the workflow to simulate incoming customer requests for automated processing.

1. In the workflow visualizer, select the **+** (plus) icon to add a new node
2. In the workflow actions menu, under **Data transformation**, select **Set variable** to add a node that initializes an array of support tickets
3. In the Set variable node editor, create a new variable by entering `SupportTickets` and selecting **Create new variable** from the drop-down
   - The new variable should appear as `Local.SupportTickets`
4. In the **To value** field, enter the following array that contains sample support tickets:
   ```
   [ 
   "The API returns a 403 error when creating invoices, but our API key hasn't changed.", 
   "Is there a way to export all invoices as a CSV?", 
   "I was charged twice for the same invoice last Friday and my customer is also seeing two receipts. Can someone fix this?",
   "I have an issue."
   ]
   ```
5. Select **Done** to save the node

### 2.3 Add a For-Each Loop to Process Tickets
In this task, you will configure a for-each loop to iterate through each support ticket and process them individually within the workflow.

1. Select the **+** icon next to Set variable, scroll under **Flow**, and then choose **For each** to add a loop for processing each support ticket
2. In the For each node editor, set **Select the items to loop for each** to `Local.SupportTickets`
3. Enter `CurrentTicket` in the **Loop Value Variable** field
4. Select **Create new variable "CurrentTicket"**
5. Select **Done** to save the node

### 2.4 Invoke an Agent to Classify the Ticket
In this task, you will invoke the Triage Agent to classify each support ticket into a category and generate a confidence score using structured JSON output.

1. Select the **+** (plus) icon within the For each node to add a new node that classifies the current support ticket
2. In the workflow actions menu, under **Invoke**, select **Agent** to add an agent node
3. In the Agent pane, open the **Select an agent** dropdown, and then choose **Create a new agent**
4. In the Create an agent pane, enter `Triage-Agent` as the agent name, and then select **Create**
5. In the **Details** tab, select the **Parameters** icon next to the model name
6. In the Parameters pane, open the **Text format** dropdown, and then select **JSON Schema**
7. In the Add response format pane, enter the following definition and select **Save**:
   ```json
   {
     "name": "category_response",
     "schema": {
       "type": "object",
       "properties": {
         "customer_issue": {
           "type": "string"
         },
         "category": {
           "type": "string"
         },
         "confidence": {
           "type": "number"
         }
       },
       "additionalProperties": false,
       "required": [
         "customer_issue",
         "category",
         "confidence"
       ]
     },
     "strict": true
   }
   ```
   Exit the Parameters pane after saving the response format.
8. In the Agent Details pane, set the **Instructions** field to the following prompt:
   ```
   Classify the user's problem description into exactly ONE category from the list below. Provide a confidence score from 0 to 1.

   Billing
   - Charges, refunds, duplicate payments
   - Missing or incorrect payouts
   - Subscription pricing or invoices being charged

   Technical
   - API errors, integrations, webhooks
   - Platform bugs or unexpected behavior

   General
   - How-to questions
   - Feature availability
   - Data exports, reports, or UI navigation

   Important rules
   - Questions about exporting, viewing, or downloading invoices are General, not Billing
   - Billing ONLY applies when money was charged, refunded, or paid incorrectly
   ```
9. Select **Node settings** tab beside the Details tab to configure the input and output of the agent
10. Set the **Input message** field to the `Local.CurrentTicket` variable
11. Under **Save agent output message as**, create a new variable by entering `TriageOutputText` and select **Create new variable** from the drop-down
12. Under **Save output json_object/json_schema as**, create a new variable by entering `TriageOutputJson` and select **Create new variable** from the drop-down
13. Select **Done** to save the node

### 2.5 Handle Low-Confidence Classifications
In this task, you will add conditional logic to evaluate the confidence score and determine whether the ticket classification is reliable for further automated processing.

1. Select the **+** icon next to Triage-Agent, and then choose **If / else** under **Flow** to add a conditional logic node for handling low-confidence classifications
>> Important: Make sure to select the **+** icon next to the Triage-Agent node inside the For each loop, not the one outside of it, to ensure the condition is evaluated for each individual ticket.
2. In the If / else node editor, select **+ Add a path** to create the **If** branch. Then select the Pencil icon in the If branch to edit the condition.
3. Set the **Condition** field to the following expression to check if the confidence score is above 0.6:
   ```
   Local.TriageOutputJson.confidence > 0.6
   ```
4. Select **Done** to save the node

### 2.6 Recommend Additional Info for Low-Confidence Tickets
In this task, you will configure the workflow to request additional details from the customer when the ticket classification confidence is low.

1. In the visualizer, beside the **Else** branch of the If / else condition node, select the **+** (plus) icon to add a new node that recommends additional information for low-confidence tickets
2. In the workflow actions menu, under **Basics**, select **Deliver a message** to add a send message activity
3. In the Deliver message node editor, set the **Message to send** field to the following response:
   ```
   The support ticket classification has low confidence. Requesting more details about the issue: "{Local.CurrentTicket}"
   ```
4. Select **Done**

### 2.7 Route the Ticket Based on Category
In this task, you will add routing logic to identify billing issues and escalate them to the human support team while allowing other categories to continue through automation.

1. In the visualizer, beside the **If** branch of the If / else condition node, select the **+** (plus) icon to add a new node that routes the ticket based on its category
2. In the workflow actions menu, under **Flow**, select **If / else** to add another conditional logic node
3. In the If / else node editor, select **+ Add a path** to create the **If** branch. Then select the Pencil icon in the If branch to edit the condition.
4. Set the **Condition** field to the following expression to check if the ticket category is "Billing":
   ```
   Local.TriageOutputJson.category = "Billing"
   ```
5. Select **Done**
6. Select the **+** (plus) icon beside the If branch of the If / else node to add a new node that drafts a response
7. In the workflow actions menu, under **Basics**, select **Deliver message** to add a send message activity
8. In the Deliver message node editor, set the **Message to send** to the following response:
   ```
   Escalate billing issue to human support team.
   ```
9. Select **Done** to save the node

### 2.8 Generate a Recommended Response
In this task, you will invoke the Resolution Agent to automatically generate a professional support response for non-billing tickets based on the classified category.

1. In the visualizer, select the **+** (plus) icon beside the **Else** branch of the second If / else node to add a new node that drafts a response for non-billing tickets
2. In the workflow actions menu, under **Invoke**, select **Agent** to add an agent node
3. In the Agent pane, open the **Select an agent** dropdown, and then select **Create a new agent** from the list
4. In the Create an agent pane, enter `Resolution-Agent` as the agent name, and then select **Create**
5. In the agent editor, set the **Instructions** field to the following prompt:
   ```
   You are a customer support resolution assistant for ContosoPay, a B2B payments and invoicing platform.

   Your task is to draft a clear, professional, and friendly support response based on the issue category and customer message.

   Guidelines:
   If the issue category is Technical:
   Suggest 1–2 common troubleshooting steps at a high level.
   Avoid asking for logs, credentials, or sensitive data.
   Do not imply fault by the customer.

   If the issue category is General:
   Provide a concise, helpful explanation or guidance.
   Keep the response under 5 sentences.

   Tone:
   Professional, calm, and supportive
   Clear and concise
   No emojis

   Output:
   Return only the drafted response text.
   Do not include internal reasoning or analysis.
   ```
6. Select **Node settings** to configure the input and output of the agent
7. Set the **Input message** field to the `Local.TriageOutputText` variable
8. Under **Save agent output message as**, create a new variable by entering `ResolutionOutputText` and select **Create new variable** from the drop-down
9. Select **Done** to save the node
10. Ensure that your workflow matches the one illustrated in **workflow.jpg** found in the Workflow folder of this repository.

### 2.9 Preview the Workflow
In this task, you will test and validate the workflow by running a preview to observe how support tickets are processed, classified, escalated, and resolved automatically.

1. Select the **Save** button to save all changes to your workflow
2. Select the **Preview** button to start the workflow
3. In the Preview pane, enter the following text to trigger the workflow:
   ```
   Start processing support tickets.
   ```
4. Select the **Send** icon
5. Observe the workflow as it processes each support ticket in sequence
6. Review the messages generated by the workflow in the chat window

You should see output indicating that billing issues are being escalated, technical and general issues receive drafted responses, and issues with low confidence are flagged for further review. For example:
```
Current Ticket:
The API returns a 403 error when creating invoices, but our API key hasn't changed.

Resolution-Agent:
Thank you for reaching out about the 403 error when creating invoices. This error typically indicates a permissions or access issue. 
Please ensure that your API key has the necessary permissions for invoice creation and that your request is being sent to the correct endpoint. 
If the issue persists, try regenerating your API key and updating it in your integration to see if that resolves the problem.
```

---

## Step 3: Use Your Workflow in Code

### 3.1 Prepare the Environment
In this task, you will prepare the environment in Microsoft Azure by setting up Cloud Shell, cloning the repository, and accessing the Python files required to invoke the workflow programmatically.

1. In the Azure portal, select the **Cloud Shell** icon in the top navigation bar to open a new Cloud Shell session
2. In the Cloud Shell toolbar, open the **Settings** menu and choose **Go to Classic version** from the drop-down
   > **Note:** Ensure you've switched to the classic version of the cloud shell before continuing.
3. In the cloud shell pane, enter the following commands to clone the GitHub repo containing the code files for this exercise:
   ```bash
   rm -r ai-agents -f
   git clone https://github.com/MicrosoftLearning/mslearn-ai-agents ai-agents
   ```
   > **Tip:** As you enter commands into the cloud shell, the output may take up a large amount of the screen buffer and the cursor on the current line may be obscured. You can clear the screen by entering the `clear` command to make it easier to focus on each task.
4. When the repo has been cloned, enter the following command to change the working directory to the folder containing the code files and list them all:
   ```bash
   cd ai-agents/Labfiles/08-build-workflow-ms-foundry/Python
   ls -a -l
   ```
   - The provided files include application code and a file for configuration settings

### 3.2 Configure the Application Settings
In this task, you will configure the application settings by installing dependencies and updating the project endpoint details to connect your code with Microsoft Foundry.

1. In the cloud shell command-line pane, enter the following command to install the libraries you'll use:
   ```bash
   python -m venv labenv
   source labenv/bin/activate
   pip install -r requirements.txt
   ```
   > **Tip:** As you enter commands into the cloud shell, the output may take up a large amount of the screen buffer. You can clear the screen by entering the `clear` command to make it easier to focus on each task.
2. Enter the following command to edit the configuration file that is provided:
   ```bash
   code .env
   ```
3. In the code file, replace the placeholder values with the correct details for your project:
   - **PROJECT_ENDPOINT:** Your Foundry project endpoint
   
   > **Note:** You can find your project endpoint in the Foundry portal by navigating to the Home page.
4. After you've replaced the placeholder, use the **CTRL+S** command to save your changes
5. Use the **CTRL+Q** command to close the code editor while keeping the cloud shell command line open

### 3.3 Connect to the Workflow and Run It
In this task, you will connect your Python application to the workflow and run it programmatically using the Azure AI Projects SDK to automate customer support processing.

> **Tip:** As you add code, be sure to maintain the correct indentation. Use the comment indentation levels as a guide.

1. Enter the following command to edit the workflow.py file:
   ```bash
   code workflow.py
   ```
2. Review the code in the file, noting that it contains comments indicating where you will add code to connect to your workflow and run it
3. Find the comment `# Add references` and add the following code to import the classes you'll need:
```python
# Add references
from azure.identity import AzureCliCredential
from azure.ai.projects import AIProjectClient
from azure.ai.projects.models import IndexType
```
4. Note that code to load the project endpoint from your environment variables has been provided
5. Find the comment `# Connect to the AI Project client`, and add the following code to create an AI Project Client connected to your project:
```python
# Connect to the AI Project client
with (
   AzureCliCredential() as credential,
   AIProjectClient(endpoint=endpoint, credential=credential) as project_client,
   project_client.get_openai_client() as openai_client,
):
```

6. Find the comment `# Specify the workflow` and add the following code:
   ```python
   # Specify the workflow
   workflow = {
       "name": "ContosoPay-Customer-Support-Triage",
       "version": "1",
   }
   ```
   - Be sure to use the exact name and version number of the workflow you created in the Foundry portal. You can verify this in the Agents tab of the Foundry portal under Workflows.
   - Be sure your code is properly indented to be within the context of the `with` statement that creates the AI Project Client

7. Find the comment `# Create a conversation and run the workflow`, and add the following code to create a conversation and invoke your workflow:
   ```python
   # Create a conversation and run the workflow
   conversation = openai_client.conversations.create()
   print(f"Created conversation (id: {conversation.id})")
    
   stream = openai_client.responses.create(
      conversation=conversation.id,
      extra_body={"agent_reference": {"name": workflow["name"], "type": "agent_reference"}},
      input="Start",
      stream=True,
      metadata={"x-ms-debug-mode-enabled": "1"},
   )
   ```
   - This code will stream the output of the workflow execution to the console, allowing you to see the flow of messages as the workflow processes each ticket
   - Be sure your code is properly indented to be within the context of the `with` statement that creates the AI Project Client

8. Find the comment `# Process events from the workflow run`, and add the following code to process the streamed output and print messages to the console:
   ```python
   # Process events from the workflow run
   for event in stream:
       if (event.type == "response.completed"):
           print("\nResponse completed:")
           for message in event.response.output:
               if message.content:
                   for content_item in message.content:
                       if content_item.type == 'output_text':
                           print(content_item.text)
       if (event.type == "response.output_item.done") and hasattr(event.item, 'action_id'):
           print(f"item action ID '{event.item.action_id}' is '{event.item.status}' (previous action ID: '{event.item.previous_action_id}')")
   ```
   - Be sure your code is properly indented to be within the context of the `with` statement that creates the AI Project Client

9. Find the comment `# Clean up resources`, and enter the following code to delete the conversation when it is no longer required:
   ```python
   # Clean up resources
   openai_client.conversations.delete(conversation_id=conversation.id)
   print("\nConversation deleted")
   ```
   - Be sure your code is properly indented to be within the context of the `with` statement that creates the AI Project Client

10. Use the **CTRL+S** command to save your changes to the code file
11. Use the **CTRL+Q** command to close the code editor while keeping the cloud shell command line open
12. Ensure that your final code matches the structure and content of the provided workflow.py file found in the Workflow folder of this repository.

### 3.4 Run the Application
In this task, you will execute the Python application to run and validate the AI-powered workflow end-to-end.

1. Login to Azure through the CLI by entering the following command and following the steps to authenticate:
   ```bash
   az login
   ```
   - Click the URL provided in the terminal and open it in a new browser tab. 
   - Enter the code provided in the terminal to authenticate your session then click Next.
   - Select your Azure account then click Continue to complete the login process. 
   - Once you see the message "You have signed in..." in the browser, return to the Cloud Shell.
   - Select your subscription by pressing Enter.

2. In the Cloud Shell console, enter the following command to run the application:
   ```bash
   python workflow.py
   ```
3. Wait a moment for the workflow to process the tickets
4. As the workflow runs, you should see output in the console indicating the progress of the workflow, including messages generated by the agents and status updates for each action
5. When the workflow completes, you should see output similar to the following:
   ```
   Created conversation (id: {id})
   item action ID 'action-{id}' is 'completed' (previous action ID: 'trigger_id')
   item action ID 'action-{id}' is 'completed' (previous action ID: 'action-{id}')
   item action ID 'action-{id}' is 'completed' (previous action ID: 'action-{id}_Start')
   ...

   Response completed:
   {"customer_issue":"The API returns a 403 error when creating invoices, but our API key hasn't changed.","category":"Technical","confidence":1}
   Thank you for reaching out. A 403 error typically indicates a permissions issue. Please ensure that your API key has the necessary permissions to create invoices and that it has not expired or been restricted. If the issue persists, try regenerating your API key and updating it in your integration. Let us know if you need further assistance.
   ```
6. If you are encountering issues, review your code for any syntax errors or indentation issues, and ensure that your workflow in the Foundry portal matches the one you are trying to invoke in your code.
> **Tip:** You may copy the code provided in the workflow.py file found in the Workflow folder of this repository and paste it into your workflow.py file in the cloud shell to ensure accuracy.
7. In the Cloud Shell window, select the **Close (X)** icon to exit Cloud Shell

---

## Step 4: Build a Group Chat Orchestration

### 4.1 Overview of Group Chat
Group chat orchestration models a collaborative conversation among multiple agents, coordinated by an orchestrator that determines speaker selection and conversation flow. This pattern is ideal for scenarios requiring iterative refinement, collaborative problem-solving, or multi-perspective analysis.

**Key Characteristics:**
- **Centralized Coordination:** An orchestrator coordinates who speaks next (unlike handoff patterns where agents directly transfer control)
- **Iterative Refinement:** Agents can review and build upon each other's responses in multiple rounds
- **Intelligent Speaker Selection:** An agent-based orchestrator makes strategic decisions about who should speak next
- **Shared Context:** All agents see the full conversation history, enabling collaborative refinement

**What This Lab Demonstrates:**
- Group Chat orchestration is NOT simple turn-taking
- Agents can be highly effective without any tools (no file search, no APIs, no external data)
- Orchestration logic and role separation create value through iterative improvement
- Shared context enables collaborative reasoning and quality control

### 4.2 Prepare the Group Chat Environment

1. In the Cloud Shell, ensure you're still in the working directory:
   ```bash
   cd ~/ai-agents/Labfiles/08-build-workflow-ms-foundry/Python
   ```
2. Add the model deployment in the .env file:  
   ```bash
   code .env
   ```
   - Place this in the file `MODEL_DEPLOYMENT_NAME=gpt-4.1`
   - Click **CTRL+S** to save the file and **CTRL+Q** to exit the editor.

3. Create a new Python file for the group chat example:
   ```bash
   code group_chat_quality_control.py
   ```

### 4.3 Understanding the Collaborative Reasoning Scenario

In this lab, you'll create a group chat where three specialized agents collaborate to explain technical concepts to non-technical audiences using language suitable for a 10-year-old through iterative refinement.

**The Agents (No Tools):**

1. **Explainer Agent**
   - Produces the initial explanation
   - Focuses on clarity and correctness
   - Avoids jargon
   - Does not critique or revise

2. **Critic Agent**
   - Reviews the explanation
   - Identifies problems: jargon, missing explanations, confusing logic
   - Does not rewrite, only critiques

3. **Refiner Agent**
   - Revises the explanation
   - Incorporates the Critic's feedback
   - Produces the improved version

**The Orchestrator's Decision Logic:**
- If no explanation exists → call Explainer
- If explanation exists but no critique → call Critic
- If critique exists → call Refiner
- Optionally send revised response back to Critic for validation
- End workflow once quality is acceptable

This demonstrates **non-linear orchestration** where the manager makes intelligent decisions based on conversation state.

### 4.4 Implement the Group Chat with Agent-Based Orchestrator

1. In the `group_chat_quality_control.py` file, add the following code to set up the client and define the three specialized agents:
```python
import os
import asyncio
from dotenv import load_dotenv
from agent_framework.foundry import FoundryChatClient
from azure.identity import AzureCliCredential
from agent_framework import Agent
from agent_framework.orchestrations import GroupChatBuilder
from agent_framework import AgentResponseUpdate

load_dotenv()
endpoint = os.environ["PROJECT_ENDPOINT"]
model = os.environ["MODEL_DEPLOYMENT_NAME"]

# Initialize the Azure OpenAI client
client = FoundryChatClient(
   project_endpoint=endpoint,
   model=model,
   credential=AzureCliCredential(),
)

# Create the Explainer agent - produces initial explanations
explainer = Agent(
   client=client,
   name="Explainer",
   description="Creates clear initial explanations of technical concepts for 10-year-olds",
   instructions="""You are an expert at explaining technical concepts to 10-year-old children.

   Your role:
   - Produce the initial explanation of the given topic
   - Focus on clarity and correctness
   - Use very simple language a 10-year-old would understand
   - Use fun, relatable analogies from a child's everyday life
   - Do NOT critique or revise - only explain

   Guidelines:
   - Keep explanations short and simple (3-5 paragraphs)
   - Use examples from games, toys, school, or daily activities kids know
   - Break down complex ideas into very simple parts
   - Use short sentences
   - Assume the reader is a 10-year-old with no technical background""",
)

# Create the Critic agent - identifies problems
critic = Agent(
   client=client,
   name="Critic",
   description="Reviews explanations to ensure they're understandable by 10-year-olds",
   instructions="""You are a quality control specialist ensuring explanations are clear for 10-year-old children.

   Your role:
   - Review the explanation as if you're checking if a 10-year-old would understand it
   - Identify specific problems such as:
     * Big words or complicated terms a 10-year-old wouldn't know
     * Missing explanations of important ideas
     * Confusing logic or sentences that are too long or complicated
     * Assumptions that the child knows things they probably don't
     * Abstract concepts that need concrete examples from a child's life
   - Provide constructive, specific feedback
   - Do NOT rewrite - only critique

   Guidelines:
   - Be specific about what needs improvement
   - Quote problematic phrases when possible
   - Explain why a 10-year-old would find something confusing
   - Suggest simpler words or more relatable examples from kids' daily lives
   - Check if sentences are short enough and vocabulary is age-appropriate
   
   IMPORTANT - When to indicate completion:
   - If the explanation is clear, simple, uses kid-friendly language, and a 10-year-old could understand it
   - State explicitly: "This explanation is now clear and appropriate for a 10-year-old"
   - Provide any minor suggestions if needed, but indicate the work is essentially complete""",
)

# Create the Refiner agent - improves based on feedback
refiner = Agent(
   client=client,
   name="Refiner",
   description="Revises explanations to make them perfect for 10-year-olds",
   instructions="""You are an editor who improves explanations to be perfect for 10-year-old children.

   Your role:
   - Read the original explanation
   - Review the Critic's feedback carefully
   - Revise the explanation to address ALL issues raised
   - Make it even simpler and more fun for kids to understand
   - Do NOT ignore any critique points

   Guidelines:
   - Address each piece of feedback specifically
   - Replace big or complicated words with simple ones a 10-year-old knows
   - Add missing explanations using examples from kids' daily lives
   - Use shorter sentences and simpler logic
   - Keep it fun and relatable to a child's experiences
   - Keep the same approximate length""",
)
```

2. Add the orchestrator agent that makes intelligent decisions about speaker selection:
```python
orchestrator = Agent(
   name="Orchestrator",
   description="Coordinates the collaborative explanation refinement process for 10-year-olds",
   instructions="""You coordinate a team of three agents to produce high-quality explanations suitable for 10-year-old children.

   Your team:
   - Explainer: Creates initial explanations for kids
   - Critic: Reviews to ensure a 10-year-old would understand
   - Refiner: Revises based on critique to make it kid-friendly

   Decision logic:
   1. If no explanation exists yet → select Explainer
   2. If explanation exists but hasn't been critiqued → select Critic
   3. If critique exists but hasn't been addressed → select Refiner
   4. After refinement → send back to Critic for validation
   5. Continue cycles of critique and refinement until the Critic indicates the explanation is satisfactory
   
   TERMINATION: When the Critic's feedback shows the explanation is clear, uses kid-friendly language,
   and is suitable for a 10-year-old, FINISH the conversation. Look for positive indicators like
   "clear for a 10-year-old," "appropriate for children," "kid-friendly," or minimal/minor feedback.
   
   Always select the most appropriate agent based on the current conversation state.
   Think about what has been done and what needs to happen next.""",
   client=client,
)
```

3. Build the group chat workflow with the agent-based orchestrator:
```python
# Build group chat with agent-based orchestrator
workflow = GroupChatBuilder(
   participants=[explainer, critic, refiner],
   # Terminate when reaching message limit (allows for multiple refinement cycles)
   termination_condition=lambda messages: sum(1 for msg in messages if msg.role == "assistant") >= 15,
   intermediate_outputs=True,  # Enable intermediate outputs to see all agent messages
   orchestrator_agent=orchestrator,
).build()
```

4. Add the main execution function to run the collaborative reasoning task:
```python
async def run_quality_control_chat():
   """Run the group chat with quality control workflow."""
   task = "Explain async/await in Python to a 10-year-old child."

   print(f"Task: {task}\n")
   print("=" * 80)
   print("Collaborative Reasoning and Quality Control (for 10-year-olds)")
   print("=" * 80)

   # Keep track of the last author to format output nicely in streaming mode
   last_author: str | None = None
   
   # Run the workflow with streaming enabled
   async for event in workflow.run(task, stream=True):
       if event.type == "output":
           data = event.data
           if isinstance(data, AgentResponseUpdate):
               author = data.author_name
               
               # Print agent name when we encounter a new author
               if author != last_author:
                   if last_author is not None:
                       print("\n")
                   print(f"\n[{author}]:", end=" ", flush=True)
                   last_author = author
               
               # Skip empty text chunks but after we've printed the agent name
               if data.text and not data.text.isspace():
                   print(data.text, end="", flush=True)
           elif isinstance(data, list):  
               # The output of the group chat workflow is a collection of chat messages from all participants
               outputs = data
               print("\n\n" + "=" * 80)
               print("Final Conversation Transcript:")
               print("=" * 80)
               for message in outputs:
                   print(f"\n[{message.author_name or message.role}]")
                   print(message.text)
                   print("-" * 80)

   print("\nWorkflow completed.")

# Run the async function
if __name__ == "__main__":
   asyncio.run(run_quality_control_chat())
```

5. Save the file using **CTRL+S** and close the editor with **CTRL+Q**
> **Tip:** You may copy the code provided in the group_chat_quality_control.py file found in the Workflow folder of this repository and paste it into your file in the cloud shell to ensure accuracy.

### 4.5 Run the Group Chat Quality Control Workflow

1. Install first the agent framework library by entering the following command in the Cloud Shell console:
   ```bash
   pip install agent_framework==1.2.2
   ```
2. Enter the following command to run the group chat:
   ```bash
   python group_chat_quality_control.py
   ```

3. Observe the collaborative workflow:
   - **Explainer** creates the initial explanation
   - **Critic** reviews and identifies specific problems (jargon, unclear logic, etc.)
   - **Refiner** revises the explanation addressing all critique points
   - **Orchestrator** may send it back to Critic for validation or end if quality is satisfactory

4. Notice the key aspects:
   - ✅ No tools are used - only role instructions and shared context
   - ✅ Orchestrator makes intelligent decisions, not round-robin
   - ✅ Each agent has a clear, distinct role
   - ✅ Iterative refinement improves quality
   - ✅ Conversation continues until quality criteria are met

**Expected Output:**
```plaintext
Task: Explain async/await in Python to a 10-year-old child.               

================================================================================
Collaborative Reasoning and Quality Control (for 10-year-olds)
================================================================================

[Explainer]: Imagine you’re waiting for your cookies to bake in the oven. You could just sit there and watch the oven the whole time. But that wouldn’t be fun, right? Instead, you can play a game, draw, or read a book while the cookies bake. When the cookies are ready, you stop what you’re doing and eat them!

In Python, “async” is a way to tell the computer, “I’m going to start something, like baking cookies. While I wait for it to finish, I can do other things.” “Await” is like checking if the cookies are ready or stopping your game to go eat them when they are done.

So, async/await is just a fun way for computers to not get bored while waiting. They can do lots of things at once, like playing games while waiting for cookies to bake. This makes them faster and more helpful!

In code, you say “async” for the things that can happen at the same time. You say “await” for the moments you need to check if those things are finished. It’s like making busy time fun!


[Critic]: Review:

1. "Imagine you’re waiting for your cookies to bake in the oven." – This is a clear and relatable example.
2. "You could just sit there and watch the oven... But that wouldn’t be fun..." – Good comparison, easy to understand for 10-year-olds.
3. "Instead, you can play a game, draw, or read a book while the cookies bake. When the cookies are ready, you stop what you’re doing and eat them!" – This is a strong real-life analogy.
4. "In Python, 'async' is a way to tell the computer, 'I’m going to start something, like baking cookies. While I wait for it to finish, I can do other things.' 'Await' is like checking if the cookies are ready or stopping your game to go eat them when they are done." – This is very clear, using simple language and connecting to the analogy.
5. "So, async/await is just a fun way for computers to not get bored while waiting..." – Using the phrase 'not get bored' might be slightly abstract for some kids, but in the context it works, especially with the cookie analogy.
6. "They can do lots of things at once, like playing games while waiting for cookies to bake." – Good, concrete example.
7. "In code, you say 'async' for the things that can happen at the same time. You say 'await' for the moments you need to check if those things are finished. It’s like making busy time fun!" – Clear and summarizes the analogy well.

...

Conclusion:This explanation is now clear and appropriate for a10-year-old. No further changes are needed. Great job!


[Orchestrator]: Awesome! The explanation of async/await in Python is now perfect for a 10-year-old and ready to use.
Workflow completed.
```

---

## Verification Checklist

### Azure Resources (Step 1)
- [ ] Resource group `rg-foundry-workflows` created
- [ ] Foundry resource `foundry-workflows-<yourname>` created
- [ ] Foundry Portal accessed successfully
- [ ] GPT-4.1 model deployed
- [ ] Model deployment verified in Playground

### Sequential Workflow (Steps 2-3)
- [ ] Blank workflow created in Microsoft Foundry
- [ ] Support ticket array variable initialized
- [ ] For-each loop configured to process tickets
- [ ] Triage Agent created with JSON schema output
- [ ] Triage Agent properly classifies tickets with confidence scores
- [ ] Conditional logic handles low-confidence classifications
- [ ] Low-confidence tickets request additional information
- [ ] Billing issues are properly routed for escalation
- [ ] Resolution Agent created for non-billing tickets
- [ ] Resolution Agent generates appropriate responses
- [ ] Workflow preview tested successfully
- [ ] Cloud Shell environment prepared
- [ ] Python application configured with project endpoint
- [ ] Workflow invoked successfully from Python code
- [ ] Application executed and validated workflow processing

### Group Chat Orchestration (Step 4)
- [ ] Group chat scenario and objectives understood
- [ ] Collaborative reasoning use case (no tools) explained
- [ ] Group chat Python file created (`group_chat_quality_control.py`)
- [ ] Explainer agent defined with clear role instructions
- [ ] Critic agent defined with review capabilities
- [ ] Refiner agent defined with revision capabilities
- [ ] Orchestrator agent created with intelligent decision logic
- [ ] Group chat workflow built with agent-based orchestrator
- [ ] Quality control workflow executed successfully
- [ ] Iterative refinement process observed (Explain → Critique → Refine)
- [ ] Orchestrator making intelligent (non-round-robin) decisions
- [ ] Final refined explanation demonstrates improvement
- [ ] Understood that no tools are needed for collaborative reasoning
- [ ] Context synchronization principles understood

---

## Clean Up Resources

To avoid incurring charges, delete the resources when you're finished with the lab:

1. In the Azure Portal, navigate to **Resource groups**
2. Select `rg-foundry-workflows`
3. Click **Delete resource group**
4. Type the resource group name to confirm
5. Click **Delete**

> **Note:** This will delete all resources including the Foundry resource and any associated workflows.

---

## Summary and Key Takeaways

In this lab, you successfully:

1. ✅ Created Azure resources (Resource Group and Foundry resource)
2. ✅ Deployed a GPT-4.1 model in Microsoft Foundry
3. ✅ Created a sequential workflow in Microsoft Foundry for customer support automation
4. ✅ Built a Triage Agent with structured JSON output for ticket classification
5. ✅ Implemented conditional logic for handling low-confidence classifications
6. ✅ Created routing logic to escalate billing issues to human support
7. ✅ Built a Resolution Agent to generate professional support responses
8. ✅ Tested the workflow in the Foundry portal preview
9. ✅ Connected to the workflow programmatically using Azure AI Projects SDK
10. ✅ Executed the workflow from Python code and validated the automation
11. ✅ Implemented a Group Chat orchestration focused on collaborative reasoning
12. ✅ Created specialized agents (Explainer, Critic, Refiner) without any tools
13. ✅ Built an intelligent agent-based orchestrator with strategic decision-making
14. ✅ Experienced iterative refinement through role separation and quality control
15. ✅ Understood that effective collaboration doesn't require tools or external data
16. ✅ Learned context synchronization principles in multi-agent systems

---

## Lab Completion Badge

Congratulations! 🎉 You have completed the **Build a Workflow in Microsoft Foundry** lab.

You now have hands-on experience with:
- Creating sequential workflows in Microsoft Foundry
- Building AI agents with structured JSON outputs
- Implementing conditional logic and routing
- Invoking workflows programmatically via Azure AI Projects SDK
- Creating Group Chat orchestrations with agent-based orchestrators
- Implementing collaborative reasoning workflows without tools
- Understanding role separation and iterative refinement patterns
- Building quality control systems through specialized agent collaboration
- Managing context synchronization in multi-agent systems

---

**End of Lab**
