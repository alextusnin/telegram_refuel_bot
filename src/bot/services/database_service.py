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
    
    # Car operations
    def create_car(self, user_id: int, name: str, make: str = None, model: str = None, 
                   year: int = None, license_plate: str = None, is_default: bool = False) -> Car:
        """Create a new car for a user."""
        session = self.get_session()
        try:
            # If this is set as default, unset other default cars for this user
            if is_default:
                session.query(Car).filter(
                    Car.user_id == user_id,
                    Car.is_default == True
                ).update({Car.is_default: False})
            
            # Create new car
            new_car = Car(
                user_id=user_id,
                name=name,
                make=make,
                model=model,
                year=year,
                license_plate=license_plate,
                is_default=is_default,
                is_active=True
            )
            
            session.add(new_car)
            session.commit()
            session.refresh(new_car)
            
            logger.info(f"Created new car: {new_car.name} for user {user_id}")
            return new_car
            
        except SQLAlchemyError as e:
            session.rollback()
            logger.error(f"Error creating car: {e}")
            raise
        finally:
            session.close()
    
    def get_user_cars(self, user_id: int, active_only: bool = True) -> List[Car]:
        """Get all cars for a user."""
        session = self.get_session()
        try:
            query = session.query(Car).filter(Car.user_id == user_id)
            if active_only:
                query = query.filter(Car.is_active == True)
            
            cars = query.order_by(Car.is_default.desc(), Car.created_at.desc()).all()
            return cars
            
        except SQLAlchemyError as e:
            logger.error(f"Error getting user cars: {e}")
            raise
        finally:
            session.close()
    
    def get_car_by_id(self, car_id: int, user_id: int) -> Optional[Car]:
        """Get a specific car by ID for a user."""
        session = self.get_session()
        try:
            car = session.query(Car).filter(
                Car.id == car_id,
                Car.user_id == user_id
            ).first()
            return car
            
        except SQLAlchemyError as e:
            logger.error(f"Error getting car by ID: {e}")
            raise
        finally:
            session.close()
    
    def get_default_car(self, user_id: int) -> Optional[Car]:
        """Get the default car for a user."""
        session = self.get_session()
        try:
            car = session.query(Car).filter(
                Car.user_id == user_id,
                Car.is_default == True,
                Car.is_active == True
            ).first()
            return car
            
        except SQLAlchemyError as e:
            logger.error(f"Error getting default car: {e}")
            raise
        finally:
            session.close()
    
    def set_default_car(self, car_id: int, user_id: int) -> bool:
        """Set a car as the default car for a user."""
        session = self.get_session()
        try:
            # Unset all other default cars for this user
            session.query(Car).filter(
                Car.user_id == user_id,
                Car.is_default == True
            ).update({Car.is_default: False})
            
            # Set the specified car as default
            result = session.query(Car).filter(
                Car.id == car_id,
                Car.user_id == user_id
            ).update({Car.is_default: True})
            
            session.commit()
            
            if result > 0:
                logger.info(f"Set car {car_id} as default for user {user_id}")
                return True
            return False
            
        except SQLAlchemyError as e:
            session.rollback()
            logger.error(f"Error setting default car: {e}")
            raise
        finally:
            session.close()
    
    def update_car(self, car_id: int, user_id: int, **kwargs) -> Optional[Car]:
        """Update car information."""
        session = self.get_session()
        try:
            car = session.query(Car).filter(
                Car.id == car_id,
                Car.user_id == user_id
            ).first()
            
            if not car:
                return None
            
            for key, value in kwargs.items():
                if hasattr(car, key):
                    setattr(car, key, value)
            
            session.add(car)
            session.commit()
            session.refresh(car)
            
            logger.info(f"Updated car: {car.name}")
            return car
            
        except SQLAlchemyError as e:
            session.rollback()
            logger.error(f"Error updating car: {e}")
            raise
        finally:
            session.close()
    
    def deactivate_car(self, car_id: int, user_id: int) -> bool:
        """Deactivate a car."""
        session = self.get_session()
        try:
            result = session.query(Car).filter(
                Car.id == car_id,
                Car.user_id == user_id
            ).update({Car.is_active: False})
            
            session.commit()
            
            if result > 0:
                logger.info(f"Deactivated car {car_id} for user {user_id}")
                return True
            return False
            
        except SQLAlchemyError as e:
            session.rollback()
            logger.error(f"Error deactivating car: {e}")
            raise
        finally:
            session.close()
    
    def delete_car(self, car_id: int, user_id: int) -> bool:
        """Delete a car and all its refuel entries."""
        session = self.get_session()
        try:
            # First, get the car to check if it exists and get its name for logging
            car = session.query(Car).filter(
                Car.id == car_id,
                Car.user_id == user_id
            ).first()
            
            if not car:
                return False
            
            car_name = car.name
            was_default = car.is_default
            
            # Delete the car (this will cascade delete all refuel entries due to CASCADE in the model)
            session.delete(car)
            session.commit()
            
            # If the deleted car was the default, set another car as default
            if was_default:
                remaining_cars = session.query(Car).filter(
                    Car.user_id == user_id,
                    Car.is_active == True
                ).order_by(Car.created_at.asc()).first()
                
                if remaining_cars:
                    remaining_cars.is_default = True
                    session.commit()
                    logger.info(f"Set '{remaining_cars.name}' as new default car after deleting '{car_name}'")
            
            logger.info(f"Deleted car '{car_name}' (ID: {car_id}) and all its refuel entries for user {user_id}")
            return True
            
        except SQLAlchemyError as e:
            session.rollback()
            logger.error(f"Error deleting car: {e}")
            raise
        finally:
            session.close()
    
    def get_car_refuel_count(self, car_id: int, user_id: int) -> int:
        """Get the number of refuel entries for a car."""
        session = self.get_session()
        try:
            count = session.query(Refuel).join(Car).filter(
                Car.id == car_id,
                Car.user_id == user_id
            ).count()
            return count
            
        except SQLAlchemyError as e:
            logger.error(f"Error getting car refuel count: {e}")
            raise
        finally:
            session.close()


