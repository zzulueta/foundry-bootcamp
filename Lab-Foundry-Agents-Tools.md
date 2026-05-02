# Lab: Building Advanced Foundry Agents with Code Interpreter, OpenAPI Tools, and Custom MCP Servers

## Overview
In this hands-on lab, you will create a single advanced AI agent using Microsoft Foundry with three different types of tools:
1. **Code Interpreter** (Built-in tool) - Execute Python code for analysis and visualizations
2. **OpenAPI Tool** (Alpha Vantage API) - Fetch live stock quotes directly from external API
3. **Custom MCP Server** (Logic App) - Receive stock data from agent and store in Azure Table Storage

This lab demonstrates how to combine multiple tool types to create a comprehensive financial analysis agent that can fetch data, store it persistently, and perform advanced analysis with code execution.

**Estimated Time:** 90 minutes

**Prerequisites:**
- An Azure account with an active subscription
- Access to a role that allows you to create Foundry resources (e.g., Azure AI Owner)
- Access to create Logic Apps in your Azure subscription
- Basic understanding of AI agents and REST APIs
- A free API key from Alpha Vantage

---

## Lab Architecture
By the end of this lab, you will have:
- A Microsoft Foundry resource with a deployed project
- An Azure Storage account with Table Storage for persisting stock data
- **One Agent (stockanalyst)** with three tools:
  - **Tool 1:** Code Interpreter (built-in) - for calculations and visualizations
  - **Tool 2:** OpenAPI Tool (Alpha Vantage API) - fetches live stock quotes from external API
  - **Tool 3:** Custom MCP Server (Logic App) - receives stock data and stores it in Azure Table Storage
- An Azure Logic App that accepts stock data from the agent and persists it to Table Storage
- Understanding of how to combine built-in, OpenAPI, and custom MCP tools in a single agent

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
   - **Resource group name:** `rg-foundry-tools`
   - **Region:** `Australia East`
5. Click **Review + Create**, then **Create**

### 1.3 Create an Azure Storage Account
1. In the Azure Portal, click **Create a resource**
2. Search for **Storage Account** and select it
3. Click **Create**
4. Configure the storage account:
   - **Subscription:** Select your subscription
   - **Resource group:** `rg-foundry-tools`
   - **Storage account name:** `ststocks<yourname>` (must be globally unique, lowercase, no hyphens)
   - **Region:** `Australia East`
   - **Preferred storage type:** `Azure Blob Storage or Azure Data Lake Storage Gen2`
   - **Performance:** Standard
   - **Redundancy:** Locally-redundant storage (LRS)
5. Click **Review + Create**, then **Create**
6. Wait for deployment to complete
7. Once deployed, navigate to the storage account

### 1.4 Create Table Storage
1. In your storage account, navigate to **Data storage** > **Tables** in the left menu
2. Click **+ Table**
3. Configure the table:
   - **Table name:** `stockquotes`
4. Click **OK**
5. The table will be created immediately

### 1.5 Get Storage Account Connection Details
1. In your storage account, navigate to **Security + networking** > **Access keys** in the left menu
2. Locate Connection string under key1. 
3. Click **Show**.
4. Copy the **Connection string**.
5. Save these securely - you'll need them for the Logic App

