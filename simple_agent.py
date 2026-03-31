"""
Simple Zoo Q&A Agent — Track 1 Project
======================================
A simple AI agent that answers questions about zoo animals.
Following the exact codelab pattern.

This is a basic agent that:
- Uses ADK
- Uses Gemini model
- Performs question answering (about zoo animals)
- Accepts input via HTTP → returns response
"""

import os
from dotenv import load_dotenv
from google.adk import Agent

# Load environment
load_dotenv()

MODEL = os.getenv("MODEL", "gemini-2.5-flash")

# Root agent - simple question answering about zoo animals
root_agent = Agent(
    name="zoo_qa_agent",
    model=MODEL,
    description="Answers questions about zoo animals",
    instruction="""
    You are a Zoo Animal Expert. Your job is to answer questions about animals that visitors might see at a zoo.

    You have knowledge about:
    - Mammals (lions, tigers, elephants, giraffes, monkeys, zebras, etc.)
    - Birds (parrots, eagles, owls, penguins, flamingos, etc.)
    - Reptiles (snakes, turtles, lizards, crocodiles)
    - Aquatic animals (fish, sharks, dolphins, sea lions)
    - Insects and arachnids

    When a user asks about an animal, provide:
    1. A brief introduction (where it lives, what it eats)
    2. 2-3 interesting facts
    3. One "did you know" fact

    Keep answers friendly, informative, and suitable for all ages.
    """,
)

__all__ = ["root_agent"]
