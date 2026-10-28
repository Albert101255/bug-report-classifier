from locust import HttpUser, between, task


class TriagePlatformUser(HttpUser):
    wait_time = between(1, 3)

    @task(3)
    def predict_single_issue(self):
        self.client.post(
            "/api/v1/triage/predict",
            json={
                "description": "Database connection timeout error when querying postgres pool",
                "subject": "DB Pool Starvation",
            },
        )

    @task(1)
    def get_analytics(self):
        self.client.get("/api/v1/analytics/summary")
