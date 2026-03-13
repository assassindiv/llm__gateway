import os

from locust import HttpUser, constant_throughput, task


class GatewayUser(HttpUser):
    wait_time = constant_throughput(0.01)
    def on_start(self):
        api_key = os.getenv("API_KEY") or os.getenv("LOAD_TEST_API_KEY") or "test-key-123"

        self.headers = {
            "Content-Type": "application/json",
            "x-api-key": api_key,
        }

    @task
    def chat(self):
        with self.client.post(
            "/chat",
            headers=self.headers,
            json={
                "model": os.getenv("MODEL", "llama-3.3-70b-versatile"),
                "messages": [{"role": "user", "content": "What is AI?"}],
            },
            catch_response=True,
        ) as response:
            if response.status_code == 401:
                response.failure("Unauthorized: missing x-api-key header.")
            elif response.status_code == 403:
                response.failure("Forbidden: invalid API key. Current key: test-key-123 unless API_KEY is set.")
            elif response.status_code >= 400:
                response.failure(f"HTTP {response.status_code}: {response.text}")
