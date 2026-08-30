# Lab: Azure Machine Learning with Diabetes Dataset

## Overview
In this hands-on lab, you will learn how to use Azure Machine Learning to build predictive models using both Automated Machine Learning (AutoML) and traditional notebook-based approaches. You'll work with the Diabetes dataset to predict diabetes diagnosis and compare different machine learning techniques.

**Estimated Time:** 90 minutes

**Prerequisites:**
- An Azure account with an active subscription
- Access to a role that allows you to create Azure Machine Learning resources (e.g., Contributor)
- Basic understanding of machine learning concepts
- Familiarity with Python and Jupyter notebooks

---

## Lab Architecture
By the end of this lab, you will have:
- An Azure Machine Learning workspace deployed
- A compute instance for running notebooks
- The Diabetes dataset uploaded as a registered data asset
- An AutoML classification experiment completed with model evaluation
- A custom notebook with manual model training using scikit-learn
- Comparison of AutoML vs manual approach results
- Understanding of model deployment options

---

## Dataset Overview

The **Diabetes Dataset** contains medical predictor variables and one target variable (Outcome). Predictor variables include:
- **Pregnancies:** Number of times pregnant
- **Glucose:** Plasma glucose concentration
- **BloodPressure:** Diastolic blood pressure (mm Hg)
- **SkinThickness:** Triceps skinfold thickness (mm)
- **Insulin:** 2-Hour serum insulin (mu U/ml)
- **BMI:** Body mass index (weight in kg/(height in m)^2)
- **DiabetesPedigreeFunction:** Diabetes pedigree function (genetic factor)
- **Age:** Age in years
- **Outcome:** Class variable (0 or 1) - whether patient has diabetes

**Task:** Binary classification to predict whether a patient has diabetes based on medical measurements.

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
   - **Resource group name:** `rg-azure-ml`
   - **Region:** `Australia East`
5. Click **Review + Create**, then **Create**

---

## Step 2: Create Azure Machine Learning Workspace

### 2.1 Create Azure Machine Learning Workspace
1. In the Azure Portal, click **Create a resource**
2. Search for **Azure Machine Learning** and select it
3. Click **Create**
4. Configure the workspace:
   - **Subscription:** Select your subscription
   - **Resource group:** `rg-azure-ml`
   - **Workspace name:** `ml-diabetes-<yourname>` (must be unique)
   - **Region:** `Australia East`
   - **Storage account:** (auto-created)
   - **Key vault:** (auto-created)
   - **Application insights:** (auto-created)
   - **Container registry:** None
5. Click **Review + Create**, then **Create**
6. Wait for deployment to complete (typically 3-5 minutes)

