"""Database management utilities."""

import sqlite3
import os
import logging
from typing import List, Optional
from datetime import datetime

from ..models.refuel import RefuelEntry
from config.settings import settings

logger = logging.getLogger(__name__)

class DatabaseManager:
    """Manages SQLite database operations for the refuel bot."""
    
    def __init__(self, db_path: str = None):
        """Initialize database manager.
        
        Args:
            db_path: Path to SQLite database file. Uses settings default if None.
        """
        self.db_path = db_path or settings.DATABASE_PATH
        self._ensure_database_directory()
        self._create_tables()
        logger.info(f"DatabaseManager initialized with database: {self.db_path}")
    
    def _ensure_database_directory(self):
        """Ensure the database directory exists."""
        db_dir = os.path.dirname(self.db_path)
        if db_dir:  # Only create directory if path has a directory component
            os.makedirs(db_dir, exist_ok=True)
            logger.debug(f"Ensured database directory exists: {db_dir}")
    
    def _create_tables(self):
        """Create database tables if they don't exist."""
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                
                # Create refuel_entries table
                cursor.execute('''
                    CREATE TABLE IF NOT EXISTS refuel_entries (
                        id INTEGER PRIMARY KEY AUTOINCREMENT,
                        user_id INTEGER NOT NULL,
                        date TEXT NOT NULL,
                        odometer REAL NOT NULL,
                        liters REAL NOT NULL,
                        total_price REAL NOT NULL,
                        price_per_liter REAL,
                        distance_since_last REAL,
                        fuel_efficiency REAL,
                        comment TEXT,
                        created_at TEXT DEFAULT CURRENT_TIMESTAMP
                    )
                ''')
                
                # Create index for faster user queries
                cursor.execute('''
                    CREATE INDEX IF NOT EXISTS idx_user_id 
                    ON refuel_entries(user_id)
                ''')
                
                conn.commit()
                logger.info("Database tables created/verified successfully")
                
        except sqlite3.Error as e:
            logger.error(f"Error creating database tables: {e}")
            raise
    
    def add_refuel_entry(self, entry: RefuelEntry) -> int:
        """Add a new refuel entry to the database.
        
        Args:
            entry: RefuelEntry object to add
            
        Returns:
            int: The ID of the newly created entry
            
        Raises:
            sqlite3.Error: If database operation fails
        """
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                
                # Prepare data for insertion
                entry_data = (
                    entry.user_id,
                    entry.date.isoformat() if entry.date else datetime.now().isoformat(),
                    entry.odometer,
                    entry.liters,
                    entry.total_price,
                    entry.price_per_liter,
                    entry.distance_since_last,
                    entry.fuel_efficiency,
                    entry.comment
                )
                
                cursor.execute('''
                    INSERT INTO refuel_entries 
                    (user_id, date, odometer, liters, total_price, price_per_liter, 
                     distance_since_last, fuel_efficiency, comment)
                    VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
                ''', entry_data)
                
                entry_id = cursor.lastrowid
                conn.commit()
                
                logger.info(f"Added refuel entry {entry_id} for user {entry.user_id}")
                return entry_id
                
        except sqlite3.Error as e:
            logger.error(f"Error adding refuel entry: {e}")
            raise
    
    def get_recent_entries(self, user_id: int, limit: int = 10) -> List[RefuelEntry]:
        """Get recent refuel entries for a user.
        
        Args:
            user_id: Telegram user ID
            limit: Maximum number of entries to return
            
        Returns:
            List[RefuelEntry]: List of recent refuel entries
            
        Raises:
            sqlite3.Error: If database operation fails
        """
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                cursor.execute('''
                    SELECT id, user_id, date, odometer, liters, total_price, 
                           price_per_liter, distance_since_last, fuel_efficiency, comment
                    FROM refuel_entries 
                    WHERE user_id = ? 
                    ORDER BY date DESC 
                    LIMIT ?
                ''', (user_id, limit))
                
                entries = []
                for row in cursor.fetchall():
                    entry = RefuelEntry(
                        id=row[0],
                        user_id=row[1],
                        date=datetime.fromisoformat(row[2]) if row[2] else None,
                        odometer=row[3],
                        liters=row[4],
                        total_price=row[5],
                        price_per_liter=row[6],
                        distance_since_last=row[7],
                        fuel_efficiency=row[8],
                        comment=row[9]
                    )
                    entries.append(entry)
                
                logger.debug(f"Retrieved {len(entries)} recent entries for user {user_id}")
                return entries
                
        except sqlite3.Error as e:
            logger.error(f"Error getting recent entries: {e}")
            raise
    
    def get_last_entry(self, user_id: int) -> Optional[RefuelEntry]:
        """Get the last refuel entry for a user.
        
        Args:
            user_id: Telegram user ID
            
        Returns:
            Optional[RefuelEntry]: Last refuel entry or None if no entries exist
        """
        entries = self.get_recent_entries(user_id, 1)
        return entries[0] if entries else None
    
    def get_user_statistics(self, user_id: int) -> dict:
        """Get fuel consumption statistics for a user.
        
        Args:
            user_id: Telegram user ID
            
        Returns:
            dict: Statistics including total fuel, total cost, average efficiency, etc.
        """
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                cursor.execute('''
                    SELECT 
                        COUNT(*) as total_refuels,
                        SUM(liters) as total_fuel,
                        SUM(total_price) as total_cost,
                        AVG(price_per_liter) as avg_price_per_liter,
                        AVG(fuel_efficiency) as avg_efficiency,
                        SUM(distance_since_last) as total_distance
                    FROM refuel_entries 
                    WHERE user_id = ? AND fuel_efficiency IS NOT NULL
                ''', (user_id,))
                
                row = cursor.fetchone()
                if row and row[0] > 0:  # If we have at least one entry
                    return {
                        'total_refuels': row[0],
                        'total_fuel': round(row[1] or 0, 2),
                        'total_cost': round(row[2] or 0, 2),
                        'avg_price_per_liter': round(row[3] or 0, 2),
                        'avg_efficiency': round(row[4] or 0, 2),
                        'total_distance': round(row[5] or 0, 1)
                    }
                else:
                    return {
                        'total_refuels': 0,
                        'total_fuel': 0,
                        'total_cost': 0,
                        'avg_price_per_liter': 0,
                        'avg_efficiency': 0,
                        'total_distance': 0
                    }
                    
        except sqlite3.Error as e:
            logger.error(f"Error getting user statistics: {e}")
            raise
    
    def delete_entry(self, entry_id: int, user_id: int) -> bool:
        """Delete a refuel entry.
        
        Args:
            entry_id: ID of the entry to delete
            user_id: User ID (for security - can only delete own entries)
            
        Returns:
            bool: True if entry was deleted, False if not found
        """
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                cursor.execute('''
                    DELETE FROM refuel_entries 
                    WHERE id = ? AND user_id = ?
                ''', (entry_id, user_id))
                
                deleted_count = cursor.rowcount
                conn.commit()
                
                if deleted_count > 0:
                    logger.info(f"Deleted refuel entry {entry_id} for user {user_id}")
                    return True
                else:
                    logger.warning(f"Refuel entry {entry_id} not found for user {user_id}")
                    return False
                    
        except sqlite3.Error as e:
            logger.error(f"Error deleting refuel entry: {e}")
            raise
    
    def get_database_info(self) -> dict:
        """Get information about the database.
        
        Returns:
            dict: Database information including file size, entry count, etc.
        """
        try:
            info = {
                'database_path': self.db_path,
                'file_exists': os.path.exists(self.db_path),
                'file_size': 0,
                'total_entries': 0,
                'total_users': 0
            }
            
            if info['file_exists']:
                info['file_size'] = os.path.getsize(self.db_path)
                
                with sqlite3.connect(self.db_path) as conn:
                    cursor = conn.cursor()
                    
                    # Get total entries
                    cursor.execute('SELECT COUNT(*) FROM refuel_entries')
                    info['total_entries'] = cursor.fetchone()[0]
                    
                    # Get total unique users
                    cursor.execute('SELECT COUNT(DISTINCT user_id) FROM refuel_entries')
                    info['total_users'] = cursor.fetchone()[0]
            
            return info
            
        except sqlite3.Error as e:
            logger.error(f"Error getting database info: {e}")
            return {'error': str(e)}
