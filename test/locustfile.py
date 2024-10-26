from locust import HttpUser, between, task


class WebsiteUser(HttpUser):
    wait_time = between(5, 15)

    def on_start(self) -> None:
        self.client.cookies.set("authentication",
                                "338e63b0-b40e-4cbf-9611-322fa9af4740")

    @task
    def index(self):
        self.client.get("/")

    @task
    def summary(self):
        self.client.get("/summary")

    @task
    def pointsdisplay(self):
        self.client.get("/pointsdisplay")
