# Video Game Trading API
This Read Me is AI generated.
I See Why its not always implemented this sucked to do.
A RESTful API for trading video games, built with FastAPI and SQLAlchemy. This API is compliant with Richardson Maturity Model Level 3 (HATEOAS).

## Features

- **User Management**: Self-registration, profile updates, password changes
- **Video Game Listings**: Create, read, update, and delete game listings
- **Trade Offers**: Propose, accept, reject, and cancel game trades
- **Email Notifications**: Asynchronous email notifications via Kafka
- **Multi-Container Deployment**: Load-balanced API with NGINX
- **HATEOAS Support**: All responses include hypermedia links
- **OpenAPI Documentation**: Auto-generated interactive API docs
- **SQLite Database**: Lightweight relational database for data persistence

## Requirements

- Python 3.8+
- FastAPI
- SQLAlchemy
- Uvicorn

## Installation

1. Clone the repository:
```bash
git clone <repository-url>
cd Distributed-Systems
```

2. Install dependencies:
```bash
pip install -r requirements.txt
```

3. Run the server:
```bash
python run.py
```

The API will be available at `http://localhost:8000`

## API Documentation

Once the server is running, visit:
- **Swagger UI**: http://localhost:8000/docs
- **ReDoc**: http://localhost:8000/redoc
- **OpenAPI JSON**: http://localhost:8000/openapi.json

## API Endpoints

### Users
- `POST /users` - Register a new user
- `GET /users/{user_id}` - Get user by ID
- `GET /users` - Get all users (paginated)
- `PUT /users/{user_id}` - Update user profile

### Video Games
- `POST /games?owner_id={user_id}` - Create a new game listing
- `GET /games/{game_id}` - Get game by ID
- `GET /games` - Get all games (paginated)
- `GET /users/{user_id}/games` - Get games by user
- `PUT /games/{game_id}` - Update game listing
- `DELETE /games/{game_id}` - Delete game listing

### Trade Offers
- `POST /trade-offers` - Create a new trade offer
- `GET /trade-offers/{trade_offer_id}` - Get trade offer by ID
- `GET /trade-offers` - Get all trade offers (with optional status filter)
- `GET /trade-offers/user/{user_id}/sent` - Get trade offers sent by a user
- `GET /trade-offers/user/{user_id}/received` - Get trade offers received by a user
- `PUT /trade-offers/{trade_offer_id}/accept` - Accept a trade offer
- `PUT /trade-offers/{trade_offer_id}/reject` - Reject a trade offer
- `PUT /trade-offers/{trade_offer_id}/cancel` - Cancel a trade offer

## Data Models

### User
- name
- email (unique)
- password
- street_address

### Video Game
- name
- publisher
- year_published
- gaming_system
- condition (mint, good, fair, poor)
- previous_owners (optional)
- owner_id (foreign key to User)

### Trade Offer
- offered_game_id (foreign key to VideoGame)
- requested_game_id (foreign key to VideoGame)
- offerer_id (foreign key to User)
- receiver_id (foreign key to User)
- status (pending, accepted, rejected, cancelled)
- created_at
- updated_at

## Docker

### Multi-Container Deployment Architecture

This API is deployed using a **multi-container setup** with:
- **2 API instances** (api1 and api2) running the FastAPI application
- **NGINX load balancer** distributing traffic using round-robin algorithm
- **Shared SQLite database** volume for data persistence

### Quick Start with Docker Compose

```bash
# Start all services (2 API instances + NGINX)
docker-compose up --build -d

# View logs from all services
docker-compose logs -f

# View logs from specific service
docker-compose logs -f api1
docker-compose logs -f api2
docker-compose logs -f nginx

# Stop all services
docker-compose down
```

### Access the API

Once the containers are running:
- **Load Balancer**: http://localhost:8080/ (NGINX distributes to api1 or api2)
- **Swagger UI**: http://localhost:8080/docs
- **ReDoc**: http://localhost:8080/redoc
- **Health Check**: http://localhost:8080/health

### Verify Load Distribution

Each API response includes an `X-Instance-Name` header showing which instance handled the request:
```bash
# Make multiple requests and check which instance responds
curl -I http://localhost:8080/
# Look for: X-Instance-Name: API-1 or API-2
```

### Single Container Mode (Development)

For development, you can run a single instance:
```bash
# Build the image
docker build -t videogame-trading-api .

# Run single container
docker run -d --name videogame-api -p 8000:8000 videogame-trading-api

# Access at http://localhost:8000/
```

## Email Notification System

### Architecture

The API uses Apache Kafka for asynchronous email notifications:
- **Kafka Broker**: Message queue for notification events
- **API Producers**: API instances send notification events to Kafka
- **Email Consumer**: Separate service consumes events and sends emails

### Events Triggering Notifications

| Event | Recipients | Description |
|-------|-----------|-------------|
| Password Changed | User | Notifies user when their password is changed |
| Trade Offer Created | Offerer, Receiver | Notifies both parties when a trade offer is created |
| Trade Offer Accepted | Offerer, Receiver | Notifies both parties when a trade offer is accepted |
| Trade Offer Rejected | Offerer, Receiver | Notifies both parties when a trade offer is rejected |

### Email Configuration

To enable email sending, configure SMTP settings in your `.env` file:

```bash
SMTP_HOST=smtp.gmail.com
SMTP_PORT=587
SMTP_USERNAME=your-email@gmail.com
SMTP_PASSWORD=your-app-password
FROM_EMAIL=noreply@videogametrading.com
```

**Note**: If SMTP credentials are not configured, the email service will log the email content instead of sending it.

### Kafka Configuration

Kafka is automatically configured in docker-compose.yml:
- **Bootstrap Servers**: `kafka:9092`
- **Topic**: `email-notifications`
- **Consumer Group**: `email-notification-group`

### Testing Notifications

1. **Change Password**:
```bash
curl -X PUT http://localhost:8080/users/1/password \
  -H "Content-Type: application/json" \
  -d '{"new_password": "newpassword123"}'
```

2. **Create Trade Offer**:
```bash
curl -X POST http://localhost:8080/trade-offers \
  -H "Content-Type: application/json" \
  -d '{"offered_game_id": 1, "requested_game_id": 2}'
```

3. **Accept Trade Offer**:
```bash
curl -X PUT http://localhost:8080/trade-offers/1/accept
```

4. **View Email Service Logs**:
```bash
docker-compose logs -f email-service
```

## Testing

Import the `postman_collection.json` file into Postman to test all API endpoints.

## Project Structure

```
.
├── app/
│   ├── __init__.py
│   ├── main.py           # FastAPI application
│   ├── models.py         # SQLAlchemy models
│   ├── schemas.py        # Pydantic schemas
│   ├── database.py       # Database configuration
│   ├── config.py         # Application settings
│   ├── hateoas.py        # HATEOAS link generation
│   ├── services/
│   │   └── kafka_producer.py  # Kafka notification producer
│   └── routers/
│       ├── users.py      # User endpoints
│       ├── games.py      # Game endpoints
│       └── trade_offers.py  # Trade offer endpoints
├── email_service/
│   ├── Dockerfile        # Email service container
│   ├── consumer.py       # Kafka consumer & email sender
│   └── requirements.txt  # Email service dependencies
├── nginx/
│   ├── Dockerfile        # NGINX container
│   └── nginx.conf        # Load balancer configuration
├── docker-compose.yml    # Multi-container orchestration
├── postman_collection.json
├── requirements.txt
├── run.py
└── README.md
```

## License

MIT

