# Lab: Document Intelligence and Content Understanding with Azure AI

## Overview
In this hands-on lab, you will learn how to extract structured information from unstructured documents using Azure AI Document Intelligence and analyze audio recordings using Azure AI Content Understanding. This lab demonstrates how to process real-world documents like forms and analyze customer service call recordings to extract valuable insights.

**Estimated Time:** 90 minutes

**Prerequisites:**
- An Azure account with an active subscription
- Access to a role that allows you to create Azure AI resources (e.g., Contributor or Owner)
- Basic understanding of document processing and AI services
- Sample COVID consent forms (provided in the Forms folder)
- Sample call center recordings (provided in the Recordings folder)

---

## Lab Architecture
By the end of this lab, you will have:
- An Azure AI Document Intelligence resource configured for custom form extraction
- A custom document model trained to extract patient information from COVID consent forms
- An Azure AI Content Understanding resource for audio analysis
- A content understanding model that extracts insights from customer service call recordings
- Tested both models with real sample data

**What You'll Extract:**

**From Forms (Document Intelligence):**
- Last Name, First Name, Middle Name
- Date of Birth, Age, Gender
- Home Address, City, State, Zip
- Vaccine Arm (left or right)
- Previous Dose Received (Y or N)
- Manufacturer of Previous Dose Received

**From Call Recordings (Content Understanding):**
- Customer Name
- Agent Name
- Summary of Call
- Resolution of Call
- Product Name mentioned in the call
- Sentiment of the Call

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
   - **Resource group name:** `rg-documents`
   - **Region:** `Australia East`
5. Click **Review + Create**, then **Create**

### 1.3 Create an Azure Storage Account
1. In the Azure Portal, click **Create a resource**
2. Search for **Storage Account** and select it
3. Click **Create**
4. Configure the storage account:
   - **Subscription:** Select your subscription
   - **Resource group:** `rg-documents`
   - **Storage account name:** `stdocumentai<yourname>` (must be globally unique, lowercase, no hyphens)
   - **Region:** `Australia East`
   - **Performance:** Standard
   - **Redundancy:** Locally-redundant storage (LRS)
5. Click **Review + Create**, then **Create**
6. Wait for deployment to complete (typically 1-2 minutes)
7. Click **Go to resource**

### 1.4 Create Containers and Upload Sample Documents
1. In your storage account, navigate to **Data storage** > **Containers** in the left menu

#### Upload Training Forms
2. Click **+ Container**
3. Configure the container:
   - **Name:** `training-forms`
   - **Public access level:** Private (no anonymous access)
4. Click **Create**
5. Click on the **training-forms** container
6. Click **Upload**
7. Upload all PDF files from the `Unstructured Data\Forms\Training Files` folder
8. Click **Upload** and wait for completion

#### Upload Test Forms
9. Click **Containers** in the breadcrumb navigation to return to the containers list
10. Click **+ Container**
11. Configure the container:
    - **Name:** `test-forms`
    - **Public access level:** Private (no anonymous access)
12. Click **Create**
13. Click on the **test-forms** container
14. Click **Upload**
15. Upload all PDF files from the `Unstructured Data\Forms\Test Files` folder
16. Click **Upload** and wait for completion

#### Create Call Recordings Container
17. Click **Containers** in the breadcrumb navigation to return to the containers list
18. Click **+ Container**
19. Configure the container:
    - **Name:** `call-recordings`
    - **Public access level:** Private (no anonymous access)
20. Click **Create**

### 1.5 Create an Azure Document Intelligence Resource
1. In the Azure Portal, click **Create a resource**
2. Search for **Document Intelligence** and select it
3. Click **Create**
4. Configure the Document Intelligence resource:
   - **Subscription:** Select your subscription
   - **Resource group:** `rg-documents`
   - **Region:** `Australia East`
   - **Name:** `doc-intel-<yourname>` (must be globally unique)
   - **Pricing tier:** Standard S0
