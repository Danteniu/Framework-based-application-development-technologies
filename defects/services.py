from __future__ import annotations

from typing import Any

from django.db import transaction

from .models import Defect, DefectHistory


@transaction.atomic
def log_defect_action(
    *,
    defect: Defect,
    actor,
    action: str,
    from_status: str | None = None,
    to_status: str | None = None,
    changes: dict[str, Any] | None = None,
) -> None:
    DefectHistory.objects.create(
        defect=defect,
        actor=actor if getattr(actor, "is_authenticated", False) else None,
        action=action,
        from_status=from_status,
        to_status=to_status,
        changes=changes,
    )


