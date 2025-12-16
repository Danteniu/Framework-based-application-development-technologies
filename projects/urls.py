from django.urls import path

from . import views

app_name = "projects"

urlpatterns = [
    path("", views.list_projects, name="list"),
    path("create/", views.create_project, name="create"),
    path("<int:project_id>/edit/", views.edit_project, name="edit"),
    path("<int:project_id>/delete/", views.delete_project, name="delete"),
    path("stages/", views.list_stages, name="stages"),
    path("stages/create/", views.create_stage, name="stage_create"),
    path("stages/<int:stage_id>/edit/", views.edit_stage, name="stage_edit"),
    path("stages/<int:stage_id>/delete/", views.delete_stage, name="stage_delete"),
]


