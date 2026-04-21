-- Table for storing jobs to prevent duplicates
CREATE TABLE IF NOT EXISTS jobs (
    id SERIAL PRIMARY KEY,
    job_url TEXT UNIQUE NOT NULL,
    title TEXT,
    company TEXT,
    location TEXT,
    date_posted TEXT,
    description TEXT,
    scraped_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    ai_score INTEGER,
    ai_analysis JSONB,
    processed BOOLEAN DEFAULT FALSE
);

-- Index for fast URL lookups
CREATE INDEX IF NOT EXISTS idx_job_url ON jobs(job_url);
