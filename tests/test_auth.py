import pytest
from datetime import timedelta
from app.auth import create_access_token, verify_token
from app.schemas import TokenData
from jose import jwt
from app.config import settings


class TestJWTAuth:
    """Tests for JWT authentication functionality."""

    def test_create_access_token(self):
        """Test JWT token creation."""
        data = {"sub": "test_user_123"}
        token = create_access_token(data)

        assert token is not None
        assert len(token) > 0

        # Decode and verify
        payload = jwt.decode(
            token, settings.JWT_SECRET_KEY, algorithms=[settings.JWT_ALGORITHM]
        )
        assert payload["sub"] == "test_user_123"
        assert "exp" in payload

    def test_create_access_token_with_expiry(self):
        """Test JWT token creation with custom expiry."""
        data = {"sub": "test_user_123"}
        expires_delta = timedelta(minutes=5)
        token = create_access_token(data, expires_delta)

        payload = jwt.decode(
            token, settings.JWT_SECRET_KEY, algorithms=[settings.JWT_ALGORITHM]
        )
        assert payload["sub"] == "test_user_123"

    def test_token_contains_expiration(self):
        """Test that token contains expiration claim."""
        data = {"sub": "test_user_123"}
        token = create_access_token(data)

        payload = jwt.decode(
            token, settings.JWT_SECRET_KEY, algorithms=[settings.JWT_ALGORITHM]
        )
        assert "exp" in payload
