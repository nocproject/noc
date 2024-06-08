# ----------------------------------------------------------------------
# msgstream command
# ----------------------------------------------------------------------
# Copyright (C) 2007-2022 The NOC Project
# See LICENSE for details
# ----------------------------------------------------------------------

# Python modules
import datetime
import argparse
import functools
from dateutil.parser import parse
from typing import Optional

# NOC modules
from noc.core.management.base import BaseCommand
from noc.core.ioloop.util import run_sync
from noc.core.msgstream.client import MessageStreamClient
from noc.core.msgstream.metadata import Metadata, PartitionMetadata
from noc.core.debug import error_report

TS_NS = 1000_0000_00


class Command(BaseCommand):
    """
    Manage streams
    """

    help = "Manage MessageStream Client"

    @staticmethod
    def valid_date(s):
        try:
            return int(parse(s).timestamp())
        except ValueError:
            msg = "Not a valid date: '{0}'.".format(s)
            raise argparse.ArgumentTypeError(msg)

    def add_arguments(self, parser):
        subparsers = parser.add_subparsers(dest="cmd", required=True)
        # show-metadata
        sm = subparsers.add_parser("show-metadata")
        sm.add_argument("--name")
        # create-stream
        create_parser = subparsers.add_parser("create-stream")
        create_parser.add_argument("--name")
        create_parser.add_argument("--subject")
        create_parser.add_argument("--partitions", type=int, default=1)
        create_parser.add_argument("--rf", type=int)
        # drop-stream
        delete_parser = subparsers.add_parser("delete-stream")
        delete_parser.add_argument("--name")
        # alter partition num
        alter_parser = subparsers.add_parser("alter-stream")
        alter_parser.add_argument("--name")
        alter_parser.add_argument("--partitions", type=int, default=0)
        # subscribe
        subscribe_parser = subparsers.add_parser("subscribe")
        subscribe_parser.add_argument("--name")
        subscribe_parser.add_argument("--partition", type=int, default=0)
        subscribe_parser.add_argument("--cursor", type=str, default="")
        subscribe_parser.add_argument("--start-offset", type=int, default=None)
        subscribe_parser.add_argument("--start-ts", type=self.valid_date, default=None)
        # set-cursor
        set_cursor_parser = subparsers.add_parser("set-cursor")
        set_cursor_parser.add_argument("--name")
        set_cursor_parser.add_argument("--stream")
        set_cursor_parser.add_argument("--partition", type=int, default=0)
        set_cursor_parser.add_argument("--offset", type=int, default=0)
        # fetch-cursor
        fetch_cursor_parser = subparsers.add_parser("fetch-cursor")
        fetch_cursor_parser.add_argument("--name")
        fetch_cursor_parser.add_argument("--stream")
        fetch_cursor_parser.add_argument("--partition", type=int, default=0)
        # benchmark-publisher
        benchmark_publisher_parser = subparsers.add_parser("benchmark-publisher")
        benchmark_publisher_parser.add_argument("--name")
        benchmark_publisher_parser.add_argument("--num-messages", type=int, default=1000)
        benchmark_publisher_parser.add_argument("--payload-size", type=int, default=64)
        benchmark_publisher_parser.add_argument("--batch", type=int, default=1)
        benchmark_publisher_parser.add_argument("--wait-for-stream", action="store_true")
        # benchmark-subscriber
        benchmark_subscriber_parser = subparsers.add_parser("benchmark-subscriber")
        benchmark_subscriber_parser.add_argument("--name")
        benchmark_subscriber_parser.add_argument("--cursor")

    def handle(self, cmd, *args, **options):
        return getattr(self, f'handle_{cmd.replace("-", "_")}')(*args, **options)

    def handle_show_metadata(self, name: Optional[str] = None, *args, **options):
        async def get_meta() -> Metadata:
            async with MessageStreamClient() as client:
                return await client.fetch_metadata()

        async def get_partition_meta(stream, partition) -> PartitionMetadata:
            async with MessageStreamClient() as client:
                return await client.fetch_partition_metadata(stream, partition)

        meta: Metadata = run_sync(get_meta)
        self.print(f"# Brokers ({len(meta.brokers)})")
        self.print("%-20s | %s" % ("ID", "HOST:PORT"))
        b_map = {}
        for broker in meta.brokers:
            self.print("%-20s | %s:%s" % (broker.id, broker.host, broker.port))
            b_map[broker.id] = broker.host
        self.print("# Streams")
        for stream in meta.metadata:
            if stream.startswith("__"):
                continue
            if name and stream != name:
                continue
            print(f"  ## Name: {stream}")
            for p in sorted(meta.metadata[stream]):
                print(f"    ### Partition: {p}")
                try:
                    p_meta: PartitionMetadata = run_sync(
                        functools.partial(get_partition_meta, stream, p)
                    )
                except Exception as e:
                    print("[%s|%s] Failed getting data for partition: %s" % (stream, p, e))
                    error_report()
                    continue
                print("    Leader        : %s" % b_map[p_meta.leader])
                print(
                    "    Replicas      : %s"
                    % ", ".join([str(b_map[x]) for x in sorted(p_meta.replicas)])
                )
                print(
                    "    ISR           : %s"
                    % ", ".join([str(b_map[x]) for x in sorted(p_meta.isr)])
                )
                print("    HighWatermark : %s" % p_meta.high_watermark)
                print("    NewestOffset  : %s" % p_meta.newest_offset)

    def handle_create_stream(
        self,
        name: str,
        partitions: int = 1,
        rf: int = 1,
        *args,
        **kwargs,
    ):
        async def create():
            async with MessageStreamClient() as client:
                await client.create_stream(
                    name=name,
                    partitions=partitions,
                    replication_factor=rf,
                )

        run_sync(create)

    def handle_delete_stream(self, name: str, *args, **kwargs):
        async def delete():
            async with MessageStreamClient() as client:
                await client.delete_stream(name)

        run_sync(delete)

    def handle_alter_stream(
        self,
        name: str,
        partitions: int = 1,
        rf: int = 1,
        *args,
        **kwargs,
    ):
        async def alter():
            async with MessageStreamClient() as client:
                meta = await client.fetch_metadata(name)
                stream_meta = meta.metadata[name] if name in meta.metadata else None
                await client.alter_stream(
                    name=name,
                    current_meta=stream_meta,
                    new_partitions=partitions,
                    replication_factor=rf,
                )

        run_sync(alter)

    def handle_subscribe(
        self,
        name: str,
        partition: int = 0,
        cursor: str = "",
        start_offset: Optional[int] = None,
        start_ts: Optional[int] = None,
        *args,
        **kwargs,
    ):
        async def subscribe():
            async with MessageStreamClient() as client:
                async for msg in client.subscribe(
                    stream=name,
                    partition=partition,
                    start_offset=start_offset,
                    cursor_id=cursor or None,
                    start_timestamp=start_ts,
                ):
                    print(
                        f"# Subject: {msg.subject} "
                        f"Partition: {msg.partition} "
                        f"Offset: {msg.offset} "
                        f"Timestamp: {msg.timestamp} "
                        f"({datetime.datetime.fromtimestamp(msg.timestamp / client.client.TIMESTAMP_MULTIPLIER)})"
                        f"Key: {msg.key} Headers: {msg.headers}"
                    )
                    print(msg.value)

        if start_ts:
            start_offset = None
            start_ts *= 1000000000
        run_sync(subscribe)

    def handle_set_cursor(
        self, name: str, stream: str, partition: int = 0, offset: int = 0, *args, **kwargs
    ):
        async def set_cursor():
            async with MessageStreamClient() as client:
                await client.set_cursor(
                    stream=stream, partition=partition, cursor_id=name, offset=offset
                )

        run_sync(set_cursor)

    def handle_fetch_cursor(self, name: str, stream: str, partition: int = 0, *args, **kwargs):
        async def fetch_cursor():
            async with MessageStreamClient() as client:
                cursor = await client.fetch_cursor(
                    stream=stream, partition=partition, cursor_id=name
                )
                print(cursor)

        run_sync(fetch_cursor)


if __name__ == "__main__":
    Command().run()
