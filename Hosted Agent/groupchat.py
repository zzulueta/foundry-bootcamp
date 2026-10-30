# Copyright (c) Microsoft. All rights reserved.

"""Fit Score Review Panel - a group chat orchestration.

A panel of agents debates and refines a resume-to-job fit score.
An orchestrator agent picks the next speaker and ends the chat on consensus.
"""

import logging
import os

from agent_framework import Agent
from agent_framework.foundry import FoundryChatClient
from agent_framework.orchestrations import GroupChatBuilder
from agent_framework_foundry_hosting import ResponsesHostServer
from azure.identity import DefaultAzureCredential
from dotenv import load_dotenv

logger = logging.getLogger("fit-score-review-panel")
logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(name)s - %(levelname)s - %(message)s")

load_dotenv(override=True)

MAX_PANEL_ROUNDS = 8

MATCHER_INSTRUCTIONS = """\
You are the Matcher on a Fit Score Review Panel.
The user message contains a resume and a job description.

Formatting: Begin every response with this exact standalone line:
********** **MATCHER** **********
The name must be bold. Keep the ten literal asterisks on each side, include
the spaces shown, and put the response body on the following line.

On your FIRST turn, produce a concise fit report with:
- Fit score out of 100 and a compact breakdown: Required Skills 40,
  Experience 25, Certifications 15, Preferred Skills 10, Domain Alignment 10.
- Up to 3 strongest matches and up to 5 most important gaps.
- Partial matches only when relevant, clearly separate from missing skills.
- One short experience/certification note only if it affects the score.

On later turns, address only the Skeptic's and Advocate's specific feedback.
Revise the score/report only when their evidence warrants it, and briefly list
what changed. Do not repeat unchanged sections.

Keep the entire response under 200 words. Use compact bullets, avoid lengthy
explanations, and cite resume/JD evidence briefly. Never invent skills or
experience.
"""

SKEPTIC_INSTRUCTIONS = """\
You are the Skeptic and Bias Checker on a Fit Score Review Panel.
Review the Matcher's latest fit report.

Formatting: Begin every response with this exact standalone line:
********** **SKEPTIC** **********
The name must be bold. Keep the ten literal asterisks on each side, include
the spaces shown, and put the response body on the following line.

- Challenge claims not backed by explicit resume evidence.
- Flag inflated "partial matches" and overstated experience (e.g. years claimed vs shown).
- Flag potential bias: penalizing career gaps, non-traditional titles, education pedigree,
  or anything unrelated to the JD requirements.
- Suggest concrete score adjustments (e.g. "Experience 20 -> 16 because ...").

Be concise: bullet points only. If you have no further objections, say "No objections."
"""

ADVOCATE_INSTRUCTIONS = """\
You are the Candidate Advocate on a Fit Score Review Panel.
Review the Matcher's latest fit report.

Formatting: Begin every response with this exact standalone line:
********** **ADVOCATE** **********
The name must be bold. Keep the ten literal asterisks on each side, include
the spaces shown, and put the response body on the following line.

- Identify transferable skills the Matcher missed or undervalued
  (e.g. AWS -> Azure, Kubernetes -> container orchestration, team lead -> stakeholder management).
- Point to specific resume evidence for every argument.
- Do not exaggerate; argue only what the resume supports.
- Suggest concrete score adjustments.

Be concise: bullet points only. If you have no further points, say "No further points."
"""

HIRING_MANAGER_INSTRUCTIONS = """\
You are the Hiring Manager persona on a Fit Score Review Panel.
You evaluate fit; you do NOT make a hire/no-hire decision.

Formatting: Begin every response with this exact standalone line:
********** **HIRING MANAGER** **********
The name must be bold. Keep the ten literal asterisks on each side, include
the spaces shown, and put the response body on the following line.

- Weigh the Skeptic's and Advocate's arguments against what the role truly needs.
- Separate true must-haves from nice-to-haves in the JD.
- When the panel has converged, output:
  "FINAL FIT SCORE: <score>/100" followed by a 2-3 sentence rationale and
  the final Missing Skills list (this feeds upskilling roadmap planning).
"""

ORCHESTRATOR_INSTRUCTIONS = """\
You moderate a Fit Score Review Panel that evaluates how well a resume matches a job description.

Participants:
- Matcher: produces and revises the fit report.
- Skeptic: challenges weak evidence and flags bias.
- Advocate: surfaces missed transferable skills.
- HiringManager: weighs arguments and declares the final fit score.

Guidelines:
- Always start with Matcher.
- Require every participant response to begin with the exact standalone format
  specified in that participant's instructions: ten literal asterisks, the
  bold uppercase participant name, then ten literal asterisks. Put the response
  body on the next line.
- Require both Skeptic and Advocate to provide at least one substantive response
  reviewing the report before the conversation can terminate.
- Do not count an empty response as a contribution; if either response is empty,
  select that participant again.
- Send the conversation back to Matcher to revise when either suggested score changes.
- Call HiringManager once Skeptic and Advocate have no further material objections.
- Terminate only after HiringManager has stated "FINAL FIT SCORE".
- If the input lacks a resume or a job description, terminate immediately and ask the user for it.
"""


def main():
    client = FoundryChatClient(
        project_endpoint=os.environ["FOUNDRY_PROJECT_ENDPOINT"],
        model=os.environ["AZURE_AI_MODEL_DEPLOYMENT_NAME"],
        credential=DefaultAzureCredential(),
    )

    matcher = Agent(
        client=client,
        name="Matcher",
        description="Produces and revises the evidence-based resume-to-JD fit report.",
        instructions=MATCHER_INSTRUCTIONS,
    )
    skeptic = Agent(
        client=client,
        name="Skeptic",
        description="Challenges unsupported claims and flags bias in the fit report.",
        instructions=SKEPTIC_INSTRUCTIONS,
    )
    advocate = Agent(
        client=client,
        name="Advocate",
        description="Surfaces transferable skills the Matcher missed or undervalued.",
        instructions=ADVOCATE_INSTRUCTIONS,
    )
    hiring_manager = Agent(
        client=client,
        name="HiringManager",
        description="Weighs the panel's arguments and declares the final fit score.",
        instructions=HIRING_MANAGER_INSTRUCTIONS,
    )

    orchestrator_agent = Agent(
        client=client,
        name="Orchestrator",
        description="Moderates the Fit Score Review Panel by selecting the next speaker.",
        instructions=ORCHESTRATOR_INSTRUCTIONS,
    )

    workflow_agent = (
        GroupChatBuilder(
            name="FitScoreReviewPanel",
            participants=[matcher, skeptic, advocate, hiring_manager],
            orchestrator_agent=orchestrator_agent,
            # Hard stop in case the orchestrator never reaches consensus
            max_rounds=MAX_PANEL_ROUNDS,
            intermediate_output_from=[matcher, skeptic, advocate, hiring_manager],
        )
        .build()
        .as_agent()
    )

    logger.info(
        "Group chat built: Matcher, Skeptic, Advocate, HiringManager (orchestrator-selected, max %d rounds)",
        MAX_PANEL_ROUNDS,
    )

    server = ResponsesHostServer(workflow_agent)
    server.run()


if __name__ == "__main__":
    main()
