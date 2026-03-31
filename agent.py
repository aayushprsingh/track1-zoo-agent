"""
Zoo Guide Agent — Track 1 Project
=================================
A multi-agent AI system built with Google ADK that helps users learn about
animals at a zoo. Combines a greeting agent, a Wikipedia research agent,
and a response formatting agent in a sequential workflow.

Architecture:
    User → Greeter (root_agent) → add_prompt_to_state tool
         → Tour Guide Workflow (SequentialAgent)
           → Comprehensive Researcher (Wikipedia tool)
           → Response Formatter
         → User gets final response

Built for: Google Cloud Gen AI Academy APAC 2026 — Cohort 1 Track 1
Deployed to: Google Cloud Run (serverless, auto-scaling)

Author: Aayush Pratap Singh
"""

import os
import logging
import functools
from typing import Optional

import google.cloud.logging
from dotenv import load_dotenv

from google.adk import Agent
from google.adk.agents import SequentialAgent
from google.adk.tools.tool_context import ToolContext
from google.adk.tools.langchain_tool import LangchainTool

from langchain_community.tools import WikipediaQueryRun
from langchain_community.utilities import WikipediaAPIWrapper

# =============================================================================
# SETUP & CONFIGURATION
# =============================================================================

# Load environment variables from .env file
load_dotenv()

# Validate required environment variables
_REQUIRED_ENV_VARS = ["PROJECT_ID", "MODEL"]
_missing = [v for v in _REQUIRED_ENV_VARS if not os.getenv(v)]
if _missing:
    logging.warning(f"Missing env vars: {_missing} — using defaults")

# Cloud Logging setup (works on Cloud Run)
try:
    cloud_logging_client = google.cloud.logging.Client()
    cloud_logging_client.setup_logging()
except Exception as e:
    # Fall back to basic config if Cloud Logging fails (local dev)
    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s | %(levelname)-8s | %(name)s | %(message)s",
        datefmt="%Y-%m-%d %H:%M:%S",
    )

logger = logging.getLogger(__name__)

# Configuration from environment
MODEL_NAME = "gemini-2.5-flash"  # Hardcoded to ensure deployment uses correct model
WIKIPEDIA_LANG = os.getenv("WIKIPEDIA_LANG", "en")
LOG_LEVEL = os.getenv("LOG_LEVEL", "INFO").upper()

# Set log level
if LOG_LEVEL in ("DEBUG", "INFO", "WARNING", "ERROR"):
    logging.getLogger().setLevel(getattr(logging, LOG_LEVEL))

logger.info(f"Zoo Guide Agent starting — Model: {MODEL_NAME}, Wikipedia lang: {WIKIPEDIA_LANG}")


# =============================================================================
# TOOLS
# =============================================================================

def _handle_tool_errors(func):
    """Decorator to catch and log tool errors gracefully."""
    @functools.wraps(func)
    def wrapper(*args, **kwargs):
        try:
            return func(*args, **kwargs)
        except Exception as e:
            logger.error(f"Tool error in {func.__name__}: {e}")
            return {"status": "error", "message": str(e)}
    return wrapper


@_handle_tool_errors
def add_prompt_to_state(
    tool_context: ToolContext,
    prompt: str,
) -> dict:
    """
    Saves the user's zoo-related question to the agent's shared state.

    This tool acts as a conversation starter — it captures what the user
    wants to know and stores it so the downstream agents can access it.

    Args:
        tool_context: ADK's ToolContext — provides access to agent state
        prompt: The user's question about an animal or zoo exhibit

    Returns:
        dict: Status indicator ("success" or "error")
    """
    if not prompt or not isinstance(prompt, str):
        logger.warning(f"Invalid prompt received: {repr(prompt)}")
        return {"status": "error", "message": "Prompt must be a non-empty string"}

    # Limit prompt length to prevent token overflow
    prompt = prompt.strip()[:2000]

    tool_context.state["PROMPT"] = prompt
    logger.info(f"[STATE] User prompt saved: '{prompt[:100]}...'")

    return {"status": "success"}


@_handle_tool_errors
def _build_wikipedia_tool() -> LangchainTool:
    """
    Build the Wikipedia tool with configurable language and error handling.

    Returns:
        LangchainTool: Configured Wikipedia tool wrapped for ADK

    Raises:
        Exception: If Wikipedia tool initialization fails
    """
    api_wrapper = WikipediaAPIWrapper(lang=WIKIPEDIA_LANG)
    raw_tool = WikipediaQueryRun(api_wrapper=api_wrapper)
    return LangchainTool(tool=raw_tool)


# Build Wikipedia tool — fail gracefully if API is unavailable
try:
    wikipedia_tool = _build_wikipedia_tool()
    logger.info("Wikipedia tool initialized successfully")
except Exception as e:
    logger.error(f"Failed to initialize Wikipedia tool: {e}")
    wikipedia_tool = None


