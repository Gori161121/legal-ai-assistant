-- Legal AI Assistant
-- Legal Knowledge Database Schema v1

CREATE TABLE clients (
    id SERIAL PRIMARY KEY,
    full_name VARCHAR(120) NOT NULL,
    organization VARCHAR(120),
    email VARCHAR(120),
    status VARCHAR(30) DEFAULT 'active',
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE cases (
    id SERIAL PRIMARY KEY,
    client_id INTEGER REFERENCES clients(id),
    case_title VARCHAR(150) NOT NULL,
    case_type VARCHAR(80),
    status VARCHAR(30) DEFAULT 'open',
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE legal_documents (
    id SERIAL PRIMARY KEY,
    case_id INTEGER REFERENCES cases(id),
    title VARCHAR(150) NOT NULL,
    document_type VARCHAR(80),
    status VARCHAR(30) DEFAULT 'pending',
    uploaded_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE knowledge_entries (
    id SERIAL PRIMARY KEY,
    title VARCHAR(150) NOT NULL,
    category VARCHAR(80),
    content_summary TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE legal_insights (
    id SERIAL PRIMARY KEY,
    case_id INTEGER REFERENCES cases(id),
    insight_type VARCHAR(80),
    summary TEXT,
    recommendation TEXT,
    confidence_score DECIMAL(5,2),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX idx_cases_client ON cases(client_id);
CREATE INDEX idx_documents_case ON legal_documents(case_id);
CREATE INDEX idx_insights_case ON legal_insights(case_id);
