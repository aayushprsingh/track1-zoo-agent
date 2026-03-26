#!/usr/bin/env bash
# =============================================================================
# Zoo Guide Agent — Deploy to Google Cloud Run (Bash / Linux / Mac / Cloud Shell)
# =============================================================================
# Usage:
#   bash deploy.sh
#
# Prerequisites:
#   - Google Cloud SDK installed (gcloud)
#   - Project authenticated (gcloud auth login)
#   - .env file filled with PROJECT_ID, SERVICE_ACCOUNT, etc.
#
# What this script does:
#   1. Loads environment variables from .env
#   2. Enables required GCP APIs
#   3. Creates service account with correct IAM roles
#   4. Deploys to Cloud Run using ADK CLI
# =============================================================================

set -e  # Exit on error

echo "=============================================="
echo "🦁 Zoo Guide Agent — Cloud Run Deployment"
echo "=============================================="
echo ""

# --- Load environment variables ---
if [ -f .env ]; then
    echo "📁 Loading .env file..."
    set -a  # auto-export all variables
    source .env
    set +a
    echo "  ✓ .env loaded"
else
    echo "  ⚠️  No .env file found. Using environment variables directly."
fi

# --- Validate required variables ---
REQUIRED_VARS=("PROJECT_ID" "PROJECT_NUMBER" "SERVICE_ACCOUNT")
for var in "${REQUIRED_VARS[@]}"; do
    if [ -z "${!var}" ]; then
        echo "  ❌ ERROR: $var is not set. Fill in your .env file."
        exit 1
    fi
done

echo ""
echo "📋 Configuration:"
echo "  PROJECT_ID:      $PROJECT_ID"
echo "  PROJECT_NUMBER:   $PROJECT_NUMBER"
echo "  SERVICE_ACCOUNT:  $SERVICE_ACCOUNT"
echo "  MODEL:           ${MODEL:-gemini-2.5-flash}"
echo "  REGION:          ${REGION:-europe-west1}"
echo ""

# --- Confirm before proceeding ---
echo "⚠️  This will deploy to Cloud Run. Continue? (y/N)"
read -r response
if [ "$response" != "y" ] && [ "$response" != "Y" ]; then
    echo "Aborted."
    exit 0
fi

echo ""
echo "🚀 Step 1: Enabling GCP APIs..."
gcloud services enable \
    run.googleapis.com \
    artifactregistry.googleapis.com \
    cloudbuild.googleapis.com \
    aiplatform.googleapis.com \
    compute.googleapis.com \
    --quiet

echo "  ✓ APIs enabled"

echo ""
echo "🚀 Step 2: Creating service account..."
# Check if service account exists
if gcloud iam service-accounts describe "$SERVICE_ACCOUNT" --quiet 2>/dev/null; then
    echo "  ✓ Service account already exists: $SERVICE_ACCOUNT"
else
    gcloud iam service-accounts create "${SA_NAME:-zoo-cr-service}" \
        --display-name="Zoo Guide Agent Service Account" \
        --description="Service account for Zoo Guide ADK agent on Cloud Run"
    echo "  ✓ Service account created"
fi

echo ""
echo "🚀 Step 3: Granting Vertex AI permissions..."
gcloud projects add-iam-policy-binding "$PROJECT_ID" \
    --member="serviceAccount:$SERVICE_ACCOUNT" \
    --role="roles/aiplatform.user" \
    --quiet

echo "  ✓ Vertex AI User role granted"

echo ""
echo "🚀 Step 4: Deploying to Cloud Run..."
echo "  This takes 5-10 minutes. Please wait..."

# Deploy using ADK CLI
uvx --from google-adk==1.14.0 \
    adk deploy cloud_run \
    --project="$PROJECT_ID" \
    --region="${REGION:-europe-west1}" \
    --service_name="${SERVICE_NAME:-zoo-tour-guide}" \
    --with_ui \
    . \
    -- \
    --service-account="$SERVICE_ACCOUNT" \
    --labels="app=zoo-tour-guide,track=cohort1,project=hackathon"

echo ""
echo "=============================================="
echo "✅ Deployment complete!"
echo "=============================================="
echo ""
echo "📋 Next steps:"
echo "  1. Copy the Cloud Run URL from the output above"
echo "  2. Visit the URL to test the agent"
echo "  3. Submit the URL to the hackathon portal"
echo ""
echo "🧹 To delete later:"
echo "  gcloud run services delete ${SERVICE_NAME:-zoo-tour-guide} --region=${REGION:-europe-west1} --quiet"
echo ""
