# Contributing to Zoo Guide Agent

Thank you for your interest in contributing! This project is part of the Google Cloud Gen AI Academy APAC 2026 Cohort 1 track submission.

## How to Contribute

### Reporting Bugs
- Open an issue with the `bug` label
- Include your GCP project region, Python version, and exact error messages
- Steps to reproduce the bug

### Suggesting Features
- Open an issue with the `enhancement` label
- Describe the use case and why it would benefit the project
- Relevant documentation links

### Pull Requests
1. Fork the repository
2. Create a feature branch: `git checkout -b feature/your-feature-name`
3. Make your changes with appropriate tests
4. Ensure the code passes `python -m py_compile` on all `.py` files
5. Open a PR with a clear description

## Development Setup

```bash
# Clone your fork
git clone https://github.com/YOUR_USERNAME/track1-zoo-agent.git
cd track1-zoo-agent

# Create virtual environment
python -m venv .venv
source .venv/bin/activate  # Linux/Mac
# or
.venv\Scripts\Activate  # Windows

# Install dependencies
pip install -r requirements.txt

# Test locally
python test_agent.py
```

## Code Style
- Follow PEP 8
- Add docstrings to all functions
- Keep functions focused and small

## Questions?
Open an issue or reach out via the hackathon community channels.
