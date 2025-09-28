#!/bin/bash
# Run script for the Telegram Refuel Bot

echo "Starting Telegram Refuel Bot..."

# Wait for database to be ready
echo "Waiting for database to be ready..."
python -c "
import time
import psycopg2
import sys
import os

# Add src to Python path
sys.path.insert(0, os.path.join(os.getcwd(), 'src'))

from config.settings import settings

while True:
    try:
        conn = psycopg2.connect(
            host=settings.DB_HOST,
            port=settings.DB_PORT,
            database=settings.DB_NAME,
            user=settings.DB_USER,
            password=settings.DB_PASSWORD
        )
        conn.close()
        print('Database is ready!')
        break
    except psycopg2.OperationalError:
        print('Database not ready, waiting...')
        time.sleep(2)
"

# Run database migrations
echo "Running database migrations..."
alembic upgrade head

# Start the bot
echo "Starting bot..."
python main.py
