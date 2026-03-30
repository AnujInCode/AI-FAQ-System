#!/bin/bash
set -e

echo "🛑 Stopping any existing containers..."
docker compose down || true

echo "🚀 Starting generic Supabase (Postgres+pgvector & PostgREST) and FastAPI backend..."
docker compose up -d --build

echo "⏳ Waiting 10 seconds for databases to initialize..."
sleep 10

echo "🌱 Seeding the FAQ database..."
docker compose exec backend python -m scripts.seed_faqs

echo "✅ Success! System is running at http://localhost:8000"
