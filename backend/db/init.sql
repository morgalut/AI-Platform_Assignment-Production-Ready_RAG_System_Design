CREATE EXTENSION IF NOT EXISTS vector;

CREATE TABLE IF NOT EXISTS tickets (
    ticket_id TEXT PRIMARY KEY,
    product_tag TEXT NOT NULL,
    customer_id TEXT,
    customer_segment TEXT,
    created_at TIMESTAMP,
    resolved_at TIMESTAMP,
    resolution_summary TEXT,
    tags TEXT[],
    language TEXT
);

CREATE TABLE IF NOT EXISTS chunks (
    id UUID PRIMARY KEY,
    ticket_id TEXT REFERENCES tickets(ticket_id) ON DELETE CASCADE,
    product_tag TEXT NOT NULL,
    chunk_index INTEGER NOT NULL,
    text TEXT NOT NULL,
    embedding VECTOR(384),
    metadata JSONB,
    created_at TIMESTAMP DEFAULT NOW()
);

CREATE INDEX IF NOT EXISTS idx_chunks_embedding_hnsw
ON chunks USING hnsw (embedding vector_l2_ops);

CREATE INDEX IF NOT EXISTS idx_chunks_product_tag
ON chunks (product_tag);
