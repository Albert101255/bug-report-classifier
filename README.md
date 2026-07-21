# Bug Report Classifier — SaaS Platform

The **Bug Report Classifier Platform** is a production-grade SaaS application that automates bug report classification and triage into target engineering backlogs using **TF-IDF Feature Extraction** and **Monte Carlo Dropout (MC Dropout)** deep learning models.

---

## 🌟 Key Features

* **Real-time MC Dropout Prediction**: Instant classification (< 500ms latency) with variance-based standard deviation uncertainty scores.
* **Confidence Level Bounding**: Automatically categorizes predictions into **HIGH** (auto-assigned), **MEDIUM** (suggested), and **LOW** (review queue required).
* **Modern React Dashboard**: Sleek dark-mode interface with Quick Predict, Batch Upload (CSV), Audit Trail History, Model Analytics, Review Queue, and Settings.
* **Human Feedback Loop**: Logs human reviewer overrides to PostgreSQL for active learning and model retraining.
* **Audit Trail & Observability**: Complete database logging for every prediction, plus Prometheus telemetry metrics.
* **One-Command Deployment**: Fully containerized with Docker & Docker Compose.

---

## 🚀 Quick Start

### 1. Run Backend Pytest Suite
```bash
cd backend
python3 -m pytest -v
```

### 2. Build Frontend
```bash
cd frontend
npm run build
```

### 3. Launch Docker Stack
```bash
docker compose up -d
```

---

## 📚 Documentation

* [Architecture & System Design](docs/ARCHITECTURE.md)
* [API Documentation](docs/API_DOCS.md)
* [Deployment Guide](docs/DEPLOYMENT.md)
