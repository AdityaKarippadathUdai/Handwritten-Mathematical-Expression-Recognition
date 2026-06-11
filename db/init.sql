-- SQL Initialization Script
-- Seed data or schemas for PostgreSQL database schema can be placed here.
CREATE EXTENSION IF NOT EXISTS "uuid-ossp";

CREATE TABLE IF NOT EXISTS equation_history (
    id SERIAL PRIMARY KEY,
    image_path VARCHAR(500) NOT NULL,
    latex_output VARCHAR(2000) NOT NULL,
    confidence DOUBLE PRECISION NOT NULL,
    created_at TIMESTAMP WITHOUT TIME ZONE DEFAULT CURRENT_TIMESTAMP NOT NULL
);

CREATE INDEX IF NOT EXISTS ix_equation_history_created_at ON equation_history (created_at);
CREATE INDEX IF NOT EXISTS ix_equation_history_id ON equation_history (id);
