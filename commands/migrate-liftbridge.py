# ----------------------------------------------------------------------
# Liftbridge streams synchronization tool
# ----------------------------------------------------------------------
# Copyright (C) 2007-2020 The NOC Project
# See LICENSE for details
# ----------------------------------------------------------------------

# Python modules
from typing import Tuple, Dict
import functools

# NOC modules
from noc.core.management.base import BaseCommand
from noc.core.liftbridge.base import LiftBridgeClient, Metadata, StreamMetadata, StartPosition
from noc.main.models.pool import Pool
from noc.core.mongo.connection import connect
from noc.core.service.loader import get_dcs
from noc.core.ioloop.util import run_sync
from noc.config import config


class Command(BaseCommand):
    STREAMS = [
        # slot name, stream name
        ("mx", "message"),
        ("kafkasender", "kafkasender"),
    ]
    POOLED_STREAMS = [
        # slot name, stream name
        ("classifier-%s", "events.%s"),
        ("correlator-%s", "dispose.%s"),
    ]
    CURSOR_STREAM = {
        "events": "classifier",
        "dispose": "correlator",
        "mx": "mx",
        "kafkasender": "kafkasender",
    }

    def handle(self, *args, **options):
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

    def iter_slot_streams(self) -> Tuple[str, str]:
        # Common streams
        for slot_name, stream_name in self.STREAMS:
            yield slot_name, stream_name
        # Pooled streams
        connect()
        for pool in Pool.objects.all():
            for slot_mask, stream_mask in self.POOLED_STREAMS:
                yield slot_mask % pool.name, stream_mask % pool.name

    def iter_limits(self) -> Tuple[str, int]:
        async def get_slot_limits():
            nonlocal slot_name
            return await dcs.get_slot_limit(slot_name)

        dcs = get_dcs()
        for slot_name, stream_name in self.iter_slot_streams():
            n_partitions = run_sync(get_slot_limits)
            if n_partitions:
                yield stream_name, n_partitions

    def apply_stream_settings(self, meta: Metadata, stream: str, partitions: int, rf: int) -> bool:
        def delete_stream(name: str):
            async def wrapper():
                async with LiftBridgeClient() as client:
                    await client.delete_stream(client.get_offset_stream(name))
                    await client.delete_stream(name)

            run_sync(wrapper)

        def create_stream(name: str, n_partitions: int, replication_factor: int):
            base_name = name.split(".")[0]

            async def wrapper():
                async with LiftBridgeClient() as client:
                    await client.create_stream(
                        subject=name,
                        name=name,
                        partitions=n_partitions,
                        replication_factor=replication_factor,
                        retention_max_bytes=getattr(
                            config.liftbridge, f"stream_{base_name}_retention_max_age", 0
                        ),
                        retention_max_age=getattr(
                            config.liftbridge, f"stream_{base_name}_retention_max_bytes", 0
                        ),
                        segment_max_bytes=getattr(
                            config.liftbridge, f"stream_{base_name}_segment_max_bytes", 0
                        ),
                        segment_max_age=getattr(
                            config.liftbridge, f"stream_{base_name}_segment_max_age", 0
                        ),
                        auto_pause_time=getattr(
                            config.liftbridge, f"stream_{base_name}_auto_pause_time", 0
                        ),
                        auto_pause_disable_if_subscribers=getattr(
                            config.liftbridge,
                            f"stream_{base_name}_auto_pause_disable_if_subscribers",
                            False,
                        ),
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
                self.print("Altering stream %s" % name)
                async with LiftBridgeClient() as client:
                    # Create temporary stream with same structure, as original one
                    tmp_stream = "__tmp-%s" % name
                    self.print("Creating temporary stream %s" % tmp_stream)
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
                            stream=stream,
                            partition=partition,
                            cursor_id=self.CURSOR_STREAM[name.split(".")[0]],
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
                            self.print("  %d messages restored" % n_msg[partition])
                        else:
                            self.print("  nothing to restore")
                    # Drop temporary stream
                    self.print("Dropping temporary stream %s" % tmp_stream)
                    await client.delete_stream(tmp_stream)
                    # Uh-oh
                    self.print("Stream %s has been altered" % name)

            run_sync(wrapper)

        stream_meta = None
        for m in meta.metadata:
            if m.name == stream:
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
                    stream,
                    len(stream_meta.partitions),
                    partitions,
                )
            )
            alter_stream(stream_meta, partitions, rf)
            return True
        # Create stream
        self.print("Creating stream %s with %d partitions" % (stream, partitions))
        create_stream(stream, partitions, rf)
        return True


if __name__ == "__main__":
    Command().run()
