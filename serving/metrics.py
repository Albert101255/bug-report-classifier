from prometheus_client import Counter, Histogram, Gauge

predictions_counter = Counter(
    'predictions_total',
    'Total predictions made',
    ['team', 'confidence_level']
)

prediction_latency = Histogram(
    'prediction_latency_ms',
    'Prediction latency in milliseconds'
)

review_queue_size = Gauge(
    'review_queue_size',
    'Number of predictions awaiting human review'
)

model_confidence_avg = Gauge(
    'model_confidence_avg',
    'Average model confidence'
)
