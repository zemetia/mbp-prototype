-- MBP Prototype Database Schema
-- PostgreSQL database for persisting client data, sessions, and answers

-- Enable UUID extension
CREATE EXTENSION IF NOT EXISTS "uuid-ossp";

-- Clients table: Stores personal data and progress
CREATE TABLE IF NOT EXISTS clients (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    nama VARCHAR(255) NOT NULL,
    tanggal_lahir DATE,
    tempat_lahir VARCHAR(255),
    agama VARCHAR(100),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    last_phase INTEGER DEFAULT 0,
    last_session_id UUID,
    status VARCHAR(50) DEFAULT 'active' -- active, completed, archived
);

-- Sessions table: Stores analysis sessions
CREATE TABLE IF NOT EXISTS sessions (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    client_id UUID NOT NULL REFERENCES clients(id) ON DELETE CASCADE,
    status VARCHAR(50) DEFAULT 'active', -- active, completed, paused
    current_phase VARCHAR(50) DEFAULT 'safety',
    current_phase_number INTEGER DEFAULT 0,
    phase_complete BOOLEAN DEFAULT FALSE,
    ai_processing_complete BOOLEAN DEFAULT FALSE,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    completed_at TIMESTAMP,
    metadata JSONB DEFAULT '{}'
);

-- Add foreign key from clients to sessions for last_session_id
ALTER TABLE clients 
    ADD CONSTRAINT fk_last_session 
    FOREIGN KEY (last_session_id) 
    REFERENCES sessions(id) 
    ON DELETE SET NULL;

-- Answers table: Stores all question answers
CREATE TABLE IF NOT EXISTS answers (
    id SERIAL PRIMARY KEY,
    client_id UUID NOT NULL REFERENCES clients(id) ON DELETE CASCADE,
    session_id UUID NOT NULL REFERENCES sessions(id) ON DELETE CASCADE,
    question_id VARCHAR(100) NOT NULL,
    question_text TEXT NOT NULL,
    answer TEXT NOT NULL,
    phase VARCHAR(50) NOT NULL,
    dimensions JSONB DEFAULT '[]',
    question_type VARCHAR(20) DEFAULT 'fixed', -- fixed, flexible
    order_index INTEGER DEFAULT 0,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Indexes for performance
CREATE INDEX IF NOT EXISTS idx_clients_nama ON clients(nama);
CREATE INDEX IF NOT EXISTS idx_sessions_client_id ON sessions(client_id);
CREATE INDEX IF NOT EXISTS idx_sessions_status ON sessions(status);
CREATE INDEX IF NOT EXISTS idx_answers_client_id ON answers(client_id);
CREATE INDEX IF NOT EXISTS idx_answers_session_id ON answers(session_id);
CREATE INDEX IF NOT EXISTS idx_answers_phase ON answers(phase);

-- View to get client progress summary
CREATE OR REPLACE VIEW client_progress AS
SELECT 
    c.id as client_id,
    c.nama,
    c.last_phase,
    c.status as client_status,
    s.id as session_id,
    s.current_phase,
    s.current_phase_number,
    s.status as session_status,
    COUNT(a.id) as total_answers,
    MAX(a.created_at) as last_answer_at
FROM clients c
LEFT JOIN sessions s ON c.last_session_id = s.id
LEFT JOIN answers a ON s.id = a.session_id
GROUP BY c.id, c.nama, c.last_phase, c.status, s.id, s.current_phase, s.current_phase_number, s.status;