5. Click **Review + Create**, then **Create**
6. Wait for deployment to complete (typically 2-3 minutes)
7. Once deployed, click **Go to resource**
8. Navigate to **Resource Management > Keys and Endpoint** in the left menu
9. Copy and save (you'll need this later):
   - **KEY 1** 
   - **Endpoint** URL

### 1.6 Create a Microsoft Foundry Resource (for Content Understanding)
1. In the Azure Portal, click **Create a resource**
2. Search for **Microsoft Foundry** and select it
3. Click **Create**
4. Configure the resource:
   - **Subscription:** Select your subscription
   - **Resource group:** `rg-documents`
   - **Name:** `ai-content-<yourname>` (must be globally unique)
   - **Region:** `Australia East`
   - **Default project name:** project-cu
5. Click **Review + Create**, then **Create**
6. Wait for deployment to complete (typically 2-3 minutes)
7. Once deployed, click **Go to resource**
8. Navigate to **Resource Management > Keys and Endpoint** in the left menu
9. Copy and save (you'll need this later):
   - **KEY 1** 
   - **Foundry > API endpoint** URL

---

## Step 2: Build a Custom Document Model with Document Intelligence Studio

### 2.1 Access Document Intelligence Studio
1. Navigate to [Document Intelligence Studio](https://contentunderstanding.ai.azure.com/)
2. Sign in with your Azure account credentials
3. Select **Start with Document Intelligence**
4. Verify in the upper right corner that you are signed in by clicking the Profile icon.
5. Click on the cog icon (Settings) near your profile icon.
6. Under **Resource**, click your Document Intelligence resource (`doc-intel-<yourname>`) to select it.
7. Click **Use resource** to confirm your selection
8. Select Yes to confirm switching resources if prompted.

### 2.2 Create a Custom Extraction Model Project
1. Go back to the Document Intelligence Studio, scroll down to the **Custom models** section
2. Click **Custom extraction model**
3. Click **Create a project**

### 2.3 Configure Project Settings
1. On the **Create project** page, configure:
   - **Project name:** `covid-consent-forms`
   - **Description:** `Extract patient information from COVID-19 vaccine consent forms`
2. Click **Continue**

### 2.4 Configure Service Resource
1. On the **Configure service resource** page:
   - **Subscription:** Select your subscription
   - **Resource group:** Select `rg-documents`
   - **Document Intelligence or Cognitive Service resource:** Select `doc-intel-<yourname>`
   - **API version:** Use the latest (default)
2. Click **Continue**

### 2.5 Connect Training Data Source
1. On the **Connect training data source** page:
   - **Subscription:** Select your subscription
   - **Resource group:** Select `rg-documents`
   - **Storage account:** Select `stdocumentai<yourname>`
   - **Blob container:** Select `training-forms`
   - **Folder path:** Leave blank (will use all files in container)
2. Click **Continue**

### 2.6 Review and Create
1. Review your project configuration
2. Click **Create project**
3. Wait for the project to initialize (typically 10-20 seconds)
4. Select Skip when you see a dialog asking to label documents (you'll label them in the next step)

### 2.7 Label Your Training Documents
Now you'll label the fields you want to extract from the forms.

#### Set Up Fields
1. In the right panel, you'll see the **Fields** section
2. Click **+ Add field** to create each field you want to extract
3. Add the following fields (click **+ Add field** for each), type the Field name and press **Enter**:
   - Field: `LastName` 
   - Field: `FirstName` 
   - Field: `MiddleName` 
   - Field: `DateOfBirth` 
   - Field: `Age` 
   - Selection Mark: `Gender` 
   - Field: `HomeAddress` 
   - Field: `City` 
   - Field: `State` 
   - Field: `Zip` 
   - Selection Mark: `VaccineArm` 
   - Field: `PreviousDoseReceived` 
   - Field: `PreviousManufacturer` 

#### Label First Document
4. In the center panel, you'll see the first training document displayed
5. Select **Run layout.**
6. For each field, follow this process:
   - Select the text in the document that corresponds to the field
   - Click the proper field
   - The selected text will be highlighted and associated with that field
   - If the field is empty (e.g., middle name), select the empty location by using Draw region, then assign it to the field. This will help the model learn that this field can be empty.
7. Label all 13 fields on the first document
**Tip:** Use the zoom controls if text is too small to read clearly
8. Review your labels to ensure they are correct, consistent, and complete.

#### Label Remaining Documents
9. Click the unlabeled document in the left panel to load the next training document
10. Repeat the labeling process for all 6 training documents
11. **Best Practice:** Label at least 5 documents for a robust model and capture different variations in the forms (e.g., different handwriting, different layouts)

### 2.8 Train Your Custom Model
1. Once you've labeled all training documents, click **Train** in the top menu
2. Configure training:
   - **Model ID:** `covid-consent-v1`
   - **Description:** `Extracts patient info from COVID consent forms`
   - **Build mode:** Template (recommended for forms with consistent layout)
3. Click **Train**
4. A Training in progress notification will appear.
5. Select Go to Models
6. Wait for the model to show Status as succeeded. (typically 2-5 minutes)

### 2.9 Review Model Performance
1. After training completes, click the model to view details
2. Review the **Accuracy** metrics:
   - ✅ Accuracy should be > 90% for well-labeled fields
   - ✅ If accuracy is low, you may need to add more labeled documents or verify labels
3. Note the **Model ID** - you'll use this for testing

---

## Step 3: Test Your Document Intelligence Model

### 3.1 Navigate to Test Section
1. With your model selected, click the **Test** button in the top menu
2. You'll see the test interface

### 3.2 Test with a Sample Document
1. Click **Browse for files** or drag and drop a file
2. Select one of the test documents from your `test-forms` folder:
   - Option A: Use **Browse for files** to upload directly from your local
   - Option B: Use **Fetch from URL** to retrieve from the Azure Storage `test-forms` container
3. Select a test PDF and click **Run analysis**
4. Wait for analysis to complete (typically 5-10 seconds)

### 3.3 Review Extraction Results
1. After analysis completes, you'll see:
   - **Document view:** Original PDF with highlighted fields
   - **Fields:** Extracted values for each labeled field
   - **Confidence scores:** How confident the model is in each extraction
2. Verify the extracted values:
   - ✅ Last Name, First Name, Middle Name extracted correctly
   - ✅ Date of Birth, Age, Gender extracted correctly
   - ✅ Address fields (Home Address, City, State, Zip) extracted correctly
   - ✅ Vaccine Arm (left/right) extracted correctly
   - ✅ Previous dose information extracted correctly

### 3.4 Test with Second Document
1. Click **Browse for files** again
2. Select the other test document
3. Click **Run analysis**
4. Verify extraction accuracy

### 3.5 Review JSON Output
1. Select the **Result** Tab
2. This shows the structured data format you would receive via API
3. Note the JSON structure.

---

## Step 4: Set Up Content Understanding for Audio Analysis

### 4.1 Access Content Understanding Studio
1. Navigate to [Content Understanding Studio](https://contentunderstanding.ai.azure.com/)
2. Sign in with your Azure account credentials
3. Select **Explore Content Understanding**

### 4.2 Select Your Resource
1. Click on the settings icon near your profile icon in the top right
2. Select **Add resource**
3. Configure your resource:
   - **Subscription:** Select your subscription
   - **Resource group name:** Select `rg-documents`
   - **Resource name:** Select `ai-content-<yourname>`
   - Enable auto-deployment for required models if no default deployment available
   - Click **Next**
4. Click **Save** to confirm your resource selection
5. Verify that models are deployed successfully for the selected resource


### 4.3 Create a New Content Understanding Project
1. Select **Build**
2. Click **+ Create**
3. Configure the project:
   - **Project name:** `call-center-analysis`
   - **Description:** `Analyze customer service call recordings to extract insights`
   - **Project Type:** Select **Extract content and field with custom schema**
4. Configure Advanced settings:
   - **Connected resource:** Select `ai-content-<yourname>`
   - **Subscription:** Select your subscription
   - **Resource Group:** Select `rg-documents`
   - **Storage Account:** Select `stdocumentai<yourname>`
   - **Blob Container:** Select `call-recordings`
   - **Model for analysis:** Select the default model
5. Click **Create**

### 4.4 Upload Call Recordings
1. In your new project, click **Browse for files**
2. Upload one of the call recordings from the `Recordings` folder
3. Select Audio Analysis
4. Click **Save**

### 4.5 Define Schema for Extraction
You'll now define what information to extract from the call recordings.

1. In your project, navigate to **Schema**
2. Click **+ Add field** to create each extraction field
3. Add the following fields:

   - **Field name:** `CustomerName`
     - **Description:** `The name of the customer calling`
     - **Type:** String
     - **Method:** Generate
   
   - **Field name:** `AgentName`
     - **Description:** `The name of the customer service agent`
     - **Type:** String
     - **Method:** Generate
     
   - **Field name:** `CallSummary`
     - **Description:** `A brief summary of what the call was about`
     - **Type:** String
     - **Method:** Generate
     
   - **Field name:** `CallResolution`
     - **Description:** `Determine if the agent was able to resolve the customer's issue (e.g., Resolved, Unresolved, Escalated)`
     - **Type:** String
     - **Method:** Classify
     - **Categories:**
         - Add category: 
            - Category Name: Resolved 
            - Category Description: The customer's issue was resolved during the call
            - Category Name: Unresolved
            - Category Description: The customer's issue was not resolved during the call
            - Category Name: Escalated
            - Category Description: The customer's issue was escalated to a higher level of support
         - Click **Save**
   
   - **Field name:** `ProductName`
     - **Description:** `Identify any product names mentioned during the call`
     - **Type:** String
     - **Method:** Generate
   
   - **Field name:** `CallSentiment`
     - **Description:** `Identify the overall sentiment of the call (Positive, Neutral, Negative)`
     - **Type:** String
     - **Method:** Classify
       - **Categories:**
          - Add category: 
               - Category Name: Positive 
               - Category Description: The customer expresses positive sentiment during the call
               - Category Name: Neutral
               - Category Description: The customer expresses neutral sentiment during the call
               - Category Name: Negative
               - Category Description: The customer expresses negative sentiment during the call
          - Click **Save**

4. Click **Save**

### 4.6 Process Audio Files and Review Results
1. Click **Run analysis** at the upper left.
2. Wait for the processing to complete. This may take several minutes depending on the length of the audio and the complexity of the analysis.
3. Once processing is complete, you can review the extracted information for the call recording in the **Fields** tab.
4. Review each field's value
5. Select the **Result** tab to see the structured JSON output of the analysis, which includes all extracted fields and their values.
---

### 4.7 Analyze Remaining Recordings
1. Select **Browse for files** again to upload the next call recording from your local machine
2. Click **Run analysis** 
3. Review extracted information for each call and the JSON output.

### 4.8 Build the Analyzer
1. Select **Build analyzer** from the top beside **Run analysis**
2. Configure the analyzer:
   - **Name:** `callanalyzer`
   - **Description:** `Analyzer for processing call center recordings and extracting insights`
   - Click **Build**
3. Select **Jump to analyzer list**
4. Select the `callanalyzer` you just built and review the details
5. View the Code Examples for how to call this analyzer via code

---

## Step 5: Access Results via Cloud Shell and API

### 5.1 Enable Anonymous Access to Test Documents and Call Recordings
To access the test documents and call recordings via API, you need to enable anonymous read access to the blobs in your storage account.
1. In the Azure Portal, navigate to your storage account (`stdocumentai<yourname>`)
2. Click on **Settings > Configuration** in the left menu
3. Scroll down to **Allow Blob anonymous access** and set it to **Enabled**
4. Click **Save** to apply the changes
5. Wait for the configuration to update (typically 1-2 minutes)
6. Click on **Containers** under Data storage in the left menu
7. Click on the `test-forms` container
8. Select **Change access level** from the top menu
9. Set **Public access level** to **Blob (anonymous read access for blobs only)**
10. Click **Ok**
11. Repeat steps 7-10 for the `call-recordings` container

### 5.2 Get Document Intelligence Results via API
1. Open the Azure Cloud Shell from the Azure Portal (top right corner)
2. Select Bash environment
3. Use the following sample code to call your Document Intelligence model via API (replace placeholders with your values):

```bash
# Set variables
endpoint="<your-document-intelligence-endpoint>"
key="<your-document-intelligence-key>"
model_id="covid-consent-v1"   
file_path="<path-to-your-test-document.pdf>"

# Call the API
curl -i -v -X POST "$endpoint/documentintelligence/documentModels/$model_id:analyze?api-version=2024-11-30" \
  -H "Content-Type: application/json" \
  -H "Ocp-Apim-Subscription-Key: $key" \
  --data-ascii "{'urlSource': '$file_path'}"
```
4. Get the apim request id from the result. 
5. Use the request id to get the result of the analysis with the following command. Replace `{resultId}` with the actual request id you received from the previous command.
```bash
# GET request to retrieve results
curl -v -X GET "$endpoint/documentintelligence/documentModels/$model_id/analyzeResults/{resultId}?api-version=2024-11-30" \
  -H "Ocp-Apim-Subscription-Key: $key" | \
  jq '.analyzeResult.documents[0].fields | {
    LastName: .LastName.content,
    FirstName: .FirstName.content,
    DateOfBirth: .DateOfBirth.content,
    City: .City.content,
    State: .State.content,
    PreviousDoseReceived: .PreviousDoseReceived.content,
    PreviousManufacturer: .PreviousManufacturer.content
  }'
```
> Note the use of `jq` to parse the JSON response and extract specific fields for easier readability.
6. Review the extracted field values in the API response and compare them to the results you saw in the Document Intelligence Studio.

### Get Content Understanding Results via API
1. Use the following sample code to call your Content Understanding analyzer via API (replace placeholders with your values):

```bash 
# Set variables
endpoint="<your-content-understanding-endpoint>"
key="<your-content-understanding-key>"
analyzer_id="callanalyzer"
file_path="<path-to-your-call-recording.wav>"
# Call the API
# Analyze audio file with custom analyzer
curl -i \
  "$endpoint/contentunderstanding/analyzers/$analyzer_id:analyze?api-version=2025-11-01" \
  -H "Ocp-Apim-Subscription-Key: $key" \
  -H "Content-Type: application/json" \
  --data-raw "{
    \"inputs\": [
      {
        \"url\": \"$file_path\"
      }
    ]
  }"
```
2. Retrieve the request-id from the response header
3. Use the request-id to get the analysis results with the following command. Replace `{request-id}` with the actual request id you received from the previous command.

```bash
# Get analysis results
curl -s \
  "$endpoint/contentunderstanding/analyzerResults/{request-id}?api-version=2025-11-01" \
  -H "Ocp-Apim-Subscription-Key: $key" \
| jq '.result.contents[0].fields
      | map_values(.valueString)'
```
> Note the use of `jq` to parse the JSON response and extract the field values for easier readability.

4. Review the extracted fields (Customer Name, Agent Name, Call Summary, Call Resolution, Product Name, Call Sentiment) in the API response and compare them to the results you saw in the Content Understanding Studio.


---
## Verification Checklist

### Azure Resources
- [ ] Resource group created (`rg-documents`)
- [ ] Storage account created
- [ ] Document Intelligence resource created
- [ ] Foundry resource created

### Document Intelligence
- [ ] Document Intelligence Studio accessed
- [ ] Custom extraction project created
- [ ] All 13 fields defined in schema
- [ ] All 6 training documents labeled
- [ ] Model trained successfully
- [ ] Test documents analyzed 

### Content Understanding
- [ ] Content Understanding Studio accessed
- [ ] Audio analysis project created
- [ ] Schema defined with 6 extraction fields
- [ ] Audio files processed successfully
- [ ] Extracted fields reviewed (Customer Name, Agent Name, etc.)
- [ ] Sentiment analysis results reviewed

---

## Clean Up Resources

To avoid incurring charges, delete the resources when you're finished with the lab:

1. In the Azure Portal, navigate to **Resource groups**
2. Select `rg-documents`
3. Click **Delete resource group**
4. Type the resource group name to confirm: `rg-documents`
5. Click **Delete**
6. Wait for deletion to complete (typically 2-5 minutes)

> **Note:** This will delete all resources including Document Intelligence, Microsoft Foundry, and Storage account.

---

## Summary and Key Takeaways

In this lab, you successfully:

1. ✅ Created Azure AI resources (Storage, Document Intelligence, Microsoft Foundry)
2. ✅ Uploaded training documents to Azure Blob Storage
3. ✅ Built a custom document extraction model in Document Intelligence Studio
4. ✅ Labeled 13 fields across 6 training documents
5. ✅ Trained a custom model for COVID consent form extraction
6. ✅ Tested the model with new documents and achieved high accuracy
7. ✅ Set up Content Understanding for audio analysis
8. ✅ Processed call center recordings to extract customer insights
9. ✅ Extracted structured data: names, summaries, resolutions, products, and sentiment

### Real-World Applications

**Document Intelligence Use Cases:**
- **Healthcare:** Patient intake forms, insurance claims, medical records
- **Finance:** Loan applications, tax forms, invoices
- **Legal:** Contracts, court documents, NDAs
- **HR:** Job applications, employee onboarding, time sheets
- **Retail:** Order forms, return requests, warranty cards

**Content Understanding Use Cases:**
- **Customer Service:** Call analysis, quality assurance, agent training
- **Sales:** Sales call review, objection handling, conversion analysis
- **Compliance:** Regulatory compliance monitoring, script adherence
- **Market Research:** Customer feedback analysis, product mentions
- **Healthcare:** Patient calls, telemedicine consultations, appointment scheduling

---

## Lab Completion Badge

Congratulations! 🎉 You have completed the **Azure AI Document Intelligence and Content Understanding** lab.

You now have hands-on experience with:
- Building custom document extraction models
- Processing forms to extract structured data
- Analyzing audio recordings for customer insights
- Extracting actionable information from unstructured content
- Integrating AI services into business workflows

**Skills Acquired:**
- Document Intelligence custom model training
- Audio transcription and analysis
- Azure Content Understanding configuration
- Unstructured data processing
- AI-powered information extraction

---

**End of Lab**
