# =============================================================================
# Zoo Guide Agent — Deploy to Google Cloud Run (PowerShell / Windows)
# =============================================================================
# Usage:
#   .\deploy.ps1
#
# Prerequisites:
#   - Google Cloud SDK installed (gcloud)
#   - Project authenticated: gcloud auth login
#   - Python 3.10+ with uv package manager
#   - .env file filled with PROJECT_ID, SERVICE_ACCOUNT, etc.
#
# What this script does:
#   1. Loads environment variables from .env
#   2. Enables required GCP APIs
#   3. Creates service account with correct IAM roles
#   4. Deploys to Cloud Run using ADK CLI
# =============================================================================

param(
    [switch]$SkipConfirmation,
    [switch]$AutoCleanup
)

$ErrorActionPreference = "Stop"

Write-Host ""
Write-Host "==============================================" -ForegroundColor Cyan
Write-Host "  🦁 Zoo Guide Agent — Cloud Run Deployment" -ForegroundColor Cyan
Write-Host "==============================================" -ForegroundColor Cyan
Write-Host ""

# --- Load environment variables ---
$envPath = Join-Path $PSScriptRoot ".env"
if (Test-Path $envPath) {
    Write-Host "📁 Loading .env file..." -ForegroundColor Green
    Get-Content $envPath | ForEach-Object {
        if ($_ -match '^\s*([^#][^=]+)=(.*)$') {
            $name = $matches[1].Trim()
            $value = $matches[2].Trim()
            [System.Environment]::SetEnvironmentVariable($name, $value)
        }
    }
    Write-Host "  ✓ .env loaded`n"
} else {
    Write-Host "  ⚠️  No .env file found. Using existing environment variables.`n" -ForegroundColor Yellow
}

# --- Helper function ---
function Get-EnvOrDefault {
    param($Name, $Default)
    $val = [System.Environment]::GetEnvironmentVariable($Name)
    if ([string]::IsNullOrWhiteSpace($val)) { return $Default }
    return $val
}

# --- Read configuration ---
$PROJECT_ID = [System.Environment]::GetEnvironmentVariable("PROJECT_ID")
$PROJECT_NUMBER = [System.Environment]::GetEnvironmentVariable("PROJECT_NUMBER")
$SERVICE_ACCOUNT = [System.Environment]::GetEnvironmentVariable("SERVICE_ACCOUNT")
$SA_NAME = Get-EnvOrDefault "SA_NAME" "zoo-cr-service"
$MODEL = Get-EnvOrDefault "MODEL" "gemini-2.5-flash"
$REGION = Get-EnvOrDefault "REGION" "europe-west1"
$SERVICE_NAME = Get-EnvOrDefault "SERVICE_NAME" "zoo-tour-guide"

# --- Validate ---
$REQUIRED = @("PROJECT_ID", "PROJECT_NUMBER", "SERVICE_ACCOUNT")
$missing = $REQUIRED | Where-Object {
    [string]::IsNullOrWhiteSpace([System.Environment]::GetEnvironmentVariable($_))
}

if ($missing.Count -gt 0) {
    Write-Host "  ❌ ERROR: Missing required environment variables:" -ForegroundColor Red
    $missing | ForEach-Object { Write-Host "    - $_" -ForegroundColor Red }
    Write-Host ""
    Write-Host "  → Copy .env.example to .env and fill in the values." -ForegroundColor Yellow
    exit 1
}

Write-Host "📋 Configuration:" -ForegroundColor Green
Write-Host "  PROJECT_ID:      $PROJECT_ID"
Write-Host "  PROJECT_NUMBER:   $PROJECT_NUMBER"
Write-Host "  SERVICE_ACCOUNT: $SERVICE_ACCOUNT"
Write-Host "  MODEL:           $MODEL"
Write-Host "  REGION:          $REGION"
Write-Host "  SERVICE_NAME:    $SERVICE_NAME"
Write-Host ""

