from django.db import models


class Project(models.Model):
    name = models.CharField(max_length=200, verbose_name="Название объекта")
    description = models.TextField(blank=True, verbose_name="Описание")
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="Создан")

    class Meta:
        verbose_name = "Объект"
        verbose_name_plural = "Объекты"
        ordering = ["name"]

    def __str__(self) -> str:
        return self.name


class Stage(models.Model):
    project = models.ForeignKey(Project, on_delete=models.CASCADE, related_name="stages", verbose_name="Объект")
    name = models.CharField(max_length=200, verbose_name="Этап/зона")
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="Создан")

    class Meta:
        verbose_name = "Этап"
        verbose_name_plural = "Этапы"
        ordering = ["project__name", "name"]
        unique_together = [("project", "name")]

    def __str__(self) -> str:
        return f"{self.project} — {self.name}"


