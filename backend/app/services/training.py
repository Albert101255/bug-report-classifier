import csv
import json
import os
import tempfile
from collections import Counter
from datetime import UTC, datetime
from pathlib import Path
from typing import Any

import joblib
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.linear_model import LogisticRegression
from sklearn.metrics import accuracy_score, classification_report, f1_score
from sklearn.model_selection import train_test_split


def _read_dataset(dataset_path: Path) -> tuple[list[str], list[str]]:
    if not dataset_path.exists():
        raise FileNotFoundError(f"Training dataset not found: {dataset_path}")

    texts: list[str] = []
    labels: list[str] = []
    with dataset_path.open("r", encoding="utf-8", newline="") as handle:
        reader = csv.DictReader(handle)
        required = {"description", "team"}
        missing = required.difference(reader.fieldnames or [])
        if missing:
            raise ValueError(
                f"Dataset is missing required columns: {', '.join(sorted(missing))}"
            )

        for row in reader:
            description = (row.get("description") or "").strip()
            subject = (row.get("subject") or "").strip()
            team = (row.get("team") or "").strip()
            combined = f"{subject} {description}".strip()
            if combined and team:
                texts.append(combined)
                labels.append(team)

    if len(texts) < 20:
        raise ValueError(
            "At least 20 labelled rows are required for baseline training."
        )

    counts = Counter(labels)
    if len(counts) < 2:
        raise ValueError("At least two target teams are required.")
    rare = [label for label, count in counts.items() if count < 2]
    if rare:
        raise ValueError(
            f"Every team needs at least two examples. Too few: {', '.join(rare)}"
        )

    return texts, labels


def _atomic_joblib_dump(value: Any, destination: Path) -> None:
    destination.parent.mkdir(parents=True, exist_ok=True)
    with tempfile.NamedTemporaryFile(dir=destination.parent, delete=False) as temporary:
        temporary_path = Path(temporary.name)
    try:
        joblib.dump(value, temporary_path)
        os.replace(temporary_path, destination)
    finally:
        temporary_path.unlink(missing_ok=True)


def _atomic_json_dump(value: Any, destination: Path) -> None:
    destination.parent.mkdir(parents=True, exist_ok=True)
    with tempfile.NamedTemporaryFile(
        mode="w",
        encoding="utf-8",
        dir=destination.parent,
        delete=False,
    ) as temporary:
        json.dump(value, temporary, indent=2)
        temporary.write("\n")
        temporary_path = Path(temporary.name)
    try:
        os.replace(temporary_path, destination)
    finally:
        temporary_path.unlink(missing_ok=True)


def train_baseline(dataset_path: Path, model_dir: Path) -> dict[str, Any]:
    texts, labels = _read_dataset(dataset_path)
    class_count = len(set(labels))
    validation_size = max(class_count, round(len(texts) * 0.2))
    validation_size = min(validation_size, len(texts) - class_count)

    train_texts, validation_texts, train_labels, validation_labels = train_test_split(
        texts,
        labels,
        test_size=validation_size,
        random_state=42,
        stratify=labels,
    )

    vectorizer = TfidfVectorizer(
        lowercase=True,
        strip_accents="unicode",
        ngram_range=(1, 2),
        min_df=1,
        max_df=0.98,
        max_features=5000,
        sublinear_tf=True,
    )
    train_vectors = vectorizer.fit_transform(train_texts)
    validation_vectors = vectorizer.transform(validation_texts)

    classifier = LogisticRegression(
        max_iter=2000,
        class_weight="balanced",
        random_state=42,
    )
    classifier.fit(train_vectors, train_labels)
    predicted = classifier.predict(validation_vectors)

    trained_at = datetime.now(UTC).isoformat()
    metadata = {
        "model_version": f"tfidf-logreg-{datetime.now(UTC).strftime('%Y%m%d%H%M%S')}",
        "framework": "scikit-learn TF-IDF + Logistic Regression",
        "trained_at": trained_at,
        "dataset": str(dataset_path),
        "training_samples": len(train_texts),
        "validation_samples": len(validation_texts),
        "classes": sorted(set(labels)),
        "vocabulary_size": len(vectorizer.vocabulary_),
        "accuracy": round(float(accuracy_score(validation_labels, predicted)), 4),
        "macro_f1": round(
            float(f1_score(validation_labels, predicted, average="macro")), 4
        ),
    }
    report = classification_report(
        validation_labels,
        predicted,
        output_dict=True,
        zero_division=0,
    )

    model_dir.mkdir(parents=True, exist_ok=True)
    _atomic_joblib_dump(vectorizer, model_dir / "tfidf_vectorizer.joblib")
    _atomic_joblib_dump(classifier, model_dir / "classifier.joblib")
    _atomic_json_dump(metadata, model_dir / "metadata.json")
    _atomic_json_dump(report, model_dir / "classification_report.json")
    return metadata