# --- Confirm ---
if (-not $SkipConfirmation) {
    $response = Read-Host "⚠️  This will deploy to Cloud Run. Continue? (y/N)"
    if ($response -ne "y" -and $response -ne "Y") {
        Write-Host "Aborted." -ForegroundColor Yellow
        exit 0
    }
}

# --- Step 1: Enable APIs ---
Write-Host ""
Write-Host "🚀 Step 1: Enabling GCP APIs..." -ForegroundColor Cyan
gcloud services enable `
    run.googleapis.com `
    artifactregistry.googleapis.com `
    cloudbuild.googleapis.com `
    aiplatform.googleapis.com `
    compute.googleapis.com `
    --quiet

Write-Host "  ✓ APIs enabled" -ForegroundColor Green

# --- Step 2: Create service account ---
Write-Host ""
Write-Host "🚀 Step 2: Setting up service account..." -ForegroundColor Cyan

try {
    $existing = gcloud iam service-accounts describe $SERVICE_ACCOUNT 2>$null
    if ($LASTEXITCODE -eq 0) {
        Write-Host "  ✓ Service account already exists: $SERVICE_ACCOUNT" -ForegroundColor Green
    }
} catch {
    gcloud iam service-accounts create $SA_NAME `
        --display-name="Zoo Guide Agent Service Account" `
        --description="Service account for Zoo Guide ADK agent on Cloud Run"

    if ($LASTEXITCODE -eq 0) {
        Write-Host "  ✓ Service account created: $SA_NAME" -ForegroundColor Green
    }
}

# --- Step 3: Grant IAM role ---
Write-Host ""
Write-Host "🚀 Step 3: Granting Vertex AI permissions..." -ForegroundColor Cyan
gcloud projects add-iam-policy-binding $PROJECT_ID `
    --member="serviceAccount:$SERVICE_ACCOUNT" `
    --role="roles/aiplatform.user" `
    --quiet

Write-Host "  ✓ Vertex AI User role granted" -ForegroundColor Green

# --- Step 4: Deploy ---
Write-Host ""
Write-Host "🚀 Step 4: Deploying to Cloud Run..." -ForegroundColor Cyan
Write-Host "  This takes 5-10 minutes. Please wait...`n" -ForegroundColor Yellow

# Change to script directory
Push-Location $PSScriptRoot

try {
    uvx --from google-adk==1.14.0 `
        adk deploy cloud_run `
        --project=$PROJECT_ID `
        --region=$REGION `
        --service_name=$SERVICE_NAME `
        --with_ui `
        . `
        -- `
        --service-account=$SERVICE_ACCOUNT `
        --labels="app=zoo-tour-guide,track=cohort1,project=hackathon"

    if ($LASTEXITCODE -ne 0) {
        throw "Deployment failed with exit code $LASTEXITCODE"
    }

} finally {
    Pop-Location
}

Write-Host ""
Write-Host "==============================================" -ForegroundColor Green
Write-Host "  ✅ Deployment complete!" -ForegroundColor Green
Write-Host "==============================================" -ForegroundColor Green
Write-Host ""
Write-Host "📋 Next steps:" -ForegroundColor Cyan
Write-Host "  1. Copy the Cloud Run URL from the output above"
Write-Host "  2. Visit the URL to test the agent"
Write-Host "  3. Submit the URL to the hackathon portal"
Write-Host ""
Write-Host "🧹 To delete later:" -ForegroundColor Yellow
Write-Host "  gcloud run services delete $SERVICE_NAME --region=$REGION --quiet"
Write-Host ""

if ($AutoCleanup) {
    Write-Host "⏰ Auto-cleanup enabled. Deleting deployment in 60 seconds (Ctrl+C to cancel)..." -ForegroundColor Yellow
    Start-Sleep -Seconds 60
    gcloud run services delete $SERVICE_NAME --region=$REGION --quiet
    Write-Host "  ✓ Cleaned up." -ForegroundColor Green
}
