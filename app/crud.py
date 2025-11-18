"""
CRUD operations for database models.
"""
from sqlalchemy.orm import Session
from sqlalchemy.exc import IntegrityError
from app.models import User
from app.schemas import UserCreate
from app.security import hash_password


def create_user(db: Session, user: UserCreate) -> User:
    """
    Create a new user with hashed password.
    
    Args:
        db: Database session
        user: UserCreate schema with plain password
        
    Returns:
        Created User object
        
    Raises:
        IntegrityError: If username or email already exists
    """
    hashed_pwd = hash_password(user.password)
    db_user = User(
        username=user.username,
        email=user.email,
        password_hash=hashed_pwd
    )
    
    try:
        db.add(db_user)
        db.commit()
        db.refresh(db_user)
        return db_user
    except IntegrityError as e:
        db.rollback()
        raise e


def get_user_by_username(db: Session, username: str) -> User | None:
    """
    Get user by username.
    
    Args:
        db: Database session
        username: Username to search for
        
    Returns:
        User object or None if not found
    """
    return db.query(User).filter(User.username == username).first()


def get_user_by_email(db: Session, email: str) -> User | None:
    """
    Get user by email.
    
    Args:
        db: Database session
        email: Email to search for
        
    Returns:
        User object or None if not found
    """
    return db.query(User).filter(User.email == email).first()
