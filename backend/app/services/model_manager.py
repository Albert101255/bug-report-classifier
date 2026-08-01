import json
import logging
import re
import time
from pathlib import Path
from typing import Any

import joblib
import numpy as np
from app.config import settings

logger = logging.getLogger(__name__)

TEAM_KEYWORDS: dict[str, tuple[str, ...]] = {
    "BL-101 (Authentication & AuthZ)": (
        "auth",
        "authentication",
        "login",
        "logout",
        "oauth",
        "password",
        "session",
        "jwt",
        "permission",
    ),
    "BL-102 (Database & ORM)": (
        "database",
        "postgres",
        "postgresql",
        "mysql",
        "sql",
        "orm",
        "query",
        "connection pool",
        "migration",
    ),
    "BL-103 (UI Components & Design System)": (
        "ui",
        "css",
        "react",
        "component",
        "dropdown",
        "button",
        "layout",
        "responsive",
        "theme",
    ),
    "BL-104 (Payment Gateway & Billing)": (
        "payment",
        "stripe",
        "billing",
        "invoice",
        "charge",
        "credit card",
        "checkout",
        "refund",
    ),
    "BL-105 (Cloud Infrastructure & K8s)": (
        "k8s",
        "kubernetes",
        "pod",
        "cloud",
        "docker",
        "container",
        "oomkilled",
        "deployment",
        "cpu limit",
    ),
    "BL-106 (API Gateway & Microservices)": (
        "api",
        "fastapi",
        "gateway",
        "rest",
        "endpoint",
        "microservice",
        "http 404",
        "http 500",
        "timeout",
    ),
    "BL-107 (Search & Indexing Engine)": (
        "search",
        "elasticsearch",
        "index",
        "ranking",
        "filter",
        "full text",
        "autocomplete",
    ),
    "BL-108 (Notification & Webhooks)": (
        "email",
        "notification",
        "smtp",
        "webhook",
        "dispatch",
        "push notification",
        "sms",
    ),
    "BL-109 (Analytics & Telemetry)": (
        "metric",
        "prometheus",
        "grafana",
        "telemetry",
        "latency",
        "analytics",
        "dashboard",
        "tracking",
    ),
    "BL-110 (Security & Compliance)": (
        "security",
        "injection",
        "vulnerability",
        "xss",
        "csrf",
        "attack",
        "exploit",
        "compliance",
        "encryption",
    ),
}


