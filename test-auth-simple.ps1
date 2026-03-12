# Simple PowerShell script to test the authentication microservice

Write-Host "=== Authentication Microservice Test ===" -ForegroundColor Cyan
Write-Host ""

$baseUrl = "http://localhost:8080"

# Test 1: Register
Write-Host "Test 1: Register user..." -ForegroundColor Yellow
$registerBody = '{"name":"Test User","email":"testuser@example.com","password":"testpassword123"}'
try {
    $response = Invoke-WebRequest -Uri "$baseUrl/register" -Method Post -Body $registerBody -ContentType "application/json" -UseBasicParsing
    Write-Host "✓ Registration successful (or user exists)" -ForegroundColor Green
} catch {
    Write-Host "✓ User likely already exists" -ForegroundColor Yellow
}
Write-Host ""

# Test 2: Login
Write-Host "Test 2: Login and get token..." -ForegroundColor Yellow
$loginBody = "username=testuser@example.com&password=testpassword123"
try {
    $response = Invoke-RestMethod -Uri "$baseUrl/token" -Method Post -Body $loginBody -ContentType "application/x-www-form-urlencoded"
    $token = $response.access_token
    Write-Host "✓ Login successful!" -ForegroundColor Green
    Write-Host "Token: $($token.Substring(0, [Math]::Min(50, $token.Length)))..." -ForegroundColor Gray
} catch {
    Write-Host "✗ Login failed: $($_.Exception.Message)" -ForegroundColor Red
    exit 1
}
Write-Host ""

# Test 3: Create game with auth
Write-Host "Test 3: Create game (with authentication)..." -ForegroundColor Yellow
$gameBody = '{"name":"The Legend of Zelda","publisher":"Nintendo","year_published":1986,"gaming_system":"NES","condition":"good"}'
$headers = @{
    "Authorization" = "Bearer $token"
    "Content-Type" = "application/json"
}
try {
    $response = Invoke-RestMethod -Uri "$baseUrl/games" -Method Post -Body $gameBody -Headers $headers
    Write-Host "✓ Game created successfully!" -ForegroundColor Green
    Write-Host "Game ID: $($response.id)" -ForegroundColor Gray
} catch {
    Write-Host "✗ Game creation failed: $($_.Exception.Message)" -ForegroundColor Red
}
Write-Host ""

# Test 4: Try without auth (should fail)
Write-Host "Test 4: Try to create game without auth (should fail)..." -ForegroundColor Yellow
try {
    $response = Invoke-RestMethod -Uri "$baseUrl/games" -Method Post -Body $gameBody -ContentType "application/json"
    Write-Host "✗ Unexpected success!" -ForegroundColor Red
} catch {
    Write-Host "✓ Correctly rejected!" -ForegroundColor Green
}
Write-Host ""

Write-Host "=== Tests Complete ===" -ForegroundColor Cyan

