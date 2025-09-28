"""SQLAlchemy database models with relationships."""

from datetime import datetime
from typing import Optional, List
from sqlalchemy import Column, Integer, Float, String, DateTime, ForeignKey, Index, Boolean
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship, Session
from sqlalchemy.sql import func

Base = declarative_base()

class User(Base):
    """User model - stores Telegram user information."""
    
    __tablename__ = 'users'
    
    # Primary key
    id = Column(Integer, primary_key=True, autoincrement=True)
    
    # Telegram user information
    telegram_id = Column(Integer, unique=True, nullable=False, index=True)
    username = Column(String(255), nullable=True)
    first_name = Column(String(255), nullable=True)
    last_name = Column(String(255), nullable=True)
    
    # User preferences
    is_active = Column(Boolean, default=True, nullable=False)
    language_code = Column(String(10), nullable=True)
    
    # Timestamps
    created_at = Column(DateTime, default=func.now(), nullable=False)
    updated_at = Column(DateTime, default=func.now(), onupdate=func.now(), nullable=False)
    
    # Relationships
    cars = relationship("Car", back_populates="user", cascade="all, delete-orphan")
    
    def __repr__(self):
        return f"<User(id={self.id}, telegram_id={self.telegram_id}, username={self.username})>"
    
    def to_dict(self):
        """Convert to dictionary."""
        return {
            'id': self.id,
            'telegram_id': self.telegram_id,
            'username': self.username,
            'first_name': self.first_name,
            'last_name': self.last_name,
            'is_active': self.is_active,
            'language_code': self.language_code,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'updated_at': self.updated_at.isoformat() if self.updated_at else None
        }

class Car(Base):
    """Car model - stores car information for each user."""
    
    __tablename__ = 'cars'
    
    # Primary key
    id = Column(Integer, primary_key=True, autoincrement=True)
    
    # Foreign key to user
    user_id = Column(Integer, ForeignKey('users.id', ondelete='CASCADE'), nullable=False, index=True)
    
    # Car information
    name = Column(String(255), nullable=False)  # e.g., "My Honda Civic"
    make = Column(String(100), nullable=True)   # e.g., "Honda"
    model = Column(String(100), nullable=True)  # e.g., "Civic"
    year = Column(Integer, nullable=True)       # e.g., 2020
    license_plate = Column(String(20), nullable=True)
    
    # Car settings
    is_active = Column(Boolean, default=True, nullable=False)
    is_default = Column(Boolean, default=False, nullable=False)  # User's default car
    
    # Timestamps
    created_at = Column(DateTime, default=func.now(), nullable=False)
    updated_at = Column(DateTime, default=func.now(), onupdate=func.now(), nullable=False)
    
    # Relationships
    user = relationship("User", back_populates="cars")
    refuels = relationship("Refuel", back_populates="car", cascade="all, delete-orphan")
    
    # Indexes
    __table_args__ = (
        Index('idx_user_car', 'user_id', 'name'),
        Index('idx_user_default', 'user_id', 'is_default'),
    )
    
    def __repr__(self):
        return f"<Car(id={self.id}, user_id={self.user_id}, name={self.name})>"
    
    def to_dict(self):
        """Convert to dictionary."""
        return {
            'id': self.id,
            'user_id': self.user_id,
            'name': self.name,
            'make': self.make,
            'model': self.model,
            'year': self.year,
            'license_plate': self.license_plate,
            'is_active': self.is_active,
            'is_default': self.is_default,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'updated_at': self.updated_at.isoformat() if self.updated_at else None
        }

class Refuel(Base):
    """Refuel model - stores refuel entries for each car."""
    
    __tablename__ = 'refuels'
    
    # Primary key
    id = Column(Integer, primary_key=True, autoincrement=True)
    
    # Foreign key to car
    car_id = Column(Integer, ForeignKey('cars.id', ondelete='CASCADE'), nullable=False, index=True)
    
    # Refuel data
    date = Column(DateTime, nullable=False, default=func.now())
    odometer = Column(Float, nullable=False)
    liters = Column(Float, nullable=False)
    total_price = Column(Float, nullable=False)
    
    # Calculated fields
    price_per_liter = Column(Float, nullable=True)
    distance_since_last = Column(Float, nullable=True)
    fuel_efficiency = Column(Float, nullable=True)
    
    # Additional information
    fuel_type = Column(String(50), nullable=True)  # e.g., "Regular", "Premium"
    station_name = Column(String(255), nullable=True)
    comment = Column(String(500), nullable=True)
    
    # Timestamps
    created_at = Column(DateTime, default=func.now(), nullable=False)
    updated_at = Column(DateTime, default=func.now(), onupdate=func.now(), nullable=False)
    
    # Relationships
    car = relationship("Car", back_populates="refuels")
    
    # Indexes for better performance
    __table_args__ = (
        Index('idx_car_date', 'car_id', 'date'),
        Index('idx_car_odometer', 'car_id', 'odometer'),
    )
    
    def __repr__(self):
        return f"<Refuel(id={self.id}, car_id={self.car_id}, odometer={self.odometer})>"
    
    def calculate_price_per_liter(self):
        """Calculate price per liter."""
        if self.liters and self.total_price and self.liters > 0:
            self.price_per_liter = round(self.total_price / self.liters, 2)
    
    def calculate_distance(self, previous_odometer: float) -> Optional[float]:
        """Calculate distance since last refuel."""
        if not self.odometer or not previous_odometer:
            return None
        if self.odometer < previous_odometer:
            return None  # Invalid odometer reading
        return round(self.odometer - previous_odometer, 1)
    
    def calculate_efficiency(self, distance: float) -> Optional[float]:
        """Calculate fuel efficiency in km/L."""
        if not self.liters or self.liters <= 0 or not distance:
            return None
        return round(distance / self.liters, 2)
    
    def to_dict(self):
        """Convert to dictionary."""
        return {
            'id': self.id,
            'car_id': self.car_id,
            'date': self.date.isoformat() if self.date else None,
            'odometer': self.odometer,
            'liters': self.liters,
            'total_price': self.total_price,
            'price_per_liter': self.price_per_liter,
            'distance_since_last': self.distance_since_last,
            'fuel_efficiency': self.fuel_efficiency,
            'fuel_type': self.fuel_type,
            'station_name': self.station_name,
            'comment': self.comment,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'updated_at': self.updated_at.isoformat() if self.updated_at else None
        }
