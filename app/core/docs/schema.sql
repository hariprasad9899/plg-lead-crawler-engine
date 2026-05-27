CREATE EXTENSION IF NOT EXISTS "pgcrypto";

CREATE TYPE entity_status AS ENUM (
    'pending',
    'processing',
    'completed',
    'failed'
);

CREATE TABLE intent_jobs (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    request_name TEXT NOT NULL,
    original_query TEXT NOT NULL,
    created_by UUID,
    status entity_status NOT NULL DEFAULT 'pending',
    total_seed_urls INTEGER DEFAULT 0,
    created_at TIMESTAMPTZ NOT NULL DEFAULT now(),
    updated_at TIMESTAMPTZ NOT NULL DEFAULT now()
);

CREATE TABLE generated_intents (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    intent_job_id UUID NOT NULL
        REFERENCES intent_jobs(id)
        ON DELETE CASCADE,
    intent_text TEXT NOT NULL,
    priority INTEGER DEFAULT 50,
    created_at TIMESTAMPTZ NOT NULL DEFAULT now()
);

CREATE TABLE search_queries (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    generated_intent_id UUID NOT NULL
        REFERENCES generated_intents(id)
        ON DELETE CASCADE,
    query TEXT NOT NULL,
    source VARCHAR(50),
    priority INTEGER DEFAULT 50,
    status entity_status NOT NULL DEFAULT 'pending',
    created_at TIMESTAMPTZ NOT NULL DEFAULT now()
);

CREATE TABLE discovered_urls (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    search_query_id UUID NOT NULL
        REFERENCES search_queries(id)
        ON DELETE CASCADE,
    url TEXT NOT NULL,
    normalized_url TEXT NOT NULL,
    domain TEXT NOT NULL,
    title TEXT,
    source_engine VARCHAR(50),
    priority_score INTEGER DEFAULT 50,
    discovery_depth INTEGER DEFAULT 0,
    crawl_status entity_status NOT NULL DEFAULT 'pending',
    first_seen_at TIMESTAMPTZ NOT NULL DEFAULT now(),
    last_seen_at TIMESTAMPTZ NOT NULL DEFAULT now()
);

CREATE UNIQUE INDEX idx_discovered_url_unique
ON discovered_urls(normalized_url);

CREATE INDEX idx_discovered_crawl
ON discovered_urls(crawl_status);