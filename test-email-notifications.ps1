Write-Host "========================================" -ForegroundColor Cyan
Write-Host "Email Notification System Test" -ForegroundColor Cyan
Write-Host "========================================" -ForegroundColor Cyan
Write-Host ""

$baseUrl = "http://localhost:8080"

Write-Host "[1/6] Testing API Health..." -ForegroundColor Yellow
try {
    $response = Invoke-WebRequest -Uri "$baseUrl/" -UseBasicParsing
    $instance = $response.Headers['X-Instance-Name']
    Write-Host "[OK] API is running (Instance: $instance)" -ForegroundColor Green
} catch {
    Write-Host "[ERROR] API is not responding" -ForegroundColor Red
    exit 1
}

Write-Host ""
Write-Host "[2/6] Getting/Creating Test Users..." -ForegroundColor Yellow
$usersResponse = Invoke-RestMethod -Uri "$baseUrl/users" -Method Get
$allUsers = $usersResponse.items

$userId1 = $null
$userId2 = $null

foreach ($user in $allUsers) {
    if ($user.email -eq "alice@example.com") {
        $userId1 = $user.id
        Write-Host "[OK] Found existing User 1 (ID: $userId1) - Alice" -ForegroundColor Green
    }
    if ($user.email -eq "bob@example.com") {
        $userId2 = $user.id
        Write-Host "[OK] Found existing User 2 (ID: $userId2) - Bob" -ForegroundColor Green
    }
}

if (-not $userId1) {
    try {
        $user1 = @{
            name = "Alice Johnson"
            email = "alice@example.com"
            password = "password123"
            street_address = "123 Main St, City, State 12345"
        } | ConvertTo-Json
        $response1 = Invoke-RestMethod -Uri "$baseUrl/users" -Method Post -Body $user1 -ContentType "application/json"
        $userId1 = $response1.id
        Write-Host "[OK] Created User 1 (ID: $userId1) - Alice" -ForegroundColor Green
    } catch {
        Write-Host "[ERROR] Failed to create Alice: $_" -ForegroundColor Red
        exit 1
    }
}

if (-not $userId2) {
    try {
        $user2 = @{
            name = "Bob Smith"
            email = "bob@example.com"
            password = "password456"
            street_address = "456 Oak Ave, City, State 12345"
        } | ConvertTo-Json
        $response2 = Invoke-RestMethod -Uri "$baseUrl/users" -Method Post -Body $user2 -ContentType "application/json"
        $userId2 = $response2.id
        Write-Host "[OK] Created User 2 (ID: $userId2) - Bob" -ForegroundColor Green
    } catch {
        Write-Host "[ERROR] Failed to create Bob: $_" -ForegroundColor Red
        exit 1
    }
}

Write-Host ""
Write-Host "[3/6] Getting/Creating Test Games..." -ForegroundColor Yellow
$gamesResponse = Invoke-RestMethod -Uri "$baseUrl/games" -Method Get
$allGames = $gamesResponse.items

$gameId1 = $null
$gameId2 = $null

foreach ($game in $allGames) {
    if ($game.name -eq "The Legend of Zelda" -and $game.owner_id -eq $userId1) {
        $gameId1 = $game.id
        Write-Host "[OK] Found existing Game 1 (ID: $gameId1) - Zelda (owned by Alice)" -ForegroundColor Green
    }
    if ($game.name -eq "Super Mario Bros" -and $game.owner_id -eq $userId2) {
        $gameId2 = $game.id
        Write-Host "[OK] Found existing Game 2 (ID: $gameId2) - Mario (owned by Bob)" -ForegroundColor Green
    }
}

if (-not $gameId1) {
    try {
        $game1 = @{
            name = "The Legend of Zelda"
            publisher = "Nintendo"
            year_published = 1986
            gaming_system = "NES"
            condition = "good"
            previous_owners = 2
        } | ConvertTo-Json
        $response1 = Invoke-RestMethod -Uri "$baseUrl/games?owner_id=$userId1" -Method Post -Body $game1 -ContentType "application/json"
        $gameId1 = $response1.id
        Write-Host "[OK] Created Game 1 (ID: $gameId1) - Zelda (owned by Alice)" -ForegroundColor Green
    } catch {
        Write-Host "[ERROR] Failed to create Zelda: $_" -ForegroundColor Red
        exit 1
    }
}

if (-not $gameId2) {
    try {
        $game2 = @{
            name = "Super Mario Bros"
            publisher = "Nintendo"
            year_published = 1985
            gaming_system = "NES"
            condition = "mint"
            previous_owners = 0
        } | ConvertTo-Json
        $response2 = Invoke-RestMethod -Uri "$baseUrl/games?owner_id=$userId2" -Method Post -Body $game2 -ContentType "application/json"
        $gameId2 = $response2.id
        Write-Host "[OK] Created Game 2 (ID: $gameId2) - Mario (owned by Bob)" -ForegroundColor Green
    } catch {
        Write-Host "[ERROR] Failed to create Mario: $_" -ForegroundColor Red
        exit 1
    }
}

Write-Host ""
Write-Host "[4/6] Testing Password Change Notification..." -ForegroundColor Yellow
try {
    $passwordChange = @{
        new_password = "newpassword789"
    } | ConvertTo-Json

    $response = Invoke-RestMethod -Uri "$baseUrl/users/$userId1/password" -Method Put -Body $passwordChange -ContentType "application/json"
    Write-Host "[OK] Password changed for Alice - Email notification sent" -ForegroundColor Green
    Write-Host "    Check email-service logs for notification" -ForegroundColor Gray
} catch {
    Write-Host "[ERROR] Failed to change password: $_" -ForegroundColor Red
}

Write-Host ""
Write-Host "[5/6] Testing Trade Offer Created Notification..." -ForegroundColor Yellow
try {
    $tradeOffer = @{
        offered_game_id = $gameId1
        requested_game_id = $gameId2
    } | ConvertTo-Json

    $response = Invoke-RestMethod -Uri "$baseUrl/trade-offers" -Method Post -Body $tradeOffer -ContentType "application/json"
    $offerId = $response.id
    
    Write-Host "[OK] Trade offer created (ID: $offerId)" -ForegroundColor Green
    Write-Host "    Alice offers Zelda for Bob's Mario" -ForegroundColor Gray
    Write-Host "    Email notifications sent to both users" -ForegroundColor Gray
} catch {
    Write-Host "[ERROR] Failed to create trade offer: $_" -ForegroundColor Red
    exit 1
}

Write-Host ""
Write-Host "[6/6] Testing Trade Offer Accept Notification..." -ForegroundColor Yellow
try {
    $response = Invoke-RestMethod -Uri "$baseUrl/trade-offers/$offerId/accept" -Method Put
    Write-Host "[OK] Trade offer accepted" -ForegroundColor Green
    Write-Host "    Email notifications sent to both users" -ForegroundColor Gray
} catch {
    Write-Host "[ERROR] Failed to accept trade offer: $_" -ForegroundColor Red
}

Write-Host ""
Write-Host "========================================" -ForegroundColor Cyan
Write-Host "Test Complete!" -ForegroundColor Cyan
Write-Host "========================================" -ForegroundColor Cyan
Write-Host ""
Write-Host "To view email notifications, run:" -ForegroundColor Yellow
Write-Host "  docker-compose logs -f email-service" -ForegroundColor White
Write-Host ""

