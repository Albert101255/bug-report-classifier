from locust import HttpUser, task, between

class BugClassifierUser(HttpUser):
    wait_time = between(1, 3)

    @task
    def predict_bug(self):
        self.client.post(
            "/api/v1/predict/single",
            json={"description": "Database connection timeout error when querying postgres pool"}
        )

    @task
    def get_history(self):
        self.client.get("/api/v1/predictions/history")