### 1.6 Obtain Alpha Vantage API Key
1. Navigate to [https://www.alphavantage.co/support/#api-key](https://www.alphavantage.co/support/#api-key)
2. Enter your email address in the "Get your free API key today" form
3. Click **GET FREE API KEY**
4. Get your API key from the site.
5. Copy and save your API key securely - you'll need it in Step 4

> **Note:** Alpha Vantage provides a free tier with up to 25 API requests per day, which is sufficient for this lab.

---

## Step 2: Setup Foundry Resource and Deploy Models

### 2.1 Create a Foundry Resource
1. In the Azure Portal, click **Create a resource**
2. Search for **Microsoft Foundry** and select it
3. Click **Create**
4. Configure the resource:
   - **Subscription:** Select your subscription
   - **Resource group:** `rg-foundry-tools`
   - **Name:** `foundry-tools-<yourname>` (must be globally unique)
   - **Region:** `Australia East`
   - **Default project name:** `agents-tools`
5. Click **Review + Create**, then **Create**
6. Wait for deployment to complete (typically 1-2 minutes)

### 2.2 Access Microsoft Foundry Portal
1. Once deployment completes, click **Go to resource**
2. Click **Go to Foundry Portal** or navigate to [https://ai.azure.com/](https://ai.azure.com/)
3. Sign in with your Azure credentials
4. Verify that your project (`agents-tools`) is selected in the upper left corner

### 2.3 Deploy GPT-4.1 Model
1. In Microsoft Foundry, navigate to **Build** > **Models**
2. Click **Deploy a base model**
3. Search for **gpt-4.1** and select it
4. Click **Deploy** > **Custom settings**
5. Configure the deployment:
   - **Deployment name:** `gpt-4.1`
   - **Deployment type:** **Global Standard**
   - **Tokens per minute rate limit:** `50000`
6. Click **Deploy**
7. Wait for deployment to complete

### 2.4 Test Model Deployment
1. Once deployed, test in the Playground:
   ```
   Write a Python function to calculate fibonacci numbers.
   ```
2. Verify you receive a response with working code
3. In the agent playground, ask a simple coding question:
   ```
   Write and execute Python code to generate the first 10 fibonacci numbers and create a bar chart showing them.
   ```
4. Verify that the model responds with a Python code snippet but cannot execute it.

---

## Step 3: Create Agent with Code Interpreter

### 3.1 Navigate to Agent Builder
1. In Microsoft Foundry Portal, navigate to **Build** > **Agents**
2. Click **Create agent**

### 3.2 Configure Agent Basics
1. On the **Create an agent** page:
   - **Agent name:** `stockanalyst`
2. Click **Create and open playground**

### 3.3 Configure Agent Instructions
1. In the agent configuration page, navigate to the **Instructions** tab
2. Add the following instructions:
   ```
   You are an expert financial data analyst AI assistant. Your capabilities include:

   - Fetching live stock market data from external APIs
   - Storing stock data for future reference
   - Writing and executing Python code to analyze financial data
   - Creating charts, graphs, and statistical analyses of stock performance
   - Calculating financial metrics and indicators
   - Performing technical analysis and data transformations

   Guidelines:
   - Use the get_stock_quote tool to fetch current stock prices from Alpha Vantage
   - Use the stock-storage-mcp tool to store stock information in Azure Table Storage
   - Use Code Interpreter to perform calculations, analyze data, and create visualizations
   - Write clean, well-commented Python code
   - Explain your analysis and findings clearly
   - If you create visualizations, describe what they show
   - Always validate your results and explain your methodology

   When analyzing stocks:
   1. First, fetch the stock data using the get_stock_quote tool
   2. Save the data using the stock-storage-mcp tool for future reference
   3. Analyze the data structure and key metrics
   4. Perform the requested analysis using Python
   5. Create visualizations when appropriate
   6. Summarize key findings and insights

   Be professional, thorough, and educational in your responses.
   ```

### 3.4 Enable Code Interpreter Tool and Remove Web Search
1. Navigate to the **Tools** section of the agent configuration
2. Click **Add** and look for **Code Interpreter** and enable it.
3. Click **Add** and look for **Web search** and disable it.
4. Click the Save button at the top right to save the agent.

### 3.5 Test Code Interpreter 
1. In the **Tools** section, ensure that **Code Interpreter** is listed as an enabled tool
2. Ensure that **Web search** is not listed
3. In the agent playground, ask a simple coding question to verify:
   ```
   Write and execute Python code to generate the first 10 fibonacci numbers and create a bar chart showing them.
   ```
4. Verify that the agent responds with Python code and executes it to produce a bar chart visualization.
5. You can download the bar chart image and verify it shows the correct Fibonacci numbers.
6. Ask a calculation question:
   ```
   Calculate the compound interest for a $10,000 investment at 5% annual rate for 10 years, compounded monthly. Show the calculations step by step.
   ```
7. Verify the agent performs calculations using Python

---

## Step 4: Add the Alpha Vantage OpenAPI Tool

### 4.1 Add Alpha Vantage Stock API as OpenAPI Tool
1. In the **Tools** section, click **Browse all tools**
2. Select **Custom** > **OpenAPI tool** > **Create**
3. Configure the OpenAPI tool:
   - **Name:** `get_stock_quote`
   - **Description:** `Fetches current stock price and company information from Alpha Vantage API for a given stock symbol`
   - **Authentication method:** Select **Anonymous**

4. In the **OpenAPI 3.0+ schema** box, paste the following schema:
   ```json
   {
     "openapi": "3.0.0",
     "info": {
       "title": "Stock Quote API",
       "version": "1.0.0",
       "description": "API for retrieving stock market data from Alpha Vantage"
     },
     "servers": [
       {
         "url": "https://www.alphavantage.co"
       }
     ],
     "paths": {
       "/query": {
         "get": {
           "operationId": "getStockQuote",
           "summary": "Get stock quote",
           "description": "Retrieves the current stock price and information for a symbol",
           "parameters": [
             {
               "name": "function",
               "in": "query",
               "required": true,
               "schema": {
                 "type": "string",
                 "enum": ["GLOBAL_QUOTE"]
               },
               "description": "API function type"
             },
             {
               "name": "symbol",
               "in": "query",
               "required": true,
               "schema": {
                 "type": "string"
               },
               "description": "Stock symbol (e.g., MSFT, AAPL, GOOGL)"
             },
             {
               "name": "apikey",
               "in": "query",
               "required": true,
               "schema": {
                 "type": "string",
                 "default": "YOUR_API_KEY_HERE"
               },
               "description": "Your Alpha Vantage API key"
             }
           ],
           "responses": {
             "200": {
               "description": "Successful response",
               "content": {
                 "application/json": {
                   "schema": {
                     "type": "object"
                   }
                 }
               }
             }
           }
         }
       }
     }
   }
   ```

5. **Important:** Replace `YOUR_API_KEY_HERE` in the schema with your actual Alpha Vantage API key from Step 1.6
   - Find the `"default": "YOUR_API_KEY_HERE"` line in the schema
   - Replace `YOUR_API_KEY_HERE` with your API key (keep the quotes)
   - Example: `"default": "ABC123XYZ456"`

6. Click **Create tool**

> **Note:** For simplicity in this lab, we're embedding the API key directly in the OpenAPI schema. In production environments, you should use secure credential storage.

7. Click **Save** in the upper right corner

### 4.2 Test OpenAPI Tool (Alpha Vantage)
1. Ask the agent to fetch stock data:
   ```
   Get me the current stock price for Microsoft (MSFT).
   ```
2. Observe the agent:
   - ✅ Calls the `get_stock_quote` OpenAPI tool
   - ✅ Fetches data from Alpha Vantage API
   - ✅ Displays current stock price and information

3. Try fetching multiple stocks:
   ```
   What are the current prices for Apple (AAPL) and Tesla (TSLA)?
   ```
4. Verify the agent successfully retrieves data for both stocks

### 4.3 Test Combined Tools (Code Interpreter + OpenAPI)
1. Ask a question requiring both tools:
   ```
   Get the current prices for Microsoft, Apple, and Google. Then calculate the total value if I owned 100 shares of each, and create a pie chart showing the portfolio allocation.
   ```
2. Observe the agent:
   - ✅ Uses OpenAPI tool to fetch stock prices (3 calls)
   - ✅ Uses Code Interpreter to perform calculations
   - ✅ Creates visualization with pie chart
   - ✅ Provides comprehensive analysis

---

## Step 5: Create Azure Logic App to Store Stock Data

### 5.1 Understanding the Logic App Purpose
We will create a Logic App that:
- Accepts stock data from the agent (symbol, price, date, and other metrics)
- Stores the stock data in Azure Table Storage for persistence
- Returns a confirmation response to the agent

This demonstrates:
- Using Azure Logic Apps as a data persistence layer
- Building custom MCP servers for stateful operations
- Separating concerns: API fetching (OpenAPI) vs data storage (MCP)

**Why This Architecture:**
- **OpenAPI Tool** handles external API calls (Alpha Vantage)
- **Logic App (MCP)** handles Azure-specific operations (Table Storage)
- Clean separation of concerns
- Each tool has a single, clear responsibility

### 5.2 Create a Logic App
1. In the Azure Portal, click **Create a resource**
2. Search for **Logic App** and select it
3. Click **Create**
4. Select **Workflow Service Plan** and click **Select**
5. Configure the Logic App:
   - **Subscription:** Select your subscription
   - **Resource group:** `rg-foundry-tools`
   - **Logic app name:** `logic-stocks-<yourname>`
   - **Region:** `Australia East`
   - **Windows Plan:** **Accept new default**
   - **Pricing Plan:** Workflow Standard WS1
   - **Zone redundancy:** Disabled
6. Click **Review + Create**, then **Create**
7. Wait for deployment to complete
8. Click **Go to resource**

### 5.3 Create a Logic App Workflow
1. In your Logic App, click **Workflows > Workflows** in the left menu
2. Select **+ Create**
3. Create Workflow:
   - **Workflow name:** `workflow-stocks-<yourname>`
   - Select **Stateful**
   - Click **Create**
4. Select the newly created workflow and to open the Logic App Designer.

### 5.4 Add an HTTP Trigger
1. Click **Add a trigger**
2. Search for **When an HTTP request is received** and select it
3. Configure the HTTP trigger:
   - Click **Use sample payload to generate schema**
   - Enter the following JSON sample:
     ```json
     {
       "symbol": "MSFT",
       "price": "383.45",
       "open": "380.50",
       "high": "385.20",
       "low": "378.10",
       "volume": "25000000",
       "tradingDay": "2026-05-01",
       "change": "3.65",
       "changePercent": "0.96%"
     }
     ```
   - Click **Done**
   - **Method:** Select **POST**
4. The JSON schema will be auto-generated

### 5.5 Add Azure Table Storage Connection
1. Click **New step** (the + icon below the trigger) and select **Add an action**
2. Search for **Azure Table Storage** and select **Insert or Update Entity**
3. Configure the connection:
   - **Connection name:** `stocks-table-connection`
   - **Authentication Type:** Connection String
   - **Connection String:** Enter your storage account connection string from Step 1.5
4. Click **Create new**

### 5.6 Configure Insert or Update Entity
1. Configure the Table Storage action:
   - **Table:** `stockquotes`
2. Configure the Entity by pasting the following JSON in the **Entity** field:
     ```json
     {
       "PartitionKey": "@{triggerBody()?['symbol']}",
       "RowKey": "@{utcNow('yyyyMMddHHmmss')}",
       "Symbol": "@{triggerBody()?['symbol']}",
       "Price": "@{triggerBody()?['price']}",
       "Open": "@{triggerBody()?['open']}",
       "High": "@{triggerBody()?['high']}",
       "Low": "@{triggerBody()?['low']}",
       "Volume": "@{triggerBody()?['volume']}",
       "TradingDay": "@{triggerBody()?['tradingDay']}",
       "Change": "@{triggerBody()?['change']}",
       "ChangePercent": "@{triggerBody()?['changePercent']}"
     }
     ```
Note: This configuration uses the stock symbol as the PartitionKey and a timestamp as the RowKey to ensure uniqueness. In addition, we are retrieving all relevant stock data from the trigger body and storing it as properties in the Table Storage entity.

### 5.7 Add Response Action
1. Click **New step** (the + icon below the trigger) and select **Add an action**
2. Search for **Response** and select the **Response** action
3. Configure the Response:
   - **Status Code:** `200`
   - **Body:** Build a confirmation response:
     ```json
     {
       "success": true,
       "message": "Stock data saved successfully",
       "symbol": "@{triggerBody()?['symbol']}",
       "price": "@{triggerBody()?['price']}",
       "storedAt": "@{utcNow()}"
     }
     ```
4. Add a response header:
   - **Key:** `Content-Type`
   - **Value:** `application/json`

### 5.8 Save and Get Logic App URL
1. Click **Save** at the top of the designer
2. Click back on the **When an HTTP request is received** trigger
3. After saving, the **HTTP POST URL** will be generated
4. Click the **Copy** icon to copy the URL
5. Save this URL. You will need this for testing.

**Important:** This URL contains a SAS token for authentication. Keep it secure.

### 5.9 Test the Logic App
1. In the Azure Portal, click the **Cloud Shell** icon (>_) at the top right of the page
2. Select **Bash**.
3. Wait for the Cloud Shell to initialize
4. Run the following curl command to test your Logic App (replace `[Your Logic App URL]` with your actual Logic App HTTP POST URL from Step 5.8):
   ```bash
   curl -X POST "[Your Logic App URL]" \
     -H "Content-Type: application/json" \
     -d '{
       "symbol": "MSFT",
       "price": "383.45",
       "open": "380.50",
       "high": "385.20",
       "low": "378.10",
       "volume": "25000000",
       "tradingDay": "2026-05-01",
       "change": "3.65",
       "changePercent": "0.96%"
     }'
   ```
5. You should receive a JSON response similar to:
   ```json
   {
     "success": true,
     "message": "Stock data saved successfully",
     "symbol": "MSFT",
     "price": "383.45",
     "storedAt": "2026-05-01T10:30:45Z"
   }
   ```
6. Navigate to the Runs history in the Logic App designer.
7. Select the latest run to see the details of the execution.
8. Verify that you see green check marks for all steps, indicating success.
9. Navigate to your storage account in Azure Portal (`ststocks<yourname>`)
10. Go to **Storage Browser** > **Tables** > **stockquotes**
11. Verify the MSFT entity was created with all the stock data fields

### 5.10 Create an MCP Server using the Logic App
1. Navigate back to the Logic App (`logic-stocks-<yourname>`)
2. In the left menu, click on **MCP servers** under the **Agents** section
3. Select **Use existing workflows**
4. Create an MCP server:
   - **MCP Server Name:** `stockstoragemcp`
   - **Description:** `MCP server to receive stock data from agent and store in Azure Table Storage using Logic App`
   - **Workflow:** Select the workflow you just created (`workflow-stocks-<yourname>`)
   - Click **Create**
5. Refresh the page and verify that the MCP server is listed under Servers.
6. Under Authentication, click **Edit**
   - Select **Key-based** Method
   - Click **Save**.
7. Under Authentication, click **Generate key** beside API keys. 
8. Generate MCP API key:
   - **Duration:** `24 hours`
   - **Access key:** `Primary key`
   - Click **Generate** and copy the generated API key. Save this securely. This will be used for authentication when the agent calls this MCP server.
   - Click **Close** after copying the key.
9. Under Servers, select **Copy URL** for the `stockstoragemcp` server. This is the URL that the agent will call to send stock data to the Logic App.

---

## Step 6: Add MCP Tool to Agent

### 6.1 Return to Agent Configuration
1. Return to the Microsoft Foundry Portal, navigate to **Build** > **Agents**
2. Select your **stockanalyst** agent
3. Navigate to the **Tools** section

### 6.2 Add Custom MCP Server Tool
1. Click **Add** and select **Browse all tools**
2. Select Custom tab and click **Model Context Protocol (MCP)**
3. Click **Create**
4. Add Model Context Protocol Tool:
   - **Name:** `stock-storage-mcp`
   - **Remote MCP Server endpoint:** Paste the MCP server URL you copied in Step 5.10 (the URL for `stockstoragemcp`)
   - **Authentication:** Select **Key-based** 
   - **Credential:** 
       - **Key name:** `X-API-KEY`
       - **Key value:** The MCP API key you generated in Step 5.10
   - Click **Connect**

### 6.3 Verify All Three Tools
1. In the **Tools** section, verify you have:
   - ✅ **Code Interpreter** (built-in)
   - ✅ **get_stock_quote** (OpenAPI - Alpha Vantage)
   - ✅ **stock-storage-mcp** (MCP Server - Logic App)
2. Ensure **Web search** is removed

### 6.4 Configure MCP Tool Definition
1. Select the three dots next to the `stock-storage-mcp` tool and click **Configure**.
2. Under Approval setting for tools in this MCP server for this agent, select **Always auto-approve all tools** to allow the agent to call this MCP server without prompting for approval each time.
3. Click **Apply**.

### 6.5 Save the Agent
1. Click **Save** in the upper right corner

---

## Step 7: Test the Complete Agent with All Three Tools

### 7.1 Test Full Workflow (Fetch + Store)
1. In the agent playground, ask:
   ```
   Get the current stock price for Meta (META) and save it to storage.
   ```
2. Observe the agent:
   - ✅ Calls `get_stock_quote` OpenAPI tool to fetch from Alpha Vantage
   - ✅ Calls `stock-storage-mcp` MCP tool to store in Table Storage
   - ✅ Displays the stock information and confirmation

3. Verify in Azure Portal:
   - Navigate to your storage account > **Storage browser** > **Tables** > **stockquotes**
   - Verify the META entity was created with all data fields

### 7.2 Test Multiple Stocks
1. Ask the agent to fetch and store multiple stocks:
   ```
   Get the current prices for Apple (AAPL), Tesla (TSLA), and Amazon (AMZN), and save them all to storage.
   ```
2. Observe the agent:
   - ✅ Makes 3 calls to `get_stock_quote`
   - ✅ Makes 3 calls to `stock-storage-mcp`
   - ✅ Confirms all data is stored

3. Verify in Logic App runs history that all calls were successful.
   - Navigate to the Workflows > Workflows > Select your workflow > Run history

4. Verify in Table Storage that all 3 entities were created
   - Navigate to your storage account > **Storage browser** > **Tables** > **stockquotes**
   - Verify that the entities were created with all data fields

### 7.3 Test Code Interpreter with Stored Data
1. Ask for analysis:
   ```
   I just saved stock data for Microsoft, Apple, and Amazon. Can you create a bar chart comparing their current prices?
   ```
2. Observe the agent:
   - ✅ Uses information from previous queries
   - ✅ Uses Code Interpreter to create visualization
   - ✅ Displays a bar chart comparing the three stocks
   - ✅ Lets you download the chart image

### 7.4 Test Complex Combined Workflow
1. Ask a comprehensive question:
   ```
   Fetch the current stock prices for Microsoft, Google, and Apple. Save all of them to storage. Then analyze which stock has the best performance based on the change percent, and create a visualization showing the price changes.
   ```
2. Observe the agent workflow:
   - ✅ **Step 1:** Fetches 3 stock quotes (OpenAPI tool - 3 calls)
   - ✅ **Step 2:** Saves 3 stock records (MCP tool - 3 calls)
   - ✅ **Step 3:** Analyzes performance (Code Interpreter)
   - ✅ **Step 4:** Creates visualization (Code Interpreter)
   - ✅ Provides comprehensive analysis with charts

### 7.5 Test Workflow Without Storage
1. Ask the agent to just analyze without storing:
   ```
   Get the current price for Netflix (NFLX) and calculate what 50 shares would be worth. Don't save it.
   ```
2. Observe the agent:
   - ✅ Calls `get_stock_quote` only
   - ✅ Uses Code Interpreter for calculation
   - ✅ Skips the `stock-storage-mcp` tool as requested

### 7.6 Review Agent Logs
1. Click on **Logs** at the bottom of the playground
2. Review the sequence of tool invocations
3. Examine:
   - OpenAPI calls to Alpha Vantage
   - MCP calls to Logic App
   - Code Interpreter executions
4. Verify data flow between tools

---

## Step 8: Understanding the Three Tool Types

**Use Code Interpreter when:**
- ✅ You need to perform calculations or data analysis
- ✅ You want to create visualizations (charts, graphs)
- ✅ You need to process or transform data
- ✅ No external services required
- ✅ Python capabilities are sufficient

**Use OpenAPI Tools when:**
- ✅ You're calling external REST APIs
- ✅ The API has predictable request/response patterns
- ✅ You want direct API integration
- ✅ The API provides data retrieval operations
- ✅ Simple authentication (API key, bearer token)

**Use Logic Apps as a Custom MCP when:**
- ✅ You need Azure-specific operations (Storage, Cosmos DB, etc.)
- ✅ You want to orchestrate multiple steps
- ✅ You need error handling, retry logic, conditions
- ✅ You're building workflows that persist data
- ✅ You need stateful operations

---

## Verification Checklist

### Part 1: Azure Resources
- [ ] Resource group `rg-foundry-tools` created
- [ ] Storage account created
- [ ] Table `stockquotes` created
- [ ] Storage account connection string obtained
- [ ] Alpha Vantage API key obtained
- [ ] Foundry resource created
- [ ] GPT-4.1 model deployed

### Part 2: Logic App (MCP Server)
- [ ] Logic App created
- [ ] HTTP trigger configured with stock data JSON schema
- [ ] Table Storage connection created
- [ ] Insert or Update Entity action configured
- [ ] Response action configured
- [ ] Logic App URL obtained
- [ ] Logic App tested independently with sample data
- [ ] MCP server created using the Logic App workflow

### Part 3: Agent Configuration
- [ ] Agent `stockanalyst` created
- [ ] Agent instructions configured
- [ ] Code Interpreter tool added
- [ ] OpenAPI tool added (`get_stock_quote` - Alpha Vantage)
- [ ] MCP server connection added (`stock-storage-mcp` - Logic App)
- [ ] Web search removed
- [ ] Agent saved

### Part 4: Testing
- [ ] OpenAPI tool successfully fetches stock data from Alpha Vantage
- [ ] MCP tool successfully stores data in Table Storage
- [ ] Data visible in Azure Portal Table Storage
- [ ] Code Interpreter executes Python and creates visualizations
- [ ] All three tools work together in combined workflows
- [ ] Agent logs show all tool invocations

---

## Clean Up Resources

To avoid incurring charges, delete the resources when finished:

1. In the Azure Portal, navigate to **Resource groups**
2. Select `rg-foundry-tools`
3. Click **Delete resource group**
4. Type the resource group name to confirm
5. Click **Delete**

> **Note:** This will delete all resources including Foundry, Storage, and Logic App.

---

## Summary and Key Takeaways

In this lab, you successfully:

1. ✅ Created a single agent with three different tool types
2. ✅ Implemented Code Interpreter for code execution and data analysis
3. ✅ Integrated external Alpha Vantage API using OpenAPI tool specification
4. ✅ Built a custom Azure Logic App as an MCP server for data persistence
5. ✅ Demonstrated clean separation of concerns: Fetch (OpenAPI) vs Store (MCP) vs Analyze (Code Interpreter)
6. ✅ Tested various agent capabilities and tool combinations

---

## Lab Completion Badge

Congratulations! 🎉 You have completed the **Microsoft Foundry Agents with Code Interpreter, OpenAPI Tools, and Custom MCP Servers** lab.

You now have hands-on experience with:
- Configuring Code Interpreter for data analysis
- Integrating external APIs using OpenAPI tool specifications
- Building custom MCP servers with Azure Logic Apps
- Creating sophisticated multi-tool agent workflows
- Integrating agents with Azure services and third-party APIs

**End of Lab**
