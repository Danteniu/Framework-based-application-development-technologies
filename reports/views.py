from __future__ import annotations

import csv
from datetime import datetime

from django.contrib.auth.decorators import login_required
from django.db.models import Count
from django.db.models import Q
from django.http import HttpRequest, HttpResponse
from django.shortcuts import redirect, render

from accounts.models import UserRole
from defects.models import Defect, DefectStatus
from .excel import defects_to_xlsx


def _is_report_viewer(request: HttpRequest) -> bool:
    return request.user.is_authenticated and request.user.role in (UserRole.MANAGER, UserRole.OBSERVER)

def _filtered_defects(request: HttpRequest):
    qs = Defect.objects.select_related("project", "stage", "assignee").order_by("-created_at")
    status = request.GET.get("status") or ""
    priority = request.GET.get("priority") or ""
    project_id = request.GET.get("project") or ""
    q = request.GET.get("q") or ""
    if status:
        qs = qs.filter(status=status)
    if priority:
        qs = qs.filter(priority=priority)
    if project_id.isdigit():
        qs = qs.filter(project_id=int(project_id))
    if q:
        qs = qs.filter(Q(title__icontains=q) | Q(description__icontains=q))
    sort = request.GET.get("sort") or "-created_at"
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
    return qs


@login_required
def dashboard(request: HttpRequest) -> HttpResponse:
    if not _is_report_viewer(request):
        return redirect("defects:list")

    by_status = list(
        Defect.objects.values("status").annotate(cnt=Count("id")).order_by("status")
    )
    status_map = {k: 0 for k, _ in DefectStatus.choices}
    for row in by_status:
        status_map[row["status"]] = row["cnt"]

    return render(
        request,
        "reports/dashboard.html",
        {
            "status_labels": [label for _, label in DefectStatus.choices],
            "status_values": [status_map[k] for k, _ in DefectStatus.choices],
            "total": Defect.objects.count(),
        },
    )


@login_required
def export_csv(request: HttpRequest) -> HttpResponse:
    if not _is_report_viewer(request):
        return redirect("defects:list")

    qs = _filtered_defects(request)
    response = HttpResponse(content_type="text/csv; charset=utf-8")
    response["Content-Disposition"] = f'attachment; filename="defects_{datetime.now().strftime("%Y%m%d_%H%M%S")}.csv"'

    writer = csv.writer(response)
    writer.writerow(["ID", "Заголовок", "Объект", "Этап", "Статус", "Приоритет", "Исполнитель", "Срок", "Создано"])
    for d in qs:
        writer.writerow(
            [
                d.id,
                d.title,
                d.project.name,
                d.stage.name if d.stage else "",
                d.get_status_display(),
                d.get_priority_display(),
                d.assignee.username if d.assignee else "",
                d.due_date.isoformat() if d.due_date else "",
                d.created_at.strftime("%Y-%m-%d %H:%M"),
            ]
        )
    return response


@login_required
def export_xlsx(request: HttpRequest) -> HttpResponse:
    if not _is_report_viewer(request):
        return redirect("defects:list")
    qs = _filtered_defects(request)
    return defects_to_xlsx(qs)


