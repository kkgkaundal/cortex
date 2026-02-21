"""
SQLite schema for Cortex memory system.
"""

SCHEMA_SQL = """
CREATE TABLE IF NOT EXISTS memory_tiers (
    tier TEXT PRIMARY KEY,
    description TEXT,
    last_maintenance TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

INSERT OR IGNORE INTO memory_tiers (tier, description) VALUES
    ('HOT', 'Active RAM cache for frequently accessed items'),
    ('WARM', 'Main SQLite database for current knowledge'),
    ('COLD', 'Archived historical data');

CREATE TABLE IF NOT EXISTS episodic_memory (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    event_type TEXT NOT NULL,
    command TEXT,
    result TEXT,
    duration_ms INTEGER,
    context TEXT,
    session_id TEXT,
    tier TEXT DEFAULT 'WARM',
    FOREIGN KEY (session_id) REFERENCES sessions(id)
);

CREATE INDEX IF NOT EXISTS idx_episodic_timestamp ON episodic_memory(timestamp);
CREATE INDEX IF NOT EXISTS idx_episodic_session ON episodic_memory(session_id);
CREATE INDEX IF NOT EXISTS idx_episodic_tier ON episodic_memory(tier);

CREATE TABLE IF NOT EXISTS semantic_memory (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    topic TEXT NOT NULL,
    fact TEXT NOT NULL,
    confidence REAL DEFAULT 0.5,
    source TEXT,
    source_type TEXT,
    reliability REAL DEFAULT 0.5,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    access_count INTEGER DEFAULT 0,
    tier TEXT DEFAULT 'WARM'
);

CREATE INDEX IF NOT EXISTS idx_semantic_topic ON semantic_memory(topic);
CREATE INDEX IF NOT EXISTS idx_semantic_confidence ON semantic_memory(confidence);
CREATE INDEX IF NOT EXISTS idx_semantic_tier ON semantic_memory(tier);

CREATE TABLE IF NOT EXISTS skill_memory (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    skill_name TEXT UNIQUE NOT NULL,
    description TEXT,
    steps TEXT,
    prerequisites TEXT,
    confidence REAL DEFAULT 0.5,
    success_count INTEGER DEFAULT 0,
    failure_count INTEGER DEFAULT 0,
    avg_duration_ms INTEGER,
    last_used TIMESTAMP,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    tier TEXT DEFAULT 'WARM'
);

CREATE INDEX IF NOT EXISTS idx_skill_name ON skill_memory(skill_name);
CREATE INDEX IF NOT EXISTS idx_skill_confidence ON skill_memory(confidence);
CREATE INDEX IF NOT EXISTS idx_skill_last_used ON skill_memory(last_used);

CREATE TABLE IF NOT EXISTS sessions (
    id TEXT PRIMARY KEY,
    start_time TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    end_time TIMESTAMP,
    summary TEXT,
    context TEXT,
    event_count INTEGER DEFAULT 0
);

CREATE INDEX IF NOT EXISTS idx_session_start ON sessions(start_time);

CREATE TABLE IF NOT EXISTS learning_sources (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    source_type TEXT NOT NULL,
    source_url TEXT,
    source_path TEXT,
    content_hash TEXT,
    fetched_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    reliability REAL DEFAULT 0.5,
    metadata TEXT
);

CREATE INDEX IF NOT EXISTS idx_source_type ON learning_sources(source_type);

CREATE TABLE IF NOT EXISTS sandbox_experiments (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    experiment_type TEXT NOT NULL,
    plan TEXT NOT NULL,
    command TEXT,
    status TEXT,
    duration_ms INTEGER,
    logs TEXT,
    files_changed TEXT,
    errors TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    skill_id INTEGER,
    FOREIGN KEY (skill_id) REFERENCES skill_memory(id)
);

CREATE INDEX IF NOT EXISTS idx_sandbox_status ON sandbox_experiments(status);
CREATE INDEX IF NOT EXISTS idx_sandbox_created ON sandbox_experiments(created_at);

CREATE TABLE IF NOT EXISTS internet_learning (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    query TEXT NOT NULL,
    topic TEXT NOT NULL,
    content TEXT NOT NULL,
    source_url TEXT,
    steps TEXT,
    requirements TEXT,
    alternatives TEXT,
    reliability REAL DEFAULT 0.5,
    fetched_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    used_count INTEGER DEFAULT 0
);

CREATE INDEX IF NOT EXISTS idx_internet_topic ON internet_learning(topic);
CREATE INDEX IF NOT EXISTS idx_internet_query ON internet_learning(query);

CREATE TABLE IF NOT EXISTS consolidation_log (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    operation TEXT NOT NULL,
    records_processed INTEGER,
    records_archived INTEGER,
    started_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    completed_at TIMESTAMP,
    status TEXT
);

CREATE TABLE IF NOT EXISTS system_metadata (
    key TEXT PRIMARY KEY,
    value TEXT,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

INSERT OR IGNORE INTO system_metadata (key, value) VALUES
    ('schema_version', '1.0.0'),
    ('created_at', datetime('now'));
"""

def get_schema():
    """Returns the complete schema SQL."""
    return SCHEMA_SQL
