"""
Integration tests using real FastAPI app and PostgreSQL database.
"""
import pytest
import os
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.exc import IntegrityError
from app.main import app
from app.database import Base, get_db, init_db
from app.models import User
from app.crud import create_user, get_user_by_username, get_user_by_email
from app.schemas import UserCreate

# Use test database URL from environment or default
TEST_DATABASE_URL = os.getenv(
    "DATABASE_URL",
    "postgresql://user:password@localhost:5432/fastapi_test"
)

# Create test engine and session
engine = create_engine(TEST_DATABASE_URL)
TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


@pytest.fixture(scope="function")
def db_session():
    """
    Create a fresh database session for each test.
    Creates all tables before test and drops them after.
    """
    # Create tables
    Base.metadata.create_all(bind=engine)
    
    # Create session
    session = TestingSessionLocal()
    
    try:
        yield session
    finally:
        session.close()
        # Drop all tables after test
        Base.metadata.drop_all(bind=engine)


@pytest.fixture(scope="function")
def client(db_session):
    """
    Create a test client with database session override.
    """
    def override_get_db():
        try:
            yield db_session
        finally:
            pass
    
    app.dependency_overrides[get_db] = override_get_db
    
    with TestClient(app) as test_client:
        yield test_client
    
    app.dependency_overrides.clear()


@pytest.mark.integration
class TestUserCreation:
    """Integration tests for user creation endpoint."""
    
    def test_create_user_success(self, client, db_session):
        """Test successful user creation."""
        user_data = {
            "username": "testuser",
            "email": "test@example.com",
            "password": "password123"
        }
        
        response = client.post("/users/", json=user_data)
        
        assert response.status_code == 201
        data = response.json()
        assert data["username"] == "testuser"
        assert data["email"] == "test@example.com"
        assert "id" in data
        assert "created_at" in data
        assert "password" not in data
        assert "password_hash" not in data
        
        # Verify user in database
        user = db_session.query(User).filter(User.username == "testuser").first()
        assert user is not None
        assert user.email == "test@example.com"
        assert user.password_hash != "password123"  # Should be hashed
    
    def test_create_user_duplicate_username(self, client, db_session):
        """Test that duplicate username returns 400 error."""
        user_data = {
            "username": "testuser",
            "email": "test1@example.com",
            "password": "password123"
        }
        
        # Create first user
        response1 = client.post("/users/", json=user_data)
        assert response1.status_code == 201
        
        # Try to create second user with same username
        user_data2 = {
            "username": "testuser",
            "email": "test2@example.com",
            "password": "password456"
        }
        
        response2 = client.post("/users/", json=user_data2)
        assert response2.status_code == 400
        assert "username" in response2.json()["detail"].lower()
    
    def test_create_user_duplicate_email(self, client, db_session):
        """Test that duplicate email returns 400 error."""
        user_data = {
            "username": "testuser1",
            "email": "test@example.com",
            "password": "password123"
        }
        
        # Create first user
        response1 = client.post("/users/", json=user_data)
        assert response1.status_code == 201
        
        # Try to create second user with same email
        user_data2 = {
            "username": "testuser2",
            "email": "test@example.com",
            "password": "password456"
        }
        
        response2 = client.post("/users/", json=user_data2)
        assert response2.status_code == 400
        assert "email" in response2.json()["detail"].lower()
    
    def test_create_user_invalid_email(self, client):
        """Test that invalid email returns 422 validation error."""
        user_data = {
            "username": "testuser",
            "email": "invalid-email",
            "password": "password123"
        }
        
        response = client.post("/users/", json=user_data)
        assert response.status_code == 422
    
    def test_create_user_short_password(self, client):
        """Test that short password returns 422 validation error."""
        user_data = {
            "username": "testuser",
            "email": "test@example.com",
            "password": "pass"
        }
        
        response = client.post("/users/", json=user_data)
        assert response.status_code == 422


@pytest.mark.integration
class TestHealthEndpoints:
    """Integration tests for health check endpoints."""
    
    def test_root_endpoint(self, client):
        """Test root endpoint returns welcome message."""
        response = client.get("/")
        assert response.status_code == 200
        assert "message" in response.json()
    
    def test_health_endpoint(self, client):
        """Test health check endpoint."""
        response = client.get("/health")
        assert response.status_code == 200
        assert response.json()["status"] == "healthy"


@pytest.mark.integration
class TestCRUDFunctions:
    """Integration tests for CRUD functions."""
    
    def test_create_user_with_integrity_error(self, db_session):
        """Test create_user raises IntegrityError on duplicate."""
        user_data = UserCreate(
            username="testuser",
            email="test@example.com",
            password="password123"
        )
        
        # Create first user
        create_user(db_session, user_data)
        
        # Try to create duplicate - should raise IntegrityError
        with pytest.raises(IntegrityError):
            create_user(db_session, user_data)
    
    def test_get_user_by_username_not_found(self, db_session):
        """Test get_user_by_username returns None when not found."""
        result = get_user_by_username(db_session, "nonexistent")
        assert result is None
    
    def test_get_user_by_email_not_found(self, db_session):
        """Test get_user_by_email returns None when not found."""
        result = get_user_by_email(db_session, "nonexistent@example.com")
        assert result is None
    
    def test_get_user_by_username_found(self, db_session):
        """Test get_user_by_username returns user when found."""
        user_data = UserCreate(
            username="testuser",
            email="test@example.com",
            password="password123"
        )
        create_user(db_session, user_data)
        
        result = get_user_by_username(db_session, "testuser")
        assert result is not None
        assert result.username == "testuser"
    
    def test_get_user_by_email_found(self, db_session):
        """Test get_user_by_email returns user when found."""
        user_data = UserCreate(
            username="testuser",
            email="test@example.com",
            password="password123"
        )
        create_user(db_session, user_data)
        
        result = get_user_by_email(db_session, "test@example.com")
        assert result is not None
        assert result.email == "test@example.com"


@pytest.mark.integration
class TestRouteEdgeCases:
    """Test edge cases in routes."""
    
    def test_create_user_race_condition_integrity_error(self, client, db_session, monkeypatch):
        """Test IntegrityError handling in route when checks pass but insert fails."""
        from app import routes
        
        # Mock create_user in routes module to raise IntegrityError
        def mock_create_user(db, user):
            raise IntegrityError("mock", "mock", "mock")
        
        monkeypatch.setattr(routes, "create_user", mock_create_user)
        
        user_data = {
            "username": "testuser",
            "email": "test@example.com",
            "password": "password123"
        }
        
        response = client.post("/users/", json=user_data)
        assert response.status_code == 400
        assert "already exists" in response.json()["detail"].lower()


@pytest.mark.integration
class TestDatabaseFunctions:
    """Integration tests for database functions."""
    
    def test_get_db_generator(self):
        """Test get_db yields a session."""
        gen = get_db()
        db = next(gen)
        assert db is not None
        try:
            gen.close()
        except StopIteration:
            pass
