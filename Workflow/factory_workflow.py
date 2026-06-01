"""
Factory Assembly Line Workflow
==============================
Demonstrates Executors, Edges, and Workflows from the Agent Framework docs.

WORKFLOW OVERVIEW:
This script simulates a factory assembly line where products move through inspection,
painting, and packaging stations. The workflow combines AI agents (for decision-making)
with regular executors (for deterministic operations).

WORKFLOW GRAPH:
  [inspect_station]     (AgentExecutor — AI quality control inspector)
        |
        ├── defective ──→ [scrap_station]        → yields "SCRAPPED: {reason}"
        │
        └── good     ──→ [to_paint_request]      (bridge 1: AgentExecutorResponse → str)
                               │
                         [paint_station]          (Executor — applies paint/finish)
                               │
                         [to_package_request]     (bridge 2: str → AgentExecutorRequest)
                               │
                         [package_station]        (AgentExecutor — AI packaging specialist)
                               │
                         [package_result]         → yields "METHOD: {method}. REASON: {reason}"

KEY CONCEPTS:

1. Executors: Nodes in the workflow that perform work. Two types:
   - AgentExecutor: Wraps an AI agent for intelligent decision-making
   - Regular Executor: Performs deterministic data transformation

2. Edges: Connect executors to define flow. Can have conditions for routing.
   - Unconditional edges: Always forward messages to the next node
   - Conditional edges: Use predicates to decide which path to take

3. Bridges: Translation nodes between AI agents and regular executors.
   - AgentExecutor inputs/outputs use AgentExecutorRequest/Response
   - Regular executors use plain Python types (str, int, dict, etc.)
   - Bridges convert between these two type systems

4. WorkflowContext: Provided to each executor, allows:
   - send_message(): Forward to the next executor in the graph
   - yield_output(): Emit final results (terminal nodes only)

5. Message Flow: Messages flow through the graph following edges until they reach
   terminal nodes (nodes that only call yield_output, not send_message).
"""

import asyncio
import os
from typing import Any

from dotenv import load_dotenv
from pydantic import BaseModel
from typing_extensions import Never  # Type hint: marks a terminal node (never calls send_message)

from agent_framework import (
    Agent,                  # AI agent class - defines behavior, instructions, and model
    AgentExecutor,          # Wraps an AI agent as a workflow node that can be connected via edges
    AgentExecutorRequest,   # Input message type for AgentExecutor (wraps user messages)
    AgentExecutorResponse,  # Output message type from AgentExecutor (wraps AI responses)
    Executor,               # Base class for creating class-based executor nodes
    Message,                # Message object containing role and contents
    WorkflowBuilder,        # Builder pattern for constructing workflow graphs from executors + edges
    WorkflowContext,        # Runtime context provided to each executor with send_message/yield_output
    executor,               # Decorator: turns an async function into an executor node
    handler,                # Decorator: marks a method as the message handler in an Executor class
)
from agent_framework.foundry import FoundryChatClient  # Azure AI Foundry chat client
from azure.identity import AzureCliCredential  # Azure CLI authentication

# Load environment variables from .env file (PROJECT_ENDPOINT, MODEL_DEPLOYMENT_NAME)
load_dotenv()


# ─── Data Model ───────────────────────────────────────────────────────────────
# Pydantic models define the structured data format that AI agents must return.
# Using structured output ensures reliable parsing and type safety.

class InspectionResult(BaseModel):
    """
    Structured JSON output from the AI quality control inspector agent.
    
    The 'quality' field drives conditional edge routing:
    - "good" → product continues to paint station
    - "defective" → product goes to scrap station
    
    Fields:
        quality: Must be exactly "good" or "defective" (controls workflow routing)
        reason: Explanation for the quality assessment
        product: Name or description of the inspected product
    """
    quality: str   # "good" or "defective" — determines which conditional edge fires
    reason: str
    product: str


