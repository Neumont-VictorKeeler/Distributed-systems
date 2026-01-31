Write-Host "=== Video Game Trading API - Multi-Container Test ===" -ForegroundColor Cyan
Write-Host ""

Write-Host "Checking Docker status..." -ForegroundColor Yellow
try {
    docker info | Out-Null
    Write-Host "[OK] Docker is running" -ForegroundColor Green
} catch {
    Write-Host "[ERROR] Docker is not running. Please start Docker Desktop and try again." -ForegroundColor Red
    exit 1
}

Write-Host ""
Write-Host "Step 1: Building and starting all services..." -ForegroundColor Yellow
docker-compose up --build -d

if ($LASTEXITCODE -ne 0) {
    Write-Host "[ERROR] Failed to start services!" -ForegroundColor Red
    exit 1
}

Write-Host "[OK] Services started" -ForegroundColor Green
Write-Host ""

Write-Host "Step 2: Waiting for services to be healthy..." -ForegroundColor Yellow
Start-Sleep -Seconds 10

Write-Host ""
Write-Host "Step 3: Checking service status..." -ForegroundColor Yellow
docker-compose ps

Write-Host ""
Write-Host "Step 4: Testing load distribution..." -ForegroundColor Yellow
Write-Host "Making 6 requests to verify round-robin distribution:" -ForegroundColor Cyan

for ($i = 1; $i -le 6; $i++) {
    try {
        $response = Invoke-WebRequest -Uri "http://localhost:8080/" -UseBasicParsing
        $instance = $response.Headers["X-Instance-Name"]
        $statusCode = $response.StatusCode

        if ($instance) {
            Write-Host "  Request ${i}: Status $statusCode - Handled by: $instance" -ForegroundColor Green
        } else {
            Write-Host "  Request ${i}: Status $statusCode - Instance header not found" -ForegroundColor Yellow
        }
    } catch {
        Write-Host "  Request ${i}: Failed - $_" -ForegroundColor Red
    }
    Start-Sleep -Milliseconds 500
}

Write-Host ""
Write-Host "Step 5: Testing Trade Offers endpoint..." -ForegroundColor Yellow
try {
    $response = Invoke-WebRequest -Uri "http://localhost:8080/trade-offers" -UseBasicParsing
    $instance = $response.Headers["X-Instance-Name"]
    if ($response.StatusCode -eq 200) {
        Write-Host "[OK] Trade Offers endpoint accessible - Handled by: $instance" -ForegroundColor Green
    }
} catch {
    Write-Host "[ERROR] Trade Offers endpoint failed: $_" -ForegroundColor Red
}

Write-Host ""
Write-Host "Step 6: Viewing recent logs..." -ForegroundColor Yellow
Write-Host "--- API-1 Logs ---" -ForegroundColor Cyan
docker-compose logs --tail=5 api1

Write-Host ""
Write-Host "--- API-2 Logs ---" -ForegroundColor Cyan
docker-compose logs --tail=5 api2

Write-Host ""
Write-Host "--- NGINX Logs ---" -ForegroundColor Cyan
docker-compose logs --tail=5 nginx

Write-Host ""
Write-Host "=== Test Complete ===" -ForegroundColor Cyan
Write-Host ""
Write-Host "Services are running. Access points:" -ForegroundColor Yellow
Write-Host "  Load Balancer:  http://localhost:8080/" -ForegroundColor White
Write-Host "  API Docs:       http://localhost:8080/docs" -ForegroundColor White
Write-Host "  ReDoc:          http://localhost:8080/redoc" -ForegroundColor White
Write-Host "  Health Check:   http://localhost:8080/health" -ForegroundColor White
Write-Host ""
Write-Host "Useful commands:" -ForegroundColor Yellow
Write-Host "  View all logs:       docker-compose logs -f" -ForegroundColor White
Write-Host "  View specific logs:  docker-compose logs -f api1" -ForegroundColor White
Write-Host "  Stop services:       docker-compose down" -ForegroundColor White
Write-Host "  Restart services:    docker-compose restart" -ForegroundColor White
Write-Host ""
Write-Host "Press Ctrl+C to exit (services will keep running)." -ForegroundColor Green

