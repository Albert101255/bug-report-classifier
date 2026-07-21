#!/usr/bin/env python3
import os
import pickle
import numpy as np
import pandas as pd
from sklearn.feature_extraction.text import TfidfVectorizer
import tensorflow as tf
from tensorflow import keras
from tensorflow.keras.models import Sequential
from tensorflow.keras.layers import Dense, Dropout, Input, LeakyReLU

def generate_seed_model():
    model_dir = "/home/albert/project 1/bug_classification_research/saved_models/tfidf_model"
    os.makedirs(model_dir, exist_ok=True)
    
    # 1. Team Labels (Sample 47 Teams or core backlog IDs)
    teams = [
        "BL-101 (Authentication & AuthZ)",
        "BL-102 (Database & ORM)",
        "BL-103 (UI Components & Design System)",
        "BL-104 (Payment Gateway & Billing)",
        "BL-105 (Cloud Infrastructure & K8s)",
        "BL-106 (API Gateway & Microservices)",
        "BL-107 (Search & Indexing Engine)",
        "BL-108 (Notification & Webhooks)",
        "BL-109 (Analytics & Telemetry)",
        "BL-110 (Security & Compliance)"
    ]
    label_to_id = {i: team for i, team in enumerate(teams)}
    
    # 2. Sample Training Bug Descriptions
    sample_texts = [
        "User login failed with HTTP 500 error when submitting OAuth token in auth service",
        "Database connection pool exhausted during high load queries on postgres cluster",
        "React component CSS dropdown menu overflow issue in dark mode dashboard layout",
        "Stripe payment webhook verification failed due to missing signature header",
        "Kubernetes pod crashing with OOMKilled memory limit exception in deployment",
        "FastAPI REST endpoint returning 404 for valid user profile request",
        "Elasticsearch index query timeout when fetching full-text search results",
        "Email notification failed to dispatch due to SMTP socket connection reset",
        "Prometheus latency metrics gauge not updating during background task execution",
        "SQL injection vulnerability detected in unsanitized search input parameter"
    ]
    
    # 3. Fit TF-IDF Vectorizer
    vectorizer = TfidfVectorizer(max_features=500, min_df=1, ngram_range=(1, 2))
    tfidf_matrix = vectorizer.fit_transform(sample_texts).toarray()
    
    # 4. Build Monte Carlo Dropout Keras Model
    tf.compat.v1.disable_eager_execution()
    
    model = Sequential([
        Input(shape=(tfidf_matrix.shape[1],), name="TFIDF_Features"),
        Dense(128),
        LeakyReLU(alpha=0.1),
        Dropout(0.3, trainable=True),
        Dense(64),
        LeakyReLU(alpha=0.1),
        Dropout(0.3, trainable=True),
        Dense(len(teams), activation="softmax", name="softmax_output")
    ])
    
    model.compile(loss="categorical_crossentropy", optimizer="adam", metrics=["accuracy"])
    
    # Fake fit for 2 epochs to save weights
    dummy_labels = keras.utils.to_categorical(np.arange(len(teams)), num_classes=len(teams))
    model.fit(tfidf_matrix, dummy_labels, epochs=3, verbose=0)
    
    # Save Artifacts
    with open(os.path.join(model_dir, "tfidf_vectorizer.pkl"), "wb") as f:
        pickle.dump(vectorizer, f)
        
    with open(os.path.join(model_dir, "label_to_id.pkl"), "wb") as f:
        pickle.dump(label_to_id, f)
        
    model.save(os.path.join(model_dir, "tfidf_classifier.h5"))
    print("Successfully generated seed TF-IDF model and vectorizer in saved_models/tfidf_model/")

if __name__ == "__main__":
    generate_seed_model()
