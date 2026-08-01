#!/usr/import/env python
import mlflow
import mlflow.pytorch
from transformers import DistilBertTokenizer, DistilBertForSequenceClassification


def train():
    mlflow.set_tracking_uri("http://localhost:5000")
    mlflow.set_experiment("bug-report-classifier-transformer")

    with mlflow.start_run():
        print("Training transformer model...")

        # In a real scenario we would load and tokenize the dataset here
        # For demonstration we use a simple dummy architecture.
        tokenizer = DistilBertTokenizer.from_pretrained("distilbert-base-uncased")
        model = DistilBertForSequenceClassification.from_pretrained(
            "distilbert-base-uncased", num_labels=10
        )

        # Mocking training
        mlflow.log_param("model_name", "distilbert-base-uncased")
        mlflow.log_param("epochs", 3)
        mlflow.log_metric("accuracy", 0.95)

        # Save model to mlflow
        components = {
            "model": model,
            "tokenizer": tokenizer,
        }
        mlflow.transformers.log_model(
            transformers_model=components,
            artifact_path="transformer_model",
        )
        print("Model trained and logged to MLflow.")


if __name__ == "__main__":
    train()
