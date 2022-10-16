# ----------------------------------------------------------------------
# Liftbridge streams synchronization tool
# ----------------------------------------------------------------------
# Copyright (C) 2007-2022 The NOC Project
# See LICENSE for details
# ----------------------------------------------------------------------

# Python modules
from typing import Tuple, Dict, Iterable
import functools

# NOC modules
from noc.core.management.base import BaseCommand
from noc.core.liftbridge.base import (
    LiftBridgeClient,
    Metadata,
    StreamMetadata,
    StartPosition,
    STREAM_CONFIG,
    StreamConfig,
)
from noc.core.mongo.connection import connect
from noc.core.ioloop.util import run_sync
from noc.core.clickhouse.loader import loader as bi_loader
from noc.core.bi.dictionaries.loader import loader as bi_dict_loader
from noc.main.models.pool import Pool
from noc.pm.models.metricscope import MetricScope


class Command(BaseCommand):
    _slots = None

    def add_arguments(self, parser):
        parser.add_argument(
            "--slots",
            dest="slots",
            type=int,
            required=False,
            help="Static slot count (used for tests)",
        )

    def handle(self, slots=None, *args, **options):
        if slots:
            self._slots = slots
        changed = False
        # Get liftbridge metadata
        meta = self.get_meta()
        rf = min(len(meta.brokers), 2)
        # Apply settings
        for stream, partitions in self.iter_limits():
            if not partitions:
                self.print("Stream '%s' without partition. Skipping.." % partitions)
                continue
            self.print("Ensuring stream %s" % stream)
            changed |= self.apply_stream_settings(stream, partitions, rf)
        if changed:
            self.print("CHANGED")
        else:
            self.print("OK")

    def get_meta(self) -> Metadata:
        async def get_meta() -> Metadata:
            async with LiftBridgeClient() as client:
                return await client.fetch_metadata()

        return run_sync(get_meta)

    def iter_limits(self) -> Iterable[Tuple[str, int]]:
        connect()

        # Configured streams
        for stream in STREAM_CONFIG:
            yield stream, None
            # Pooled streams
            # for pool in Pool.objects.all():
            #     yield f"{stream}.{pool.name}", None
        # Metric scopes
        for scope in MetricScope.objects.all():
            yield f"ch.{scope.table_name}", None
        # BI models
        for name in bi_loader:
            bi_model = bi_loader[name]
            if not bi_model:
                continue
            yield f"ch.{bi_model._meta.db_table}", None
        # BI Dictionary models
        for name in bi_dict_loader:
            bi_dict_model = bi_dict_loader[name]
            if bi_dict_model:
                yield f"ch.{bi_dict_model._meta.db_table}", None

    def apply_stream_settings(self, stream: str, partitions: int, rf: int) -> bool:
        async def ensure_stream() -> bool:
            async with LiftBridgeClient() as client:
                return await client.ensure_stream(stream, partitions=partitions)

        return run_sync(ensure_stream)


if __name__ == "__main__":
    Command().run()
