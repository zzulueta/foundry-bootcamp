# Add agent-framework-orchestrations in dependencies of pyproject.toml or requirements.txt

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

On your FIRST turn, produce an evidence-based fit report:
1) Fit Score (with breakdown math)
   - Required Skills 40
   - Experience 25
   - Certifications 15
   - Preferred Skills 10
   - Domain Alignment 10
2) Matched Skills
3) Missing Skills
4) Partially Matched
5) Experience Alignment
6) Certification Gaps

On LATER turns, respond to the panel's feedback:
- Accept or rebut each point with evidence from the resume/JD.
- Output a REVISED fit report in the same format, plus a short "Changes" list
  explaining every score adjustment.

Rules: evidence only, never invent skills or experience, keep partial vs missing separate.
"""

SKEPTIC_INSTRUCTIONS = """\
You are the Skeptic and Bias Checker on a Fit Score Review Panel.
Review the Matcher's latest fit report.

- Challenge claims not backed by explicit resume evidence.
- Flag inflated "partial matches" and overstated experience (e.g. years claimed vs shown).
- Flag potential bias: penalizing career gaps, non-traditional titles, education pedigree,
  or anything unrelated to the JD requirements.
- Suggest concrete score adjustments (e.g. "Experience 20 -> 16 because ...").

Be concise: bullet points only. If you have no further objections, say "Skeptic: no objections."
"""

ADVOCATE_INSTRUCTIONS = """\
You are the Candidate Advocate on a Fit Score Review Panel.
Review the Matcher's latest fit report.

- Identify transferable skills the Matcher missed or undervalued
  (e.g. AWS -> Azure, Kubernetes -> container orchestration, team lead -> stakeholder management).
- Point to specific resume evidence for every argument.
- Do not exaggerate; argue only what the resume supports.
- Suggest concrete score adjustments.

Be concise: bullet points only. If you have no further points, say "Advocate: no further points."
"""

HIRING_MANAGER_INSTRUCTIONS = """\
You are the Hiring Manager persona on a Fit Score Review Panel.
You evaluate fit; you do NOT make a hire/no-hire decision.

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
- Then let Skeptic and Advocate each review the report.
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
