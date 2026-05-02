import os
from dotenv import load_dotenv

# Add references
from azure.identity import AzureCliCredential
from azure.ai.projects import AIProjectClient
from azure.ai.projects.models import IndexType

load_dotenv()
endpoint = os.environ["PROJECT_ENDPOINT"]

# Connect to the AI Project client
with (
   AzureCliCredential() as credential,
   AIProjectClient(endpoint=endpoint, credential=credential) as project_client,
   project_client.get_openai_client() as openai_client,
):

    # Specify the workflow
    workflow = {
       "name": "ContosoPay-Customer-Support-Triage",
       "version": "2",
    }
    
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
 
    # Clean up resources
    openai_client.conversations.delete(conversation_id=conversation.id)
    print("\nConversation deleted")

