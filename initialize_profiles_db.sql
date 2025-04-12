-- Crear el usuario solo si no existe
DO
$$
BEGIN
   IF NOT EXISTS (SELECT 1 FROM pg_roles WHERE rolname = 'profile_db') THEN
      CREATE USER profile_db WITH PASSWORD 'profile-pass';
   END IF;
END
$$;

-- Crear la base de datos solo si no existe
DO
$$
BEGIN
   IF NOT EXISTS (SELECT 1 FROM pg_database WHERE datname = 'classconnect_profiles') THEN
      CREATE DATABASE classconnect_profiles;
   END IF;
END
$$;

-- Grant privileges on the database
GRANT ALL PRIVILEGES ON DATABASE classconnect_profiles TO profile_db;

-- Connect to the database
\c classconnect_profiles

-- Grant privileges
GRANT ALL PRIVILEGES ON ALL TABLES IN SCHEMA public TO profile_db;
GRANT ALL PRIVILEGES ON ALL SEQUENCES IN SCHEMA public TO profile_db;

ALTER DEFAULT PRIVILEGES IN SCHEMA public GRANT ALL ON TABLES TO profile_db;
ALTER DEFAULT PRIVILEGES IN SCHEMA public GRANT ALL ON SEQUENCES TO profile_db;

-- Enable extensions
CREATE EXTENSION IF NOT EXISTS "uuid-ossp";

-- Create profiles table with explicit UUID (no default)
DROP TABLE IF EXISTS profiles;

CREATE TABLE profiles (
    uuid UUID PRIMARY KEY,
    email TEXT NOT NULL,
    role TEXT NOT NULL,
    display_name TEXT,
    phone TEXT,
    location TEXT,
    birthday TEXT,
    gender TEXT,
    description TEXT,
    display_image TEXT,
    created_at TIMESTAMP DEFAULT NOW(),
    updated_at TIMESTAMP DEFAULT NOW()
);

-- Índice para búsquedas por UUID (relación lógica con users)
CREATE INDEX IF NOT EXISTS profiles_uuid_idx ON profiles(uuid);
CREATE INDEX IF NOT EXISTS profiles_email_idx ON profiles(email);