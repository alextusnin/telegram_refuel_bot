-- Initialize the refuel_bot database
-- This script runs when the PostgreSQL container starts for the first time

-- Create the database (if it doesn't exist)
-- Note: The database is already created by POSTGRES_DB environment variable

-- Create extensions if needed
CREATE EXTENSION IF NOT EXISTS "uuid-ossp";

-- Set timezone
SET timezone = 'UTC';
