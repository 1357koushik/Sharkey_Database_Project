from locust import HttpUser, between, task


class TransactionUser(HttpUser):
    wait_time = between(0.1, 0.6)

    @task(4)
    def tables(self):
        with self.client.get("/api/tables", name="GET /api/tables", catch_response=True) as resp:
            data = resp.json()
            tables = data.get("tables", {})
            if not data.get("ok"):
                resp.failure(data.get("error", "tables request failed"))
            elif sorted(tables.keys()) != ["Booking", "Complaint", "Facility", "Member"]:
                resp.failure("tables response missing expected relations")
            else:
                resp.success()

    @task(2)
    def wal(self):
        with self.client.get("/api/wal", name="GET /api/wal", catch_response=True) as resp:
            data = resp.json()
            if not data.get("ok"):
                resp.failure(data.get("error", "wal request failed"))
            elif "total" not in data or "recent" not in data:
                resp.failure("wal response missing expected fields")
            else:
                resp.success()

    @task(1)
    def recovery(self):
        with self.client.get("/api/acid/recover", name="GET /api/acid/recover", catch_response=True) as resp:
            data = resp.json()
            recovery = data.get("recovery", {})
            if not data.get("ok"):
                resp.failure(data.get("error", "recovery request failed"))
            elif "status" not in recovery or "records" not in recovery:
                resp.failure("recovery response missing expected fields")
            else:
                resp.success()

    @task(1)
    def race_condition(self):
        payload = {"attempts": 12, "stock": 5, "delay_ms": 20}
        with self.client.post("/api/acid/stress", json=payload, name="POST /api/acid/stress", catch_response=True) as resp:
            data = resp.json()
            if not data.get("ok"):
                resp.failure(data.get("error", "race condition request failed"))
            elif data.get("final_stock") != data.get("expected_final_stock"):
                resp.failure("race condition final stock mismatch")
            elif data.get("bookings_created", data.get("orders_created")) != data.get("successful_bookings"):
                resp.failure("race condition booking count mismatch")
            else:
                resp.success()

    @task(1)
    def browser_stress(self):
        payload = {"requests": 200, "concurrency": 10}
        with self.client.post("/api/stress/load", json=payload, name="POST /api/stress/load", catch_response=True) as resp:
            data = resp.json()
            if not data.get("ok"):
                resp.failure(data.get("error", "stress load request failed"))
            elif data.get("completed_requests") != data.get("total_requests"):
                resp.failure("stress load completed request mismatch")
            elif data.get("failed_requests") != 0:
                resp.failure("stress load reported failed requests")
            else:
                resp.success()
