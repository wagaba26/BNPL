# AWS Infrastructure Setup Script for BNPL Platform
# This script helps set up AWS resources needed for deployment
# Prerequisites: AWS CLI installed and configured

param(
    [Parameter(Mandatory=$true)]
    [string]$Region = "us-east-1",
    
    [Parameter(Mandatory=$false)]
    [string]$Environment = "production",
    
    [Parameter(Mandatory=$false)]
    [string]$DbPassword = "",
    
    [Parameter(Mandatory=$false)]
    [string]$DbInstanceClass = "db.t3.micro"
)

$ErrorActionPreference = "Stop"

Write-Host "=========================================" -ForegroundColor Cyan
Write-Host "BNPL Platform - AWS Infrastructure Setup" -ForegroundColor Cyan
Write-Host "=========================================" -ForegroundColor Cyan
Write-Host ""

# Check AWS CLI
Write-Host "Checking AWS CLI..." -ForegroundColor Yellow
try {
    $awsVersion = aws --version
    Write-Host "✓ AWS CLI found: $awsVersion" -ForegroundColor Green
} catch {
    Write-Host "✗ AWS CLI not found. Please install AWS CLI first." -ForegroundColor Red
    exit 1
}

# Get AWS Account ID
Write-Host "Getting AWS Account ID..." -ForegroundColor Yellow
$accountId = aws sts get-caller-identity --query Account --output text
if (-not $accountId) {
    Write-Host "✗ Failed to get AWS Account ID. Check your AWS credentials." -ForegroundColor Red
    exit 1
}
Write-Host "✓ AWS Account ID: $accountId" -ForegroundColor Green
Write-Host ""

# Generate random password if not provided
if ([string]::IsNullOrEmpty($DbPassword)) {
    $DbPassword = -join ((48..57) + (65..90) + (97..122) | Get-Random -Count 32 | ForEach-Object {[char]$_})
    Write-Host "Generated database password (save this!): $DbPassword" -ForegroundColor Yellow
    Write-Host ""
}

# S3 Bucket Setup
Write-Host "Setting up S3 bucket..." -ForegroundColor Yellow
$bucketName = "bnpl-documents-$Region-$accountId"
try {
    $bucketExists = aws s3 ls "s3://$bucketName" 2>&1
    if ($LASTEXITCODE -eq 0) {
        Write-Host "✓ S3 bucket already exists: $bucketName" -ForegroundColor Green
    } else {
        if ($Region -eq "us-east-1") {
            aws s3 mb "s3://$bucketName" --region $Region
        } else {
            aws s3 mb "s3://$bucketName" --region $Region --region $Region
        }
        Write-Host "✓ Created S3 bucket: $bucketName" -ForegroundColor Green
    }
} catch {
    Write-Host "✗ Failed to create S3 bucket: $_" -ForegroundColor Red
}

# Configure S3 CORS
Write-Host "Configuring S3 CORS..." -ForegroundColor Yellow
$corsConfig = @"
{
    "CORSRules": [
        {
            "AllowedHeaders": ["*"],
            "AllowedMethods": ["GET", "PUT", "POST", "DELETE", "HEAD"],
            "AllowedOrigins": ["*"],
            "ExposeHeaders": ["ETag"],
            "MaxAgeSeconds": 3000
        }
    ]
}
"@
$corsConfig | Out-File -FilePath "$env:TEMP\s3-cors.json" -Encoding utf8
aws s3api put-bucket-cors --bucket $bucketName --cors-configuration "file://$env:TEMP\s3-cors.json" 2>&1 | Out-Null
Write-Host "✓ S3 CORS configured" -ForegroundColor Green

# ECR Repositories
Write-Host "Setting up ECR repositories..." -ForegroundColor Yellow
$repos = @("bnpl-backend", "bnpl-frontend")
foreach ($repo in $repos) {
    try {
        $repoExists = aws ecr describe-repositories --repository-names $repo --region $Region 2>&1
        if ($LASTEXITCODE -eq 0) {
            Write-Host "✓ ECR repository already exists: $repo" -ForegroundColor Green
        } else {
            aws ecr create-repository --repository-name $repo --region $Region | Out-Null
            Write-Host "✓ Created ECR repository: $repo" -ForegroundColor Green
        }
    } catch {
        Write-Host "✗ Failed to create ECR repository $repo : $_" -ForegroundColor Red
    }
}

# RDS Setup (Manual - requires VPC configuration)
Write-Host ""
Write-Host "=========================================" -ForegroundColor Cyan
Write-Host "RDS Database Setup (Manual Steps)" -ForegroundColor Cyan
Write-Host "=========================================" -ForegroundColor Cyan
Write-Host ""
Write-Host "RDS requires manual setup via AWS Console or CloudFormation." -ForegroundColor Yellow
Write-Host "Use the following configuration:" -ForegroundColor Yellow
Write-Host ""
Write-Host "  Database Engine: PostgreSQL 15.x" -ForegroundColor White
Write-Host "  Instance Class: $DbInstanceClass" -ForegroundColor White
Write-Host "  Master Username: bnpl_user" -ForegroundColor White
Write-Host "  Master Password: $DbPassword" -ForegroundColor White
Write-Host "  Database Name: bnpl_db" -ForegroundColor White
Write-Host "  Allocated Storage: 20 GB" -ForegroundColor White
Write-Host ""
Write-Host "After creating RDS, update your backend DATABASE_URL:" -ForegroundColor Yellow
Write-Host "  DATABASE_URL=postgresql://bnpl_user:$DbPassword@<rds-endpoint>:5432/bnpl_db" -ForegroundColor White
Write-Host ""

# Save configuration
$config = @{
    Region = $Region
    Environment = $Environment
    AccountId = $accountId
    S3Bucket = $bucketName
    DbPassword = $DbPassword
    ECRBackend = "$accountId.dkr.ecr.$Region.amazonaws.com/bnpl-backend"
    ECRFrontend = "$accountId.dkr.ecr.$Region.amazonaws.com/bnpl-frontend"
} | ConvertTo-Json

$configFile = ".aws-deploy-config.json"
$config | Out-File -FilePath $configFile -Encoding utf8
Write-Host "✓ Configuration saved to $configFile" -ForegroundColor Green
Write-Host ""

Write-Host "=========================================" -ForegroundColor Cyan
Write-Host "Next Steps:" -ForegroundColor Cyan
Write-Host "=========================================" -ForegroundColor Cyan
Write-Host "1. Create RDS PostgreSQL instance (see instructions above)" -ForegroundColor White
Write-Host "2. Run database migrations: cd backend && alembic upgrade head" -ForegroundColor White
Write-Host "3. Build and push Docker images (see deploy/build-and-push.ps1)" -ForegroundColor White
Write-Host "4. Deploy backend to ECS/Elastic Beanstalk" -ForegroundColor White
Write-Host "5. Deploy frontend to Amplify/Elastic Beanstalk" -ForegroundColor White
Write-Host ""
Write-Host "Configuration saved to: $configFile" -ForegroundColor Green

