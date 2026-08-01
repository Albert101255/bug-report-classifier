# Bug Report Classifier — SaaS Platform

The **Bug Report Classifier Platform** is a production-grade SaaS application that automates bug report classification and triage into target engineering backlogs.

It uses advanced NLP techniques including **DistilBERT Transformer** integration and **Monte Carlo Dropout (MC Dropout)** deep learning models, managed by **MLflow** for experiment tracking and model registry.

---

## 🌟 Key Features

* **DistilBERT & MC Dropout Prediction**: Instant classification with deep-learning-based transformer pipelines and variance-based standard deviation uncertainty scores.
* **MLflow Integration**: Full model lifecycle management, experiment tracking, and artifact registry.
* **Confidence Level Bounding**: Automatically categorizes predictions into **HIGH** (auto-assigned), **MEDIUM** (suggested), and **LOW** (review queue required).
* **Modern React Dashboard**: Sleek interface with Quick Predict, Batch Upload (CSV), Audit Trail History, Model Analytics, Review Queue, and Settings.
* **Human Feedback Loop**: Logs human reviewer overrides to PostgreSQL for active learning and model retraining.
* **Audit Trail & Observability**: Complete database logging for every prediction, plus Prometheus/Grafana telemetry metrics.
* **One-Command Deployment**: Fully containerized with Docker & Docker Compose. Kubernetes manifests provided for production scaling.

---

## 🚀 Quick Start

### 1. Launch the Docker Stack
This will spin up the API, Frontend UI, PostgreSQL, Redis, MLflow, Prometheus, and Grafana:
```bash
docker-compose up -d --build
```

### 2. Access the Applications
- **Frontend Dashboard**: `http://localhost:3000`
- **Backend API**: `http://localhost:8000/docs` (Swagger UI)
- **MLflow Tracking Server**: `http://localhost:5000`
- **Grafana Metrics**: `http://localhost:3001` (login: admin/admin)
- **Prometheus**: `http://localhost:9090`

---

## 🏗 Kubernetes Deployment

We provide production-ready Kubernetes manifests in the `k8s/` directory.

```bash
kubectl apply -f k8s/deployment.yaml
kubectl apply -f k8s/service.yaml
```

---

## 📚 Documentation

* [Architecture & System Design](docs/ARCHITECTURE.md)
* [API Documentation](docs/API_DOCS.md)
* [Deployment Guide](docs/DEPLOYMENT.md)
