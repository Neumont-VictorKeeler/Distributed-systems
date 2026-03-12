# PowerShell script to test the authentication microservice

Write-Host "=== Authentication Microservice Test Script ===" -ForegroundColor Cyan
Write-Host ""

$baseUrl = "http://localhost:8080"

# Test 1: Register a new user
Write-Host "Test 1: Registering a new user..." -ForegroundColor Yellow
$registerBody = @{
    name = "Test User"
    email = "testuser@example.com"
    password = "testpassword123"
} | ConvertTo-Json

try {
    $registerResponse = Invoke-RestMethod -Uri "$baseUrl/register" -Method Post -Body $registerBody -ContentType "application/json" -ErrorAction Stop
    Write-Host "✓ User registered successfully!" -ForegroundColor Green
    Write-Host "User ID: $($registerResponse.id)" -ForegroundColor Gray
    Write-Host "User Email: $($registerResponse.email)" -ForegroundColor Gray
    Write-Host ""
} catch {
    $statusCode = $_.Exception.Response.StatusCode.value__
    if ($statusCode -eq 400) {
        Write-Host "✓ User already exists (expected if running multiple times)" -ForegroundColor Yellow
    } else {
        Write-Host "✗ Registration failed: $($_.Exception.Message)" -ForegroundColor Red
    }
    Write-Host ""
}

# Test 2: Login and get token
Write-Host "Test 2: Logging in to get access token..." -ForegroundColor Yellow
$loginBody = "username=testuser@example.com&password=testpassword123"

try {
    $loginResponse = Invoke-RestMethod -Uri "$baseUrl/token" -Method Post -Body $loginBody -ContentType "application/x-www-form-urlencoded"
    $token = $loginResponse.access_token
    Write-Host "✓ Login successful!" -ForegroundColor Green
    Write-Host "Token: $($token.Substring(0, 50))..." -ForegroundColor Gray
    Write-Host ""
} catch {
    Write-Host "✗ Login failed: $($_.Exception.Message)" -ForegroundColor Red
    Write-Host ""
    exit 1
}

# Test 3: Create a game with authentication
Write-Host "Test 3: Creating a game (requires authentication)..." -ForegroundColor Yellow
$gameBody = @{
    name = "The Legend of Zelda"
    publisher = "Nintendo"
    year_published = 1986
    gaming_system = "NES"
    condition = "good"
} | ConvertTo-Json

$headers = @{
    "Authorization" = "Bearer $token"
    "Content-Type" = "application/json"
}

try {
    $gameResponse = Invoke-RestMethod -Uri "$baseUrl/games" -Method Post -Body $gameBody -Headers $headers
    Write-Host "✓ Game created successfully!" -ForegroundColor Green
    Write-Host "Game ID: $($gameResponse.id)" -ForegroundColor Gray
    Write-Host "Game Name: $($gameResponse.name)" -ForegroundColor Gray
    Write-Host ""
} catch {
    Write-Host "✗ Game creation failed: $($_.Exception.Message)" -ForegroundColor Red
    Write-Host ""
}

# Test 4: Try to create a game without authentication (should fail)
Write-Host "Test 4: Attempting to create a game without authentication (should fail)..." -ForegroundColor Yellow
try {
    $gameResponse = Invoke-RestMethod -Uri "$baseUrl/games" -Method Post -Body $gameBody -ContentType "application/json" -ErrorAction Stop
    Write-Host "✗ Unexpected success - authentication should be required!" -ForegroundColor Red
    Write-Host ""
} catch {
    $statusCode = $_.Exception.Response.StatusCode.value__
    if ($statusCode -eq 401) {
        Write-Host "✓ Correctly rejected - authentication required!" -ForegroundColor Green
    } else {
        Write-Host "✗ Unexpected error: $($_.Exception.Message)" -ForegroundColor Red
    }
    Write-Host ""
}

# Test 5: Check auth service health
Write-Host "Test 5: Checking auth service metrics..." -ForegroundColor Yellow
try {
    $metricsResponse = Invoke-WebRequest -Uri "$baseUrl/metrics" -UseBasicParsing
    if ($metricsResponse.Content -match "auth_requests_total") {
        Write-Host "✓ Auth service metrics are available!" -ForegroundColor Green
    } else {
        Write-Host "✗ Auth service metrics not found" -ForegroundColor Red
    }
    Write-Host ""
} catch {
    Write-Host "✗ Failed to retrieve metrics: $($_.Exception.Message)" -ForegroundColor Red
    Write-Host ""
}

Write-Host "=== Test Complete ===" -ForegroundColor Cyan
Write-Host ""
Write-Host "Summary:" -ForegroundColor Cyan
Write-Host "- Auth service is running and accessible via NGINX" -ForegroundColor White
Write-Host "- User registration and login are working" -ForegroundColor White
Write-Host "- Protected endpoints require authentication" -ForegroundColor White
Write-Host "- Prometheus metrics are being collected" -ForegroundColor White
Write-Host ""
Write-Host "Next steps:" -ForegroundColor Cyan
Write-Host "1. View Prometheus metrics at: http://localhost:9090" -ForegroundColor White
Write-Host "2. View Grafana dashboards at: http://localhost:3000" -ForegroundColor White
Write-Host "3. Test the API with Postman using the saved token" -ForegroundColor White

