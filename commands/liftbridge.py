# ----------------------------------------------------------------------
# liftbridge command
# ----------------------------------------------------------------------
# Copyright (C) 2007-2020 The NOC Project
# See LICENSE for details
# ----------------------------------------------------------------------

# Python modules
from typing import Optional
from time import perf_counter
import datetime
import functools
import argparse
from dateutil.parser import parse

# NOC modules
from noc.core.management.base import BaseCommand
from noc.core.ioloop.util import run_sync
from noc.core.liftbridge.base import LiftBridgeClient, Metadata, PartitionMetadata
from noc.core.text import alnum_key

TS_NS = 1000_0000_00


class Command(BaseCommand):
    """
    Manage Liftbridge streams
    """

    help = "Manage Liftbridge streams"

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
        subparsers.add_parser("show-metadata")
        # create-stream
        create_parser = subparsers.add_parser("create-stream")
        create_parser.add_argument("--name")
        create_parser.add_argument("--subject")
        create_parser.add_argument("--partitions", type=int, default=1)
        create_parser.add_argument("--rf", type=int)
        # drop-stream
        delete_parser = subparsers.add_parser("delete-stream")
        delete_parser.add_argument("--name")
        # subscribe
        subscribe_parser = subparsers.add_parser("subscribe")
        subscribe_parser.add_argument("--name")
        subscribe_parser.add_argument("--partition", type=int, default=0)
        subscribe_parser.add_argument("--cursor", type=str, default="")
        subscribe_parser.add_argument("--start-offset", type=int, default=0)
        subscribe_parser.add_argument("--start-ts", type=self.valid_date, default=0)
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
        return getattr(self, "handle_%s" % cmd.replace("-", "_"))(*args, **options)

    def handle_show_metadata(self, *args, **options):
        async def get_meta() -> Metadata:
            async with LiftBridgeClient() as client:
                return await client.fetch_metadata()

        async def get_partition_meta(stream, partition) -> PartitionMetadata:
            async with LiftBridgeClient() as client:
                return await client.fetch_partition_metadata(stream, partition)

        meta: Metadata = run_sync(get_meta)
        self.print("# Brokers (%d)" % len(meta.brokers))
        self.print("%-20s | %s" % ("ID", "HOST:PORT"))
        for broker in meta.brokers:
            self.print("%-20s | %s:%s" % (broker.id, broker.host, broker.port))
        self.print("# Streams")
        for stream in meta.metadata:
            print("  ## Name: %s Subject: %s" % (stream.name, stream.subject))
            for p in sorted(stream.partitions):
                print("    ### Partition: %d" % p)
                try:
                    p_meta: PartitionMetadata = run_sync(
                        functools.partial(get_partition_meta, stream.name, p)
                    )
                except Exception as e:
                    print("[%s|%s] Failed getting data for partition: %s" % (stream.name, p, e))
                    continue
                print("    Leader        : %s" % p_meta.leader)
                print("    Replicas      : %s" % ", ".join(sorted(p_meta.replicas, key=alnum_key)))
                print("    ISR           : %s" % ", ".join(sorted(p_meta.isr, key=alnum_key)))
                print("    HighWatermark : %s" % p_meta.high_watermark)
                print("    NewestOffset  : %s" % p_meta.newest_offset)

    def handle_create_stream(
        self,
        name: str,
        subject: Optional[str] = None,
        partitions: int = 1,
        rf: int = 1,
        *args,
        **kwargs,
    ):
        async def create():
            async with LiftBridgeClient() as client:
                await client.create_stream(
                    name=name,
                    subject=subject,
                    partitions=partitions,
                    replication_factor=rf,
                )

        subject = subject or name
        run_sync(create)

    def handle_delete_stream(self, name: str, *args, **kwargs):
        async def delete():
            async with LiftBridgeClient() as client:
                await client.delete_stream(name)

        run_sync(delete)

    def handle_subscribe(
        self,
        name: str,
        partition: int = 0,
        cursor: str = "",
        start_offset: int = 0,
        start_ts: int = None,
        *args,
        **kwargs,
    ):
        async def subscribe():
            async with LiftBridgeClient() as client:
                async for msg in client.subscribe(
                    stream=name,
                    partition=partition,
                    start_offset=start_offset,
                    cursor_id=cursor or None,
                    start_timestamp=start_ts,
                ):
                    print(
                        "# Subject: %s Partition: %s Offset: %s Timestamp: %s Key: %s Headers: %s"
                        % (
                            msg.subject,
                            msg.partition,
                            msg.offset,
                            f"{msg.timestamp} ({datetime.datetime.fromtimestamp(msg.timestamp / TS_NS)})",
                            msg.key,
                            msg.headers,
                        )
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
            async with LiftBridgeClient() as client:
                await client.set_cursor(
                    stream=stream, partition=partition, cursor_id=name, offset=offset
                )

        run_sync(set_cursor)

    def handle_fetch_cursor(self, name: str, stream: str, partition: int = 0, *args, **kwargs):
        async def fetch_cursor():
            async with LiftBridgeClient() as client:
                cursor = await client.fetch_cursor(
                    stream=stream, partition=partition, cursor_id=name
                )
                print(cursor)

        run_sync(fetch_cursor)

    def handle_benchmark_publisher(
        self,
        name: str,
        num_messages: int,
        payload_size: int = 64,
        batch=1,
        wait_for_stream=False,
        *args,
        **kwargs,
    ):
        async def publisher():
            async with LiftBridgeClient() as client:
                payload = b" " * payload_size
                t0 = perf_counter()
                for _ in self.progress(range(num_messages), num_messages):
                    await client.publish(payload, stream=name, wait_for_stream=wait_for_stream)
                dt = perf_counter() - t0
            self.print("%d messages sent in %.2fms" % (num_messages, dt * 1000))
            self.print(
                "%d msg/sec, %d bytes/sec" % (num_messages / dt, num_messages * payload_size / dt)
            )

        async def batch_publisher():
            async with LiftBridgeClient() as client:
                payload = b" " * payload_size
                t0 = perf_counter()
                out = []
                n_acks = 0
                for _ in self.progress(range(num_messages), num_messages):
                    out += [client.get_publish_request(payload, stream=name)]
                    if len(out) == batch:
                        async for ack in client.publish_async(out):
                            n_acks += 1
                        out = []
                if out:
                    async for _ in client.publish_async(out):
                        n_acks += 1
                    out = []
                dt = perf_counter() - t0
            self.print("%d messages sent in %.2fms (%d acks)" % (num_messages, dt * 1000, n_acks))
            self.print(
                "%d msg/sec, %d bytes/sec" % (num_messages / dt, num_messages * payload_size / dt)
            )

        if batch == 1:
            run_sync(publisher)
        else:
            print("batch")
            run_sync(batch_publisher)

    def handle_benchmark_subscriber(self, name: str, cursor: Optional[str] = None, *args, **kwargs):
        async def subscriber():
            async with LiftBridgeClient() as client:
                report_interval = 1.0
                t0 = perf_counter()
                total_msg = last_msg = 0
                total_size = last_size = 0
                async for msg in client.subscribe(name):
                    total_msg += 1
                    total_size += len(msg.value)
                    t = perf_counter()
                    dt = t - t0
                    if dt >= report_interval:
                        self.print(
                            "%d msg/sec, %d bytes/sec"
                            % ((total_msg - last_msg) / dt, (total_size - last_size) / dt)
                        )
                        t0 = t
                        last_msg = total_msg
                        last_size = total_size
                    if cursor:
                        await client.set_cursor(
                            stream=name, partition=0, cursor_id=cursor, offset=msg.offset
                        )

        run_sync(subscriber)


if __name__ == "__main__":
    Command().run()
