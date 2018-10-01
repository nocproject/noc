# -*- coding: utf-8 -*-
# ---------------------------------------------------------------------
# job management
# ---------------------------------------------------------------------
# Copyright (C) 2007-2012 The NOC Project
# See LICENSE for details
# ---------------------------------------------------------------------

# Python modules
from __future__ import print_function
import argparse
from datetime import datetime, timedelta
import csv
import time
import sys
from pymongo import UpdateOne
# NOC modules
from noc.core.management.base import BaseCommand
from noc.core.scheduler.scheduler import Scheduler


SHARDING_SCHEDULER = {"discovery", "correlator", "escalator"}


class Command(BaseCommand):
    """
    Manage Jobs
    """
    help = "Manage Jobs"
    default_time = timedelta(minutes=5)

    @staticmethod
    def valid_date(s):
        print(s)
        try:
            return datetime.strptime(s, "%Y-%m-%d %H:%M")
        except ValueError:
            msg = "Not a valid date: '{0}'.".format(s)
            raise argparse.ArgumentTypeError(msg)

    @staticmethod
    def scheduler(s):
        scheduler, pool = "scheduler", "default"
        if "." in s:
            scheduler, pool = s.split(".")
        if scheduler in SHARDING_SCHEDULER:
                # raise argparse.ArgumentTypeError("Scheduler: %s, not supporting sharding")
            return Scheduler(scheduler, pool=pool).get_collection()
        return Scheduler(scheduler).get_collection()

    def add_arguments(self, parser):
        parser.add_argument("--scheduler", "-s",
                            dest="scheduler",
                            default=Scheduler("scheduler").get_collection(),
                            type=self.scheduler,
                            help="Select scheduler. For sharded use SCHEDULER_NAME.SHARD_NAME"
                            ),
        parser.add_argument("--format", "-f",
                            dest="store",
                            # action="format",
                            choices=["json", "csv"],
                            help="Set output format"
                            ),
        subparsers = parser.add_subparsers(dest="cmd")
        # load command
        list_parser = subparsers.add_parser("list")
        list_parser.add_argument("--name",
                                 help="Job name in scheduler")
        list_parser.add_argument(
            "key",
            nargs=argparse.REMAINDER,
            help="List of job key"
        )
        get_parser = subparsers.add_parser("get")
        get_parser.add_argument("--id",
                                help="Job name in scheduler")
        subparsers.add_parser("set")
        # Parse Job Field
        reschedule = subparsers.add_parser("reschedule",
                                           help="Shift Jobs to interval")
        reschedule.add_argument("--name",
                                help="Job name in scheduler")
        reschedule.add_argument("--start",
                                type=self.valid_date,
                                help="Start interval for place")
        reschedule.add_argument("--end",
                                type=self.valid_date,
                                help="End interval for place")
        reschedule.add_argument("--force",
                                default=False,
                                action="store_true", help="Really do reschedule")
        reschedule.add_argument(
            "key",
            nargs=argparse.REMAINDER,
            help="List of job key"
        )
        parser.add_argument('infile', nargs='?',
                            type=argparse.FileType('r'),
                            default=sys.stdin)

    def init_json(self):
        pass

    def init_csv(self):
        self.writer = csv.writer(sys.stdout)
        self.writer.writerow([
            "Run", "ID", "Name", "Key", "Status", "Last Status",
            "Runs", "Last Run", "Last Duration",
            "Interval", "Failed Interval", "Offset"
        ])

    def format_json(self, job):
        self.print(job)

    def format_csv(self, job):
        # s = job["schedule"] or {}
        self.writer.writerow([
            job["ts"], job["_id"], job["jcls"], job["key"],
            job["s"], job.get("ls", ""), job.get("runs", 0),
            job.get("last", ""), job.get("ldur", ""),
            # s.get("interval", ""), s.get("failed_interval", ""),
            # s.get("offset", "")
        ])

    def handle(self, cmd, *args, **options):
        if "infile" in options and not sys.stdin.isatty():
            for line in options["infile"]:
                options["key"] += [int(line)]
        return getattr(self, "handle_%s" % cmd)(*args, **options)

    def handle_list(self, scheduler, *args, **options):
        q = {}
        if options.get("name"):
            q["jcls"] = options["name"]
        if options.get("key"):
            q["key"] = {"$in": [int(x) for x in options["key"]]}
        fname = options.get("format", "csv")
        format = getattr(self, "format_%s" % fname)
        # Print header
        getattr(self, "init_%s" % fname)()
        # Print jobs
        for j in scheduler.find(q).sort("ts").limit(50):
            format(j)

    def handle_get(self, scheduler, *args, **options):
        fname = options.get("format", "csv")
        format = getattr(self, "format_%s" % fname)
        # Print header
        getattr(self, "init_%s" % fname)()
        # Print jobs
        for j in scheduler.find().sort("ts"):
            format(j)

    def handle_set(self, scheduler, *args, **options):
        raise NotImplementedError()

    def handle_reschedule(self, scheduler, *args, **options):
        bulk = []
        q = {}
        shift_interval = self.default_time
        if options.get("name"):
            q["jcls"] = options["name"]
        if options.get("key"):
            q["key"] = {"$in": [int(x) for x in options["key"]]}
        if not options.get("start"):
            self.die("Setting start date for resheduling")
        start = options.get("start")
        if options.get("end"):
            shift_interval = max(shift_interval, options["end"] - options["start"])
        for j in scheduler.find(q).sort("ts"):
            start += shift_interval
            self.print("Change: ", j["ts"], "-->", start)
            bulk += [UpdateOne({"_id": j["_id"]}, {"$set": {"ts": start}})]
        if options.get("force", False):
            self.print("Jobs will be reschedule")
            for i in reversed(range(1, 10)):
                self.print("%d\n" % i)
                time.sleep(1)
            scheduler.bulk_write(bulk)
            # Job.get_next_timestamp(64000)


if __name__ == "__main__":
    Command().run()
