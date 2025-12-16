from __future__ import annotations

import shutil
from datetime import datetime, timedelta
from pathlib import Path

from django.conf import settings
from django.core.management.base import BaseCommand


class Command(BaseCommand):
    help = "Создать резервную копию БД (для SQLite — копирование файла)."

    def add_arguments(self, parser):
        parser.add_argument(
            "--retention-days",
            type=int,
            default=14,
            help="Сколько дней хранить бэкапы (по умолчанию 14).",
        )

    def handle(self, *args, **options):
        db = settings.DATABASES["default"]
        engine = db.get("ENGINE", "")

        backups_dir = Path(settings.BASE_DIR) / "backups"
        backups_dir.mkdir(exist_ok=True)

        if engine.endswith("sqlite3"):
            src = Path(db["NAME"])
            if not src.exists():
                self.stderr.write(self.style.ERROR(f"SQLite файл не найден: {src}"))
                return 1
            ts = datetime.now().strftime("%Y%m%d_%H%M%S")
            dst = backups_dir / f"db_{ts}.sqlite3"
            shutil.copy2(src, dst)
            self.stdout.write(self.style.SUCCESS(f"Backup created: {dst}"))
        else:
            self.stderr.write(
                self.style.ERROR("Для не-SQLite БД добавьте внешний бэкап (pg_dump / mysqldump).")
            )
            return 2

        retention_days = int(options["retention_days"])
        cutoff = datetime.now() - timedelta(days=retention_days)
        for p in backups_dir.glob("db_*.sqlite3"):
            try:
                mtime = datetime.fromtimestamp(p.stat().st_mtime)
                if mtime < cutoff:
                    p.unlink(missing_ok=True)
            except OSError:
                pass

        return 0


