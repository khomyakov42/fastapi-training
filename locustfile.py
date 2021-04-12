import uuid
import random
from locust import task, HttpUser, between, events


ACCOUNT_IDS = []


class BillsUser(HttpUser):
    wait_time = between(0, 1)

    def on_start(self):
        resp = self.client.post("/customers/", json={
            "name": str(uuid.uuid4())
        }, name="create_customer")
        assert 200 <= resp.status_code < 400
        data = resp.json()
        assert "id" in data
        self.account_id = data["id"]
        ACCOUNT_IDS.append(self.account_id)

        resp = self.client.post(f"/accounts/{self.account_id}/deposit", json={
            "amount": "300000"
        }, name="deposit")
        assert 200 <= resp.status_code < 400

    @task(1)
    def deposit(self):
        self.client.post(f"/accounts/{self.account_id}/deposit", json={
            "amount": "300000"
        }, name="deposit")

    @task(30)
    def transfer(self):
        self.client.post(f"/accounts/{self.account_id}/transfer", json={
            "amount": "1000",
            "account_id": random.choice(ACCOUNT_IDS)
        }, name="transfer")
