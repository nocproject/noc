# ----------------------------------------------------------------------
# Liftbridge Collector
# ----------------------------------------------------------------------
# Copyright (C) 2007-2020 The NOC Project
# See LICENSE for details
# ----------------------------------------------------------------------

# Python modules
import functools
import random

# Third-party modules
from gufo.liftbridge.client import LiftbridgeClient
from gufo.liftbridge.types import Metadata, PartitionMetadata

# NOC modules
from .base import BaseCollector
from noc.core.ioloop.util import run_sync
from noc.config import config


class LiftbridgeStreamCollector(BaseCollector):
    name = "liftbridge"

    CURSOR_STREAM = {
        "events": "classifier",
        "dispose": "correlator",
        "message": "mx",
        "kafkasender": "kafkasender",
        "jobs": "worker",
        "metrics": "metrics",
    }

    async def resolve_liftbridge(self):
        if hasattr(self, "_broker"):
            return self._broker
        addresses = await config.find_parameter("liftbridge.addresses").async_get()
        # Use random broker from seed
        svc = random.choice(addresses)
        self._broker = [f"{svc.host}:{svc.port}"]

    async def get_meta(self) -> Metadata:
        await self.resolve_liftbridge()
        async with LiftbridgeClient(self._broker) as client:
            return await client.get_metadata()

    async def get_partition_meta(self, stream, partition) -> PartitionMetadata:
        await self.resolve_liftbridge()
        async with LiftbridgeClient(self._broker) as client:
            return await client.get_partition_metadata(stream, partition)

    async def fetch_cursor(self, stream, partition, name):
        await self.resolve_liftbridge()
        async with LiftbridgeClient(self._broker) as client:
            return await client.get_cursor(stream=stream, partition=partition, cursor_id=name)

    def iter_ch_cursors(self, stream, partition):
        # Parse
        cluster = config.clickhouse.cluster_topology.split(",")
        for replica in range(int(cluster[partition])):
            cursor = run_sync(
                functools.partial(self.fetch_cursor, stream, partition, f"chwriter-{replica}")
            )
            yield (
                (
                    "stream_cursor_offset",
                    ("name", stream),
                    ("partition", partition),
                    ("cursor_id", f"chwriter-{replica}"),
                ),
                cursor,
            )

    def iter_metrics(self):
        meta: Metadata = run_sync(self.get_meta)

        for stream in meta.metadata:
            for p in sorted(stream.partitions):
                if stream.name.startswith("_"):
                    continue
                name, pool, cursor = stream.name, None, -1
                if name.startswith("ch"):
                    # Chwriter streams
                    for r in self.iter_ch_cursors(name, p):
                        yield r
                elif "." in name:
                    name, pool = name.split(".", 1)
                if name in self.CURSOR_STREAM:
                    cursor = run_sync(
                        functools.partial(
                            self.fetch_cursor, stream.name, p, self.CURSOR_STREAM[name]
                        )
                    )
                    if pool:
                        yield (
                            (
                                "stream_cursor_offset",
                                ("name", stream.name),
                                ("partition", p),
                                ("cursor_id", self.CURSOR_STREAM[name]),
                                ("pool", pool),
                            ),
                            cursor,
                        )
                    else:
                        yield (
                            (
                                "stream_cursor_offset",
                                ("name", stream.name),
                                ("partition", p),
                                ("cursor_id", self.CURSOR_STREAM[name]),
                            ),
                            cursor,
                        )

                try:
                    p_meta: PartitionMetadata = run_sync(
                        functools.partial(
                            self.get_partition_meta,
                            stream.name,
                            p,
                        )
                    )
                except Exception as e:
                    self.logger.error(
                        "[%s|%s] Failed getting data for partition: %s", stream.name, p, e
                    )
                    continue
                if pool:
                    yield (
                        (
                            "stream_newest_offset",
                            ("name", stream.name),
                            ("partition", p),
                            ("pool", pool),
                        ),
                        p_meta.newest_offset,
                    )
                    yield (
                        (
                            "stream_high_watermark",
                            ("name", stream.name),
                            ("partition", p),
                            ("pool", pool),
                        ),
                        p_meta.high_watermark,
                    )
                else:
                    yield (
                        (
                            "stream_newest_offset",
                            ("name", stream.name),
                            ("partition", p),
                        ),
                        p_meta.newest_offset,
                    )
                    yield (
                        (
                            "stream_high_watermark",
                            ("name", stream.name),
                            ("partition", p),
                        ),
                        p_meta.high_watermark,
                    )
