from locust import HttpUser, between, task


class WebUser(HttpUser):
    wait_time = between(0.5, 2.0)

    @task(5)
    def defects_list(self):
        self.client.get("/accounts/login/", name="login_page")
        self.client.get("/", name="defects_list")

    @task(1)
    def dashboard(self):
        self.client.get("/reports/dashboard/", name="dashboard")


