# Video Game Trading API

A RESTful API for trading video games, built with FastAPI and SQLAlchemy. This API is compliant with Richardson Maturity Model Level 3 (HATEOAS).

## Features

- **User Management**: Self-registration, profile updates
- **Video Game Listings**: Create, read, update, and delete game listings
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

## Testing

Run the test suite:
```bash
python debug_test.py
```

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
│   └── routers/
│       ├── users.py      # User endpoints
│       └── games.py      # Game endpoints
├── requirements.txt
├── run.py
└── README.md
```

## License

MIT

