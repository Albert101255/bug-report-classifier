from prometheus_client import Counter, Gauge, Histogram

PREDICTIONS_TOTAL = Counter(
    "bug_predictions_total",
    "Total bug classification predictions",
    ["confidence_level", "engine"],
)
PREDICTION_LATENCY = Histogram(
    "bug_prediction_latency_ms",
    "Bug prediction latency in milliseconds",
)
REVIEW_QUEUE_SIZE = Gauge(
    "bug_review_queue_size",
    "Number of predictions awaiting human review",
)
