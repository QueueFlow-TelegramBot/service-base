import pytest
from datetime import datetime


class TestCreateUser:
    """Tests for POST /user endpoint."""

    def test_create_user_success(self, client, test_user_data):
        """Test successful user creation."""
        response = client.post("/user", json=test_user_data)

        assert response.status_code == 201
        data = response.json()
        assert data["telegram_id"] == test_user_data["telegram_id"]
        assert data["display_name"] == test_user_data["display_name"]
        assert "id" in data
        assert "created_at" in data

    def test_create_user_duplicate_telegram_id(self, client, test_user_data):
        """Test creating user with duplicate telegram_id fails."""
        # Create first user
        response1 = client.post("/user", json=test_user_data)
        assert response1.status_code == 201

        # Try to create duplicate
        response2 = client.post("/user", json=test_user_data)
        assert response2.status_code == 409
        assert "already exists" in response2.json()["detail"]

    def test_create_user_missing_telegram_id(self, client):
        """Test creating user without telegram_id fails."""
        response = client.post("/user", json={"display_name": "Test"})
        assert response.status_code == 422

    def test_create_user_missing_display_name(self, client):
        """Test creating user without display_name fails."""
        response = client.post("/user", json={"telegram_id": "123"})
        assert response.status_code == 422

    def test_create_user_empty_display_name(self, client):
        """Test creating user with empty display_name fails."""
        response = client.post(
            "/user", json={"telegram_id": "test_123", "display_name": ""}
        )
        assert response.status_code == 422


class TestUpdateUser:
    """Tests for PUT /user endpoint."""

    def test_update_user_success(self, client, test_user_data, get_auth_token):
        """Test successful user update."""
        new_name = "Updated Test User"
        response = client.put(
            "/user",
            json={"display_name": new_name},
            headers={"Authorization": f"Bearer {get_auth_token}"},
        )

        assert response.status_code == 200
        data = response.json()
        assert data["display_name"] == new_name
        assert data["telegram_id"] == test_user_data["telegram_id"]

    def test_update_user_without_auth(self, client):
        """Test updating user without authentication fails."""
        response = client.put("/user", json={"display_name": "New Name"})
        assert response.status_code == 401

    def test_update_user_invalid_token(self, client):
        """Test updating user with invalid token fails."""
        response = client.put(
            "/user",
            json={"display_name": "New Name"},
            headers={"Authorization": "Bearer invalid_token"},
        )
        assert response.status_code == 401

    def test_update_user_empty_display_name(self, client, get_auth_token):
        """Test updating user with empty display_name fails."""
        response = client.put(
            "/user",
            json={"display_name": ""},
            headers={"Authorization": f"Bearer {get_auth_token}"},
        )
        assert response.status_code == 422


class TestGetUser:
    """Tests for GET /user endpoints."""

    def test_get_user_by_telegram_id(self, client, test_user_data, create_test_user):
        """Test getting user by telegram_id."""
        response = client.get(f"/user/{test_user_data['telegram_id']}")

        assert response.status_code == 200
        data = response.json()
        assert data["telegram_id"] == test_user_data["telegram_id"]
        assert data["display_name"] == test_user_data["display_name"]

    def test_get_user_not_found(self, client):
        """Test getting non-existent user."""
        response = client.get("/user/nonexistent_user")
        assert response.status_code == 404
        assert "not found" in response.json()["detail"].lower()

    def test_get_current_user(self, client, test_user_data, get_auth_token):
        """Test getting current user info."""
        response = client.get(
            "/user/me", headers={"Authorization": f"Bearer {get_auth_token}"}
        )

        assert response.status_code == 200
        data = response.json()
        assert data["telegram_id"] == test_user_data["telegram_id"]

    def test_get_current_user_without_auth(self, client):
        """Test getting current user without authentication fails."""
        response = client.get("/user/me")
        assert response.status_code == 401


class TestTokenGeneration:
    """Tests for POST /user/token endpoint."""

    def test_generate_token_success(self, client, test_user_data, create_test_user):
        """Test successful token generation."""
        response = client.post(
            f"/user/token?telegram_id={test_user_data['telegram_id']}"
        )

        assert response.status_code == 200
        data = response.json()
        assert "access_token" in data
        assert data["token_type"] == "bearer"
        assert len(data["access_token"]) > 0

    def test_generate_token_user_not_found(self, client):
        """Test token generation for non-existent user fails."""
        response = client.post("/user/token?telegram_id=nonexistent_user")
        assert response.status_code == 404

    def test_token_is_valid(self, client, test_user_data, create_test_user):
        """Test that generated token works for authentication."""
        # Generate token
        token_response = client.post(
            f"/user/token?telegram_id={test_user_data['telegram_id']}"
        )
        token = token_response.json()["access_token"]

        # Use token to access protected endpoint
        response = client.get("/user/me", headers={"Authorization": f"Bearer {token}"})

        assert response.status_code == 200
        assert response.json()["telegram_id"] == test_user_data["telegram_id"]


class TestMultipleUsers:
    """Tests for scenarios with multiple users."""

    def test_create_multiple_users(self, client, test_user_data, another_user_data):
        """Test creating multiple users."""
        response1 = client.post("/user", json=test_user_data)
        response2 = client.post("/user", json=another_user_data)

        assert response1.status_code == 201
        assert response2.status_code == 201
        assert response1.json()["id"] != response2.json()["id"]

    def test_user_isolation(self, client, test_user_data, another_user_data):
        """Test that users can only update their own profiles."""
        # Create two users
        client.post("/user", json=test_user_data)
        client.post("/user", json=another_user_data)

        # Get token for first user
        token_response = client.post(
            f"/user/token?telegram_id={test_user_data['telegram_id']}"
        )
        token = token_response.json()["access_token"]

        # Update with first user's token
        response = client.put(
            "/user",
            json={"display_name": "Updated Name"},
            headers={"Authorization": f"Bearer {token}"},
        )

        assert response.status_code == 200

        # Verify second user is unchanged
        user2_response = client.get(f"/user/{another_user_data['telegram_id']}")
        assert (
            user2_response.json()["display_name"] == another_user_data["display_name"]
        )
