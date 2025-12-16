from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.db.models.deletion import ProtectedError
from django.http import HttpRequest, HttpResponse
from django.shortcuts import get_object_or_404, redirect, render

from accounts.models import UserRole

from .forms import ProjectForm, StageForm
from .models import Project, Stage


def _require_manager(request: HttpRequest) -> bool:
    return request.user.is_authenticated and request.user.role == UserRole.MANAGER


@login_required
def list_projects(request: HttpRequest) -> HttpResponse:
    projects = Project.objects.all()
    return render(request, "projects/list.html", {"projects": projects})


@login_required
def create_project(request: HttpRequest) -> HttpResponse:
    if not _require_manager(request):
        return redirect("projects:list")
    if request.method == "POST":
        form = ProjectForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect("projects:list")
    else:
        form = ProjectForm()
    return render(request, "generic/form.html", {"form": form, "title": "Создать объект"})


@login_required
def edit_project(request: HttpRequest, project_id: int) -> HttpResponse:
    if not _require_manager(request):
        return redirect("projects:list")
    project = get_object_or_404(Project, id=project_id)
    if request.method == "POST":
        form = ProjectForm(request.POST, instance=project)
        if form.is_valid():
            form.save()
            return redirect("projects:list")
    else:
        form = ProjectForm(instance=project)
    return render(request, "generic/form.html", {"form": form, "title": "Редактировать объект"})


@login_required
def delete_project(request: HttpRequest, project_id: int) -> HttpResponse:
    if not _require_manager(request):
        return redirect("projects:list")
    project = get_object_or_404(Project, id=project_id)
    if request.method == "POST":
        try:
            project.delete()
            messages.success(request, "Объект удалён.")
        except ProtectedError:
            messages.error(request, "Нельзя удалить объект: есть связанные дефекты.")
        return redirect("projects:list")
    return render(
        request,
        "generic/confirm_delete.html",
        {"title": "Удалить объект", "object_name": project.name, "cancel_url": "projects:list"},
    )


@login_required
def list_stages(request: HttpRequest) -> HttpResponse:
    stages = Stage.objects.select_related("project").all()
    return render(request, "projects/stages.html", {"stages": stages})


@login_required
def create_stage(request: HttpRequest) -> HttpResponse:
    if not _require_manager(request):
        return redirect("projects:stages")
    if request.method == "POST":
        form = StageForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect("projects:stages")
    else:
        form = StageForm()
    return render(request, "generic/form.html", {"form": form, "title": "Создать этап"})


@login_required
def edit_stage(request: HttpRequest, stage_id: int) -> HttpResponse:
    if not _require_manager(request):
        return redirect("projects:stages")
    stage = get_object_or_404(Stage, id=stage_id)
    if request.method == "POST":
        form = StageForm(request.POST, instance=stage)
        if form.is_valid():
            form.save()
            messages.success(request, "Этап обновлён.")
            return redirect("projects:stages")
    else:
        form = StageForm(instance=stage)
    return render(request, "generic/form.html", {"form": form, "title": "Редактировать этап"})


@login_required
def delete_stage(request: HttpRequest, stage_id: int) -> HttpResponse:
    if not _require_manager(request):
        return redirect("projects:stages")
    stage = get_object_or_404(Stage, id=stage_id)
    if request.method == "POST":
        try:
            stage.delete()
            messages.success(request, "Этап удалён.")
        except ProtectedError:
            messages.error(request, "Нельзя удалить этап: есть связанные дефекты.")
        return redirect("projects:stages")
    return render(
        request,
        "generic/confirm_delete.html",
        {"title": "Удалить этап", "object_name": str(stage), "cancel_url": "projects:stages"},
    )

