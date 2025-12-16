from django.contrib import admin

from .models import Project, Stage


@admin.register(Project)
class ProjectAdmin(admin.ModelAdmin):
    search_fields = ("name",)
    list_display = ("name", "created_at")


@admin.register(Stage)
class StageAdmin(admin.ModelAdmin):
    search_fields = ("name", "project__name")
    list_display = ("name", "project", "created_at")
    list_filter = ("project",)


