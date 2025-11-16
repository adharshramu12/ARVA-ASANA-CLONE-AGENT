# Start Asana Clone Development Server
Write-Host "======================================================================" -ForegroundColor Cyan
Write-Host "  ASANA CLONING AGENT - Starting Development Server" -ForegroundColor Cyan
Write-Host "======================================================================" -ForegroundColor Cyan
Write-Host ""

Set-Location "C:\Users\Administrator\Desktop\asana-cloning-agent\frontend"

Write-Host "Checking dependencies..." -ForegroundColor Yellow
if (-Not (Test-Path "node_modules")) {
    Write-Host "Installing npm packages..." -ForegroundColor Yellow
    npm install
} else {
    Write-Host "Dependencies already installed" -ForegroundColor Green
}

Write-Host ""
Write-Host "======================================================================" -ForegroundColor Cyan
Write-Host "  Starting Next.js Development Server" -ForegroundColor Cyan
Write-Host "======================================================================" -ForegroundColor Cyan
Write-Host ""
Write-Host "  Server will be available at:" -ForegroundColor Green
Write-Host "  http://localhost:3000" -ForegroundColor Green
Write-Host ""
Write-Host "  Press Ctrl+C to stop the server" -ForegroundColor Yellow
Write-Host "======================================================================" -ForegroundColor Cyan
Write-Host ""

npm run dev
