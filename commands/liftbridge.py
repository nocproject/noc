# ----------------------------------------------------------------------
# liftbridge command
# ----------------------------------------------------------------------
# Copyright (C) 2007-2020 The NOC Project
# See LICENSE for details
# ----------------------------------------------------------------------

# Python modules
from typing import Optional
from time import perf_counter

# NOC modules
from noc.core.management.base import BaseCommand
from noc.core.ioloop.util import run_sync
from noc.core.liftbridge.base import LiftBridgeClient, Metadata
from noc.core.text import alnum_key


class Command(BaseCommand):
    """
    Manage Liftbridge streams
    """

    help = "Manage Liftbridge streams"

    def add_arguments(self, parser):
        subparsers = parser.add_subparsers(dest="cmd")
        # show-metadata
        subparsers.add_parser("show-metadata")
        # create-stream
        create_parser = subparsers.add_parser("create-stream")
        create_parser.add_argument("--name")
        create_parser.add_argument("--subject")
        create_parser.add_argument("--partitions", type=int, default=1)
        create_parser.add_argument("--rf", type=int)
        create_parser.add_argument("--init-offsets", action="store_true")
        # drop-stream
        delete_parser = subparsers.add_parser("delete-stream")
        delete_parser.add_argument("--name")
        # subscribe
        subscribe_parser = subparsers.add_parser("subscribe")
        subscribe_parser.add_argument("--name")
        subscribe_parser.add_argument("--partition", type=int, default=0)
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
        benchmark_subscriber_parser.add_argument("--commit-offset", action="store_true")

    def handle(self, cmd, *args, **options):
        return getattr(self, "handle_%s" % cmd.replace("-", "_"))(*args, **options)

    def handle_show_metadata(self, *args, **options):
        async def get_meta() -> Metadata:
            async with LiftBridgeClient() as client:
                return await client.fetch_metadata()

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
                p_meta = stream.partitions[p]
                print("    Leader   : %s" % p_meta.leader)
                print("    Replicas : %s" % ", ".join(sorted(p_meta.replicas, key=alnum_key)))
                print("    ISR      : %s" % ", ".join(sorted(p_meta.isr, key=alnum_key)))

    def handle_create_stream(
        self,
        name: str,
        subject: Optional[str] = None,
        partitions: int = 1,
        rf: int = 1,
        init_offsets: bool = False,
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
                    init_offsets=init_offsets,
                )

        subject = subject or name
        run_sync(create)

    def handle_delete_stream(self, name: str, *args, **kwargs):
        async def delete():
            async with LiftBridgeClient() as client:
                await client.delete_stream(name)

        run_sync(delete)

    def handle_subscribe(self, name: str, partition: int = 0, *args, **kwargs):
        async def subscribe():
            async with LiftBridgeClient() as client:
                async for msg in client.subscribe(stream=name, partition=partition, start_offset=0):
                    print(
                        "# Subject: %s Partition: %s Offset: %s Timestamp: %s Key: %s"
                        % (msg.subject, msg.partition, msg.offset, msg.timestamp, msg.key)
                    )
                    print(msg.value)

        run_sync(subscribe)

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
                            print(ack)
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

    def handle_benchmark_subscriber(self, name: str, commit_offset: bool = False, *args, **kwargs):
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
                    if commit_offset:
                        await client.commit_offset(name, partition=0, offset=msg.offset)

        run_sync(subscriber)


if __name__ == "__main__":
    Command().run()
