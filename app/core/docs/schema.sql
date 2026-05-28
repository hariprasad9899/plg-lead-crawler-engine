CREATE EXTENSION IF NOT EXISTS "pgcrypto";

-- =========================================================
-- ENUMS
-- =========================================================

CREATE TYPE job_status AS ENUM (
    'pending',
    'running',
    'paused',
    'completed',
    'failed'
);

CREATE TYPE query_status AS ENUM (
    'pending',
    'processing',
    'completed',
    'failed'
);

CREATE TYPE crawl_status AS ENUM (
    'pending',
    'queued',
    'crawling',
    'completed',
    'failed',
    'blocked',
    'timeout'
);

CREATE TYPE crawl_provider AS ENUM (
    'scraperapi',
    'playwright',
    'axios',
    'zenrows',
    'firecrawl',
    'manual'
);

-- =========================================================
-- INTENT JOBS
-- =========================================================

CREATE TABLE intent_jobs (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    tenant_id UUID,
    created_by UUID,
    request_name TEXT NOT NULL,
    original_query TEXT NOT NULL,
    status job_status NOT NULL DEFAULT 'pending',
    -- Product customer is selling
    product_name TEXT,
    product_description TEXT,
    -- ICP (Ideal Customer Profile)
    target_industries JSONB,
    target_countries JSONB,
    target_regions JSONB,
    min_company_size INTEGER,
    max_company_size INTEGER,
    target_personas JSONB,
    target_technologies JSONB,
    excluded_technologies JSONB,
    excluded_domains JSONB,
    -- Buying signal configuration
    buying_signals JSONB,
    negative_signals JSONB,
    signal_priority_weights JSONB,
    -- Monitoring configuration
    monitoring_frequency_hours INTEGER DEFAULT 6,
    lead_score_threshold INTEGER DEFAULT 70,
    max_urls_per_run INTEGER DEFAULT 50,
    -- Runtime metrics
    total_seed_urls INTEGER DEFAULT 0,
    total_discovered_urls INTEGER DEFAULT 0,
    total_processed_urls INTEGER DEFAULT 0,
    total_qualified_leads INTEGER DEFAULT 0,
    last_run_at TIMESTAMPTZ,
    next_run_at TIMESTAMPTZ,
    created_at TIMESTAMPTZ NOT NULL DEFAULT now(),
    updated_at TIMESTAMPTZ NOT NULL DEFAULT now()
);

CREATE INDEX idx_intent_jobs_status ON intent_jobs(status);
CREATE INDEX idx_intent_jobs_next_run ON intent_jobs(next_run_at);
CREATE INDEX idx_intent_jobs_tenant ON intent_jobs(tenant_id);

-- =========================================================
-- GENERATED INTENTS
-- =========================================================

CREATE TABLE generated_intents (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    tenant_id UUID,
    intent_job_id UUID NOT NULL REFERENCES intent_jobs(id) ON DELETE CASCADE,
    intent_text TEXT NOT NULL,
    priority INTEGER DEFAULT 50,
    created_at TIMESTAMPTZ NOT NULL DEFAULT now()
);

CREATE INDEX idx_generated_intents_job ON generated_intents(intent_job_id);

-- =========================================================
-- SEARCH QUERIES
-- =========================================================

CREATE TABLE search_queries (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    tenant_id UUID,
    generated_intent_id UUID NOT NULL REFERENCES generated_intents(id) ON DELETE CASCADE,
    query TEXT NOT NULL,
    source VARCHAR(50),
    priority INTEGER DEFAULT 50,
    status query_status NOT NULL DEFAULT 'pending',
    created_at TIMESTAMPTZ NOT NULL DEFAULT now()
);

CREATE INDEX idx_search_queries_status ON search_queries(status);

-- =========================================================
-- GLOBAL URL REGISTRY
-- =========================================================

CREATE TABLE canonical_urls (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    normalized_url TEXT NOT NULL UNIQUE,
    url TEXT NOT NULL,
    domain TEXT NOT NULL,
    title TEXT,
    content_hash TEXT,
    global_crawl_status crawl_status DEFAULT 'pending',
    first_seen_at TIMESTAMPTZ DEFAULT now(),
    last_crawled_at TIMESTAMPTZ
);

CREATE INDEX idx_canonical_domain ON canonical_urls(domain);
CREATE INDEX idx_canonical_crawl_status ON canonical_urls(global_crawl_status);

-- =========================================================
-- TENANT URL DISCOVERY MAPPING
-- =========================================================

CREATE TABLE discovered_urls (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    tenant_id UUID,
    canonical_url_id UUID NOT NULL REFERENCES canonical_urls(id) ON DELETE CASCADE,
    search_query_id UUID NOT NULL REFERENCES search_queries(id) ON DELETE CASCADE,
    source_engine VARCHAR(50),
    priority_score INTEGER DEFAULT 50,
    discovery_depth INTEGER DEFAULT 0,
    crawl_status crawl_status DEFAULT 'pending',
    discovered_at TIMESTAMPTZ DEFAULT now()
);

CREATE INDEX idx_discovered_tenant ON discovered_urls(tenant_id);
CREATE INDEX idx_discovered_canonical ON discovered_urls(canonical_url_id);
CREATE INDEX idx_discovered_crawl_status ON discovered_urls(crawl_status);

-- =========================================================
-- PAGE SNAPSHOTS / CRAWL HISTORY
-- =========================================================

CREATE TABLE crawled_pages (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    canonical_url_id UUID NOT NULL REFERENCES canonical_urls(id) ON DELETE CASCADE,
    crawl_provider crawl_provider,
    raw_html TEXT,
    extracted_text TEXT,
    metadata JSONB,
    content_hash TEXT,
    response_status_code INTEGER,
    crawl_duration_ms INTEGER,
    error_message TEXT,
    crawler_version TEXT,
    crawled_at TIMESTAMPTZ DEFAULT now()
);

CREATE INDEX idx_crawled_pages_url ON crawled_pages(canonical_url_id);
CREATE INDEX idx_crawled_pages_provider ON crawled_pages(crawl_provider);
CREATE INDEX idx_crawled_pages_crawled_at ON crawled_pages(crawled_at);