class PackagingResult(BaseModel):
    """
    Structured JSON output from the AI packaging specialist agent.
    
    The agent analyzes product characteristics (size, fragility) to determine
    the optimal packaging method.
    
    Fields:
        packaging_method: Description of packaging approach (e.g., "bubble wrap in small box")
        reasoning: Explanation of why this method suits the product
    """
    packaging_method: str  # e.g. "bubble wrap in small box", "pallet wrap"
    reasoning: str


# ─── Condition Functions (Edge routing predicates) ────────────────────────────
# Condition functions are predicates that determine whether a message should
# flow along a particular edge. They enable branching logic in the workflow.

def get_condition(expected_quality: str):
    """
    Factory function that creates an edge condition predicate.
    
    Returns a function that checks if the inspection result's quality matches
    the expected value. This enables conditional routing based on AI decisions.
    
    Args:
        expected_quality: The quality value to match ("good" or "defective")
        
    Returns:
        A predicate function that returns True when quality matches, False otherwise
        
    Usage in workflow:
        .add_edge(inspect_agent, scrap_station, condition=get_condition("defective"))
        .add_edge(inspect_agent, paint_path, condition=get_condition("good"))
    """
    def condition(message: Any) -> bool:
        """
        Edge predicate that evaluates at runtime for each message.
        
        Args:
            message: The message flowing through the workflow (AgentExecutorResponse)
            
        Returns:
            True if the message should flow along this edge, False otherwise
        """
        # Allow non-AgentExecutorResponse messages to pass through to avoid dead-ends
        if not isinstance(message, AgentExecutorResponse):
            return True
        
        try:
            # Parse the AI agent's JSON response into our structured model
            result = InspectionResult.model_validate_json(message.agent_response.text)
            # Check if quality matches what this edge expects
            return result.quality == expected_quality
        except Exception:
            # If parsing fails, block this edge (returns False)
            # This prevents malformed responses from progressing
            return False
    
    return condition


# ─── Executors ────────────────────────────────────────────────────────────────
# Executors are the "nodes" in the workflow graph that perform work.
# Each executor receives a message, processes it, and either:
#   1. Forwards to the next executor via ctx.send_message()
#   2. Emits a final output via ctx.yield_output() (terminal nodes only)
#
# WorkflowContext type parameters control what an executor can do:
#   WorkflowContext[SendType]          — can send messages of type SendType to next node
#   WorkflowContext[Never, OutputType] — terminal node, can only yield_output (no send_message)
#   WorkflowContext[SendType, OutputType] — can both send and yield (rare, usually one or the other)

@executor(id="scrap_station")
async def scrap_station(
    response: AgentExecutorResponse,  # Input: AI inspector's response about defective product
    ctx: WorkflowContext[Never, str]  # Terminal: can only yield_output (no downstream nodes)
) -> None:
    """
    Terminal node for defective products — scraps them and emits final output.
    
    This executor is reached via the "defective" conditional edge from inspect_station.
    It parses the inspection result, logs the decision, and yields a final output string.
    
    Args:
        response: The AI inspector's structured response (contains quality, reason, product)
        ctx: Workflow context with Never for send (terminal node) and str for output type
        
    Returns:
        None (side effect: calls ctx.yield_output with final scrap message)
        
    Type annotation WorkflowContext[Never, str] means:
        - Never: This node CANNOT call ctx.send_message() (it's a dead-end/terminal)
        - str: This node emits final outputs as strings via ctx.yield_output()
    """
    # Parse the AI agent's JSON response into our InspectionResult model
    result = InspectionResult.model_validate_json(response.agent_response.text)
    
    # Log the defective decision (visible in console output)
    print(f"  [inspect_station] DEFECTIVE — {result.reason}")
    print(f"  [scrap_station]   Scrapping '{result.product}'...")
    
    # Emit the final workflow output for this path
    # yield_output sends results to the workflow caller (visible in events.get_outputs())
    await ctx.yield_output(
        f"[SCRAP STATION] Scrapped '{result.product}'. Reason: {result.reason}"
    )


