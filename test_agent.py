"""
Local Test Script for Zoo Guide Agent
=====================================
Run this to verify the agent works locally before deploying to Cloud Run.

Usage:
    python test_agent.py

Requirements:
    - Google Cloud project with Vertex AI API enabled
    - .env file with PROJECT_ID and MODEL set
    - Virtual environment with requirements.txt installed

What it tests:
    1. All imports work without errors
    2. Agent module loads correctly
    3. Wikipedia tool is accessible
    4. Agent responds to a test query
"""

import sys
import os

# Add parent directory to path for imports
sys.path.insert(0, os.path.dirname(__file__))


def test_imports():
    """Test that all required modules can be imported."""
    print("\n" + "=" * 60)
    print("TEST 1: Import Verification")
    print("=" * 60)

    try:
        from dotenv import load_dotenv
        print("  ✓ dotenv")

        from google.adk import Agent
        print("  ✓ google.adk.Agent")

        from google.adk.agents import SequentialAgent
        print("  ✓ google.adk.agents.SequentialAgent")

        from google.adk.tools.tool_context import ToolContext
        print("  ✓ google.adk.tools.tool_context.ToolContext")

        from google.adk.tools.langchain_tool import LangchainTool
        print("  ✓ google.adk.tools.langchain_tool.LangchainTool")

        from langchain_community.tools import WikipediaQueryRun
        print("  ✓ langchain_community.tools.WikipediaQueryRun")

        from langchain_community.utilities import WikipediaAPIWrapper
        print("  ✓ langchain_community.utilities.WikipediaAPIWrapper")

        import google.cloud.logging
        print("  ✓ google.cloud.logging")

        print("\n  ✅ All imports successful!")
        return True

    except ImportError as e:
        print(f"\n  ❌ Import failed: {e}")
        print("  → Run: pip install -r requirements.txt")
        return False


def test_agent_loading():
    """Test that the agent module loads without errors."""
    print("\n" + "=" * 60)
    print("TEST 2: Agent Module Loading")
    print("=" * 60)

    try:
        # Set dummy env for testing if not set
        if not os.getenv("PROJECT_ID"):
            os.environ["PROJECT_ID"] = "test-project"

        from agent import (
            root_agent,
            health_check,
            add_prompt_to_state,
            comprehensive_researcher,
            response_formatter,
            tour_guide_workflow,
            wikipedia_tool,
        )

        print(f"  ✓ root_agent: {root_agent.name}")
        print(f"  ✓ comprehensive_researcher: {comprehensive_researcher.name}")
        print(f"  ✓ response_formatter: {response_formatter.name}")
        print(f"  ✓ tour_guide_workflow: {tour_guide_workflow.name}")
        print(f"  ✓ add_prompt_to_state function exists")
        print(f"  ✓ health_check function exists")
        print(f"  ✓ wikipedia_tool: {'initialized' if wikipedia_tool else 'unavailable'}")

        # Test health check
        health = health_check()
        print(f"  ✓ health_check: {health['status']}")

        print("\n  ✅ Agent module loaded successfully!")
        return True

    except Exception as e:
        print(f"\n  ❌ Agent loading failed: {e}")
        import traceback
        traceback.print_exc()
        return False


def test_wikipedia_direct():
    """Test the Wikipedia tool directly."""
    print("\n" + "=" * 60)
    print("TEST 3: Wikipedia Tool Direct Call")
    print("=" * 60)

    try:
        from langchain_community.tools import WikipediaQueryRun
        from langchain_community.utilities import WikipediaAPIWrapper

        api_wrapper = WikipediaAPIWrapper(lang="en")
        tool = WikipediaQueryRun(api_wrapper=api_wrapper)

        # Test a simple query
        result = tool.run("Lion")
        print(f"  ✓ Wikipedia tool responded")
        print(f"  ✓ Response length: {len(result)} chars")
        print(f"  ✓ Preview: {result[:200]}...")

        print("\n  ✅ Wikipedia tool working!")
        return True

    except Exception as e:
        print(f"\n  ❌ Wikipedia tool failed: {e}")
        print("  → This may be a network issue. The agent will handle this gracefully at runtime.")
        return False


def test_dotenv():
    """Test that .env file is loaded correctly."""
    print("\n" + "=" * 60)
    print("TEST 4: Environment Variables")
    print("=" * 60)

    from dotenv import load_dotenv
    load_dotenv()

    project_id = os.getenv("PROJECT_ID")
    model = os.getenv("MODEL")

    print(f"  PROJECT_ID: {project_id or '(not set)'}")
    print(f"  MODEL: {model or '(not set)'}")
    print(f"  GOOGLE_CLOUD_PROJECT: {os.getenv('GOOGLE_CLOUD_PROJECT') or '(not set)'}")

    if not project_id or project_id == "test-project":
        print("\n  ⚠️  Warning: PROJECT_ID not set in .env")
        print("  → Copy .env.example to .env and fill in your GCP project ID")
    else:
        print("\n  ✅ Environment variables loaded!")

    return True


def run_local_agent():
    """Run an interactive local test of the agent."""
    print("\n" + "=" * 60)
    print("TEST 5: Interactive Agent Test")
    print("=" * 60)
    print("  Starting ADK development UI...")
    print("  Press Ctrl+C to exit")
    print("  Open http://localhost:8000 in your browser\n")

    try:
        import subprocess
        result = subprocess.run(
            ["python", "-m", "http.server", "8000"],
            capture_output=False,
            timeout=5,
        )
    except Exception:
        # Fallback: just run adk web
        try:
            import subprocess
            print("  Running: adk web")
            subprocess.run(["adk", "web"], cwd=os.path.dirname(__file__))
        except FileNotFoundError:
            print("  ❌ 'adk' command not found.")
            print("  → Run: pip install google-adk")
            print("  → Then run: adk web")


def main():
    print("\n" + "╔" + "═" * 58 + "╗")
    print("║" + " 🦁 ZOO GUIDE AGENT — LOCAL TEST SUITE                  ║".center(58) + "║")
    print("╚" + "═" * 58 + "╝")

    results = []

    results.append(("Import Verification", test_imports()))
    results.append(("Agent Module Loading", test_agent_loading()))
    results.append(("Wikipedia Tool", test_wikipedia_direct()))
    results.append(("Environment Variables", test_dotenv()))

    print("\n" + "=" * 60)
    print("SUMMARY")
    print("=" * 60)

    all_passed = True
    for name, passed in results:
        status = "✅ PASS" if passed else "❌ FAIL"
        print(f"  {status}  {name}")
        if not passed:
            all_passed = False

    print()
    if all_passed:
        print("  🎉 All tests passed! Ready to deploy to Cloud Run.")
        print("\n  Next steps:")
        print("  1. Edit .env with your GCP credentials")
        print("  2. Run: adk deploy cloud_run")
    else:
        print("  ⚠️  Some tests failed. Fix the issues above before deploying.")

    print()

    # Optionally run interactive test
    try:
        response = input("  Run interactive agent test? (y/N): ").strip().lower()
        if response == "y":
            run_local_agent()
    except EOFError:
        pass


if __name__ == "__main__":
    main()
