from pathlib import Path

from app.config import settings
from app.services.model_manager import ModelManager
from app.services.training import train_baseline


def test_rule_fallback_is_deterministic(tmp_path: Path, monkeypatch) -> None:
    monkeypatch.setattr(settings, "MODEL_DIR", tmp_path / "missing")
    manager = ModelManager()
    first = manager.predict("OAuth login session fails after JWT refresh")
    second = manager.predict("OAuth login session fails after JWT refresh")

    assert first["predicted_team"] == "BL-101 (Authentication & AuthZ)"
    assert first["confidence_score"] == second["confidence_score"]
    assert first["top_keywords"] == second["top_keywords"]


def test_trained_model_loads_and_predicts(tmp_path: Path, monkeypatch) -> None:
    repository_root = Path(__file__).resolve().parents[2]
    dataset = repository_root / "data" / "demo_bug_reports.csv"
    model_dir = tmp_path / "models"
    metadata = train_baseline(dataset, model_dir)

    monkeypatch.setattr(settings, "MODEL_DIR", model_dir)
    manager = ModelManager()
    result = manager.predict("PostgreSQL connection pool is exhausted during a query")

    assert manager.is_loaded is True
    assert metadata["framework"] == "scikit-learn TF-IDF + Logistic Regression"
    assert result["engine"] == "tfidf-logreg"
    assert result["predicted_team"] in metadata["classes"]
    assert 0.0 <= result["confidence_score"] <= 1.0
