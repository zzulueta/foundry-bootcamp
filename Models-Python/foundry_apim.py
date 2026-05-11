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