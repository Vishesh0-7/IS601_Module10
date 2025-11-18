"""
Unit tests for password hashing and schema validation.
"""
import pytest
from pydantic import ValidationError
from sqlalchemy.exc import IntegrityError
from app.security import hash_password, verify_password
from app.schemas import UserCreate, UserRead
from app.models import User
from app.crud import get_user_by_username, get_user_by_email, create_user


@pytest.mark.unit
class TestPasswordHashing:
    """Test password hashing and verification."""
    
    def test_hash_password(self):
        """Test that password hashing works."""
        password = "securepassword123"
        hashed = hash_password(password)
        
        assert hashed != password
        assert len(hashed) > 0
        assert hashed.startswith("$2b$")  # bcrypt prefix
    
    def test_verify_password_correct(self):
        """Test password verification with correct password."""
        password = "securepassword123"
        hashed = hash_password(password)
        
        assert verify_password(password, hashed) is True
    
    def test_verify_password_incorrect(self):
        """Test password verification with incorrect password."""
        password = "securepassword123"
        wrong_password = "wrongpassword"
        hashed = hash_password(password)
        
        assert verify_password(wrong_password, hashed) is False
    
    def test_different_hashes_for_same_password(self):
        """Test that same password produces different hashes (salt)."""
        password = "securepassword123"
        hash1 = hash_password(password)
        hash2 = hash_password(password)
        
        assert hash1 != hash2
        assert verify_password(password, hash1) is True
        assert verify_password(password, hash2) is True


@pytest.mark.unit
class TestUserCreateSchema:
    """Test UserCreate schema validation."""
    
    def test_valid_user_create(self):
        """Test creating valid UserCreate schema."""
        user = UserCreate(
            username="testuser",
            email="test@example.com",
            password="password123"
        )
        
        assert user.username == "testuser"
        assert user.email == "test@example.com"
        assert user.password == "password123"
    
    def test_invalid_email(self):
        """Test that invalid email raises validation error."""
        with pytest.raises(ValidationError) as exc_info:
            UserCreate(
                username="testuser",
                email="invalid-email",
                password="password123"
            )
        
        errors = exc_info.value.errors()
        assert any(error["type"] == "value_error" for error in errors)
    
    def test_short_username(self):
        """Test that username shorter than 3 characters raises error."""
        with pytest.raises(ValidationError) as exc_info:
            UserCreate(
                username="ab",
                email="test@example.com",
                password="password123"
            )
        
        errors = exc_info.value.errors()
        assert any("username" in str(error) for error in errors)
    
    def test_short_password(self):
        """Test that password shorter than 8 characters raises error."""
        with pytest.raises(ValidationError) as exc_info:
            UserCreate(
                username="testuser",
                email="test@example.com",
                password="pass"
            )
        
        errors = exc_info.value.errors()
        assert any("password" in str(error) for error in errors)
    
    def test_missing_fields(self):
        """Test that missing required fields raise validation error."""
        with pytest.raises(ValidationError):
            UserCreate(username="testuser")
    
    def test_long_username(self):
        """Test that username longer than 50 characters raises error."""
        with pytest.raises(ValidationError) as exc_info:
            UserCreate(
                username="a" * 51,
                email="test@example.com",
                password="password123"
            )
        
        errors = exc_info.value.errors()
        assert any("username" in str(error) for error in errors)


@pytest.mark.unit
class TestUserModel:
    """Test User model."""
    
    def test_user_repr(self):
        """Test User __repr__ method."""
        user = User(
            id=1,
            username="testuser",
            email="test@example.com",
            password_hash="hashed"
        )
        
        repr_str = repr(user)
        assert "User" in repr_str
        assert "testuser" in repr_str
        assert "test@example.com" in repr_str
        assert str(1) in repr_str


@pytest.mark.unit
class TestUserReadSchema:
    """Test UserRead schema."""
    
    def test_user_read_from_orm(self):
        """Test UserRead schema with from_attributes."""
        from datetime import datetime
        user = User(
            id=1,
            username="testuser",
            email="test@example.com",
            password_hash="hashed",
            created_at=datetime.now()
        )
        
        user_read = UserRead.model_validate(user)
        assert user_read.id == 1
        assert user_read.username == "testuser"
        assert user_read.email == "test@example.com"
        assert hasattr(user_read, 'created_at')