# =============================================================================
# SPECIALIST AGENTS
# =============================================================================

# --- Agent 1: Comprehensive Researcher ---
# The "brain" — uses Wikipedia to gather facts about the requested animal/topic

comprehensive_researcher = Agent(
    name="comprehensive_researcher",
    model=MODEL_NAME,
    description=(
        "Primary researcher that accesses Wikipedia to find detailed "
        "information about animals, habitats, diet, lifespan, and conservation."
    ),
    instruction="""
    You are an expert zoology research assistant. Your task is to thoroughly
    answer the user's question about animals using the Wikipedia tool.

    Guidelines:
    1. Analyze the user's PROMPT carefully
    2. Use the Wikipedia tool to search for relevant, accurate information
    3. If the question is broad (e.g., "tell me about elephants"), search for
       the specific animal name
    4. If the question is specific (e.g., "what do penguins eat?"), search for
       that exact topic
    5. Return all the useful facts you find — name, scientific details,
       habitat, diet, behavior, conservation status, fun facts

    Important: You MUST use the Wikipedia tool for every query.
    Do not make up facts. If Wikipedia doesn't have the answer, say so.

    PROMPT:
    {PROMPT}
    """,
    tools=[wikipedia_tool] if wikipedia_tool else [],
    output_key="research_data",
)


# --- Agent 2: Response Formatter ---
# The "voice" — transforms raw research into friendly, readable answers

response_formatter = Agent(
    name="response_formatter",
    model=MODEL_NAME,
    description="Converts raw research data into a friendly, engaging zoo guide response.",
    instruction="""
    You are the friendly, enthusiastic voice of the Zoo Tour Guide. Your job
    is to take raw research data and present it as an engaging, easy-to-read
    response that a zoo visitor would enjoy.

    Your style:
    - Warm and conversational, like a knowledgeable friend
    - Use short paragraphs and bullet points for readability
    - Include interesting "did you know?" style facts
    - Never be clinical or robotic
    - If information is missing, acknowledge it gracefully

    Structure your response:
    1. Direct answer to the question (1-2 sentences)
    2. Key facts (as bullet points or short paragraphs)
    3. One interesting "fun fact" if available
    4. Offer to answer a follow-up question

    RESEARCH_DATA:
    {research_data}
    """,
)


# =============================================================================
# WORKFLOW AGENT
# =============================================================================

# SequentialAgent runs sub-agents in order, passing state between them
# Step 1: comprehensive_researcher (saves output to "research_data" key)
# Step 2: response_formatter (reads "research_data" from state)

tour_guide_workflow = SequentialAgent(
    name="tour_guide_workflow",
    description="Two-step workflow: research an animal, then format a friendly answer.",
    sub_agents=[
        comprehensive_researcher,   # Step 1: Gather facts from Wikipedia
        response_formatter,         # Step 2: Present in friendly format
    ],
)


# =============================================================================
# ROOT AGENT (Entry Point)
# =============================================================================

root_agent = Agent(
    name="greeter",
    model=MODEL_NAME,
    description=(
        "Main entry point for the Zoo Tour Guide. Greets visitors and "
        "guides them through the animal research experience."
    ),
    instruction="""
    You are the welcoming Zoo Tour Guide — friendly, knowledgeable, and enthusiastic
    about animals!

    Your role:
    1. When a conversation starts, greet the user warmly and invite them to
       ask you about any animal at the zoo
    2. When the user asks a question, use the 'add_prompt_to_state' tool
       to save their exact question to the conversation state
    3. After saving the prompt, immediately hand off to the 'tour_guide_workflow'
       agent to research and answer the question

    Example greetings:
    - "Welcome to the Zoo! I'm your guide. Ask me about any animal — from lions and elephants to penguins and eagles!"
    - "Hi there! Which animal would you like to learn about today? I can tell you about habitats, diet, fun facts, and more!"

    IMPORTANT: Always use add_prompt_to_state first, then transfer to tour_guide_workflow.
    Never skip the add_prompt_to_state step — it's how the workflow knows what to research.
    """,
    tools=[add_prompt_to_state],
    sub_agents=[tour_guide_workflow],
)


# =============================================================================
# HEALTH CHECK (for Cloud Run liveness probes)
# =============================================================================

def health_check() -> dict:
    """
    Simple health check for Cloud Run.

    Returns a dict indicating service health status.
    Cloud Run calls this on /health endpoint automatically.

    Returns:
        dict: Health status with component states
    """
    return {
        "status": "healthy",
        "service": "zoo-tour-guide-agent",
        "model": MODEL_NAME,
        "wikipedia_tool": "initialized" if wikipedia_tool else "unavailable",
        "version": "1.0.0",
    }


# =============================================================================
# MODULE EXPORTS
# =============================================================================

__all__ = [
    "root_agent",
    "health_check",
    "add_prompt_to_state",
    "comprehensive_researcher",
    "response_formatter",
    "tour_guide_workflow",
]
