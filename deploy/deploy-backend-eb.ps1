# Deploy Backend to AWS Elastic Beanstalk
# Prerequisites: EB CLI installed (pip install awsebcli)

param(
    [Parameter(Mandatory=$false)]
    [string]$EnvironmentName = "bnpl-backend-prod",
    
    [Parameter(Mandatory=$false)]
    [string]$Region = "us-east-1"
)

$ErrorActionPreference = "Stop"

Write-Host "=========================================" -ForegroundColor Cyan
Write-Host "Deploy Backend to Elastic Beanstalk" -ForegroundColor Cyan
Write-Host "=========================================" -ForegroundColor Cyan
Write-Host ""

# Check EB CLI
Write-Host "Checking EB CLI..." -ForegroundColor Yellow
try {
    $ebVersion = eb --version
    Write-Host "✓ EB CLI found: $ebVersion" -ForegroundColor Green
} catch {
    Write-Host "✗ EB CLI not found. Install with: pip install awsebcli" -ForegroundColor Red
    exit 1
}

# Navigate to backend directory
Set-Location backend

# Check if already initialized
if (-not (Test-Path ".elasticbeanstalk")) {
    Write-Host "Initializing Elastic Beanstalk..." -ForegroundColor Yellow
    Write-Host "You will be prompted for configuration. Use:" -ForegroundColor Yellow
    Write-Host "  - Platform: Python 3.11" -ForegroundColor White
    Write-Host "  - Application name: bnpl-backend" -ForegroundColor White
    Write-Host "  - Region: $Region" -ForegroundColor White
    Write-Host ""
    eb init -p python-3.11 --region $Region
}

# Check if environment exists
Write-Host "Checking environment..." -ForegroundColor Yellow
$envExists = eb list | Select-String $EnvironmentName
if (-not $envExists) {
    Write-Host "Creating environment: $EnvironmentName" -ForegroundColor Yellow
    Write-Host "This will take 5-10 minutes..." -ForegroundColor Yellow
    
    # Create environment with Docker platform (if using Dockerfile)
    # Or use Python platform for direct deployment
    eb create $EnvironmentName --platform "Python 3.11" --region $Region
} else {
    Write-Host "Environment exists: $EnvironmentName" -ForegroundColor Green
}

# Set environment variables
Write-Host ""
Write-Host "Setting environment variables..." -ForegroundColor Yellow
Write-Host "You need to provide:" -ForegroundColor Yellow
Write-Host "  - DATABASE_URL (from RDS endpoint)" -ForegroundColor White
Write-Host "  - SECRET_KEY (strong random key)" -ForegroundColor White
Write-Host "  - Other required variables" -ForegroundColor White
Write-Host ""

$dbUrl = Read-Host "Enter DATABASE_URL (postgresql://user:pass@host:5432/db)"
$secretKey = Read-Host "Enter SECRET_KEY"
$lenderCode = Read-Host "Enter LENDER_ADMIN_CODE (or press Enter for default)"

$envVars = @(
    "DATABASE_URL=$dbUrl",
    "SECRET_KEY=$secretKey",
    "ALGORITHM=HS256",
    "ACCESS_TOKEN_EXPIRE_MINUTES=30",
    "DEBUG=False"
)

if (-not [string]::IsNullOrEmpty($lenderCode)) {
    $envVars += "LENDER_ADMIN_CODE=$lenderCode"
}

$envVarsString = $envVars -join " "
eb setenv $envVarsString

# Deploy
Write-Host ""
Write-Host "Deploying application..." -ForegroundColor Yellow
eb deploy $EnvironmentName

Write-Host ""
Write-Host "=========================================" -ForegroundColor Cyan
Write-Host "✓ Deployment complete!" -ForegroundColor Green
Write-Host "=========================================" -ForegroundColor Cyan
Write-Host ""
Write-Host "Get your application URL:" -ForegroundColor Yellow
eb status $EnvironmentName
Write-Host ""
Write-Host "View logs:" -ForegroundColor Yellow
Write-Host "  eb logs $EnvironmentName" -ForegroundColor White
Write-Host ""
Write-Host "Open in browser:" -ForegroundColor Yellow
Write-Host "  eb open $EnvironmentName" -ForegroundColor White

