from __future__ import annotations

from datetime import datetime

from django.http import HttpResponse
from openpyxl import Workbook

from defects.models import Defect


def defects_to_xlsx(qs) -> HttpResponse:
    wb = Workbook()
    ws = wb.active
    ws.title = "Дефекты"

    ws.append(["ID", "Заголовок", "Объект", "Этап", "Статус", "Приоритет", "Исполнитель", "Срок", "Создано"])
    for d in qs:
        ws.append(
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

    response = HttpResponse(
        content_type="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
    )
    response["Content-Disposition"] = (
        f'attachment; filename="defects_{datetime.now().strftime("%Y%m%d_%H%M%S")}.xlsx"'
    )
    wb.save(response)
    return response