@executor(id="to_paint_request")
async def to_paint_request(
    response: AgentExecutorResponse,  # Input: AI inspector's response about good product
    ctx: WorkflowContext[str]         # Can send str to next node (PaintStation)
) -> None:
    """
    Bridge node: Converts AgentExecutorResponse → str for PaintStation.
    
    This is a "bridge" because:
    - Input: AgentExecutorResponse (from AI agent)
    - Output: str (for regular Executor)
    
    AI agents output AgentExecutorResponse, but regular executors expect plain types.
    This bridge extracts the product name from the AI response and forwards it as a string.
    
    Args:
        response: The AI inspector's response indicating a good product
        ctx: Workflow context that can send str messages downstream
        
    Returns:
        None (side effect: calls ctx.send_message with product name as string)
        
    Type annotation WorkflowContext[str] means:
        - str: This node sends string messages via ctx.send_message()
        - No second type param: This node doesn't yield final outputs
    """
    # Parse the inspection result to extract product information
    result = InspectionResult.model_validate_json(response.agent_response.text)
    
    # Log the decision
    print(f"  [inspect_station] GOOD — {result.reason}")
    print(f"  [to_paint_request] Forwarding '{result.product}' to paint station...")
    
    # Forward just the product name as a string to the next executor
    # send_message delivers this to the next node in the graph (PaintStation)
    await ctx.send_message(result.product)


class PaintStation(Executor):
    """
    Regular Executor (not an AI agent) that applies paint/finish to products.
    
    This is a class-based executor rather than a function-based one.
    The @handler decorator marks which method receives incoming messages.
    
    Class-based executors are useful when you need:
    - State across multiple invocations
    - Multiple helper methods
    - Complex initialization logic
    
    For simple transformations, function-based executors (like scrap_station) are cleaner.
    """

    @handler
    async def paint(
        self,
        product: str,                  # Input: plain string (product name)
        ctx: WorkflowContext[str]      # Can send str to next node
    ) -> None:
        """
        Applies paint/finish to the product and forwards it downstream.
        
        This is a deterministic operation (no AI) that:
        1. Receives a product name as a string
        2. Appends paint status to the name
        3. Forwards the modified string to the next node
        
        Args:
            product: Name of the product to paint (plain string)
            ctx: Workflow context for sending messages downstream
            
        Returns:
            None (side effect: calls ctx.send_message with painted product)
        """
        # Simulate painting operation (just appends text in this example)
        print(f"  [paint_station]    Applying paint/finish to '{product}'...")
        
        # Forward the painted product to the next executor (to_package_request bridge)
        await ctx.send_message(f"{product} [painted & finished]")


@executor(id="to_package_request")
async def to_package_request(
    product: str,                              # Input: plain string (painted product)
    ctx: WorkflowContext[AgentExecutorRequest] # Output: AgentExecutorRequest for AI agent
) -> None:
    """
    Bridge node: Converts str → AgentExecutorRequest for PackageStation AI agent.
    
    This is a "bridge" because:
    - Input: str (from regular Executor)
    - Output: AgentExecutorRequest (for AI agent)
    
    Regular executors output plain types, but AI agents expect AgentExecutorRequest.
    This bridge constructs a proper request with a prompt for the AI packaging agent.
    
    Args:
        product: Description of the painted product (plain string)
        ctx: Workflow context that can send AgentExecutorRequest messages
        
    Returns:
        None (side effect: calls ctx.send_message with constructed AgentExecutorRequest)
        
    Type annotation WorkflowContext[AgentExecutorRequest] means:
        - AgentExecutorRequest: This node sends AI agent requests via ctx.send_message()
        - These requests will be processed by the next AI agent in the workflow
    """
    print(f"  [to_package_request] Sending '{product}' to packaging agent...")
    
    # Construct a prompt for the AI packaging agent
    # The prompt instructs the agent what to do and what format to respond in
    prompt = (
        f"Product to package: {product}\n\n"
        "Determine the best packaging method for this product based on its size and fragility.\n"
        "Reply with ONLY this JSON structure, no other fields:\n"
        '{"packaging_method": "<method>", "reasoning": "<why this method suits the product>"}'
    )
    
    # Wrap the prompt in a Message object (mimics a user message)
    # should_respond=True tells the agent to generate a response
    request = AgentExecutorRequest(
        messages=[Message(role="user", contents=[prompt])],
        should_respond=True,
    )
    
    # Forward the request to the AI packaging agent
    await ctx.send_message(request)


