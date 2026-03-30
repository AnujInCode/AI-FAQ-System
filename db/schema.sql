-- 1. Enable pgvector extension
create extension if not exists vector;

-- 2. faqs table
create table if not exists faqs (
  id bigserial primary key,
  question text not null,
  answer text not null,
  embedding vector(384), -- Dimension for text-embedding-3-small
  created_at timestamp with time zone default timezone('utc'::text, now()) not null,
  updated_at timestamp with time zone default timezone('utc'::text, now()) not null
);

-- 3. query_logs table (upgraded for analytics)
drop table if exists query_logs;
create table if not exists query_logs (
  id bigserial primary key,
  query text not null,
  response text not null,
  confidence_score float not null,
  sources text[] default '{}',
  matched_faq_ids bigint[] default '{}', -- Added for detailed tracking
  top_scores float[] default '{}',       -- Added for detailed tracking
  latency_ms integer,
  prompt_version text,                   -- Important for AB testing prompts
  created_at timestamp with time zone default timezone('utc'::text, now()) not null
);

-- 4. unanswered_queries table
create table if not exists unanswered_queries (
  id bigserial primary key,
  query text not null,
  created_at timestamp with time zone default timezone('utc'::text, now()) not null
);

-- 5. Function for cosine similarity search
-- Returns top k matches above a certain threshold
create or replace function match_faqs (
  query_embedding vector(384),
  match_threshold float,
  match_count int
)
returns table (
  id bigint,
  question text,
  answer text,
  similarity float
)
language plpgsql
as $$
begin
  return query
  select
    faqs.id,
    faqs.question,
    faqs.answer,
    1 - (faqs.embedding <=> query_embedding) as similarity
  from faqs
  where 1 - (faqs.embedding <=> query_embedding) > match_threshold
  order by similarity desc
  limit match_count;
end;
$$;

-- 6. Indexes for fast retrieval
create index on faqs using ivfflat (embedding vector_cosine_ops)
  with (lists = 100);
