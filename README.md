# 🦁 Zoo Guide Agent

> An AI-powered zoo tour guide built with Google ADK, Wikipedia, and Cloud Run.
> Part of **Google Cloud Gen AI Academy APAC 2026 — Cohort 1, Track 1**.

[![Track](https://img.shields.io/badge/Track-1%20AI%20Agents-4285F4?style=flat-square)](https://vision.hack2skill.com/event/apac-genaiacademy)
[![ADK](https://img.shields.io/badge/ADK-1.14.0-Google%20AI?style=flat-square)](https://google.github.io/adk-docs/)
[![Python](https://img.shields.io/badge/Python-3.10+-blue?style=flat-square)](https://python.org)
[![License](https://img.shields.io/badge/License-MIT-green?style=flat-square)](LICENSE)
[![Cloud Run](https://img.shields.io/badge/Cloud%20Run-Deployed-4285F4?style=flat-square)](https://cloud.google.com/run)

---

## 🎯 What It Does

Ask the agent about any animal — it will research facts from Wikipedia and
respond with a friendly, engaging zoo guide explanation.

**Example interactions:**
> "Tell me about polar bears"
> "What do penguins eat?"
> "Where can I find lions in the wild?"

---

## 🏗️ Architecture

```
User Input
    │
    ▼
┌──────────────────────────────────────┐
│  Greeter Agent (root_agent)          │
│  - Greets the user                  │
│  - Saves prompt to shared state      │
│  - Hands off to workflow             │
└────────────────┬─────────────────────┘
                 │ SequentialAgent
                 ▼
┌──────────────────────────────────────┐
│  Tour Guide Workflow                 │
│                                      │
│  ┌───────────────────────────────┐   │
│  │ 1. Comprehensive Researcher  │   │
│  │    → Wikipedia Tool (LangChain)   │
│  │    → Gathers animal facts     │   │
│  └───────────────┬───────────────┘   │
│                  │ Passes "research_data" │
│  ┌───────────────▼───────────────┐   │
│  │ 2. Response Formatter        │   │
│  │    → Converts to friendly     │   │
│  │       readable response       │   │
│  └───────────────────────────────┘   │
└────────────────┬─────────────────────┘
                 │
                 ▼
        Final Response to User
```

**Tech stack:** ADK · SequentialAgent · LangChain WikipediaTool · Gemini 2.5 Flash · Cloud Run

---

## 📁 Project Structure

```
track1-zoo-agent/
├── .env                    ← GCP credentials (gitignored)
├── .env.example            ← Template for .env
├── .gitignore
├── LICENSE                 ← MIT License
├── README.md               ← This file
├── CONTRIBUTING.md         ← Contribution guidelines
├── requirements.txt        ← Python dependencies
├── __init__.py             ← Package marker
├── agent.py                ← ADK agent code (main logic)
├── test_agent.py           ← Local test script
├── deploy.sh               ← Bash deployment script
├── deploy.ps1              ← PowerShell deployment script
└── .github/
    └── ISSUE_TEMPLATES/    ← Bug reports & feature requests
```

---

## 🚀 Quick Start

### Prerequisites

- Python 3.10 or higher
- Google Cloud account with billing enabled
- Google Cloud SDK (`gcloud`)
- GCP Project with Vertex AI API enabled

### 1. Clone & Setup

```bash
# Clone the repository
git clone https://github.com/aayushprsingh/track1-zoo-agent.git
cd track1-zoo-agent

# Create virtual environment
python -m venv .venv
source .venv/bin/activate    # Linux/Mac
# .venv\Scripts\Activate       # Windows

# Install dependencies
pip install -r requirements.txt
```

### 2. Configure Environment

```bash
# Copy the template
cp .env.example .env

# Edit .env with your values
# Required: PROJECT_ID, PROJECT_NUMBER, SERVICE_ACCOUNT
```

### 3. Test Locally

```bash
# Run the test suite
python test_agent.py

# Or start the interactive web UI
adk web
# Open http://localhost:8000 in your browser
```

### 4. Deploy to Cloud Run

**Option A — PowerShell (Windows):**
```powershell
.\deploy.ps1
```

**Option B — Bash (Linux/Mac/Cloud Shell):**
```bash
bash deploy.sh
```

**Option C — Manual:**
```bash
# Enable APIs
gcloud services enable run.googleapis.com artifactregistry.googleapis.com \
    cloudbuild.googleapis.com aiplatform.googleapis.com compute.googleapis.com

# Create service account
gcloud iam service-accounts create zoo-cr-service --display-name="Zoo Guide"

# Grant permissions
gcloud projects add-iam-policy-binding $PROJECT_ID \
    --member="serviceAccount:zoo-cr-service@$PROJECT_ID.iam.gserviceaccount.com" \
    --role="roles/aiplatform.user"

# Deploy
uvx --from google-adk==1.14.0 adk deploy cloud_run \
    --project=$PROJECT_ID \
    --region=europe-west1 \
    --service_name=zoo-tour-guide \
    --with_ui \
    . \
    -- --service-account=zoo-cr-service@$PROJECT_ID.iam.gserviceaccount.com
```

---

## 🔧 Configuration

All configuration is done via environment variables:

| Variable | Required | Default | Description |
|----------|----------|---------|-------------|
| `PROJECT_ID` | ✅ Yes | — | Your GCP project ID |
| `PROJECT_NUMBER` | ✅ Yes | — | Your GCP project number |
| `SERVICE_ACCOUNT` | ✅ Yes | — | Full service account email |
| `MODEL` | No | `gemini-2.5-flash` | Gemini model to use |
| `WIKIPEDIA_LANG` | No | `en` | Wikipedia language |
| `LOG_LEVEL` | No | `INFO` | Logging level |

---

## 📋 Features

### Multi-Agent Workflow
Three specialized agents working in sequence:
1. **Greeter** — Entry point, saves user question to state
2. **Researcher** — Uses Wikipedia to find animal facts
3. **Formatter** — Converts raw data into friendly responses

### Error Handling
- Graceful fallback if Wikipedia API is unavailable
- Tool errors are caught and logged without crashing
- Input validation on all tool calls

### Health Checks
- `health_check()` function for Cloud Run liveness probes
- Returns service status, model info, and component states

### Flexible Deployment
- Deploy via ADK CLI (`adk deploy`)
- Both bash and PowerShell scripts provided
- Supports authenticated and unauthenticated access

---

## 📚 Learning Resources

- [Google ADK Documentation](https://google.github.io/adk-docs/)
- [SequentialAgent Guide](https://google.github.io/adk-docs/agents/workflow-agents/sequential-agents/)
- [LangChain Wikipedia Tool](https://python.langchain.com/docs/integrations/tools/wikipedia/)
- [Cloud Run Deployment](https://cloud.google.com/run/docs/deploying)
- [Google Cloud Gen AI Academy](https://vision.hack2skill.com/event/apac-genaiacademy)

---

## ⚠️ Cleanup

After the hackathon deadline, delete resources to avoid charges:

```bash
# Delete Cloud Run service
gcloud run services delete zoo-tour-guide --region=europe-west1 --quiet

# Delete container images
gcloud artifacts repositories delete cloud-run-source-deploy \
    --location=europe-west1 --quiet
```

---

## 🤝 Contributing

See [CONTRIBUTING.md](CONTRIBUTING.md) for guidelines.
Bug reports and feature requests welcome!

---

## 📜 License

This project is licensed under the MIT License — see [LICENSE](LICENSE) for details.

---

**Built for:** Google Cloud Gen AI Academy APAC 2026 — Cohort 1 Track 1  
**Author:** Aayush Pratap Singh  
**Last Updated:** March 2026