@executor(id="package_result")
async def package_result(
    response: AgentExecutorResponse,  # Input: AI packaging agent's response
    ctx: WorkflowContext[Never, str]  # Terminal: can only yield_output, no downstream nodes
) -> None:
    """
    Terminal node: Parses packaging agent's response and emits final workflow output.
    
    This executor completes the "good product" path. It extracts the packaging decision
    from the AI agent's response and yields it as the final output.
    
    Args:
        response: The AI packaging agent's structured response (contains method + reasoning)
        ctx: Workflow context with Never for send (terminal) and str for output type
        
    Returns:
        None (side effect: calls ctx.yield_output with final packaging message)
        
    Type annotation WorkflowContext[Never, str] means:
        - Never: This node CANNOT call ctx.send_message() (it's terminal)
        - str: This node emits final outputs as strings via ctx.yield_output()
    """
    # Parse the AI agent's JSON response into our PackagingResult model
    result = PackagingResult.model_validate_json(response.agent_response.text)
    
    # Log the packaging decision
    print(f"  [package_station]  Packaging method chosen: {result.packaging_method}")
    
    # Emit the final workflow output for this path
    await ctx.yield_output(
        f"[PACKAGE STATION] Method: {result.packaging_method}. Reason: {result.reasoning}"
    )


# ─── Main ─────────────────────────────────────────────────────────────────────

