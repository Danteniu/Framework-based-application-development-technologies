from django.contrib.auth.models import AbstractUser
from django.db import models


class UserRole(models.TextChoices):
    MANAGER = "manager", "Менеджер"
    ENGINEER = "engineer", "Инженер"
    OBSERVER = "observer", "Наблюдатель"


class User(AbstractUser):
    role = models.CharField(
        max_length=20,
        choices=UserRole.choices,
        default=UserRole.ENGINEER,
        verbose_name="Роль",
    )

    class Meta:
        verbose_name = "Пользователь"
        verbose_name_plural = "Пользователи"

    @property
    def is_manager(self) -> bool:
        return self.role == UserRole.MANAGER

    @property
    def is_engineer(self) -> bool:
        return self.role == UserRole.ENGINEER

    @property
    def is_observer(self) -> bool:
        return self.role == UserRole.OBSERVER


