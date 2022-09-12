# ----------------------------------------------------------------------
# Liftbridge streams synchronization tool
# ----------------------------------------------------------------------
# Copyright (C) 2007-2022 The NOC Project
# See LICENSE for details
# ----------------------------------------------------------------------

# Python modules
from typing import Iterable

# NOC modules
from noc.core.management.base import BaseCommand
from noc.core.liftbridge.base import (
    LiftBridgeClient,
    Metadata,
    STREAM_CONFIG,
)
from noc.core.messagestream.base import Metadata, stream_client
from noc.core.mongo.connection import connect
from noc.core.ioloop.util import run_sync
from noc.core.clickhouse.loader import loader as bi_loader
from noc.core.bi.dictionaries.loader import loader as bi_dict_loader
from noc.main.models.pool import Pool
from noc.pm.models.metricscope import MetricScope


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
        changed = False
        # Apply settings
        for stream in self.iter_streams():
            self.print("Ensuring stream %s" % stream)
            changed |= self.apply_stream_settings(stream, partitions=slots)
        if changed:
            self.print("CHANGED")
        else:
            self.print("OK")

    def get_meta(self) -> Metadata:
        async def get_meta() -> Metadata:
            async with stream_client as client:
                return await client.fetch_metadata()

        return run_sync(get_meta)

    def iter_streams(self) -> Iterable[str]:
        connect()

        # Configured streams
        for stream in STREAM_CONFIG:
            if stream == "ch":
                continue
            if not STREAM_CONFIG[stream].pooled:
                yield stream
                continue
            # Pooled streams
            for pool in Pool.objects.all():
                yield f"{stream}.{pool.name}"
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

    def apply_stream_settings(self, stream: str, partitions: int) -> bool:
        async def ensure_stream() -> bool:
            async with LiftBridgeClient() as client:
                return await client.ensure_stream(stream, partitions=partitions)

        return run_sync(ensure_stream)


if __name__ == "__main__":
    Command().run()
