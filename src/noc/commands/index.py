# ----------------------------------------------------------------------
# Full-Text search manipulation
# ----------------------------------------------------------------------
# Copyright (C) 2007-2026 The NOC Project
# See LICENSE for details
# ----------------------------------------------------------------------

# Python modules
import argparse

# NOC modules
from noc.core.management.base import BaseCommand
from noc.core.mongo.connection import connect
from noc.main.models.textindex import TextIndex
from noc.models import FTS_MODELS, get_model


class Command(BaseCommand):
    def add_arguments(self, parser: argparse.ArgumentParser) -> None:
        subparsers = parser.add_subparsers(dest="cmd", help="sub-commands help", required=True)
        # Search parameters
        search_parser = subparsers.add_parser("search", help="Full-text search")
        search_parser.add_argument("query", nargs=1, help="Query terms")
        search_parser.add_argument(
            "--format",
            action="store",
            dest="format",
            default="yaml",
            choices=["yaml", "json"],
            help="Output format",
        )
        # Rebuild parameters
        rebuild_parser = subparsers.add_parser("rebuild", help="Rebuild index")  # noqa

    def handle(self, cmd, *args, **options):
        connect()
        getattr(self, f"handle_{cmd}")(*args, **options)

    def handle_search(self, query, format, *args, **options):
        r = []
        for qr in TextIndex.search(query[0]):
            r.append(
                {
                    "id": str(f"{qr.model}:{qr.object}"),
                    "title": str(qr.title),
                    "card": str(qr.card),
                }
            )
            if qr.tags:
                r[-1]["tags"] = [str(x) for x in qr.tags]
        if format == "yaml":
            import yaml

            yaml.dump(r, stream=self.stdout)
        else:
            import json

            json.dump(r, self.stdout)

    def handle_rebuild(self, *args, **options):
        for model_id in FTS_MODELS:
            self.stdout.write(f"Indexing {model_id}: ")
            model = get_model(model_id)
            n = 0
            for o in model.objects.all():
                TextIndex.update_index(model, o)
                n += 1
            self.stdout.write(f"{int(n)} records indexed\n")
