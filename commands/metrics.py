# ----------------------------------------------------------------------
# metrics uploading
# ----------------------------------------------------------------------
# Copyright (C) 2007-2019 The NOC Project
# See LICENSE for details
# ----------------------------------------------------------------------

# Python modules
import argparse
import gzip
import os
import random
from typing import List
from functools import partial

# NOC modules
from noc.config import config
from noc.core.management.base import BaseCommand
from noc.core.liftbridge.base import LiftBridgeClient
from noc.core.ioloop.util import run_sync


class Command(BaseCommand):
    TOPIC = "chwriter"

    def add_arguments(self, parser):
        subparsers = parser.add_subparsers(dest="cmd", required=True)
        # load command
        load_parser = subparsers.add_parser("load")
        load_parser.add_argument("--fields", help="Data fields: <table>.<field1>.<fieldN>")
        load_parser.add_argument("--chunk", type=int, default=100_000, help="Size on chunk")
        load_parser.add_argument("--rm", action="store_true", help="Remove file after uploading")
        load_parser.add_argument("input", nargs=argparse.REMAINDER, help="Input files")

    def handle(self, cmd, *args, **options):
        return getattr(self, "handle_%s" % cmd)(*args, **options)

    def handle_load(self, fields, input, chunk, rm, *args, **kwargs):
        async def upload(table: str, data: List[bytes]):
            CHUNK = 1000
            n_parts = len(config.clickhouse.cluster_topology.split(","))
            async with LiftBridgeClient() as client:
                while data:
                    chunk, data = data[:CHUNK], data[CHUNK:]
                    await client.publish(
                        b"\n".join(chunk),
                        stream=f"ch.{table}",
                        partition=random.randint(0, n_parts - 1),
                    )

        for fn in input:
            # Read data
            self.print("Reading file %s" % fn)
            if fn.endswith(".gz"):
                with gzip.GzipFile(fn) as f:
                    records = f.read().replace("\r", "").splitlines()
            else:
                with open(fn) as f:
                    records = f.read().replace("\r", "").splitlines()
            table = fn.split("-", 1)[0]
            run_sync(partial(upload, table, records))
            if rm:
                os.unlink(fn)


if __name__ == "__main__":
    Command().run()
