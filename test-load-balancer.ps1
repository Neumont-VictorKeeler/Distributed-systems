Write-Host "Testing Load Balancer Distribution" -ForegroundColor Cyan
Write-Host ""

for ($i = 1; $i -le 6; $i++) {
    try {
        $response = Invoke-WebRequest -Uri "http://localhost:8080/" -UseBasicParsing
        $instance = $response.Headers["X-Instance-Name"]
        $statusCode = $response.StatusCode
        
        if ($instance) {
            Write-Host "Request ${i}: Status $statusCode - Handled by: $instance" -ForegroundColor Green
        } else {
            Write-Host "Request ${i}: Status $statusCode - Instance header not found" -ForegroundColor Yellow
        }
    } catch {
        Write-Host "Request ${i}: Failed - $_" -ForegroundColor Red
    }
    Start-Sleep -Milliseconds 500
}

Write-Host ""
Write-Host "Testing Trade Offers endpoint..." -ForegroundColor Cyan
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
Write-Host "Access the API at:" -ForegroundColor Yellow
Write-Host "  Load Balancer:  http://localhost:8080/" -ForegroundColor White
Write-Host "  API Docs:       http://localhost:8080/docs" -ForegroundColor White
Write-Host "  Trade Offers:   http://localhost:8080/trade-offers" -ForegroundColor White

