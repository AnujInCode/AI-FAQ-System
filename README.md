# Mental Health AI FAQ System 🧠

An enterprise-grade Retrieval-Augmented Generation (RAG) platform built with FastAPI, PostgreSQL (pgvector), and local HuggingFace embeddings.

---

## 📺 Demo Video

Watch the complete system walkthrough, including the zero-hallucination semantic search, smart fallback overrides, and local latency caching.

[[ Watch the Demo Video ]](./demo/demo_video.webm)

---

## 🚀 Key Features
- **Zero-Hallucination RAG**: Strict grounding in verified knowledge bases.
- **Semantic Search**: Powered by `pgvector` for intelligent similarity matching.
- **Local-First**: Runs entirely offline via Docker (no API keys required).
- **Production Analytics**: Tracks query latency, confidence scores, and unanswered questions.
- **Interactive Widget**: Lightweight, embeddable chat interface.

## 💻 Quick Start
Run the system locally using Docker:
```bash
chmod +x run_local.sh
./run_local.sh
```
Access the dashboard at [http://localhost:8000](http://localhost:8000).
