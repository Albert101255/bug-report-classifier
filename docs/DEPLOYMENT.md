# Production Deployment Guide

## 1. Quick Start with Docker Compose

To launch the complete platform (FastAPI backend service + React frontend dashboard) with a single command:

```bash
cd "/home/albert/project 1/bug_classification_research"
docker compose up -d
```

Access services:
- **React Dashboard**: [http://localhost:3000](http://localhost:3000)
- **FastAPI OpenAPI Specs**: [http://localhost:8000/docs](http://localhost:8000/docs)
- **Prometheus Metrics**: [http://localhost:8000/metrics](http://localhost:8000/metrics)

## 2. Local Manual Setup

### Backend (Python FastAPI)
```bash
cd backend
python3 -m uvicorn app.main:app --host 0.0.0.0 --port 8000
```

### Frontend (React + Vite)
```bash
cd frontend
npm run dev
```
