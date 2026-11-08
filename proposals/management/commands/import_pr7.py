"""Однократный перенос данных из SQLite ПР7 в базу Django."""

import sqlite3
from pathlib import Path

from django.conf import settings
from django.core.management.base import BaseCommand, CommandError
from django.db import IntegrityError, transaction

from clients.models import Client
from proposals.models import Manager, Proposal


class Command(BaseCommand):
    help = "Перенести клиентов, менеджеров и предложения из базы ПР7."

    def add_arguments(self, parser):
        parser.add_argument(
            "--source",
            type=Path,
            default=settings.BASE_DIR / "data" / "offers.sqlite",
            help="Путь к исходной базе SQLite.",
        )

    def handle(self, *args, **options):
        source = options["source"].resolve()
        connection = None
        try:
            connection = sqlite3.connect(
                f"{source.as_uri()}?mode=ro",
                uri=True,
            )
            connection.row_factory = sqlite3.Row
            with transaction.atomic():
                counts = []
                for table, model in (
                    ("clients", Client),
                    ("managers", Manager),
                    ("proposals", Proposal),
                ):
                    added = 0
                    for row in connection.execute(f"SELECT * FROM {table}"):
                        data = dict(row)
                        pk = data.pop("id")
                        if model is Proposal:
                            old_status = data["status"]
                            data["status"] = {
                                label: value
                                for value, label in Proposal.Status.choices
                            }.get(old_status, old_status)
                        _, created = model.objects.get_or_create(
                            pk=pk,
                            defaults=data,
                        )
                        added += created
                    counts.append(f"{table}: {added}")
        except (sqlite3.Error, IntegrityError) as error:
            raise CommandError(f"Перенос прерван: {error}") from error
        finally:
            if connection is not None:
                connection.close()
        self.stdout.write(
            self.style.SUCCESS("Добавлено: " + ", ".join(counts)),
        )
