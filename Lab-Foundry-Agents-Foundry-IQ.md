# Lab: Building Foundry Agents with Foundry IQ

## Overview
In this hands-on lab, you will learn how to create intelligent AI agents using Microsoft Foundry, connect them to a custom knowledge base powered by Azure AI Search and Azure Storage. This lab demonstrates how to build production-ready AI agents that can answer questions based on your organization's data.

**Estimated Time:** 90 minutes

**Prerequisites:**
- An Azure account with an active subscription
- Access to a role that allows you to create Foundry resources (e.g., Azure AI Owner)
- Basic understanding of AI agents and retrieval-augmented generation (RAG)
- Sample documents to upload to your knowledge base (PDF, Word, or text files)

---

## Lab Architecture
By the end of this lab, you will have:
- A Microsoft Foundry resource with a deployed project
- An Azure Storage account with sample documents
- An Azure AI Search service for indexing and retrieval
- A knowledge base in Foundry IQ connected to your data sources
- A custom AI agent that uses the knowledge base to answer questions

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
   - **Resource group name:** `rg-foundry-agents-lab`
   - **Region:** `Australia East`
5. Click **Review + Create**, then **Create**

### 1.3 Create an Azure Storage Account
1. In the Azure Portal, click **Create a resource**
2. Search for **Storage Account** and select it
3. Click **Create**
4. Configure the storage account:
   - **Subscription:** Select your subscription
   - **Resource group:** `rg-foundry-agents-lab`
   - **Storage account name:** `stfoundry<yourname>` (must be globally unique, lowercase, no hyphens)
   - **Region:** `Australia East`
   - **Preferred storage type:** `Azure Blob Storage or Azure Data Lake Storage Gen2`
   - **Performance:** Standard
   - **Redundancy:** Locally-redundant storage (LRS)
5. Click **Review + Create**, then **Create**
6. Wait for deployment to complete (typically 1-2 minutes)
7. Click **Go to resource**

### 1.4 Create a Container and Upload Sample Documents
1. In your storage account, navigate to **Data storage** > **Containers** in the left menu
2. Click **+ Container**
3. Configure the container:
   - **Name:** `manuals`
   - **Public access level:** Private (no anonymous access)
4. Click **Create**
5. Click on the **manuals** container
6. Click **Upload**
7. Upload manuals data from the Product Data folder of this repository.
8. Click **Upload** and wait for completion
9. Perform the same steps 1-8 to create another container named `reviews` and upload reviews data from the Product Data folder of this repository.

### 1.5 Create an Azure AI Search Service
1. In the Azure Portal, click **Create a resource**
2. Search for **Azure AI Search** and select it
3. Click **Create**
4. Configure the AI Search service:
   - **Subscription:** Select your subscription
   - **Resource group:** `rg-foundry-agents-lab`
   - **Service name:** `search-foundry-<yourname>` (must be globally unique)
   - **Location:** `Australia East`
   - **Pricing tier:** Basic (sufficient for this lab)
5. Click **Review + Create**, then **Create**
6. Wait for deployment to complete (typically 3-5 minutes)

---

## Step 2: Setup a Foundry Resource

### 2.1 Create a Foundry Resource
1. In the Azure Portal, click **Create a resource**
2. Search for **Microsoft Foundry** and select it
3. Click **Create**
4. Configure the resource:
   - **Subscription:** Select your subscription
   - **Resource group:** `rg-foundry-agents-lab`
   - **Name:** `foundry-agents-<yourname>` (must be globally unique)
   - **Region:** `Australia East`
   - **Default project name:** `agents-project`
5. Click **Review + Create**, then **Create**
6. Wait for the deployment to complete (typically 1-2 minutes)

