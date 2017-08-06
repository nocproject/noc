# -*- coding: utf-8 -*-
# ----------------------------------------------------------------------
# metrics uploading
# ----------------------------------------------------------------------
# Copyright (C) 2007-2017 The NOC Project
# See LICENSE for details
# ----------------------------------------------------------------------

# Python modules
from __future__ import print_function
# Third-party modules
import nsq
# NOC modules
from noc.core.management.base import BaseCommand
from noc.config import config, CH_UNCLUSTERED, CH_REPLICATED, CH_SHARDED


class Command(BaseCommand):
    TOPIC = "chwriter"

    def add_arguments(self, parser):
        subparsers = parser.add_subparsers(dest="cmd")
        # load command
        load_parser = subparsers.add_parser("load")
        load_parser.add_argument(
            "--fields",
            help="Data fields: <table>.<field1>.<fieldN>"
        )
        load_parser.add_argument(
            "--input",
            help="Input file path"
        )
        load_parser.add_argument(
            "--chunk",
            type=int,
            default=config.nsqd.ch_chunk_size,
            help="Size on chunk"
        )

    def handle(self, cmd, *args, **options):
        return getattr(self, "handle_%s" % cmd)(*args, **options)

    def handle_load(self, fields, input, chunk, *args, **kwargs):
        def publish():
            def finish_pub(conn, data):
                if isinstance(data, nsq.Error):
                    self.print("NSQ pub error: %s" % data)
                writer.io_loop.add_callback(publish)

            if not self.items:
                # Done
                writer.io_loop.stop()
                return
            d, self.items = self.items[:chunk], self.items[chunk:]
            msg = "%s\n%s\n" % (fields, "\n".join(d))
            writer.pub(self.TOPIC, msg, callback=finish_pub)

        def on_connect():
            if writer.conns:
                # Connected
                writer.io_loop.add_callback(publish)
            else:
                self.stdout.write("Waiting for NSQ connection\n")
                writer.io_loop.call_later(config.nsqd.connect_timeout,
                                          on_connect)

        # Read data
        with open(input) as f:
            records = f.read().splitlines()
        # Shard incoming data when necessary
        tt = config.get_ch_topology_type()
        if tt == CH_UNCLUSTERED:
            # Unclustered configuration
            self.metrics["chwriter"] = records
        elif tt == CH_REPLICATED:
            # Clustered configuration
            self.metrics = {}
            for r in range(config.ch_cluster_topology[0].replicas):
                self.metrics["chwriter-1-%s" % (r + 1)] = records
        else:
            # Sharded configuration
            raise NotImplementedError()
        # Stream to NSQ
        writer = nsq.Writer([str(a) for a in config.nsqd.addresses])
        writer.io_loop.add_callback(on_connect)
        nsq.run()

if __name__ == "__main__":
    Command().run()
