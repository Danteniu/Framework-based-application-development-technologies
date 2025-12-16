import os
import re

from locust import HttpUser, between, task


class WebUser(HttpUser):
    wait_time = between(0.5, 2.0)

    def on_start(self):
        """
        Логин в Django с CSRF: GET login page -> достать csrf token -> POST credentials.
        Данные берём из env: LOCUST_USERNAME/LOCUST_PASSWORD.
        """
        username = os.environ.get("LOCUST_USERNAME", "loadtest")
        password = os.environ.get("LOCUST_PASSWORD", "loadtest")

        r = self.client.get("/accounts/login/", name="login_page")
        m = re.search(r'name="csrfmiddlewaretoken" value="([^"]+)"', r.text)
        if not m:
            return
        csrf = m.group(1)
        self.client.post(
            "/accounts/login/",
            name="login",
            data={"username": username, "password": password, "csrfmiddlewaretoken": csrf, "next": "/"},
            headers={"Referer": "/accounts/login/"},
        )

    @task(5)
    def defects_list(self):
        self.client.get("/", name="defects_list")

    @task(1)
    def dashboard(self):
        self.client.get("/reports/dashboard/", name="dashboard")


