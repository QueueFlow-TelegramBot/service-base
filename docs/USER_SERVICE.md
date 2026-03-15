# User Service - Summary

## Project Structure

```
user-service/
├── app/
│   ├── __init__.py
│   ├── main.py              # FastAPI app, routes, middleware
│   ├── config.py            # Settings from .env
│   ├── database.py          # SQLAlchemy setup
│   ├── models.py            # User database model
│   ├── schemas.py           # Pydantic request/response schemas
│   ├── auth.py              # JWT token creation/validation
│   ├── logger.py            # Structured JSON logging
│   └── routers/
│       └── users.py         # User endpoints
│
├── tests/
│   ├── conftest.py          # Pytest fixtures
│   ├── test_health.py       # Health/root endpoint tests
│   ├── test_users.py        # User CRUD tests
│   └── test_auth.py         # JWT authentication tests
│
├── .env                     # Environment variables (gitignored)
├── .env.example             # Template for .env
├── requirements.txt         # Production dependencies
├── requirements-dev.txt     # Dev dependencies (pytest, etc.)
├── Dockerfile               # Container image
├── docker-compose.yml       # Multi-container setup (app + DB)
├── Makefile                 # Common commands
├── pytest.ini               # Pytest configuration
├── start.sh                 # Local startup script
├── test_api.sh              # API test script
├── README.md                # Main documentation
├── LOCAL_TESTING.md         # Testing guide
└── PROJECT_SUMMARY.md       # This file
```

## API Endpoints

### Public Endpoints
- `GET /` - API information
- `GET /health` - Health check
- `POST /user` - Create new user
- `POST /user/token?telegram_id={id}` - Generate JWT token
- `GET /user/{telegram_id}` - Get user by Telegram ID

### Protected Endpoints (require Bearer token)
- `GET /user/me` - Get current user info
- `PUT /user` - Update current user's display name

## Quick Start Commands

```bash
# 1. Start with Docker (recommended)
make docker-up
# Access: http://localhost:8000
# Docs: http://localhost:8000/docs

# 2. Or run locally
make install
make run

# 3. Run tests
make install-dev
make test

# 4. Test the API
./test_api.sh

# 5. Stop services
make docker-down
```

## Configuration (.env)

Key environment variables:
```bash
DATABASE_URL=postgresql://user:password@postgres:5432/smartcampus_users
JWT_SECRET_KEY=dev-secret-key-change-in-production-please
LOG_LEVEL=INFO
ENV=development
```

## Database Schema

**users** table:
- `id` - UUID (primary key)
- `telegram_id` - String (unique, indexed)
- `display_name` - String
- `created_at` - Timestamp
- `updated_at` - Timestamp (auto-updated)

## Testing

### Unit Tests
```bash
make test              # Run all tests
make test-cov          # With coverage report
```

Test coverage includes:
- User creation (success, duplicates, validation)
- User updates (authenticated only)
- User retrieval (by telegram_id, current user)
- Token generation and validation
- Authentication/authorization
- Multi-user scenarios

### Manual Testing
```bash
# Create a user (any telegram_id works!)
curl -X POST http://localhost:8000/user \
  -H "Content-Type: application/json" \
  -d '{"telegram_id": "test_123", "display_name": "Test User"}'

# Get token
curl -X POST "http://localhost:8000/user/token?telegram_id=test_123"

# Use token
curl -X GET http://localhost:8000/user/me \
  -H "Authorization: Bearer YOUR_TOKEN"
```

**No real Telegram ID needed!** Use any string like `"test_123"`, `"test_dev"`, etc.

## Key Features

### 1. Authentication Flow
1. User created via `POST /user` (first time Telegram join)
2. Token generated via `POST /user/token`
3. Token used in `Authorization: Bearer {token}` header
4. Protected endpoints verify token and load user

### 2. Structured Logging
All operations logged in JSON format:
```json
{"time": "2026-03-13 10:30:00", "level": "INFO", "name": "user-service", "message": "User created: id=abc-123"}
```

### 3. Error Handling
- 400 - Bad request / Validation errors
- 401 - Unauthorized (invalid token)
- 404 - User not found
- 409 - Conflict (duplicate telegram_id)
- 422 - Unprocessable entity (validation)
- 500 - Internal server error

### 4. Docker Support
- Multi-stage build for smaller images
- Non-root user for security
- Health checks for PostgreSQL
- Volume persistence for database
- Hot-reload in development

## Integration Points

### With Telegram Bot (Cristina)
```python
# Bot sends user's Telegram ID to create user
response = requests.post(
    "http://user-service:8000/user",
    json={
        "telegram_id": str(update.effective_user.id),
        "display_name": update.effective_user.first_name
    }
)
```

### With Scheduling Service (Tudor)
```python
# Scheduling service can get user info
response = requests.get(
    f"http://user-service:8000/user/{telegram_id}"
)
user_data = response.json()
display_name = user_data["display_name"]
```

## Technologies Used

- **FastAPI** - Modern Python web framework
- **SQLAlchemy** - ORM for database
- **PostgreSQL** - Relational database
- **PyJWT** - JWT token handling
- **Pydantic** - Data validation
- **pytest** - Testing framework
- **Docker** - Containerization
- **Uvicorn** - ASGI server

## Useful Resources

- API Docs: http://localhost:8000/docs
- Health Check: http://localhost:8000/health
- Testing Guide: See `LOCAL_TESTING.md`
- Main README: See `README.md`
