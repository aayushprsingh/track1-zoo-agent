"""
Zoo Guide Agent — Track 1 Project
Google Cloud Gen AI Academy APAC 2026 — Cohort 1

A multi-agent AI system that helps users learn about animals using
Wikipedia as a knowledge source, deployed on Google Cloud Run.

Usage:
    from agent import root_agent  # for ADK
    from agent import health_check  # for health probes
"""

from . import agent

__version__ = "1.0.0"
__all__ = ["agent"]
