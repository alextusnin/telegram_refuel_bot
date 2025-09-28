"""Database service for PostgreSQL operations using SQLAlchemy."""

import logging
from typing import Optional, List
from sqlalchemy import create_engine, text
from sqlalchemy.orm import sessionmaker, Session
from sqlalchemy.exc import SQLAlchemyError

from config.settings import settings
from ..models.database import User, Car, Refuel, Base

logger = logging.getLogger(__name__)

class DatabaseService:
    """Database service for PostgreSQL operations."""
    
    def __init__(self):
        """Initialize the database service."""
        self.engine = create_engine(settings.DATABASE_URL)
        self.SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=self.engine)
        logger.info(f"DatabaseService initialized with URL: {settings.DATABASE_URL}")
    
    def get_session(self) -> Session:
        """Get a database session."""
        return self.SessionLocal()
    
    def create_tables(self):
        """Create all tables if they don't exist."""
        try:
            Base.metadata.create_all(bind=self.engine)
            logger.info("Database tables created/verified successfully")
        except SQLAlchemyError as e:
            logger.error(f"Error creating database tables: {e}")
            raise
    
    def test_connection(self) -> bool:
        """Test database connection."""
        try:
            with self.engine.connect() as connection:
                connection.execute(text("SELECT 1"))
            logger.info("Database connection test successful")
            return True
        except SQLAlchemyError as e:
            logger.error(f"Database connection test failed: {e}")
            return False
    
    # User operations
    def create_or_get_user(self, telegram_user) -> User:
        """Create a new user or get existing user by Telegram ID."""
        session = self.get_session()
        try:
            # Check if user already exists
            existing_user = session.query(User).filter(
                User.telegram_id == telegram_user.id
            ).first()
            
            if existing_user:
                logger.info(f"Found existing user: {existing_user.telegram_id}")
                return existing_user
            
            # Create new user
            new_user = User(
                telegram_id=telegram_user.id,
                username=telegram_user.username,
                first_name=telegram_user.first_name,
                last_name=telegram_user.last_name,
                language_code=telegram_user.language_code,
                is_active=True
            )
            
            session.add(new_user)
            session.commit()
            session.refresh(new_user)
            
            logger.info(f"Created new user: {new_user.telegram_id} ({new_user.username})")
            return new_user
            
        except SQLAlchemyError as e:
            session.rollback()
            logger.error(f"Error creating/getting user: {e}")
            raise
        finally:
            session.close()
    
    def get_user_by_telegram_id(self, telegram_id: int) -> Optional[User]:
        """Get user by Telegram ID."""
        session = self.get_session()
        try:
            user = session.query(User).filter(User.telegram_id == telegram_id).first()
            return user
        except SQLAlchemyError as e:
            logger.error(f"Error getting user by telegram_id {telegram_id}: {e}")
            raise
        finally:
            session.close()
    
    def update_user(self, user: User, **kwargs) -> User:
        """Update user information."""
        session = self.get_session()
        try:
            for key, value in kwargs.items():
                if hasattr(user, key):
                    setattr(user, key, value)
            
            session.add(user)
            session.commit()
            session.refresh(user)
            
            logger.info(f"Updated user: {user.telegram_id}")
            return user
            
        except SQLAlchemyError as e:
            session.rollback()
            logger.error(f"Error updating user: {e}")
            raise
        finally:
            session.close()
    
    def deactivate_user(self, telegram_id: int) -> bool:
        """Deactivate a user."""
        session = self.get_session()
        try:
            user = session.query(User).filter(User.telegram_id == telegram_id).first()
            if user:
                user.is_active = False
                session.commit()
                logger.info(f"Deactivated user: {telegram_id}")
                return True
            return False
        except SQLAlchemyError as e:
            session.rollback()
            logger.error(f"Error deactivating user: {e}")
            raise
        finally:
            session.close()
    
    def get_user_stats(self, telegram_id: int) -> dict:
        """Get user statistics."""
        session = self.get_session()
        try:
            user = session.query(User).filter(User.telegram_id == telegram_id).first()
            if not user:
                return {}
            
            # Get car count
            car_count = session.query(Car).filter(Car.user_id == user.id).count()
            
            # Get refuel count
            refuel_count = session.query(Refuel).join(Car).filter(Car.user_id == user.id).count()
            
            return {
                'user_id': user.id,
                'telegram_id': user.telegram_id,
                'username': user.username,
                'first_name': user.first_name,
                'car_count': car_count,
                'refuel_count': refuel_count,
                'is_active': user.is_active,
                'created_at': user.created_at.isoformat() if user.created_at else None
            }
            
        except SQLAlchemyError as e:
            logger.error(f"Error getting user stats: {e}")
            raise
        finally:
            session.close()


