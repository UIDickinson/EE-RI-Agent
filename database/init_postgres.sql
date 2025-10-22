-- EE Research Scout PostgreSQL Schema
-- Stores research queries, results, and cached data

-- Enable pgvector extension for embeddings
CREATE EXTENSION IF NOT EXISTS vector;

-- Queries table
CREATE TABLE IF NOT EXISTS queries (
    id SERIAL PRIMARY KEY,
    query_text TEXT NOT NULL,
    query_hash VARCHAR(64) UNIQUE NOT NULL,
    focus_areas TEXT[],
    depth VARCHAR(10) DEFAULT 'deep',
    status VARCHAR(20) DEFAULT 'processing',
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    completed_at TIMESTAMP,
    user_id VARCHAR(100),
    session_id VARCHAR(100)
);

CREATE INDEX idx_queries_hash ON queries(query_hash);
CREATE INDEX idx_queries_status ON queries(status);
CREATE INDEX idx_queries_created ON queries(created_at DESC);

-- Research results table
CREATE TABLE IF NOT EXISTS research_results (
    id SERIAL PRIMARY KEY,
    query_id INTEGER REFERENCES queries(id) ON DELETE CASCADE,
    result_type VARCHAR(50) NOT NULL, -- 'paper', 'patent', 'component'
    result_data JSONB NOT NULL,
    trl INTEGER,
    relevance_score FLOAT,
    embedding vector(1536), -- For semantic search
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX idx_results_query ON research_results(query_id);
CREATE INDEX idx_results_type ON research_results(result_type);
CREATE INDEX idx_results_trl ON research_results(trl);
CREATE INDEX idx_results_embedding ON research_results USING ivfflat (embedding vector_cosine_ops);

-- Components cache table
CREATE TABLE IF NOT EXISTS components_cache (
    id SERIAL PRIMARY KEY,
    part_number VARCHAR(100) UNIQUE NOT NULL,
    manufacturer VARCHAR(100),
    category VARCHAR(100),
    specifications JSONB,
    datasheet_url TEXT,
    trl INTEGER,
    lifecycle VARCHAR(50),
    supply_chain JSONB,
    last_updated TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    cache_valid_until TIMESTAMP
);

CREATE INDEX idx_components_part ON components_cache(part_number);
CREATE INDEX idx_components_mfr ON components_cache(manufacturer);
CREATE INDEX idx_components_lifecycle ON components_cache(lifecycle);

-- Papers cache table
CREATE TABLE IF NOT EXISTS papers_cache (
    id SERIAL PRIMARY KEY,
    doi VARCHAR(200) UNIQUE,
    title TEXT NOT NULL,
    authors TEXT[],
    abstract TEXT,
    year INTEGER,
    journal VARCHAR(200),
    url TEXT,
    embedding vector(1536),
    citations_count INTEGER,
    last_updated TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX idx_papers_doi ON papers_cache(doi);
CREATE INDEX idx_papers_year ON papers_cache(year DESC);
CREATE INDEX idx_papers_embedding ON papers_cache USING ivfflat (embedding vector_cosine_ops);

-- Patents cache table
CREATE TABLE IF NOT EXISTS patents_cache (
    id SERIAL PRIMARY KEY,
    patent_number VARCHAR(50) UNIQUE NOT NULL,
    title TEXT NOT NULL,
    applicant VARCHAR(200),
    abstract TEXT,
    filing_date DATE,
    publication_date DATE,
    status VARCHAR(50),
    office VARCHAR(10), -- 'EPO', 'CNIPA', 'JPO'
    ipc_classes TEXT[],
    embedding vector(1536),
    last_updated TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX idx_patents_number ON patents_cache(patent_number);
CREATE INDEX idx_patents_office ON patents_cache(office);
CREATE INDEX idx_patents_filing ON patents_cache(filing_date DESC);

-- Supply chain monitoring table
CREATE TABLE IF NOT EXISTS supply_chain_snapshots (
    id SERIAL PRIMARY KEY,
    part_number VARCHAR(100) NOT NULL,
    distributor VARCHAR(100) NOT NULL,
    stock_level INTEGER,
    unit_price DECIMAL(10, 2),
    lead_time_weeks INTEGER,
    lifecycle VARCHAR(50),
    snapshot_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX idx_supply_part ON supply_chain_snapshots(part_number);
CREATE INDEX idx_supply_date ON supply_chain_snapshots(snapshot_date DESC);

-- TRL classifications table
CREATE TABLE IF NOT EXISTS trl_classifications (
    id SERIAL PRIMARY KEY,
    entity_type VARCHAR(50) NOT NULL, -- 'component', 'technology', 'paper', 'patent'
    entity_id VARCHAR(200) NOT NULL,
    trl INTEGER NOT NULL CHECK (trl >= 1 AND trl <= 9),
    confidence FLOAT,
    evidence JSONB,
    justification TEXT,
    classified_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    UNIQUE(entity_type, entity_id)
);

CREATE INDEX idx_trl_entity ON trl_classifications(entity_type, entity_id);
CREATE INDEX idx_trl_level ON trl_classifications(trl);

-- Query analytics table
CREATE TABLE IF NOT EXISTS query_analytics (
    id SERIAL PRIMARY KEY,
    query_id INTEGER REFERENCES queries(id) ON DELETE CASCADE,
    execution_time_seconds INTEGER,
    sources_queried INTEGER,
    total_results INTEGER,
    cache_hits INTEGER,
    errors_encountered INTEGER,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX idx_analytics_query ON query_analytics(query_id);

-- User feedback table
CREATE TABLE IF NOT EXISTS user_feedback (
    id SERIAL PRIMARY KEY,
    query_id INTEGER REFERENCES queries(id) ON DELETE CASCADE,
    rating INTEGER CHECK (rating >= 1 AND rating <= 5),
    feedback_text TEXT,
    helpful_results TEXT[], -- Array of result IDs that were helpful
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Create views for common queries

-- View: Recent queries with results count
CREATE OR REPLACE VIEW recent_queries_summary AS
SELECT 
    q.id,
    q.query_text,
    q.status,
    q.created_at,
    q.completed_at,
    COUNT(DISTINCT rr.id) as total_results,
    COUNT(DISTINCT CASE WHEN rr.result_type = 'paper' THEN rr.id END) as papers_count,
    COUNT(DISTINCT CASE WHEN rr.result_type = 'patent' THEN rr.id END) as patents_count,
    COUNT(DISTINCT CASE WHEN rr.result_type = 'component' THEN rr.id END) as components_count
FROM queries q
LEFT JOIN research_results rr ON q.id = rr.query_id
GROUP BY q.id, q.query_text, q.status, q.created_at, q.completed_at
ORDER BY q.created_at DESC
LIMIT 50;

-- View: Components with supply chain health
CREATE OR REPLACE VIEW components_supply_health AS
SELECT 
    c.part_number,
    c.manufacturer,
    c.category,
    c.lifecycle,
    c.trl,
    COUNT(DISTINCT scs.distributor) as distributor_count,
    SUM(scs.stock_level) as total_stock,
    AVG(scs.unit_price) as avg_price,
    MAX(scs.snapshot_date) as last_checked
FROM components_cache c
LEFT JOIN supply_chain_snapshots scs ON c.part_number = scs.part_number
    AND scs.snapshot_date > CURRENT_TIMESTAMP - INTERVAL '7 days'
GROUP BY c.part_number, c.manufacturer, c.category, c.lifecycle, c.trl;

-- Function: Clean old cache entries
CREATE OR REPLACE FUNCTION clean_expired_cache()
RETURNS void AS $$
BEGIN
    DELETE FROM components_cache WHERE cache_valid_until < CURRENT_TIMESTAMP;
    DELETE FROM papers_cache WHERE last_updated < CURRENT_TIMESTAMP - INTERVAL '30 days';
    DELETE FROM patents_cache WHERE last_updated < CURRENT_TIMESTAMP - INTERVAL '30 days';
    DELETE FROM supply_chain_snapshots WHERE snapshot_date < CURRENT_TIMESTAMP - INTERVAL '90 days';
END;
$$ LANGUAGE plpgsql;

-- Grant permissions (adjust as needed)
-- GRANT ALL PRIVILEGES ON ALL TABLES IN SCHEMA public TO ee_scout_user;
-- GRANT ALL PRIVILEGES ON ALL SEQUENCES IN SCHEMA public TO ee_scout_user;