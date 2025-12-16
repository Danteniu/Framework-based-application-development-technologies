from __future__ import annotations

from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.core.paginator import Paginator
from django.db.models import Q
from django.http import HttpRequest, HttpResponse
from django.shortcuts import get_object_or_404, redirect, render

from accounts.models import UserRole
from projects.models import Project

from .forms import AttachmentForm, CommentForm, DefectForm, StatusChangeForm
from .models import Defect, DefectPriority, DefectStatus
from .services import log_defect_action


def _is_manager(request: HttpRequest) -> bool:
    return request.user.is_authenticated and request.user.role == UserRole.MANAGER


def _is_engineer(request: HttpRequest) -> bool:
    return request.user.is_authenticated and request.user.role == UserRole.ENGINEER


def _can_work_with_defect(request: HttpRequest, defect: Defect) -> bool:
    if _is_manager(request):
        return True
    if _is_engineer(request):
        return defect.assignee_id == request.user.id or defect.created_by_id == request.user.id
    return False


@login_required
def list_defects(request: HttpRequest) -> HttpResponse:
    qs = (
        Defect.objects.select_related("project", "stage", "assignee", "created_by")
        .all()
    )

    # Наблюдатель видит всё (read-only). Инженер — только свои (назначенные или созданные).
    if _is_engineer(request):
        qs = qs.filter(Q(assignee_id=request.user.id) | Q(created_by_id=request.user.id))

    status = request.GET.get("status") or ""
    priority = request.GET.get("priority") or ""
    project_id = request.GET.get("project") or ""
    q = request.GET.get("q") or ""
    sort = request.GET.get("sort") or "-created_at"

    if status:
        qs = qs.filter(status=status)
    if priority:
        qs = qs.filter(priority=priority)
    if project_id.isdigit():
        qs = qs.filter(project_id=int(project_id))
    if q:
        qs = qs.filter(Q(title__icontains=q) | Q(description__icontains=q))

    allowed_sorts = {
        "-created_at": "-created_at",
        "created_at": "created_at",
        "due_date": "due_date",
        "-due_date": "-due_date",
        "priority": "priority",
        "-priority": "-priority",
        "status": "status",
        "-status": "-status",
    }
    qs = qs.order_by(allowed_sorts.get(sort, "-created_at"))

    paginator = Paginator(qs, 25)
    page_obj = paginator.get_page(request.GET.get("page") or 1)

    projects = Project.objects.all()
    qs_params = request.GET.copy()
    qs_params.pop("page", None)
    filters_qs = qs_params.urlencode()

    return render(
        request,
        "defects/list.html",
        {
            "defects": page_obj.object_list,
            "page_obj": page_obj,
            "projects": projects,
            "status_choices": DefectStatus.choices,
            "priority_choices": DefectPriority.choices,
            "filters": {"status": status, "priority": priority, "project": project_id, "q": q, "sort": sort},
            "filters_qs": filters_qs,
        },
    )


@login_required
def defect_detail(request: HttpRequest, defect_id: int) -> HttpResponse:
    defect = get_object_or_404(
        Defect.objects.select_related("project", "stage", "assignee", "created_by"), id=defect_id
    )

    can_manage = _is_manager(request)
    can_edit = can_manage or (_is_engineer(request) and _can_work_with_defect(request, defect))
    can_comment = can_edit
    can_attach = can_edit
    can_change_status = can_edit

    comment_form = CommentForm()
    attachment_form = AttachmentForm()
    allowed_next = defect.allowed_next_statuses()
    status_labels = dict(DefectStatus.choices)
    choices = [defect.status] + allowed_next
    status_form = StatusChangeForm(initial={"status": defect.status})
    status_form.fields["status"].choices = [(s, status_labels.get(s, s)) for s in choices]

    return render(
        request,
        "defects/detail.html",
        {
            "defect": defect,
            "can_edit": can_edit,
            "can_manage": can_manage,
            "can_comment": can_comment,
            "can_attach": can_attach,
            "can_change_status": can_change_status,
            "comment_form": comment_form,
            "attachment_form": attachment_form,
            "status_form": status_form,
            "allowed_next": allowed_next,
            "allowed_next_labels": [status_labels.get(s, s) for s in allowed_next],
        },
    )


@login_required
def create_defect(request: HttpRequest) -> HttpResponse:
    if request.user.role == UserRole.OBSERVER:
        return redirect("defects:list")

    if request.method == "POST":
        form = DefectForm(request.POST, user=request.user)
        if form.is_valid():
            defect: Defect = form.save(commit=False)
            defect.created_by = request.user
            if request.user.role != UserRole.MANAGER:
                # Инженер создаёт дефект, но назначение исполнителя/срока — менеджер.
                defect.assignee = None
                defect.due_date = None
            defect.save()
            log_defect_action(defect=defect, actor=request.user, action="Создан дефект", from_status=None, to_status=defect.status)
            messages.success(request, "Дефект создан.")
            return redirect("defects:detail", defect_id=defect.id)
    else:
        form = DefectForm(user=request.user)

    return render(request, "defects/form.html", {"form": form, "title": "Создать дефект"})


