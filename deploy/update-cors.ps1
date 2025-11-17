# Update CORS Configuration in Backend
# This script helps update CORS settings for production

param(
    [Parameter(Mandatory=$true)]
    [string[]]$AllowedOrigins,
    
    [Parameter(Mandatory=$false)]
    [string]$BackendPath = "backend/app/main.py"
)

$ErrorActionPreference = "Stop"

Write-Host "=========================================" -ForegroundColor Cyan
Write-Host "Update CORS Configuration" -ForegroundColor Cyan
Write-Host "=========================================" -ForegroundColor Cyan
Write-Host ""

if (-not (Test-Path $BackendPath)) {
    Write-Host "✗ Backend file not found: $BackendPath" -ForegroundColor Red
    exit 1
}

Write-Host "Reading backend file..." -ForegroundColor Yellow
$content = Get-Content $BackendPath -Raw

# Create CORS origins list
$originsList = $AllowedOrigins | ForEach-Object { "`"$_`"" } | Join-String -Separator ",`n        "

$newCorsConfig = @"
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        $originsList
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
"@

# Replace CORS configuration
$pattern = '(?s)app\.add_middleware\(\s*CORSMiddleware,.*?allow_headers=\["\*"\],\s*\)'
$content = $content -replace $pattern, $newCorsConfig

Write-Host "Updating CORS configuration..." -ForegroundColor Yellow
$content | Set-Content $BackendPath -NoNewline

Write-Host "✓ CORS configuration updated" -ForegroundColor Green
Write-Host ""
Write-Host "Allowed origins:" -ForegroundColor Cyan
foreach ($origin in $AllowedOrigins) {
    Write-Host "  - $origin" -ForegroundColor White
}
Write-Host ""
Write-Host "Remember to rebuild and redeploy your backend!" -ForegroundColor Yellow

