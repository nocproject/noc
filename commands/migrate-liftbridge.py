# ----------------------------------------------------------------------
# Liftbridge streams synchronization tool
# ----------------------------------------------------------------------
# Copyright (C) 2007-2020 The NOC Project
# See LICENSE for details
# ----------------------------------------------------------------------

# Python modules
from typing import Tuple, Dict

# NOC modules
from noc.core.management.base import BaseCommand
from noc.core.liftbridge.base import LiftBridgeClient, Metadata, StreamMetadata, StartPosition
from noc.main.models.pool import Pool
from noc.core.mongo.connection import connect
from noc.core.service.loader import get_dcs
from noc.core.ioloop.util import run_sync


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
            async def wrapper():
                async with LiftBridgeClient() as client:
                    await client.create_stream(
                        subject=name,
                        name=name,
                        partitions=n_partitions,
                        replication_factor=replication_factor,
                    )

            run_sync(wrapper)

        def alter_stream(
            current_meta: StreamMetadata, new_partitions: int, replication_factor: int
        ):
            name = StreamMetadata.name
            old_partitions = len(current_meta.partitions)
            n_msg: Dict[int, int] = {}  # partition -> copied messages

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
                        # @todo: fetch_partition_metadata
                        current_offset = await client.get_stored_offset(stream, partitions)
                        newest_offset = stream_meta.partitions[partition].newest_offset or 0
                        if current_offset >= newest_offset:
                            async for msg in client.subscribe(
                                stream=name, partition=partition, start_offset=current_offset
                            ):
                                await client.publish(
                                    msg.value, stream=tmp_stream, partition=partition
                                )
                                n_msg[partition] += 1
                                if msg.offset == current_offset:
                                    break
                        if n_msg[partition]:
                            self.print("  %d messages has been copied" % n_msg[partition])
                        else:
                            self.print("  nothing to copy")
                    # Drop original stream
                    self.print("Dropping original stream %s" % name)
                    await client.delete_stream(client.get_offset_stream(name))
                    await client.delete_stream(name)
                    # Create new stream with required structure
                    self.print("Creating stream %s" % name)
                    await client.create_stream(
                        subject=name,
                        name=name,
                        partitions=new_partitions,
                        replication_factor=replication_factor,
                        init_offsets=True,
                    )
                    # Copy data from temporary stream to a new one
                    for partition in range(old_partitions):
                        self.print("Restoring partition %s:%s" % (tmp_stream, partition))
                        # Re-route dropped partitions to partition 0
                        dest_partition = new_partitions if partition < new_partitions else 0
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
