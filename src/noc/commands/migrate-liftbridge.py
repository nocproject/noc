# ----------------------------------------------------------------------
# Liftbridge streams synchronization tool
# ----------------------------------------------------------------------
# Copyright (C) 2007-2026 The NOC Project
# See LICENSE for details
# ----------------------------------------------------------------------

# Python modules
import argparse
import asyncio
from collections.abc import Iterable

# NOC modules
from noc.core.bi.dictionaries.loader import loader as bi_dict_loader
from noc.core.clickhouse.loader import loader as bi_loader
from noc.core.datasources.base import data_source_loader
from noc.core.ioloop.util import get_loop_factory
from noc.core.management.base import BaseCommand
from noc.core.mongo.connection import connect
from noc.core.msgstream.client import MessageStreamClient
from noc.core.msgstream.config import STREAMS
from noc.main.models.pool import Pool
from noc.pm.models.metricscope import MetricScope


class Command(BaseCommand):
    def add_arguments(self, parser: argparse.ArgumentParser) -> None:
        parser.add_argument(
            "--slots",
            dest="slots",
            type=int,
            required=False,
            help="Static slot count (used for tests)",
        )

    def handle(self, slots=None, *args, **options):
        # Apply settings
        changed = asyncio.run(self.apply_stream_settings(slots), loop_factory=get_loop_factory())
        if changed:
            self.print("CHANGED")
        else:
            self.print("OK")

    @staticmethod
    def iter_streams() -> Iterable[str]:
        connect()
        # Get all pools
        all_pools = list(Pool.objects.all())
        # Configured streams
        for stream in STREAMS:
            if stream.name == "ch":
                continue
            if not stream.sharded:
                yield stream.name
                continue
            # Pooled streams
            for pool in all_pools:
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
        # Datasource Reports
        for name in data_source_loader:
            ds_report_model = data_source_loader.get(name)
            if ds_report_model and ds_report_model.clickhouse_mirror():
                yield f"ch.{ds_report_model._get_db_table()}"

    async def apply_stream_settings(self, slots: int | None = None) -> bool:
        changed = False
        async with MessageStreamClient() as client:
            for stream in self.iter_streams():
                self.print(f"Ensuring stream {stream}")
                changed |= await client.ensure_stream(stream, partitions=slots)
        return changed
