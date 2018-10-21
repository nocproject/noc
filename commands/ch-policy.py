# -*- coding: utf-8 -*-
# ----------------------------------------------------------------------
# ./noc ch-policy command
# ----------------------------------------------------------------------
# Copyright (C) 2007-2018 The NOC Project
# See LICENSE for details
# ----------------------------------------------------------------------

# Python modules
from __future__ import print_function
from collections import namedtuple, defaultdict
import time
import datetime
# NOC modules
from noc.config import config
from noc.core.management.base import BaseCommand
from noc.core.clickhouse.connect import connection
from noc.main.models.chpolicy import CHPolicy

PartInfo = namedtuple("PartInfo", ["name", "rows", "bytes", "min_date", "max_date"])
PartitionInfo = namedtuple("PartitionInfo", ["table_name", "partition", "rows", "bytes", "min_date", "max_date"])


class Command(BaseCommand):
    help = "Apply ClickHouse policies"

    def add_arguments(self, parser):
        subparsers = parser.add_subparsers(dest="cmd")
        # get
        apply_parser = subparsers.add_parser("apply")
        apply_parser.add_argument(
            "--host",
            dest="host",
            help="ClickHouse address"
        )
        apply_parser.add_argument(
            "--port",
            dest="port",
            type=int,
            help="ClickHouse port"
        )
        apply_parser.add_argument(
            "--approve",
            dest="dry_run",
            action="store_false",
            help="Apply changes"
        )

    def handle(self, cmd, *args, **options):
        getattr(self, "handle_%s" % cmd)(*args, **options)

    def handle_apply(self, host=None, port=None, dry_run=True, *args, **options):
        read_only = dry_run
        ch = connection(host, port, read_only=read_only)
        today = datetime.date.today()
        # Get partitions
        parts = self.get_parts(ch)
        #
        partition_claimed = []
        claimed_bytes = 0
        for p in CHPolicy.objects.filter(is_active=True).order_by("table"):
            table_claimed = 0
            if not p.ttl:
                continue  # Disabled
            deadline = today - datetime.timedelta(days=p.ttl)
            is_dry = dry_run or p.dry_run
            self.print("# Table %s deadline %s%s" % (
                p.table, deadline.isoformat(), " (Dry Run)" if is_dry else ""))
            for pi in parts[p.table]:
                if pi.max_date >= deadline:
                    continue
                self.print("  Removing partition %s (%s -- %s, %d rows, %d bytes)" % (
                    pi.partition, pi.min_date, pi.max_date, pi.rows, pi.bytes))
                table_claimed += pi.bytes
                if not is_dry:
                    partition_claimed += [(p.table, pi.partition)]
            self.print("  Total %d bytes to be reclaimed" % table_claimed)
            claimed_bytes += table_claimed
        if partition_claimed:
            self.print("Claimed data will be Loss..\n")
            for i in reversed(range(1, 10)):
                self.print("%d\n" % i)
                time.sleep(1)
            for c in partition_claimed:
                ch.execute("ALTER TABLE %s.%s DROP PARTITION '%s'" % (config.clickhouse.db, c[0], c[1]))
            self.print("# Done. %d bytes to be reclaimed" % claimed_bytes)

    def get_inactive_partition(self, connect):
        """
        Get partition with inactive parts
        :param connect:
        :return:
        """
        ap = set()
        for row in connect.execute("""
          SELECT table, partition
          FROM system.parts
          WHERE
            active = 0
            AND database = %s
          GROUP BY table, partition
          ORDER BY table, partition
        """, args=(config.clickhouse.db,)
        ):
            ap.add((row[0], row[1]))
        return ap

    def get_parts(self, connect):
        """
        Get partition info
        :param connect:
        :return:
        """
        exclude_partition = self.get_inactive_partition(connect)
        partitions = defaultdict(list)
        for row in connect.execute("""
          SELECT table, partition, SUM(rows), SUM(bytes), MIN(min_date), MAX(max_date)
          FROM system.parts
          WHERE
            database = %s
          GROUP BY table, partition
          ORDER BY table, partition
        """, args=(config.clickhouse.db,)
        ):
            if (row[0], row[1]) in exclude_partition:
                self.print("Partiton %s from table %s having inactive parts. Skipping..." % (row[0], row[1]))
                continue
            partitions[row[0]] += [PartitionInfo(
                table_name=row[0],
                partition=row[1],
                rows=int(row[2]),
                bytes=int(row[3]),
                min_date=datetime.date(*[int(x) for x in row[4].split("-")]),
                max_date=datetime.date(*[int(x) for x in row[5].split("-")])
            )]
        return partitions


if __name__ == "__main__":
    Command().run()
