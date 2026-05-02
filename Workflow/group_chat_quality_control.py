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

# Build group chat with agent-based orchestrator
workflow = GroupChatBuilder(
   participants=[explainer, critic, refiner],
   # Terminate when reaching message limit (allows for multiple refinement cycles)
   termination_condition=lambda messages: sum(1 for msg in messages if msg.role == "assistant") >= 15,
   intermediate_outputs=True,  # Enable intermediate outputs to see all agent messages
   orchestrator_agent=orchestrator,
).build()

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