### 2.2 Access Microsoft Foundry Portal
1. Once deployment completes, click **Go to resource**
2. In the resource overview, click **Go to Foundry Portal** or navigate directly to [https://ai.azure.com/](https://ai.azure.com/)
3. Sign in with your Azure credentials
4. Verify that you are in the Foundry Portal and that your project (`agents-project`) is selected in the upper left corner

### 2.3 Deploy a Model for Your Agent
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

### 2.4 Verify Model Deployment
1. Once deployment completes, you should be sent to the Playground with the `gpt-4.1` model selected
2. In the input box, enter a test prompt:
   ```
   What is Microsoft Foundry?
   ```
3. Click **Submit**
4. Verify you receive a coherent response describing Microsoft Foundry

### 2.5 Deploy an Embedding Model
1. In the **Models** section, click **Deploy a base model** again
2. Search for the **text-embedding-3-large** model
3. Select the model and click **Deploy** > **Custom settings**
4. Configure the deployment:
   - **Deployment name:** `text-embedding-3-large`
   - **Deployment type:** Select **Global Standard**
   - **Tokens per minute rate limit:** `50000`
5. Click **Deploy**

---

## Step 3: Create a Knowledge Base in Foundry IQ

### 3.1 Create an Azure AI Search Index
1. In the Azure Portal, navigate to your Azure AI Search service (`search-foundry-<yourname>`)
2. In the AI Search service Overview, click **Import data**
3. Select **Azure Blob Storage** as the data source
4. Select **RAG**
5. Connect to your data:
   - **Subscription:** Select your subscription
   - **Storage account:** Select `stfoundry<yourname>`
   - **Container:** Select `manuals`
   - Click Next
6. Vectorize your text
   - **Kind:** Select `Microsoft Foundry`
   - **Subscription:** Select your subscription
   - **Microsoft Foundry project:** Select `agents-project`
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
10. Click Create

### 3.2 Verify Indexing
1. In your Azure AI Search service, navigate to **Search Management** > **Indexes** in the left menu
2. Select manuals index
3. Click Search
4. Verify in the results that your documents are indexed:
   - ✅ Chunks of text from your documents are returned
   - ✅ Title of the document is displayed
   - ✅ Text vectors are created

### 3.3 Access Foundry IQ
1. In Microsoft Foundry Portal, navigate to **Build** > **Knowledge** in the left sidebar
2. If this is your first time accessing Foundry IQ, you may see an introduction screen
3. Select your Azure AI Search resource:
   - Click **Select a resource**
   - Choose `search-foundry-<yourname>` from the list
   - Under Auth Type, choose **API Key**
   - Click **Connect**

### 3.4 Create a New Knowledge Base
1. In the Knowledge section, click **Create a knowledge base**
2. Select **Azure AI Search** under Configure a knowledge base
3. Click **Connect**
4. Create a knowledge source configuration:
   - **Name:** `productmanuals`
   - **Description:** `Knowledge base for product manuals`
   - **Select search index:** `manuals`
5. Click **Create**

### 3.5 Configure Knowledge Base Settings
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

### 3.6 Add Azure Blob as Knowledge Source
1. In your knowledge base, scroll down to the **Knowledge sources** section
2. Click **Create new**
3. Select **Azure Blob Storage**
4. Configure knowledge source:
   - **Name:** `productreviews`
   - **Description:** `Contains customer product reviews`
   - **Storage account:** Select `stfoundry<yourname>`
   - **Container:** Select `reviews`
   - **Authentication:** Select **API Key**
   - **Context extraction mode:** Select **Minimal**
   - **Embedding model:** Select `text-embedding-3-large`
   - **Chat completions model:** Select `gpt-4.1`
5. Click **Create**

**Notes**: 
- Foundry IQ can have multiple knowledge sources such as existing Azure AI Search indexes, Azure Blob Storage containers, and other data sources. This allows you to easily combine different types of data in a single knowledge base.
- Unlike the manuals data which we pre-indexed in Azure AI Search, we're adding reviews as a direct blob storage source. Foundry IQ will automatically extract and embed the content using the specified embedding model.

### 3.7 Saving the Knowledge Base
1. In the upper right select **Save knowledge base**
2. Refresh the page and wait for the product reviews knowledge source to be Active in status (this may take a few minutes)

---

## Step 4: Create an AI Agent in Foundry Portal

### 4.1 Navigate to Agent Builder
1. In Microsoft Foundry Portal, navigate to **Build** > **Agents** in the left sidebar
2. Click **Create agent**

### 4.2 Configure Agent Basics
1. On the **Create an agent** page:
   - **Agent name:** `productassistant`
2. Click **Create and open playground**

### 4.3 Configure Agent Instructions
1. In the agent configuration page, navigate to the **Instructions** tab
2. In the **Instructions** field, add detailed instructions:
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

### 4.4 Connect the Knowledge Base
1. Navigate to the **Knowledge** section of the agent configuration
2. Click **Add** then Connect to Foundry IQ.
3. Connect to Foundry IQ:
   - **Connection:** Select `search-foundry-<yourname>`
   - **Knowledge base:** Select **productkb**
4. Click **Connect**

### 4.5 Remove Web search
1. Navigate to the **Tools** section of the agent configuration
2. Under Web search select the three dots and select **Remove**

### 4.6 Save Your Agent
1. Click **Save** in the upper right corner

---

## Step 5: Test Your Agent in the Playground

### 5.1 Verify Agent Setup
1. In your agent configuration, you'll see a chat interface on the right side
2. Start with a greeting:
   ```
   Hello! Can you tell me what you can help me with?
   ```
3. Verify the agent responds appropriately and describes its capabilities

### 5.2 Test Knowledge Base Queries
1. Ask a question that should be answerable from your documents:
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

### 5.3 Test Multi-Turn Conversation
1. Ask a follow-up question:
   ```
   Can you provide more details about its warranty?
   ```
2. Verify the agent maintains context from the previous response

3. Ask a question that requires information from other knowledge sources:
   ```
   What are its main features and what do people say about them in customer reviews?
   ```
4. Verify the agent synthesizes information from multiple sources

### 5.4 Review Agent Logs
1. Click on the **Logs** at the bottom
2. Review the knowledge base searches performed

---

## Verification Checklist

- [ ] Azure Storage account created with sample documents uploaded
- [ ] Azure AI Search service provisioned
- [ ] Foundry resource created successfully
- [ ] GPT-4.1 model deployed in Foundry
- [ ] Embedding model deployed in Foundry
- [ ] Azure AI Search index created and documents indexed
- [ ] Knowledge base created in Foundry IQ
- [ ] Azure AI Search added as knowledge source in Foundry IQ
- [ ] Azure Blob Storage added as knowledge source in Foundry IQ
- [ ] Agent created with instructions configured
- [ ] Knowledge base connected to agent
- [ ] Agent tested successfully in playground getting relevant responses from the knowledge base


---

## Clean Up Resources

To avoid incurring charges, delete the resources when you're finished with the lab:

1. In the Azure Portal, navigate to **Resource groups**
2. Select `rg-foundry-agents-lab`
3. Click **Delete resource group**
4. Type the resource group name to confirm
5. Click **Delete**

> **Note:** This will delete all resources including Foundry, Storage, and AI Search.

---

## Summary and Key Takeaways

In this lab, you successfully:

1. ✅ Created Azure resources (Storage, AI Search, Foundry)
2. ✅ Deployed a GPT-4.1 model in Microsoft Foundry
3. ✅ Deployed an embedding model in Microsoft Foundry for embedding generation
4. ✅ Created an Azure AI Search index and ingested documents from Azure Blob Storage
5. ✅ Built a knowledge base in Foundry IQ with multiple knowledge sources
6. ✅ Created an AI agent with custom instructions
7. ✅ Connected the agent to the knowledge base for RAG capabilities
8. ✅ Tested the agent in the Foundry playground

### Benefits of Foundry Agents with Knowledge Bases

**Best Practice:** Building agents with custom knowledge bases provides:
- **Accurate information:** Agents ground responses in your organization's data
- **Source citations:** Users can verify information and explore source documents
- **Easy maintenance:** Update knowledge base without changing agent code
- **Scalability:** Handles thousands of documents and complex queries
- **Security:** Data stays in your Azure tenant with access controls
- **Integration:** Works seamlessly with Microsoft Teams and M365

### Architecture Patterns

**Retrieval-Augmented Generation (RAG):**
1. User asks a question
2. Agent searches knowledge base for relevant information
3. Retrieved chunks are injected into the model's context
4. Model generates response grounded in retrieved data
5. Agent cites sources in the response

This pattern is superior to fine-tuning because:
- ✅ Easier to update (just add/modify documents)
- ✅ More transparent (can see what data was used)
- ✅ More accurate (model sees actual content, not memorized patterns)
- ✅ Lower cost (no expensive fine-tuning compute)

---

## Lab Completion Badge

Congratulations! 🎉 You have completed the **Microsoft Foundry Agents with Foundry IQ** lab.

You now have hands-on experience with:
- Creating and configuring AI agents in Microsoft Foundry
- Building knowledge bases with Azure AI Search and Azure Storage
- Implementing Retrieval-Augmented Generation (RAG) patterns

---

**End of Lab**
