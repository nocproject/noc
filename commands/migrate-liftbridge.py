# ----------------------------------------------------------------------
# Liftbridge streams synchronization tool
# ----------------------------------------------------------------------
# Copyright (C) 2007-2022 The NOC Project
# See LICENSE for details
# ----------------------------------------------------------------------

# Python modules
from functools import partial
from typing import Iterable, Optional

# NOC modules
from noc.core.management.base import BaseCommand
from noc.core.msgstream.config import STREAMS
from noc.core.msgstream.client import MessageStreamClient
from noc.core.mongo.connection import connect
from noc.core.ioloop.util import run_sync
from noc.core.clickhouse.loader import loader as bi_loader
from noc.core.bi.dictionaries.loader import loader as bi_dict_loader
from noc.pm.models.metricscope import MetricScope
from noc.main.models.pool import Pool


class Command(BaseCommand):
    def add_arguments(self, parser):
        parser.add_argument(
            "--slots",
            dest="slots",
            type=int,
            required=False,
            help="Static slot count (used for tests)",
        )

    def handle(self, slots=None, *args, **options):
        # Apply settings
        changed = run_sync(partial(self.apply_stream_settings, slots))
        if changed:
            self.print("CHANGED")
        else:
            self.print("OK")

    @staticmethod
    def iter_streams() -> Iterable[str]:
        connect()

        # Configured streams
        for stream in STREAMS:
            if stream.name == "ch":
                continue
            if not stream.sharded:
                yield stream.name
                continue
            # Pooled streams
            for pool in Pool.objects.all():
                yield f"{stream.name}.{pool.name}"
        # Metric scopes
        for scope in MetricScope.objects.all():
            yield f"ch.{scope.table_name}"
        # BI models
        for name in bi_loader:
            bi_model = bi_loader[name]
            if not bi_model:
                continue
            yield f"ch.{bi_model._meta.db_table}"
        # BI Dictionary models
        for name in bi_dict_loader:
            bi_dict_model = bi_dict_loader[name]
            if bi_dict_model:
                yield f"ch.{bi_dict_model._meta.db_table}"

    async def apply_stream_settings(self, slots: Optional[int] = None) -> bool:
        changed = False
        async with MessageStreamClient() as client:
            for stream in self.iter_streams():
                self.print("Ensuring stream %s" % stream)
                changed |= await client.ensure_stream(stream, partitions=slots)
        return changed


if __name__ == "__main__":
    Command().run()