@login_required
def edit_defect(request: HttpRequest, defect_id: int) -> HttpResponse:
    if request.user.role == UserRole.OBSERVER:
        return redirect("defects:detail", defect_id=defect_id)

    defect = get_object_or_404(Defect, id=defect_id)
    if _is_engineer(request) and not _can_work_with_defect(request, defect):
        messages.error(request, "У вас нет прав на редактирование этого дефекта.")
        return redirect("defects:detail", defect_id=defect_id)

    old = {"title": defect.title, "description": defect.description, "priority": defect.priority, "assignee_id": defect.assignee_id, "due_date": str(defect.due_date) if defect.due_date else None}
    old_assignee_id = defect.assignee_id
    old_due_date = defect.due_date

    if request.method == "POST":
        form = DefectForm(request.POST, instance=defect, user=request.user)
        if form.is_valid():
            defect = form.save(commit=False)
            if request.user.role != UserRole.MANAGER:
                defect.assignee_id = old_assignee_id
                defect.due_date = old_due_date
            defect.save()
            new = {"title": defect.title, "description": defect.description, "priority": defect.priority, "assignee_id": defect.assignee_id, "due_date": str(defect.due_date) if defect.due_date else None}
            changes = {k: {"from": old[k], "to": new[k]} for k in old.keys() if old[k] != new[k]}
            if changes:
                log_defect_action(defect=defect, actor=request.user, action="Изменены поля дефекта", changes=changes)
            messages.success(request, "Изменения сохранены.")
            return redirect("defects:detail", defect_id=defect.id)
    else:
        form = DefectForm(instance=defect, user=request.user)

    return render(request, "defects/form.html", {"form": form, "title": f"Редактировать дефект #{defect.id}"})


@login_required
def add_comment(request: HttpRequest, defect_id: int) -> HttpResponse:
    if request.user.role == UserRole.OBSERVER:
        return redirect("defects:detail", defect_id=defect_id)

    defect = get_object_or_404(Defect, id=defect_id)
    if _is_engineer(request) and not _can_work_with_defect(request, defect):
        messages.error(request, "У вас нет прав на комментарии по этому дефекту.")
        return redirect("defects:detail", defect_id=defect_id)
    form = CommentForm(request.POST)
    if form.is_valid():
        comment = form.save(commit=False)
        comment.defect = defect
        comment.author = request.user
        comment.save()
        log_defect_action(defect=defect, actor=request.user, action="Добавлен комментарий")
    return redirect("defects:detail", defect_id=defect_id)


@login_required
def add_attachment(request: HttpRequest, defect_id: int) -> HttpResponse:
    if request.user.role == UserRole.OBSERVER:
        return redirect("defects:detail", defect_id=defect_id)

    defect = get_object_or_404(Defect, id=defect_id)
    if _is_engineer(request) and not _can_work_with_defect(request, defect):
        messages.error(request, "У вас нет прав на вложения по этому дефекту.")
        return redirect("defects:detail", defect_id=defect_id)
    form = AttachmentForm(request.POST, request.FILES)
    if form.is_valid():
        att = form.save(commit=False)
        att.defect = defect
        att.uploaded_by = request.user
        att.save()
        log_defect_action(defect=defect, actor=request.user, action="Добавлено вложение")
    else:
        messages.error(request, "Не удалось загрузить файл.")
    return redirect("defects:detail", defect_id=defect_id)


@login_required
def change_status(request: HttpRequest, defect_id: int) -> HttpResponse:
    if request.user.role == UserRole.OBSERVER:
        return redirect("defects:detail", defect_id=defect_id)

    defect = get_object_or_404(Defect, id=defect_id)
    if _is_engineer(request) and defect.assignee_id != request.user.id:
        messages.error(request, "Инженер может менять статус только у назначенных ему дефектов.")
        return redirect("defects:detail", defect_id=defect_id)
    form = StatusChangeForm(request.POST)
    if not form.is_valid():
        return redirect("defects:detail", defect_id=defect_id)

    new_status = form.cleaned_data["status"]
    comment = (form.cleaned_data.get("comment") or "").strip()

    if new_status == defect.status:
        return redirect("defects:detail", defect_id=defect_id)

    if new_status not in defect.allowed_next_statuses():
        messages.error(request, "Недопустимый переход статуса.")
        return redirect("defects:detail", defect_id=defect_id)

    # Менеджер может закрывать/отменять. Инженер — только рабочие статусы.
    if not _is_manager(request) and new_status in (DefectStatus.CLOSED, DefectStatus.CANCELLED):
        messages.error(request, "Недостаточно прав для закрытия/отмены.")
        return redirect("defects:detail", defect_id=defect_id)

    from_status = defect.status
    defect.status = new_status
    defect.save(update_fields=["status", "updated_at"])
    log_defect_action(defect=defect, actor=request.user, action="Изменён статус", from_status=from_status, to_status=new_status)
    if comment:
        defect.comments.create(author=request.user, body=comment)
    messages.success(request, "Статус обновлён.")
    return redirect("defects:detail", defect_id=defect_id)


