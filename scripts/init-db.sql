-- Initialize database for local development
-- This script runs when PostgreSQL container starts for the first time

-- Create database if not exists (already handled by POSTGRES_DB env var)
-- CREATE DATABASE IF NOT EXISTS aiproject;

-- Create extensions
CREATE EXTENSION IF NOT EXISTS "uuid-ossp";
CREATE EXTENSION IF NOT EXISTS "pg_stat_statements";

-- Create schemas for different services (optional organization)
CREATE SCHEMA IF NOT EXISTS auth;
CREATE SCHEMA IF NOT EXISTS profile;
CREATE SCHEMA IF NOT EXISTS content;
CREATE SCHEMA IF NOT EXISTS notifications;
CREATE SCHEMA IF NOT EXISTS chat;
CREATE SCHEMA IF NOT EXISTS analytics;

-- Grant permissions
GRANT ALL PRIVILEGES ON DATABASE aiproject TO postgres;
GRANT ALL PRIVILEGES ON ALL SCHEMAS IN DATABASE aiproject TO postgres;

-- Set default search path (optional)
-- ALTER DATABASE aiproject SET search_path TO public, auth, profile, content, notifications, chat, analytics;

-- Log the initialization
SELECT 'AI Project Database initialized successfully' as status;
