# Real-Estate-Product-Hybrid-Search-AI-Agent
A production-ready hybrid real-estate product search agent that: Automatically decides between data-source search (structured filters / transactional DB lookups) and semantic search (vector embeddings + similarity) based on the user's query.  Integrates Redis for memory/cache, and tuned for Uvicorn (ASGI) for async performance &amp; scalability.

# 🏘️ Real Estate Hybrid Search Agent

[![GitHub stars](https://img.shields.io/github/stars/your-org/real-estate-agent?style=social)](https://github.com/your-org/real-estate-agent/stargazers)  
[![License](https://img.shields.io/badge/License-MIT-lightgrey)](./LICENSE)  
[![Python Version](https://img.shields.io/badge/Python-3.11%2B-blue)](https://www.python.org/)  
[![FastAPI](https://img.shields.io/badge/FastAPI-ASGI-009688?logo=fastapi)](https://fastapi.tiangolo.com/)  
[![Redis](https://img.shields.io/badge/Cache-Redis-DC382D?logo=redis)](https://redis.io/)  
[![Vector Search](https://img.shields.io/badge/VectorDB-Embeddings-green)](#)  

> A production-ready AI Agent for real estate product search — combining structured data search and semantic vector search, built with FastAPI, Redis, and an LLM-driven decision engine.

---
## 🧐 Overview

The Real Estate Hybrid Search Agent intelligently routes user queries to the most appropriate search mode:

- **Structured Data-Source Search**: For queries that align to filters, price ranges, bedroom counts, locations, etc.  
- **Semantic Vector Search**: For natural-language queries, fuzzy matches, and intent-based search scenarios.

Built on FastAPI for async performance, Redis for caching and memory, and a pluggable vector store + LLM for intelligent decisioning.

---

## ✅ Features

- Hybrid search mode (structured vs semantic)  
- Automatic query routing via LLM heuristics  
- Redis integrated session / memory caching  
- FastAPI endpoints with Pydantic type safety  
- Docker‐ and local‐ready deployment  
- OpenAPI auto-generated documentation  
- Easily extensible vector store + datasource modules

---

## 🏗 Architecture
            +---------------------------+
            |        User Query         |
            +------------+--------------+
                         |
                         ▼
            +---------------------------+
            |    Decision Agent Layer   |
            |  (LLM + heuristics)       |
            +------------+--------------+
                         |
    ┌--------------------┴--------------------┐
    |                                         |
    ▼                                         ▼
+----------------------+ +-------------------------+
| Structured Data-Base | | Vector Store (Embeddings)|
| (CSV / SQL / API) | | Semantic Search |
+----------------------+ +--------------------------+
\ /
\ /
\ /
\ /
+---------------------------------+
| FastAPI Web API |
| Redis (Cache/Memory) |
+---------------------------------+


---

## 🧰 Tech Stack

| Component           | Technology                                         |
|---------------------|---------------------------------------------------|
| Web Framework       | FastAPI                                            |
| ASGI Server         | Uvicorn (async)                                    |
| Cache / Memory      | Redis                                              |
| Vector Store        | In‐memory stub (replaceable by Chroma/Pinecone)    |
| LLM / Decision Logic| Stub heuristics (replaceable by Ollama/OpenAI)     |
| Containerization    | Docker, docker-compose                             |
| Testing             | pytest, httpx                                       |
| CI/CD               | GitHub Actions                                     |

---

## 🏁 Getting Started

### Prerequisites
- Python 3.11 or higher  
- Redis (v6+) running locally or via Docker  
- Docker & docker-compose (optional)  
- Git  

### Setup & Installation
```bash
git clone https://github.com/<your-org>/real-estate-agent.git
cd real-estate-agent
cp env.example .env
python -m venv venv
source venv/bin/activate      # On Windows: venv\Scripts\activate
pip install -r requirements.txt

## 🏁 Running Locally
uvicorn src.main:app --host 0.0.0.0 --port 8000 --reload
Open http://localhost:8000/docs for API docs.

📡 API Reference
Health Check

Endpoint: GET /health
Response:

{ "status": "ok" }

🧠 Decision Logic

The agent receives the query.
An LLM (or heuristic) analyses the query to determine whether it’s structured (filterable) or semantic (natural language).
If structured → route to data-source search; if semantic → route to vector search.
Results are ranked and returned, with the mode field indicating which path was used.
Session info and memory may be persisted in Redis for follow-up coherence.

🙌 Acknowledgements

FastAPI
 — High-performance async web framework
Uvicorn
 — ASGI server
Redis
 — Caching and session persistence
Sentence Transformers
 — Embeddings for semantic search
LangChain/LangGraph
 — Agent orchestration (future integration)

 📜 License
This project is licensed under the MIT License.

