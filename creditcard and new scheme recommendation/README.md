# Neo4j-based AI Agent for Credit Eligibility and Product Recommendation

This project implements a "local-first" AI agent for credit eligibility assessment and product recommendation. It leverages **LangGraph** for orchestration, **Neo4j** for vector search and decision traceability, and open-source models (via Groq for fast inference, and Together AI/Fireworks AI for embeddings).

## Architecture

- **LangGraph**: Directed Acyclic Graph (DAG) for deterministic, modular multi-agent routing.
- **Neo4j**: Graph database for storing the `Customer`, `Product`, `PolicyClause`, and `Decision` nodes.
- **LLM/Embeddings**: Groq (Inference) and Together AI / Fireworks AI (Embeddings).
- **Frontend**: Streamlit dashboard for a user-friendly interface.

## Quick Start (Work in Progress)

Dependencies, environment setups, and scripts will go here as the project matures through the following phases:
1. Environment & Knowledge Graph Setup.
2. Embedding Strategy & Hybrid Retrieval.
3. Orchestration with LangGraph.
4. Traceability & Explainability.
5. Frontend & Observability.
