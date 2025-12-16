from django.test import TestCase
from django.urls import reverse

from accounts.models import User, UserRole
from projects.models import Project, Stage

from .models import Defect, DefectPriority, DefectStatus


class DefectUnitTests(TestCase):
    def setUp(self):
        self.manager = User.objects.create_user(username="m", password="pass", role=UserRole.MANAGER)
        self.engineer = User.objects.create_user(username="e", password="pass", role=UserRole.ENGINEER)
        self.observer = User.objects.create_user(username="o", password="pass", role=UserRole.OBSERVER)
        self.project = Project.objects.create(name="Объект 1")
        self.stage = Stage.objects.create(project=self.project, name="Этап A")

    def test_allowed_transitions_from_new(self):
        d = Defect.objects.create(
            project=self.project,
            stage=self.stage,
            title="t",
            description="d",
            priority=DefectPriority.MEDIUM,
            status=DefectStatus.NEW,
            created_by=self.engineer,
        )
        self.assertIn(DefectStatus.IN_PROGRESS, d.allowed_next_statuses())
        self.assertIn(DefectStatus.CANCELLED, d.allowed_next_statuses())
        self.assertNotIn(DefectStatus.CLOSED, d.allowed_next_statuses())

    def test_observer_cannot_create_defect(self):
        self.client.login(username="o", password="pass")
        resp = self.client.get(reverse("defects:create"))
        self.assertEqual(resp.status_code, 302)

    def test_engineer_create_defect_strips_assignee_and_due_date(self):
        self.client.login(username="e", password="pass")
        resp = self.client.post(
            reverse("defects:create"),
            data={
                "project": self.project.id,
                "stage": self.stage.id,
                "title": "Дефект",
                "description": "Описание",
                "priority": DefectPriority.HIGH,
                "assignee": self.manager.id,
                "due_date": "2030-01-01",
            },
            follow=True,
        )
        self.assertEqual(resp.status_code, 200)
        d = Defect.objects.get(title="Дефект")
        self.assertIsNone(d.assignee)
        self.assertIsNone(d.due_date)


class DefectIntegrationTests(TestCase):
    def setUp(self):
        self.manager = User.objects.create_user(username="m", password="pass", role=UserRole.MANAGER)
        self.engineer = User.objects.create_user(username="e", password="pass", role=UserRole.ENGINEER)
        self.project = Project.objects.create(name="Объект 1")

    def test_manager_full_flow_create_assign_status_close(self):
        self.client.login(username="m", password="pass")
        # create
        resp = self.client.post(
            reverse("defects:create"),
            data={
                "project": self.project.id,
                "stage": "",
                "title": "Д1",
                "description": "О1",
                "priority": DefectPriority.MEDIUM,
                "assignee": self.engineer.id,
                "due_date": "2030-01-01",
            },
        )
        self.assertEqual(resp.status_code, 302)
        d = Defect.objects.get(title="Д1")
        # status: new -> in_progress
        resp = self.client.post(reverse("defects:status", args=[d.id]), data={"status": DefectStatus.IN_PROGRESS, "comment": ""})
        self.assertEqual(resp.status_code, 302)
        d.refresh_from_db()
        self.assertEqual(d.status, DefectStatus.IN_PROGRESS)
        # status: in_progress -> in_review -> closed
        self.client.post(reverse("defects:status", args=[d.id]), data={"status": DefectStatus.IN_REVIEW, "comment": ""})
        self.client.post(reverse("defects:status", args=[d.id]), data={"status": DefectStatus.CLOSED, "comment": "Проверено"})
        d.refresh_from_db()
        self.assertEqual(d.status, DefectStatus.CLOSED)
        self.assertTrue(d.history.count() >= 3)

    def test_engineer_cannot_close(self):
        d = Defect.objects.create(
            project=self.project,
            title="Д2",
            description="О2",
            priority=DefectPriority.MEDIUM,
            status=DefectStatus.IN_REVIEW,
            created_by=self.manager,
        )
        self.client.login(username="e", password="pass")
        resp = self.client.post(reverse("defects:status", args=[d.id]), data={"status": DefectStatus.CLOSED, "comment": ""}, follow=True)
        d.refresh_from_db()
        self.assertNotEqual(d.status, DefectStatus.CLOSED)

    def test_engineer_sees_only_own_defects(self):
        # assigned to engineer
        Defect.objects.create(
            project=self.project,
            title="Mine",
            description="x",
            priority=DefectPriority.MEDIUM,
            status=DefectStatus.NEW,
            assignee=self.engineer,
            created_by=self.manager,
        )
        # чужой
        Defect.objects.create(
            project=self.project,
            title="NotMine",
            description="y",
            priority=DefectPriority.MEDIUM,
            status=DefectStatus.NEW,
            created_by=self.manager,
        )
        self.client.login(username="e", password="pass")
        resp = self.client.get(reverse("defects:list"))
        self.assertContains(resp, "Mine")
        self.assertNotContains(resp, "NotMine")