### 2.2 Access Azure Machine Learning Studio
1. Once deployment completes, click **Go to resource**
2. In the workspace overview, click **Launch studio** or navigate to [https://ml.azure.com/](https://ml.azure.com/)
3. Sign in with your Azure credentials
4. Verify you're in the correct workspace (`ml-diabetes-<yourname>`) displayed in the upper right corner

---

## Step 3: Create a Compute Instance

### 3.1 Create Compute Instance for Notebooks
1. In Azure Machine Learning Studio, navigate to **Manage** > **Compute** in the left sidebar
2. Select the **Compute instances** tab
3. Click **+ New**
4. Configure the compute instance:
   - **Compute name:** `compute-diabetes` (lowercase, alphanumeric only)
   - **Virtual machine type:** CPU
   - **Virtual machine size:** Click **Select from all options**
     - Search for and select **Standard_DS3_v2** (choose a different size if you have limited quota)
5. Click **Review + Create**, then **Create**
6. Wait for the compute instance to start (typically 3-5 minutes)
7. Status will change from "Creating" to "Running"

> **Note:** The compute instance will auto-shutdown after 60 minutes of inactivity to save costs.

---

## Step 4: Download and Upload Diabetes Dataset

### 4.1 Download the Diabetes Dataset
1. **Download** the `diabetes.csv` found in the Machine Learning folder of this repository to your local machine

### 4.2 Upload Dataset to Azure ML
1. In Azure Machine Learning Studio, navigate to **Assets** > **Data** in the left sidebar
2. Select the **Data assets** tab
3. Click **+ Create**
4. Configure the data asset:
   - **Name:** `diabetes-dataset`
   - **Description:** `Diabetes dataset for binary classification`
   - **Type:** Select **Tabular** under Data asset types (from Azure ML v1 APIs)
5. Click **Next**
6. **Data source:** Select **From local files**
7. Click **Next**
8. **Destination storage type:** Select the default datastore (workspaceblobstore)
9. Click **Next**
10. **File or folder selection:** Click **Upload files**
11. Browse and select the `diabetes.csv` file
12. Wait for upload to complete
13. Click **Next**
14. **Settings:** Review the file and click **Next**
15. **Schema:** Review the file schema and verify the Types for each column are correct (BMI and DiabetesPedigreeFunction are decimals while the rest are Integers)
16. Click **Next**
17. Click **Create**

### 4.3 Verify Dataset Upload
1. Navigate to **Assets** > **Data** > **Data assets**
2. Find and click on `diabetes-dataset`
3. Click the **Explore** tab
4. Verify you can see the data preview with columns: Pregnancies, Glucose, BloodPressure, SkinThickness, Insulin, BMI, DiabetesPedigreeFunction, Age, Outcome
5. Note the dataset has 768 rows and 9 columns

---

## Step 5: Automated Machine Learning (AutoML) Experience

### 5.1 Create an AutoML Experiment
1. In Azure Machine Learning Studio, navigate to **Authoring** > **Automated ML** in the left sidebar
2. Click **+ New Automated ML job**
3. Configure the job basics:
   - **Job name:** `automl-diabetes-classification`
   - **Experiment name:** `diabetes-prediction`
   - **Description:** `AutoML classification to predict diabetes outcome`
4. Click **Next**

### 5.2 Select Task Type and Dataset
1. **Task type & data:** Select **Classification**
2. **Select data:**
   - Choose `diabetes-dataset`
   - Click **Next**
3. **Configure task settings:**
   - **Target column:** Select **Outcome**
   - Expand **View additional configuration settings**
      - **Primary metric:** Select **AUC weighted**
      - **Explain best model:** Check this box ✅
      - Click **Save**
   - Expand **Limits:**
      - **Max concurrent trials:** `2`
      - **Experiment timeout (minutes):** `30`
   - Click **Next**

### 5.3 Configure Compute
1. **Select compute type:** Select **Compute cluster**
2. Click **+ New** to create a new compute cluster
3. Configure the compute cluster:
   - **Virtual machine tier:** Dedicated
   - **Virtual machine type:** CPU
   - **Virtual machine size:** Click **Select from all options**
      - Search for and select **Standard_DS3_v2** (choose a different size if you have limited quota)
      - Click **Next**
   - **Compute name:** `cpu-cluster-diabetes`
   - **Minimum number of nodes:** `0`
   - **Maximum number of nodes:** `2` (if you have limited quota, set to 1)
   - **Idle seconds before scale down:** `120`
4. Click **Create**
5. Wait for compute cluster creation (1-2 minutes)
6. Select `cpu-cluster-diabetes` from the dropdown
7. Click **Next**

### 5.4 Review and Submit AutoML Job
1. Review all settings on the summary page:
   - Task: Classification
   - Dataset: diabetes-dataset
   - Target: Outcome
   - Compute: cpu-cluster-diabetes
2. Click **Submit training job**
3. You'll be redirected to the job details page

### 5.5 Monitor AutoML Progress
1. On the job details page, you'll see:
   - **Status:** Running → Completed
   - **Data guardrails:** Checks for data quality issues
   - **Models + child jobs** tab: Various algorithms being tested
2. Do not wait for the job to complete. **Proceed to Step 6** to start working on the manual notebook while AutoML runs in the background.

---

## Step 6: Notebook Experience - Manual Model Training

### 6.1 Create a New Notebook
1. In Azure Machine Learning Studio, navigate to **Authoring** > **Notebooks** in the left sidebar
2. Look for **+ Files**. Click **+ Create new file**
3. Configure the notebook:
   - **File Location:** Users > your-username
   - **File name:** `diabetes-manual-training.ipynb`
   - **File type:** Notebook
4. Click **Create**
5. Ensure your compute instance (`compute-diabetes`) is running
   - Select `compute-diabetes` from the compute dropdown at the top
   - Compute must have a green status
6. Wait for the kernel to start 
   - Python 3.10 - SDK v2 must have a green status
7. Click **Authenticate** in the top right corner to authenticate your notebook with Azure ML workspace. Login with your Azure credentials if prompted.

### 6.2 Install Required Libraries
1. In the first cell, add the following code to install and import necessary libraries:

```python
# Cell 1: Install and import required libraries
# Install seaborn if not already installed
import sys
!{sys.executable} -m pip install seaborn -q

import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import StandardScaler
from sklearn.linear_model import LogisticRegression
from sklearn.ensemble import RandomForestClassifier, GradientBoostingClassifier
from sklearn.metrics import (
    accuracy_score, 
    precision_score, 
    recall_score, 
    f1_score, 
    roc_auc_score,
    confusion_matrix, 
    classification_report,
    roc_curve
)
import warnings
warnings.filterwarnings('ignore')

print("✅ Libraries imported successfully")
```

2. Click **Run cell**

### 6.3 Load and Explore the Dataset
1. Add a new cell. Add the following code to load the dataset from Azure ML data assets and perform basic exploration:

```python
# Cell 2: Load dataset from Azure ML Data Assets
from azure.ai.ml import MLClient
from azure.identity import DefaultAzureCredential

# Connect to Azure ML workspace
ml_client = MLClient.from_config(credential=DefaultAzureCredential())

# Get the registered data asset
data_asset = ml_client.data.get(name="diabetes-dataset", label="latest")

# Load the data
df = pd.read_csv(data_asset.path)

# Display basic information
print("Dataset Shape:", df.shape)
print("\nFirst 5 rows:")
print(df.head())
print("\nDataset Info:")
print(df.info())
print("\nBasic Statistics:")
print(df.describe())
print("\nTarget Distribution:")
print(df['Outcome'].value_counts())
```

2. Run the cell and review the output

### 6.4 Exploratory Data Analysis (EDA)
1. Add a new cell. Add the following code for visualization:

```python
# Cell 3: Exploratory Data Analysis
fig, axes = plt.subplots(3, 3, figsize=(15, 12))
fig.suptitle('Feature Distributions by Outcome', fontsize=16, y=1.00)

features = ['Pregnancies', 'Glucose', 'BloodPressure', 'SkinThickness', 
            'Insulin', 'BMI', 'DiabetesPedigreeFunction', 'Age']

for idx, feature in enumerate(features):
    row = idx // 3
    col = idx % 3
    ax = axes[row, col]
    
    df[df['Outcome']==0][feature].hist(bins=20, alpha=0.5, label='No Diabetes', ax=ax, color='blue')
    df[df['Outcome']==1][feature].hist(bins=20, alpha=0.5, label='Diabetes', ax=ax, color='red')
    
    ax.set_xlabel(feature)
    ax.set_ylabel('Frequency')
    ax.legend()

plt.tight_layout()
plt.show()

# Correlation heatmap
plt.figure(figsize=(10, 8))
sns.heatmap(df.corr(), annot=True, cmap='coolwarm', center=0, fmt='.2f')
plt.title('Feature Correlation Heatmap')
plt.show()

print("✅ EDA visualizations complete")
```

2. Run the cell and analyze the distributions

### 6.5 Data Preprocessing
1. Select Add code cell for data preparation:

```python
# Cell 4: Data Preprocessing
# Separate features and target
X = df.drop('Outcome', axis=1)
y = df['Outcome']

# Split data into train and test sets (80/20 split)
X_train, X_test, y_train, y_test = train_test_split(
    X, y, test_size=0.2, random_state=42, stratify=y
)

# Feature scaling
scaler = StandardScaler()
X_train_scaled = scaler.fit_transform(X_train)
X_test_scaled = scaler.transform(X_test)

print("✅ Data preprocessing complete")
print(f"Training set size: {X_train.shape[0]} samples")
print(f"Test set size: {X_test.shape[0]} samples")
print(f"\nTraining set target distribution:")
print(pd.Series(y_train).value_counts(normalize=True))
print(f"\nTest set target distribution:")
print(pd.Series(y_test).value_counts(normalize=True))
```

2. Run the cell

### 6.6 Train Multiple Models
1. Add a new cell to train different models:

```python
# Cell 5: Train multiple models
models = {
    'Logistic Regression': LogisticRegression(random_state=42, max_iter=1000),
    'Random Forest': RandomForestClassifier(random_state=42, n_estimators=100),
    'Gradient Boosting': GradientBoostingClassifier(random_state=42, n_estimators=100)
}

results = {}

for model_name, model in models.items():
    print(f"\n{'='*60}")
    print(f"Training {model_name}...")
    print('='*60)
    
    # Train the model
    model.fit(X_train_scaled, y_train)
    
    # Make predictions
    y_pred = model.predict(X_test_scaled)
    y_pred_proba = model.predict_proba(X_test_scaled)[:, 1]
    
    # Calculate metrics
    accuracy = accuracy_score(y_test, y_pred)
    precision = precision_score(y_test, y_pred)
    recall = recall_score(y_test, y_pred)
    f1 = f1_score(y_test, y_pred)
    auc = roc_auc_score(y_test, y_pred_proba)
    
    # Store results
    results[model_name] = {
        'Model': model,
        'Accuracy': accuracy,
        'Precision': precision,
        'Recall': recall,
        'F1-Score': f1,
        'AUC': auc,
        'Predictions': y_pred,
        'Probabilities': y_pred_proba
    }
    
    print(f"Accuracy:  {accuracy:.4f}")
    print(f"Precision: {precision:.4f}")
    print(f"Recall:    {recall:.4f}")
    print(f"F1-Score:  {f1:.4f}")
    print(f"AUC:       {auc:.4f}")

print("\n✅ Model training complete")
```

2. Run the cell and wait for all models to train

### 6.7 Compare Model Performance
1. Add a new cell for model comparison:

```python
# Cell 6: Compare model performance
# Create comparison DataFrame
comparison_df = pd.DataFrame({
    'Model': list(results.keys()),
    'Accuracy': [results[m]['Accuracy'] for m in results.keys()],
    'Precision': [results[m]['Precision'] for m in results.keys()],
    'Recall': [results[m]['Recall'] for m in results.keys()],
    'F1-Score': [results[m]['F1-Score'] for m in results.keys()],
    'AUC': [results[m]['AUC'] for m in results.keys()]
})

print("Model Performance Comparison:")
print("="*80)
print(comparison_df.to_string(index=False))
print("="*80)

# Identify best model by AUC
best_model_name = comparison_df.loc[comparison_df['AUC'].idxmax(), 'Model']
best_auc = comparison_df.loc[comparison_df['AUC'].idxmax(), 'AUC']
print(f"\n🏆 Best Model: {best_model_name} (AUC: {best_auc:.4f})")

# Visualize comparison
fig, axes = plt.subplots(1, 2, figsize=(15, 5))

# Bar chart comparison
metrics = ['Accuracy', 'Precision', 'Recall', 'F1-Score', 'AUC']
x = np.arange(len(metrics))
width = 0.25

for idx, model_name in enumerate(results.keys()):
    values = [results[model_name][metric] for metric in metrics]
    axes[0].bar(x + (idx * width), values, width, label=model_name)

axes[0].set_xlabel('Metrics')
axes[0].set_ylabel('Score')
axes[0].set_title('Model Performance Comparison')
axes[0].set_xticks(x + width)
axes[0].set_xticklabels(metrics)
axes[0].legend()
axes[0].grid(axis='y', alpha=0.3)

# ROC Curves
for model_name in results.keys():
    fpr, tpr, _ = roc_curve(y_test, results[model_name]['Probabilities'])
    auc_score = results[model_name]['AUC']
    axes[1].plot(fpr, tpr, label=f"{model_name} (AUC = {auc_score:.3f})")

axes[1].plot([0, 1], [0, 1], 'k--', label='Random Classifier')
axes[1].set_xlabel('False Positive Rate')
axes[1].set_ylabel('True Positive Rate')
axes[1].set_title('ROC Curves')
axes[1].legend()
axes[1].grid(alpha=0.3)

plt.tight_layout()
plt.show()
```

2. Run the cell and analyze the results

### 6.8 Detailed Analysis of Best Model
1. Add a new cell for detailed analysis:

```python
# Cell 7: Detailed analysis of best model
best_model = results[best_model_name]['Model']
best_predictions = results[best_model_name]['Predictions']

# Confusion Matrix
cm = confusion_matrix(y_test, best_predictions)
plt.figure(figsize=(8, 6))
sns.heatmap(cm, annot=True, fmt='d', cmap='Blues', 
            xticklabels=['No Diabetes', 'Diabetes'],
            yticklabels=['No Diabetes', 'Diabetes'])
plt.title(f'Confusion Matrix - {best_model_name}')
plt.ylabel('True Label')
plt.xlabel('Predicted Label')
plt.show()

# Classification Report
print(f"\nClassification Report - {best_model_name}:")
print("="*60)
print(classification_report(y_test, best_predictions, 
                          target_names=['No Diabetes', 'Diabetes']))

# Feature Importance (for tree-based models)
if hasattr(best_model, 'feature_importances_'):
    feature_importance = pd.DataFrame({
        'Feature': X.columns,
        'Importance': best_model.feature_importances_
    }).sort_values('Importance', ascending=False)
    
    print("\nFeature Importance:")
    print("="*60)
    print(feature_importance.to_string(index=False))
    
    # Plot feature importance
    plt.figure(figsize=(10, 6))
    plt.barh(feature_importance['Feature'], feature_importance['Importance'])
    plt.xlabel('Importance')
    plt.title(f'Feature Importance - {best_model_name}')
    plt.gca().invert_yaxis()
    plt.tight_layout()
    plt.show()

print("\n✅ Detailed analysis complete")
```

2. Run the cell and review the detailed metrics

### 6.9 Save the Best Model
1. Add a final cell to save the model:

```python
# Cell 8: Save the best model
import joblib
from azure.ai.ml.entities import Model
from azure.ai.ml.constants import AssetTypes

# Save model locally first
model_filename = f"diabetes_model_{best_model_name.replace(' ', '_').lower()}.pkl"
joblib.dump(best_model, model_filename)
print(f"✅ Model saved locally as: {model_filename}")

# Register model in Azure ML
try:
    model = Model(
        path=model_filename,
        type=AssetTypes.CUSTOM_MODEL,
        name="diabetes-manual-model",
        description=f"Best manual model: {best_model_name}",
        properties={
            "algorithm": best_model_name,
            "auc": f"{best_auc:.4f}",
            "framework": "scikit-learn"
        }
    )
    
    registered_model = ml_client.models.create_or_update(model)
    print(f"✅ Model registered in Azure ML")
    print(f"Model name: {registered_model.name}")
    print(f"Model version: {registered_model.version}")
    
except Exception as e:
    print(f"⚠️ Model registration failed: {str(e)}")
    print("This is expected if you don't have permissions to register models")

print("\n" + "="*60)
print("NOTEBOOK TRAINING COMPLETE")
print("="*60)
print(f"Best Model: {best_model_name}")
print(f"AUC Score: {best_auc:.4f}")
print("="*60)
```

2. Run the cell to save and register the model

---

## Step 7: Compare AutoML vs Manual Approach

### 7.1 Review AutoML Results
1. Navigate to **Authoring** > **Automated ML** in the left sidebar
2. Verify that the job has completed
3. Once the job completes, click the job.
4. Navigate to the **Models + child jobs** tab
5. Identify the best model (highest AUC weighted score)
6. Click on the best model name to view details
7. Go to the **Metrics** tab to review all performance metrics
8. Note the best model's performance metrics for later comparison

**Example Expected Results:**
- Best Algorithm: VotingEnsemble
- AUC Weighted: ~0.8444
- Accuracy: ~0.77
- Precision: ~0.76
- Recall: ~0.71

### 7.2 Review Manual Training Results
1. Navigate to **Notebooks** in the left sidebar
2. Open your notebook: `diabetes-manual-training.ipynb`
3. Review Cell 6 output (Model Performance Comparison)
4. Note your best manual model's metrics

### 7.3 Create Comparison Summary
1. In your notebook, add a new cell:

```python
# Cell 9: Final Comparison - AutoML vs Manual Training
print("="*80)
print("FINAL COMPARISON: AutoML vs Manual Training")
print("="*80)

print("\n📊 MANUAL TRAINING RESULTS (This Notebook):")
print("-"*80)
print(comparison_df.to_string(index=False))
print(f"\nBest Manual Model: {best_model_name}")
print(f"Best Manual AUC: {best_auc:.4f}")

print("\n\n🤖 AUTOML RESULTS:")
print("-"*80)
print("Go to: Automated ML > automl-diabetes-classification > Models + child jobs tab")
print("Review the best model's performance metrics")

print("\n\n💡 KEY INSIGHTS:")
print("-"*80)
print("1. AutoML Advantages:")
print("   ✅ Automatically tests multiple algorithms")
print("   ✅ Performs hyperparameter tuning")
print("   ✅ Provides model explanations")
print("   ✅ Faster time to first model")
print("   ✅ No coding required")

print("\n2. Manual Training Advantages:")
print("   ✅ Full control over data preprocessing")
print("   ✅ Custom feature engineering")
print("   ✅ Detailed exploratory data analysis")
print("   ✅ Better understanding of data and models")
print("   ✅ Custom evaluation metrics and visualizations")

print("\n3. Recommendation:")
print("   • Use AutoML for rapid prototyping and baseline models")
print("   • Use Manual approach for production models requiring customization")
print("   • Combine both: Start with AutoML, then refine manually")

print("\n" + "="*80)
```

2. Run the cell to see the final comparison

3. A copy of the final notebook can be seen in the Machine Learning folder of this repository as `diabetes-manual-training.ipynb`

---

## Step 8: Register AutoML Model

### 8.1 Register the Best AutoML Model
1. Navigate to **Authoring** > **Automated ML** in the left sidebar
2. Select the completed AutoML job: `automl-diabetes-classification`
3. Go to the **Models + child jobs** tab
4. Select the best algorithm (highest AUC weighted score)
5. In the details page, click **+ Register model**
6. Select the default Model type and click **Next**
7. Configure model settings:
   - **Model name:** `diabetes-automl-model`
   - **Description:** `Best model from AutoML classification`
   - Click **Next**
8. Click **Register**

### 8.2 View All Registered Models
1. Navigate to **Assets** > **Models** in the left sidebar
2. You should see:
   - Your AutoML model: `diabetes-automl-model`
   - Your manual model: `diabetes-manual-model`
3. Click on any model to view details

---

## Step 9: Model Deployment (Optional)

### 9.1 Deploy Best Model as Online Endpoint
1. Navigate to **Assets** > **Models** in the left sidebar
2. Select your best performing model (either AutoML or manual)
3. Click **Use this model** > **Real-time endpoint**
4. Configure the endpoint:
   - **Instance count:** `1`
   - **Virtual machine:** Standard_DS3_v2 (or a different size if you have limited quota)
   - **Endpoint:** New
   - **Endpoint name:** `diabetes-prediction-endpoint`
   - **Deployment name:** `diabetes-prediction-deployment`
5. Click **Deploy**
6. Wait for deployment (5-10 minutes)

> **Note:** Deployment creates a managed endpoint with compute resources. This will incur additional costs. Skip this step if you want to avoid charges.

### 9.2 Test the Deployed Endpoint
1. Once deployed, navigate to **Endpoints** in the left sidebar
2. Click on `diabetes-prediction-endpoint`
3. Go to the **Test** tab
4. Enter sample data in JSON format:
```json
{
  "input_data": {
    "columns": ["Pregnancies", "Glucose", "BloodPressure", "SkinThickness", "Insulin", "BMI", "DiabetesPedigreeFunction", "Age"],
    "data": [[6, 148, 72, 35, 0, 33.6, 0.627, 50]]
  }
}
```
5. Click **Test**
6. Review the prediction result
7. A sample output can be shown in the prediction-sample.jpg file in the Machine Learning folder of this repository

### 9.3 Consuming the Endpoint
1. In the endpoint details page, go to the **Consume** tab
2. View the REST endpoint URL
3. View the Authentication details (Primary & Secondary keys)
4. Review the sample code snippets for Python, C#, or REST API
5. You can use this information to integrate the model into applications or services
6. A sample output from Postman can be shown in the prediction-postman.jpg file in the Machine Learning folder of this repository

---

## Verification Checklist

**Azure Resources:**
- [ ] Resource group `rg-azure-ml` created
- [ ] Azure Machine Learning workspace created and accessible
- [ ] Compute instance created and running
- [ ] Compute cluster created for AutoML

**Dataset:**
- [ ] Dataset uploaded to Azure ML as data asset
- [ ] Dataset preview shows 768 rows and 9 columns

**AutoML Experience:**
- [ ] AutoML classification job created and submitted
- [ ] Job completed successfully (30 minutes runtime)
- [ ] Best model identified with AUC score

**Notebook Experience:**
- [ ] Notebook created: `diabetes-manual-training.ipynb`
- [ ] Libraries imported successfully
- [ ] Dataset loaded from Azure ML data asset
- [ ] EDA performed with visualizations
- [ ] Data preprocessing completed (train/test split, scaling)
- [ ] Multiple models trained (Logistic Regression, Random Forest, Gradient Boosting)
- [ ] Models compared with metrics and visualizations
- [ ] Best model identified and analyzed
- [ ] Model saved and registered (optional)

**Comparison:**
- [ ] AutoML results documented
- [ ] Manual training results documented
- [ ] Performance comparison completed
- [ ] Key insights identified

**Model Deployment (Optional):**
- [ ] Best model deployed as online endpoint
- [ ] Endpoint tested with sample data
- [ ] Consume details reviewed for integration

---

## Clean Up Resources

To avoid incurring charges, delete the resources when you're finished:

1. In the Azure Portal, navigate to **Resource groups**
2. Select `rg-azure-ml`
3. Click **Delete resource group**
4. Type the resource group name to confirm
5. Click **Delete**

---

## Summary and Key Takeaways

In this lab, you successfully:

1. ✅ Created an Azure Machine Learning workspace
2. ✅ Setup compute resources for ML workloads
3. ✅ Uploaded and registered the Diabetes dataset
4. ✅ **Automated ML Experience:**
   - Created and ran AutoML classification job
   - Tested multiple algorithms automatically
   - Reviewed model explanations and feature importance
   - Achieved AUC score of ~0.8444
5. ✅ **Notebook Experience:**
   - Performed exploratory data analysis (EDA)
   - Preprocessed data with proper train/test split
   - Trained multiple models manually (Logistic Regression, Random Forest, Gradient Boosting)
   - Evaluated models with comprehensive metrics
   - Visualized model performance with ROC curves
   - Created confusion matrix and classification reports
6. ✅ Compared AutoML vs Manual approaches
7. ✅ Registered models in Azure ML Model Registry
8. ✅ (Optional) Deployed model as online endpoint

### Key Concepts

**Azure Machine Learning Workspace:**
- Central hub for all ML activities
- Provides compute, storage, and deployment capabilities
- Supports both code-first and no-code approaches

**Automated Machine Learning (AutoML):**
- **Pros:** Fast, automated algorithm selection, hyperparameter tuning, no coding required
- **Cons:** Less control, black-box approach for beginners
- **Best for:** Quick prototyping, baseline models, non-technical users

**Manual Notebook Training:**
- **Pros:** Full control, custom preprocessing, better understanding, reproducible
- **Cons:** Requires coding skills, time-intensive, manual hyperparameter tuning
- **Best for:** Production models, research, custom requirements, learning

**Model Evaluation Metrics:**
- **Accuracy:** Overall correctness (good for balanced datasets)
- **Precision:** Of predicted positives, how many are correct (minimize false positives)
- **Recall:** Of actual positives, how many are detected (minimize false negatives)
- **F1-Score:** Harmonic mean of precision and recall
- **AUC-ROC:** Area under ROC curve (good for imbalanced datasets, threshold-independent)

---

## Lab Completion Badge

Congratulations! 🎉 You have completed the **Azure Machine Learning with Diabetes Dataset** lab.

You now have hands-on experience with:
- Creating and configuring Azure Machine Learning workspaces
- Using Automated Machine Learning for rapid model development
- Building custom ML models with Python and Jupyter notebooks
- Performing exploratory data analysis and data preprocessing
- Training and evaluating multiple classification algorithms
- Comparing different approaches to ML model development
- Understanding key ML metrics for healthcare prediction tasks
- Registering and managing ML models
- Deploying models as REST API endpoints

---

**End of Lab**
