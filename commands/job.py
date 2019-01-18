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
from collections import defaultdict
import math
import csv
import time
import sys
# Third-perty modules
from pymongo import UpdateOne
# NOC modules
from noc.core.management.base import BaseCommand
from noc.core.scheduler.scheduler import Scheduler
from noc.main.models.pool import Pool


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
        estimate = subparsers.add_parser("estimate")
        estimate.add_argument("--device-count",
                              type=int,
                              default=0,
                              help="Device count")
        estimate.add_argument("--box-interval",
                              type=int,
                              default=65400,
                              help="Box discovery interval (in seconds)")
        estimate.add_argument("--periodic-interval",
                              type=int,
                              default=300,
                              help="Periodic discovery interval (in seconds)")
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

    @staticmethod
    def get_task_count():
        """
        Calculate discovery tasks
        :return:
        """
        from django.db import connection
        cursor = connection.cursor()

        SQL = """SELECT mo.pool, mop.%s_discovery_interval, count(*)
                 FROM sa_managedobject mo, sa_managedobjectprofile mop
                 WHERE mo.object_profile_id = mop.id and mop.enable_%s_discovery = true and mo.is_managed = true
                 GROUP BY mo.pool, mop.%s_discovery_interval;
        """
        r = defaultdict(dict)
        r["all"]["sum_task_per_seconds"] = 0.0
        r["all"]["box_task_per_seconds"] = 0.0
        r["all"]["periodic_task_per_seconds"] = 0.0
        for s in ("box", "periodic"):
            cursor.execute(SQL % (s, s, s))
            for c in cursor.fetchall():
                p = Pool.get_by_id(c[0])
                r[p][c[1]] = c[2]
                if "sum_task_per_seconds" not in r[p]:
                    r[p]["sum_task_per_seconds"] = 0.0
                if "%s_task_per_seconds" % s not in r[p]:
                    r[p]["%s_task_per_seconds" % s] = 0.0
                r[p]["sum_task_per_seconds"] += float(c[2]) / float(c[1])
                r[p]["%s_task_per_seconds" % s] += float(c[2]) / float(c[1])
                r["all"]["sum_task_per_seconds"] += float(c[2]) / float(c[1])
                r["all"]["%s_task_per_seconds" % s] += float(c[2]) / float(c[1])
        return r

    @staticmethod
    def get_job_avg():
        """
        Calculate average time execute discovery job
        :return:
        """
        job_map = {"noc.services.discovery.jobs.periodic.job.PeriodicDiscoveryJob": "periodic",
                   "noc.services.discovery.jobs.box.job.BoxDiscoveryJob": "box"}
        r = {}
        match = {"ldur": {"$gte": 0.05}}  # If Ping fail and skipping discovery

        for pool in Pool.objects.filter():
            coll = Scheduler("discovery", pool=pool.name).get_collection()
            r[pool] = {job_map[c["_id"]]: c["avg_dur"] for c in coll.aggregate([
                {"$match": match},
                {"$group": {"_id": "$jcls", "avg_dur": {"$avg": "$ldur"}}}
            ]) if c["_id"]}
        return r

    def handle_estimate(self, device_count=None, box_interval=65400, periodic_interval=300, *args, **options):
        """
        Calculate Resource needed job
        :param device_count: Count active device
        :param box_interval: Box discovery interval
        :param periodic_interval: Periodic discovery interval
        :param
        :return:
        """

        if device_count:
            task_count = {Pool.get_by_name("default"): {
                "box_task_per_seconds": float(device_count) / float(box_interval),
                "periodic_task_per_seconds": float(device_count) / float(periodic_interval)
            }}
            job_avg = {Pool.get_by_name("default"): {
                "box": 120.0,  # Time execute box discovery (average in seconds)
                "periodic": 10  # Time execute periodic discovery (average in seconds)
            }}
        else:
            task_count = self.get_task_count()
            job_avg = self.get_job_avg()

        for pool in task_count:
            if pool == "all" or not task_count[pool]:
                continue
            job_count = (task_count[pool]["box_task_per_seconds"] * job_avg[pool].get("box", 0) +
                         task_count[pool]["periodic_task_per_seconds"] * job_avg[pool].get("periodic", 0))
            self.print("%20s %s" % ("Pool", "Threads est."))
            self.print("%40s %d" % (pool.name, math.ceil(job_count)))


if __name__ == "__main__":
    Command().run()
