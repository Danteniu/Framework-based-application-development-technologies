from __future__ import annotations

from django.conf import settings
from django.db import models
from django.utils import timezone

from projects.models import Project, Stage


class DefectPriority(models.TextChoices):
    LOW = "low", "Низкий"
    MEDIUM = "medium", "Средний"
    HIGH = "high", "Высокий"
    CRITICAL = "critical", "Критический"


class DefectStatus(models.TextChoices):
    NEW = "new", "Новая"
    IN_PROGRESS = "in_progress", "В работе"
    IN_REVIEW = "in_review", "На проверке"
    CLOSED = "closed", "Закрыта"
    CANCELLED = "cancelled", "Отменена"


class Defect(models.Model):
    project = models.ForeignKey(Project, on_delete=models.PROTECT, related_name="defects", verbose_name="Объект")
    stage = models.ForeignKey(
        Stage,
        on_delete=models.PROTECT,
        related_name="defects",
        verbose_name="Этап",
        null=True,
        blank=True,
    )
    title = models.CharField(max_length=200, verbose_name="Заголовок")
    description = models.TextField(verbose_name="Описание")
    priority = models.CharField(
        max_length=20,
        choices=DefectPriority.choices,
        default=DefectPriority.MEDIUM,
        verbose_name="Приоритет",
    )
    status = models.CharField(
        max_length=20,
        choices=DefectStatus.choices,
        default=DefectStatus.NEW,
        verbose_name="Статус",
    )
    assignee = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.PROTECT,
        related_name="assigned_defects",
        null=True,
        blank=True,
        verbose_name="Исполнитель",
    )
    due_date = models.DateField(null=True, blank=True, verbose_name="Срок устранения")
    created_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.PROTECT,
        related_name="created_defects",
        verbose_name="Автор",
    )
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="Создано")
    updated_at = models.DateTimeField(auto_now=True, verbose_name="Обновлено")

    class Meta:
        verbose_name = "Дефект"
        verbose_name_plural = "Дефекты"
        ordering = ["-created_at"]

    def __str__(self) -> str:
        return f"#{self.id} {self.title}"

    def is_overdue(self) -> bool:
        return bool(self.due_date) and self.status not in (DefectStatus.CLOSED, DefectStatus.CANCELLED) and (
            self.due_date < timezone.localdate()
        )

    def allowed_next_statuses(self) -> list[str]:
        transitions: dict[str, list[str]] = {
            DefectStatus.NEW: [DefectStatus.IN_PROGRESS, DefectStatus.CANCELLED],
            DefectStatus.IN_PROGRESS: [DefectStatus.IN_REVIEW, DefectStatus.CANCELLED],
            DefectStatus.IN_REVIEW: [DefectStatus.CLOSED, DefectStatus.IN_PROGRESS, DefectStatus.CANCELLED],
            DefectStatus.CLOSED: [],
            DefectStatus.CANCELLED: [],
        }
        return transitions.get(self.status, [])


class DefectComment(models.Model):
    defect = models.ForeignKey(Defect, on_delete=models.CASCADE, related_name="comments", verbose_name="Дефект")
    author = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.PROTECT, verbose_name="Автор")
    body = models.TextField(verbose_name="Комментарий")
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="Создан")

    class Meta:
        verbose_name = "Комментарий"
        verbose_name_plural = "Комментарии"
        ordering = ["created_at"]


def defect_attachment_path(instance: "DefectAttachment", filename: str) -> str:
    return f"defects/{instance.defect_id}/{filename}"


class DefectAttachment(models.Model):
    defect = models.ForeignKey(Defect, on_delete=models.CASCADE, related_name="attachments", verbose_name="Дефект")
    uploaded_by = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.PROTECT, verbose_name="Загрузил")
    file = models.FileField(upload_to=defect_attachment_path, verbose_name="Файл")
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="Загружен")

    class Meta:
        verbose_name = "Вложение"
        verbose_name_plural = "Вложения"
        ordering = ["-created_at"]


class DefectHistory(models.Model):
    defect = models.ForeignKey(Defect, on_delete=models.CASCADE, related_name="history", verbose_name="Дефект")
    actor = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.PROTECT,
        null=True,
        blank=True,
        verbose_name="Пользователь",
    )
    action = models.CharField(max_length=200, verbose_name="Действие")
    from_status = models.CharField(max_length=20, choices=DefectStatus.choices, null=True, blank=True)
    to_status = models.CharField(max_length=20, choices=DefectStatus.choices, null=True, blank=True)
    changes = models.JSONField(null=True, blank=True, verbose_name="Изменения")
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="Время")

    class Meta:
        verbose_name = "История дефекта"
        verbose_name_plural = "История дефектов"
        ordering = ["-created_at"]


