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