class ModelManager:
    """Load a real TF-IDF classifier and provide a deterministic fallback."""

    def __init__(self) -> None:
        self.vectorizer: Any | None = None
        self.classifier: Any | None = None
        self.is_loaded = False
        self.model_version = "rules-fallback-v1"
        self.framework = "Deterministic keyword fallback"
        self.trained_at: str | None = None
        self.vocabulary_size = 0
        self._metadata_mtime = 0.0
        self._next_reload_check = 0.0
        self._load_artifacts()

    @property
    def engine_name(self) -> str:
        return "tfidf-logreg" if self.is_loaded else "rules-fallback"

    def _paths(self) -> tuple[Path, Path, Path]:
        model_dir = Path(settings.MODEL_DIR)
        return (
            model_dir / "tfidf_vectorizer.joblib",
            model_dir / "classifier.joblib",
            model_dir / "metadata.json",
        )

    def _load_artifacts(self) -> None:
        vectorizer_path, classifier_path, metadata_path = self._paths()
        if not vectorizer_path.exists() or not classifier_path.exists():
            self._use_fallback("Model artifacts were not found")
            return

        try:
            vectorizer = joblib.load(vectorizer_path)
            classifier = joblib.load(classifier_path)
            if not hasattr(vectorizer, "transform") or not hasattr(
                classifier, "predict_proba"
            ):
                raise TypeError(
                    "Artifacts do not provide transform() and predict_proba()."
                )

            metadata: dict[str, Any] = {}
            if metadata_path.exists():
                metadata = json.loads(metadata_path.read_text(encoding="utf-8"))
                self._metadata_mtime = metadata_path.stat().st_mtime

            self.vectorizer = vectorizer
            self.classifier = classifier
            self.is_loaded = True
            self.model_version = str(metadata.get("model_version", "tfidf-logreg-v1"))
            self.framework = str(
                metadata.get("framework", "TF-IDF + Logistic Regression")
            )
            self.trained_at = metadata.get("trained_at")
            self.vocabulary_size = len(getattr(vectorizer, "vocabulary_", {}))
            logger.info("Loaded classifier %s", self.model_version)
        except Exception:
            logger.exception(
                "Could not load model artifacts; using deterministic fallback"
            )
            self._use_fallback("Model artifacts could not be loaded")

    def _use_fallback(self, reason: str) -> None:
        self.vectorizer = None
        self.classifier = None
        self.is_loaded = False
        self.model_version = "rules-fallback-v1"
        self.framework = "Deterministic keyword fallback"
        self.trained_at = None
        self.vocabulary_size = 0
        logger.warning("%s. Using rule fallback.", reason)

    def _maybe_reload(self) -> None:
        now = time.monotonic()
        if now < self._next_reload_check:
            return
        self._next_reload_check = now + max(settings.MODEL_RELOAD_SECONDS, 1)

        _, _, metadata_path = self._paths()
        if (
            metadata_path.exists()
            and metadata_path.stat().st_mtime > self._metadata_mtime
        ):
            self._load_artifacts()

    @staticmethod
    def preprocess_text(text: str) -> str:
        text = re.sub(r"<[^>]+>", " ", text or "")
        text = re.sub(r"\s+", " ", text).strip().lower()
        return text

    def _confidence_band(self, uncertainty: float) -> tuple[str, str]:
        if uncertainty <= settings.CONFIDENCE_HIGH_THRESHOLD:
            return "HIGH", "auto_assigned"
        if uncertainty <= settings.CONFIDENCE_LOW_THRESHOLD:
            return "MEDIUM", "needs_review"
        return "LOW", "needs_review"

    @staticmethod
    def _alternatives(
        classes: np.ndarray, probabilities: np.ndarray, top_index: int
    ) -> list[dict[str, Any]]:
        sorted_indices = np.argsort(probabilities)[::-1]
        alternatives: list[dict[str, Any]] = []
        for index in sorted_indices:
            if int(index) == top_index:
                continue
            probability = float(probabilities[index])
            alternatives.append(
                {
                    "team": str(classes[index]),
                    "confidence": round(probability, 4),
                    "uncertainty": round(1.0 - probability, 4),
                }
            )
            if len(alternatives) == 3:
                break
        return alternatives

    def _linear_keywords(
        self, vector: Any, predicted_class: str, clean_text: str
    ) -> list[dict[str, Any]]:
        try:
            feature_names = self.vectorizer.get_feature_names_out()
            row = vector.toarray().ravel()
            classes = [str(value) for value in self.classifier.classes_]
            class_index = classes.index(predicted_class)
            coefficients = self.classifier.coef_[class_index]
            contributions = row * coefficients
            ranked = np.argsort(contributions)[::-1]
            positives = [index for index in ranked if contributions[index] > 0][:5]
            if positives:
                max_contribution = float(contributions[positives[0]]) or 1.0
                return [
                    {
                        "word": str(feature_names[index]),
                        "score": round(
                            float(contributions[index]) / max_contribution, 3
                        ),
                    }
                    for index in positives
                ]
        except Exception:
            logger.debug("Feature contribution extraction failed", exc_info=True)

        return [
            {"word": token, "score": 1.0}
            for token in dict.fromkeys(clean_text.split())
            if len(token) > 2
        ][:5]

    def _predict_model(self, clean_text: str) -> dict[str, Any]:
        vector = self.vectorizer.transform([clean_text])
        probabilities = np.asarray(
            self.classifier.predict_proba(vector)[0], dtype=float
        )
        classes = np.asarray(self.classifier.classes_, dtype=str)
        top_index = int(np.argmax(probabilities))
        predicted_team = str(classes[top_index])
        confidence = float(probabilities[top_index])
        uncertainty = 1.0 - confidence
        confidence_level, status = self._confidence_band(uncertainty)

        return {
            "predicted_team": predicted_team,
            "confidence_score": round(confidence, 4),
            "uncertainty_score": round(uncertainty, 4),
            "confidence_level": confidence_level,
            "status": status,
            "top_alternatives": self._alternatives(classes, probabilities, top_index),
            "top_keywords": self._linear_keywords(vector, predicted_team, clean_text),
        }

    def _predict_rules(self, clean_text: str) -> dict[str, Any]:
        teams = list(TEAM_KEYWORDS)
        raw_scores = np.full(len(teams), 0.01, dtype=float)
        matched_by_team: dict[str, list[str]] = {}

        for index, team in enumerate(teams):
            matches = [
                keyword for keyword in TEAM_KEYWORDS[team] if keyword in clean_text
            ]
            if matches:
                matched_by_team[team] = matches
                raw_scores[index] += float(len(matches))

        probabilities = raw_scores / raw_scores.sum()
        top_index = int(np.argmax(probabilities))
        predicted_team = teams[top_index]
        confidence = float(probabilities[top_index])
        uncertainty = 1.0 - confidence
        confidence_level, status = self._confidence_band(uncertainty)
        keywords = matched_by_team.get(predicted_team, [])

        return {
            "predicted_team": predicted_team,
            "confidence_score": round(confidence, 4),
            "uncertainty_score": round(uncertainty, 4),
            "confidence_level": confidence_level,
            "status": status,
            "top_alternatives": self._alternatives(
                np.asarray(teams, dtype=str), probabilities, top_index
            ),
            "top_keywords": [
                {"word": keyword, "score": round(1.0 / (position + 1), 3)}
                for position, keyword in enumerate(keywords[:5])
            ],
        }

    def predict(self, description: str, subject: str = "") -> dict[str, Any]:
        self._maybe_reload()
        started_at = time.perf_counter()
        clean_text = self.preprocess_text(f"{subject} {description}")
        if not clean_text:
            raise ValueError("Bug description cannot be empty.")

        result = (
            self._predict_model(clean_text)
            if self.is_loaded
            else self._predict_rules(clean_text)
        )
        result["latency_ms"] = round((time.perf_counter() - started_at) * 1000, 2)
        result["model_version"] = self.model_version
        result["engine"] = self.engine_name
        return result

    def info(self) -> dict[str, Any]:
        return {
            "model_version": self.model_version,
            "framework": self.framework,
            "tf_idf_vocab_size": self.vocabulary_size,
            "num_teams": len(getattr(self.classifier, "classes_", TEAM_KEYWORDS)),
            "confidence_threshold_high": settings.CONFIDENCE_HIGH_THRESHOLD,
            "confidence_threshold_low": settings.CONFIDENCE_LOW_THRESHOLD,
            "last_trained_at": self.trained_at or "not-trained",
            "is_active": self.is_loaded,
        }


model_manager = ModelManager()
