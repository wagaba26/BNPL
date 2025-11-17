# Build and Push Docker Images to ECR
# Prerequisites: Docker installed and running, AWS CLI configured

param(
    [Parameter(Mandatory=$false)]
    [string]$Region = "us-east-1",
    
    [Parameter(Mandatory=$false)]
    [string]$Component = "all"  # all, backend, frontend
)

$ErrorActionPreference = "Stop"

Write-Host "=========================================" -ForegroundColor Cyan
Write-Host "Build and Push Docker Images to ECR" -ForegroundColor Cyan
Write-Host "=========================================" -ForegroundColor Cyan
Write-Host ""

# Load configuration
$configFile = ".aws-deploy-config.json"
if (Test-Path $configFile) {
    $config = Get-Content $configFile | ConvertFrom-Json
    $accountId = $config.AccountId
    $Region = $config.Region
} else {
    Write-Host "Configuration file not found. Getting AWS Account ID..." -ForegroundColor Yellow
    $accountId = aws sts get-caller-identity --query Account --output text
    if (-not $accountId) {
        Write-Host "✗ Failed to get AWS Account ID. Check your AWS credentials." -ForegroundColor Red
        exit 1
    }
}

$backendRepo = "$accountId.dkr.ecr.$Region.amazonaws.com/bnpl-backend"
$frontendRepo = "$accountId.dkr.ecr.$Region.amazonaws.com/bnpl-frontend"

# Login to ECR
Write-Host "Logging in to ECR..." -ForegroundColor Yellow
$loginCommand = aws ecr get-login-password --region $Region | docker login --username AWS --password-stdin "$accountId.dkr.ecr.$Region.amazonaws.com"
if ($LASTEXITCODE -ne 0) {
    Write-Host "✗ Failed to login to ECR" -ForegroundColor Red
    exit 1
}
Write-Host "✓ Logged in to ECR" -ForegroundColor Green
Write-Host ""

# Build and push backend
if ($Component -eq "all" -or $Component -eq "backend") {
    Write-Host "Building backend Docker image..." -ForegroundColor Yellow
    Set-Location ..
    docker build -t bnpl-backend:latest -f Dockerfile .
    if ($LASTEXITCODE -ne 0) {
        Write-Host "✗ Failed to build backend image" -ForegroundColor Red
        exit 1
    }
    Write-Host "✓ Backend image built" -ForegroundColor Green
    
    Write-Host "Tagging backend image..." -ForegroundColor Yellow
    docker tag bnpl-backend:latest "$backendRepo:latest"
    docker tag bnpl-backend:latest "$backendRepo:$(Get-Date -Format 'yyyyMMdd-HHmmss')"
    Write-Host "✓ Backend image tagged" -ForegroundColor Green
    
    Write-Host "Pushing backend image to ECR..." -ForegroundColor Yellow
    docker push "$backendRepo:latest"
    docker push "$backendRepo:$(Get-Date -Format 'yyyyMMdd-HHmmss')"
    if ($LASTEXITCODE -ne 0) {
        Write-Host "✗ Failed to push backend image" -ForegroundColor Red
        exit 1
    }
    Write-Host "✓ Backend image pushed to ECR" -ForegroundColor Green
    Write-Host "  Repository: $backendRepo" -ForegroundColor Cyan
    Write-Host ""
}

# Build and push frontend
if ($Component -eq "all" -or $Component -eq "frontend") {
    Write-Host "Building frontend Docker image..." -ForegroundColor Yellow
    Set-Location frontend
    docker build -t bnpl-frontend:latest -f Dockerfile .
    if ($LASTEXITCODE -ne 0) {
        Write-Host "✗ Failed to build frontend image" -ForegroundColor Red
        exit 1
    }
    Write-Host "✓ Frontend image built" -ForegroundColor Green
    
    Write-Host "Tagging frontend image..." -ForegroundColor Yellow
    docker tag bnpl-frontend:latest "$frontendRepo:latest"
    docker tag bnpl-frontend:latest "$frontendRepo:$(Get-Date -Format 'yyyyMMdd-HHmmss')"
    Write-Host "✓ Frontend image tagged" -ForegroundColor Green
    
    Write-Host "Pushing frontend image to ECR..." -ForegroundColor Yellow
    docker push "$frontendRepo:latest"
    docker push "$frontendRepo:$(Get-Date -Format 'yyyyMMdd-HHmmss')"
    if ($LASTEXITCODE -ne 0) {
        Write-Host "✗ Failed to push frontend image" -ForegroundColor Red
        exit 1
    }
    Write-Host "✓ Frontend image pushed to ECR" -ForegroundColor Green
    Write-Host "  Repository: $frontendRepo" -ForegroundColor Cyan
    Write-Host ""
}

Write-Host "=========================================" -ForegroundColor Cyan
Write-Host "✓ All images built and pushed successfully!" -ForegroundColor Green
Write-Host "=========================================" -ForegroundColor Cyan

