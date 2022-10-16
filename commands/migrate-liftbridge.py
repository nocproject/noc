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
            changed |= self.apply_stream_settings(meta, stream, partitions, rf)
        if changed:
            self.print("CHANGED")
        else:
            self.print("OK")

    def get_meta(self) -> Metadata:
        async def get_meta() -> Metadata:
            async with LiftBridgeClient() as client:
                return await client.fetch_metadata()

        return run_sync(get_meta)

    def iter_limits(self) -> Iterable[Tuple[StreamConfig, int]]:
        connect()

        # Configured streams
        for sc in STREAM_CONFIG.values():
            if not sc.enable:
                continue
            if not sc.pooled:
                yield sc, sc.get_partitions()
                continue
            # Pooled streams
            for pool in Pool.objects.all():
                yield sc, sc.get_partitions(pool.name)
        # Metric scopes
        for scope in MetricScope.objects.all():
            yield scope.get_stream_config()
        # BI models
        for name in bi_loader:
            bi_model = bi_loader[name]
            if not bi_model:
                continue
            yield bi_model.get_stream_config()
        # BI Dictionary models
        for name in bi_dict_loader:
            bi_dict_model = bi_dict_loader[name]
            if bi_dict_model:
                yield bi_dict_model.get_stream_config()

    def apply_stream_settings(
        self, meta: Metadata, stream: StreamConfig, partitions: int, rf: int
    ) -> bool:
        def create_stream(cfg: StreamConfig, n_partitions: int, replication_factor: int):
            minisr = 0
            if cfg.replication_factor:
                replication_factor = min(cfg.replication_factor, replication_factor)
                minisr = min(2, replication_factor)

            async def wrapper():
                async with LiftBridgeClient() as client:
                    await client.create_stream(
                        subject=cfg.name,
                        name=cfg.name,
                        partitions=n_partitions,
                        minisr=minisr,
                        replication_factor=replication_factor,
                        retention_max_bytes=cfg.retention_policy.retention_bytes,
                        retention_max_age=cfg.retention_policy.retention_ages,
                        segment_max_bytes=cfg.retention_policy.segment_bytes,
                        segment_max_age=cfg.retention_policy.segment_ages,
                        auto_pause_time=cfg.auto_pause_time,
                        auto_pause_disable_if_subscribers=cfg.auto_pause_disable,
                    )

            run_sync(wrapper)

        def alter_stream(
            current_meta: StreamMetadata, new_partitions: int, replication_factor: int
        ):
            name = current_meta.name
            old_partitions = len(current_meta.partitions)
            n_msg: Dict[int, int] = {}  # partition -> copied messages

            async def get_partition_meta(stream, partition):
                async with LiftBridgeClient() as client:
                    return await client.fetch_partition_metadata(stream, partition)

            async def wrapper():
                self.print(f"Altering stream {name}")
                async with LiftBridgeClient() as client:
                    # Create temporary stream with same structure, as original one
                    tmp_stream = f"__tmp-{name}"
                    self.print(f"Creating temporary stream {tmp_stream}")
                    await client.create_stream(
                        subject=tmp_stream,
                        name=tmp_stream,
                        partitions=old_partitions,
                        replication_factor=replication_factor,
                    )
                    # Copy all unread data to temporary stream as is
                    for partition in range(old_partitions):
                        self.print(
                            "Copying partition %s:%s to %s:%s"
                            % (name, partition, tmp_stream, partition)
                        )
                        n_msg[partition] = 0
                        # Get current offset
                        p_meta = run_sync(functools.partial(get_partition_meta, stream, partition))
                        newest_offset = p_meta.newest_offset or 0
                        # Fetch cursor
                        current_offset = await client.fetch_cursor(
                            stream=stream.name,
                            partition=partition,
                            cursor_id=stream.cursor_name,
                        )
                        if current_offset > newest_offset:
                            # Fix if cursor not set properly
                            current_offset = newest_offset
                        self.print(
                            "Start copying from current_offset: %s to newest offset: %s"
                            % (current_offset, newest_offset)
                        )
                        if current_offset < newest_offset:
                            async for msg in client.subscribe(
                                stream=name, partition=partition, start_offset=current_offset
                            ):
                                await client.publish(
                                    msg.value,
                                    stream=tmp_stream,
                                    partition=partition,
                                )
                                n_msg[partition] += 1
                                if msg.offset == newest_offset:
                                    break
                        if n_msg[partition]:
                            self.print("  %d messages has been copied" % n_msg[partition])
                        else:
                            self.print("  nothing to copy")
                    # Drop original stream
                    self.print("Dropping original stream %s" % name)
                    await client.delete_stream(name)
                    # Create new stream with required structure
                    self.print("Creating stream %s" % name)
                    await client.create_stream(
                        subject=name,
                        name=name,
                        partitions=new_partitions,
                        replication_factor=replication_factor,
                    )
                    # Copy data from temporary stream to a new one
                    for partition in range(old_partitions):
                        self.print(
                            "Restoring partition %s:%s to %s"
                            % (tmp_stream, partition, new_partitions)
                        )
                        # Re-route dropped partitions to partition 0
                        dest_partition = partition if partition < new_partitions else 0
                        n = n_msg[partition]
                        if n > 0:
                            async for msg in client.subscribe(
                                stream=tmp_stream,
                                partition=partition,
                                start_position=StartPosition.EARLIEST,
                            ):
                                await client.publish(
                                    msg.value, stream=name, partition=dest_partition
                                )
                                n -= 1
                                if not n:
                                    break
                            self.print(f"  {n_msg[partition]} messages restored")
                        else:
                            self.print("  nothing to restore")
                    # Drop temporary stream
                    self.print(f"Dropping temporary stream {tmp_stream}")
                    await client.delete_stream(tmp_stream)
                    # Uh-oh
                    self.print(f"Stream {name} has been altered")

            run_sync(wrapper)

        stream_meta = None
        for m in meta.metadata:
            if m.name == stream.name:
                stream_meta = m
                break
        # Check if stream is configured properly
        if stream_meta and len(stream_meta.partitions) == partitions:
            return False
        # Check if stream must be altered
        if stream_meta:
            self.print(
                "Altering stream %s due to partition/replication factor mismatch (%d -> %d)"
                % (
                    stream.name,
                    len(stream_meta.partitions),
                    partitions,
                )
            )
            alter_stream(stream_meta, partitions, rf)
            return True
        # Create stream
        self.print(f"Creating stream {stream.name} with {partitions} partitions")
        create_stream(stream, partitions, rf)
        return True


if __name__ == "__main__":
    Command().run()
