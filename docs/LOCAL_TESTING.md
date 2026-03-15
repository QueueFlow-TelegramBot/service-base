# Local Testing Guide

This guide shows how to test the User Service locally without needing real Telegram IDs.

## Quick Answer: No Real Telegram ID Required!

The User Service **does not validate** with Telegram's API. The `telegram_id` is just a unique string identifier stored in the database. You can use **any string value** for local testing:

```bash
# These are all valid telegram_ids for testing
"test_123"
"user_dinu"
"local_test_456"
"any_string_you_want"
```

## Testing Methods

### 1. Automated Unit Tests (Recommended)

```bash
# Install dev dependencies
make install-dev

# Run all tests
make test

# Run with coverage report
make test-cov
```

The test suite uses in-memory SQLite and creates mock users automatically. No manual setup needed!

### 2. Manual API Testing with cURL

Start the service:
```bash
# With Docker
make docker-up

# Or locally
make install
make run
```

Create a test user with any telegram_id:
```bash
curl -X POST http://localhost:8000/user \
  -H "Content-Type: application/json" \
  -d '{
    "telegram_id": "dinu_test_123",
    "display_name": "Dinu Test User"
  }'
```

Get an auth token:
```bash
curl -X POST "http://localhost:8000/user/token?telegram_id=dinu_test_123"
```

Response:
```json
{
  "access_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
  "token_type": "bearer"
}
```

Use the token to update your profile:
```bash
curl -X PUT http://localhost:8000/user \
  -H "Authorization: Bearer YOUR_TOKEN_HERE" \
  -H "Content-Type: application/json" \
  -d '{"display_name": "Updated Name"}'
```

### 3. Interactive API Docs (Swagger)

1. Start the service: `make docker-up`
2. Open http://localhost:8000/docs
3. Use any string as `telegram_id` (e.g., "test_user_1")
4. Click "Try it out" on any endpoint
5. For protected endpoints:
   - First create a user and get a token from `/user/token`
   - Click "Authorize" button at top
   - Enter: `Bearer YOUR_TOKEN`
   - Now you can access protected endpoints

### 4. Automated Test Script

Use the provided test script:
```bash
./test_api.sh
```

This script:
- Creates a user with a unique telegram_id (using timestamp)
- Tests all endpoints
- Handles authentication automatically

## Example Test Scenarios

### Scenario 1: First Time User Flow
```bash
# 1. User joins via Telegram (we simulate with any telegram_id)
curl -X POST http://localhost:8000/user \
  -H "Content-Type: application/json" \
  -d '{"telegram_id": "student_001", "display_name": "John Student"}'

# 2. Get info by telegram_id (public endpoint)
curl http://localhost:8000/user/student_001
```

### Scenario 2: Update Display Name
```bash
# 1. Create user
curl -X POST http://localhost:8000/user \
  -H "Content-Type: application/json" \
  -d '{"telegram_id": "user_002", "display_name": "Old Name"}'

# 2. Get token
TOKEN=$(curl -s -X POST "http://localhost:8000/user/token?telegram_id=user_002" | jq -r '.access_token')

# 3. Update display name
curl -X PUT http://localhost:8000/user \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d '{"display_name": "New Name"}'
```

### Scenario 3: Multiple Users
```bash
# Create multiple users with different telegram_ids
for i in {1..5}; do
  curl -X POST http://localhost:8000/user \
    -H "Content-Type: application/json" \
    -d "{\"telegram_id\": \"user_$i\", \"display_name\": \"User $i\"}"
done

# Get each user
curl http://localhost:8000/user/user_1
curl http://localhost:8000/user/user_2
```

## Common Testing Patterns

### Testing Authentication
```python
# In tests (pytest)
def test_protected_endpoint(client):
    # Create user with any telegram_id
    client.post("/user", json={
        "telegram_id": "test_123",
        "display_name": "Test"
    })

    # Get token
    token_response = client.post("/user/token?telegram_id=test_123")
    token = token_response.json()["access_token"]

    # Use token
    response = client.get(
        "/user/me",
        headers={"Authorization": f"Bearer {token}"}
    )
    assert response.status_code == 200
```

### Testing Error Cases
```bash
# Duplicate telegram_id
curl -X POST http://localhost:8000/user \
  -H "Content-Type: application/json" \
  -d '{"telegram_id": "dup_test", "display_name": "First"}'

curl -X POST http://localhost:8000/user \
  -H "Content-Type: application/json" \
  -d '{"telegram_id": "dup_test", "display_name": "Second"}'
# Should return 409 Conflict

# Non-existent user
curl http://localhost:8000/user/does_not_exist
# Should return 404 Not Found

# Invalid token
curl -X PUT http://localhost:8000/user \
  -H "Authorization: Bearer invalid_token" \
  -H "Content-Type: application/json" \
  -d '{"display_name": "New Name"}'
# Should return 401 Unauthorized
```

## Database Inspection

If you want to see the users in the database:

```bash
# Connect to PostgreSQL (Docker)
docker exec -it user-service-db psql -U user -d smartcampus_users

# List all users
SELECT * FROM users;

# Exit
\q
```

## Tips for Local Testing

1. **Use descriptive telegram_ids**: Instead of random numbers, use meaningful names like `"test_student_1"`, `"dinu_dev"`, etc.

2. **Timestamp for uniqueness**: The test script uses `date +%s` to create unique IDs

3. **Keep tokens handy**: Save your test tokens in environment variables:
   ```bash
   export TEST_TOKEN=$(curl -s -X POST "http://localhost:8000/user/token?telegram_id=your_test_id" | jq -r '.access_token')
   curl -H "Authorization: Bearer $TEST_TOKEN" http://localhost:8000/user/me
   ```

4. **Reset database**: If you want a fresh start:
   ```bash
   make docker-down
   docker volume rm user-service_postgres_data
   make docker-up
   ```

## Integration with Telegram Bot (Future)

When Cristina integrates the Telegram Bot:
- The bot will send real Telegram user IDs (e.g., `"123456789"`)
- Those are just numbers as strings
- Everything works the same way!
- No changes needed to the User Service
