from django.test import TestCase
from django.urls import reverse

from accounts.models import User, UserRole
from projects.models import Project
from defects.models import Defect, DefectPriority, DefectStatus


class ReportTests(TestCase):
    def setUp(self):
        self.manager = User.objects.create_user(username="m", password="pass", role=UserRole.MANAGER)
        self.observer = User.objects.create_user(username="o", password="pass", role=UserRole.OBSERVER)
        self.project = Project.objects.create(name="Объект 1")
        Defect.objects.create(
            project=self.project,
            title="Д1",
            description="О1",
            priority=DefectPriority.MEDIUM,
            status=DefectStatus.NEW,
            created_by=self.manager,
        )

    def test_observer_can_export_csv(self):
        self.client.login(username="o", password="pass")
        resp = self.client.get(reverse("reports:export_csv"))
        self.assertEqual(resp.status_code, 200)
        self.assertIn("text/csv", resp["Content-Type"])

    def test_dashboard_accessible_for_manager(self):
        self.client.login(username="m", password="pass")
        resp = self.client.get(reverse("reports:dashboard"))
        self.assertEqual(resp.status_code, 200)