async def main():
    """
    Main entry point: Sets up the workflow and processes products through the assembly line.
    
    This function:
    1. Loads credentials and connects to Azure AI Foundry
    2. Creates AI agents (inspect and package) with specific instructions
    3. Builds the workflow graph by connecting executors with edges
    4. Processes test products through the workflow
    5. Collects and displays final outputs
    
    Workflow Construction:
    - start_executor: The first node that receives initial messages (inspect_agent)
    - output_executors: Nodes that emit final results (scrap_station, package_result)
    - Edges: Connections between nodes, can be conditional or unconditional
    
    Message Flow Example (good product):
    1. inspect_agent (AI) → AgentExecutorResponse
    2. to_paint_request (bridge) → str
    3. paint (regular) → str
    4. to_package_request (bridge) → AgentExecutorRequest
    5. package_agent (AI) → AgentExecutorResponse
    6. package_result (terminal) → yield_output(str)
    """
    # ─── Load Configuration ───────────────────────────────────────────────────
    # These environment variables should be in a .env file:
    # PROJECT_ENDPOINT="https://your-project.region.api.azureml.ms"
    # MODEL_DEPLOYMENT_NAME="your-deployment-name"
    project_endpoint = os.getenv("PROJECT_ENDPOINT")
    model_deployment = os.getenv("MODEL_DEPLOYMENT_NAME")

    # ─── Authenticate with Azure ──────────────────────────────────────────────
    # AzureCliCredential uses your local Azure CLI login (az login)
    # This avoids hardcoding credentials in the code
    credential = AzureCliCredential()
    
    # Create the chat client that will power our AI agents
    client = FoundryChatClient(
        project_endpoint=project_endpoint,
        model=model_deployment,
        credential=credential,
    )
    
    # ─── Create AI Agents ─────────────────────────────────────────────────────
    
    # AI Agent #1: Quality Control Inspector
    # Analyzes product descriptions and classifies them as good or defective
    # The instructions are critical - they define the agent's role and output format
    inspect_agent = AgentExecutor(
        Agent(
            client=client,  # Uses the Azure AI Foundry connection
            name="InspectAgent",
            instructions=(
                "You are a factory quality control inspector. "
                "Inspect the product description and classify it. "
                "Return ONLY valid JSON with exactly these three fields: "
                "quality (string: 'good' or 'defective'), "
                "reason (string: brief explanation), "
                "product (string: the product name or description)."
            ),
        ),
        id="inspect_station",  # Unique identifier for this node in the workflow graph
    )

    # Regular Executor: Paint Station
    # Instantiate the class-based executor (defined above)
    # This is NOT an AI agent, just deterministic string manipulation
    paint = PaintStation(id="paint_station")

    # AI Agent #2: Packaging Specialist
    # Determines optimal packaging method based on product characteristics
    # Like the inspector, it must return structured JSON
    package_agent = AgentExecutor(
        Agent(
            client=client,  # Shares the same Azure AI connection
            name="PackageAgent",
            instructions=(
                "You are a packaging specialist at a factory. "
                "Given a product description, determine the best packaging method based on its size and fragility. "
                "Return ONLY valid JSON with exactly two fields: "
                "packaging_method (string: e.g. 'small box with bubble wrap'), "
                "reasoning (string: brief explanation of why this method suits the product)."
            ),
        ),
        id="package_station",
    )

    # ─── Build Workflow Graph ─────────────────────────────────────────────────
    # The WorkflowBuilder constructs a directed graph where:
    # - Nodes = Executors (both AI agents and regular functions/classes)
    # - Edges = Connections that route messages between nodes
    # - Conditions = Predicates that determine which edge to follow
    
    workflow = (
        WorkflowBuilder(
            start_executor=inspect_agent,              # Entry point: receives initial messages
            output_executors=[scrap_station, package_result]  # Terminal nodes: emit final results
        )
        # Conditional edge: If inspection finds defect, go to scrap station
        .add_edge(inspect_agent, scrap_station, condition=get_condition("defective"))
        
        # Conditional edge: If inspection passes, go to paint bridge
        .add_edge(inspect_agent, to_paint_request, condition=get_condition("good"))
        
        # Unconditional edges: Always forward to the next node
        .add_edge(to_paint_request, paint)              # Bridge → Paint
        .add_edge(paint, to_package_request)            # Paint → Bridge
        .add_edge(to_package_request, package_agent)    # Bridge → AI Packaging Agent
        .add_edge(package_agent, package_result)        # AI Agent → Terminal
        
        .build()  # Constructs the final workflow graph
    )

    # ─── Test Products ────────────────────────────────────────────────────────
    # Define test cases that will flow through the workflow
    # Each product will trigger different paths based on AI inspection results
    products = [
        "Cracked ceramic mug with visible fracture lines along the base",  # Should → scrap
        "Brand new stainless steel water bottle, no scratches or dents",  # Should → package
        "Ceramic plates with no visible damages.",                         # Should → package
    ]

    # ─── Process Each Product ─────────────────────────────────────────────────
    for product in products:
        print(f"\n{'=' * 60}")
        print(f"  Inspecting: {product}")
        print(f"{'=' * 60}")

        # Construct the initial message for the workflow
        # This is what the inspect_agent will receive first
        request = AgentExecutorRequest(
            messages=[Message(role="user", contents=[product])],
            should_respond=True,  # Tells the agent to generate a response
        )

        # Run the workflow with this product
        # workflow.run() returns an event stream that we await
        # The workflow processes the message through the graph until reaching terminal nodes
        events = await workflow.run(request)
        
        # Collect final outputs from terminal nodes (scrap_station or package_result)
        # get_outputs() returns all messages that were yielded via ctx.yield_output()
        for output in events.get_outputs():
            print(f"  Result: {output}")


# ─── Entry Point ──────────────────────────────────────────────────────────────
# asyncio.run() is the entry point for async programs
# It creates an event loop, runs main(), and cleans up when done
asyncio.run(main())
