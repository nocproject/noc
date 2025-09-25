# ---------------------------------------------------------------------
# job management
# ---------------------------------------------------------------------
# Copyright (C) 2007-2012 The NOC Project
# See LICENSE for details
# ---------------------------------------------------------------------

# Python modules
import argparse
from datetime import datetime, timedelta
from collections import defaultdict
from typing import Optional, List
from functools import partial
import math
import csv
import time
import sys

# Third-party modules
from pymongo import UpdateOne
from django.db import connection as pg_conn

# NOC modules
from noc.core.mongo.connection import connect
from noc.core.management.base import BaseCommand
from noc.core.scheduler.scheduler import Scheduler
from noc.core.service.loader import get_dcs
from noc.core.ioloop.util import run_sync
from noc.main.models.pool import Pool


SHARDING_SCHEDULER = {"discovery", "correlator", "escalator"}


class Command(BaseCommand):
    """
    Manage Jobs
    """

    help = "Manage Jobs"
    default_time = timedelta(minutes=5)
    connect()

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
            return Scheduler(scheduler, pool=pool)
        return Scheduler(scheduler)

    def add_arguments(self, parser):
        (
            parser.add_argument(
                "--scheduler",
                "-s",
                dest="scheduler",
                default=Scheduler("scheduler").get_collection(),
                type=self.scheduler,
                help="Select scheduler. For sharded use SCHEDULER_NAME.SHARD_NAME",
            ),
        )
        (
            parser.add_argument(
                "--format",
                "-f",
                dest="store",
                # action="format",
                choices=["json", "csv"],
                help="Set output format",
            ),
        )
        subparsers = parser.add_subparsers(dest="cmd", required=True)
        # load command
        list_parser = subparsers.add_parser("list")
        list_parser.add_argument("--name", help="Job name in scheduler")
        list_parser.add_argument("key", nargs=argparse.REMAINDER, help="List of job key")
        get_parser = subparsers.add_parser("get")
        get_parser.add_argument("--id", help="Job name in scheduler")
        subparsers.add_parser("set")
        estimate = subparsers.add_parser("estimate")
        estimate.add_argument("--device-count", type=int, default=0, help="Device count")
        estimate.add_argument(
            "--box-interval", type=int, default=65400, help="Box discovery interval (in seconds)"
        )
        estimate.add_argument(
            "--periodic-interval",
            type=int,
            default=300,
            help="Periodic discovery interval (in seconds)",
        )
        # Parse Job Field
        reschedule = subparsers.add_parser("reschedule", help="Shift Jobs to interval")
        reschedule.add_argument("--name", help="Job name in scheduler")
        reschedule.add_argument("--start", type=self.valid_date, help="Start interval for place")
        reschedule.add_argument("--end", type=self.valid_date, help="End interval for place")
        reschedule.add_argument(
            "--force", default=False, action="store_true", help="Really do reschedule"
        )
        reschedule.add_argument("key", nargs=argparse.REMAINDER, help="List of job key")
        parser.add_argument("infile", nargs="?", type=argparse.FileType("r"), default=sys.stdin)
        # stats command
        stat_parser = subparsers.add_parser("stats", help="Show stats")
        stat_parser.add_argument("--top", default=0, type=int, help="Top device by size")
        stat_parser.add_argument("--slots", default="0", type=str, help="Slots lists")
        #
        bucket_duration_parser = subparsers.add_parser(
            "bucket-duration", help="Show stats by backets"
        )
        bucket_duration_parser.add_argument("--backets", default=5, help="Bucket count")
        bucket_duration_parser.add_argument("--slots", default="0", type=str, help="Slots lists")
        bucket_duration_parser.add_argument(
            "--min-duration", default=5, type=int, help="Minimal job duration"
        )
        bucket_duration_parser.add_argument(
            "--detail", default=False, action="store_true", help="Show bucket elements"
        )
        #
        bucket_late_parser = subparsers.add_parser("bucket-late", help="Show stats by backets")
        bucket_late_parser.add_argument("--backets", default=5, help="Bucket count")
        bucket_late_parser.add_argument("--slots", default="0", type=str, help="Slots lists")
        bucket_late_parser.add_argument(
            "--min-duration", default=5, type=int, help="Minimal job duration"
        )
        bucket_late_parser.add_argument(
            "--detail", default=False, action="store_true", help="Show bucket elements"
        )

    def init_json(self):
        pass

    def init_csv(self):
        self.writer = csv.writer(sys.stdout)
        self.writer.writerow(
            [
                "Run",
                "ID",
                "Name",
                "Key",
                "Status",
                "Last Status",
                "Runs",
                "Last Run",
                "Last Duration",
                "Interval",
                "Failed Interval",
                "Offset",
            ]
        )

    def format_json(self, job):
        self.print(job)

    def format_csv(self, job):
        # s = job["schedule"] or {}
        self.writer.writerow(
            [
                job["ts"],
                job["_id"],
                job["jcls"],
                job["key"],
                job["s"],
                job.get("ls", ""),
                job.get("runs", 0),
                job.get("last", ""),
                job.get("ldur", ""),
                # s.get("interval", ""), s.get("failed_interval", ""),
                # s.get("offset", "")
            ]
        )

    def handle(self, cmd, *args, **options):
        if "infile" in options and not sys.stdin.isatty():
            for line in options["infile"]:
                options["key"] += [int(line)]
        return getattr(self, "handle_%s" % cmd.replace("-", "_"))(*args, **options)

    def handle_list(self, scheduler: Scheduler, *args, **options):
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
        for j in scheduler.get_collection().find(q).sort("ts").limit(50):
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

    @staticmethod
    def get_next_timestamp(interval, offset=0.0, ts=None):
        """
        Calculate next timestamp
        :param interval:
        :param offset:
        :param ts: current timestamp
        :return: datetime object
        """
        if not ts:
            ts = time.time()
        if ts and isinstance(ts, datetime):
            ts = time.mktime(ts.timetuple()) + float(ts.microsecond) / 1_000_000.0
        # Get start of current interval
        si = ts // interval * interval
        # Shift to offset
        si += offset * interval
        # Shift to interval if in the past
        if si <= ts:
            si += interval
        return datetime.fromtimestamp(si)

    def handle_fix_timepattern(self, *args, **options):
        from noc.sa.models.managedobject import ManagedObject
        import random

        procc_mos = defaultdict(set)
        time_pattern = {}
        for mo in ManagedObject.objects.filter(
            is_managed=True, object_profile__enable_box_discovery=True
        ).exclude(time_pattern=None):
            procc_mos[mo.pool.name].add(mo.id)
            time_pattern[mo.id] = mo.time_pattern
        for pool in procc_mos:
            c = Scheduler("discovery", pool=pool).get_collection()
            bulk = []
            for job in c.find(
                {
                    "jcls": "noc.services.discovery.jobs.box.job.BoxDiscoveryJob",
                    "key": {"$in": list(procc_mos[pool])},
                },
                {"o": 1, "ts": 1, "key": 1},
            ):
                tp = time_pattern[job["key"]]
                if not tp.match(job["ts"]):
                    print("Discovery job on TP", job["ts"], " ", job["key"])
                    ts = job["ts"]
                    i = 0
                    while i < 100:
                        offset = random.random()
                        ts = self.get_next_timestamp(86400, offset=offset, ts=ts)
                        if tp.match(ts):
                            bulk += [UpdateOne({"_id": job["_id"]}, {"$set": {"o": offset}})]
                            break
                        i += 1
            if bulk:
                c.bulk_write(bulk)

    def handle_reschedule(self, scheduler: Scheduler, *args, **options):
        bulk = []
        q = {}
        shift_interval = self.default_time
        coll = scheduler.get_collection()
        if options.get("name"):
            q["jcls"] = options["name"]
        if options.get("key"):
            q["key"] = {"$in": [int(x) for x in options["key"]]}
        if not options.get("start"):
            self.die("Setting start date for resheduling")
        start = options.get("start")
        if options.get("end"):
            shift_interval = max(shift_interval, options["end"] - options["start"])
        for j in coll.find(q).sort("ts"):
            start += shift_interval
            self.print("Change: ", j["ts"], "-->", start)
            bulk += [UpdateOne({"_id": j["_id"]}, {"$set": {"ts": start}})]
        if options.get("force", False):
            self.print("Jobs will be reschedule")
            for i in reversed(range(1, 10)):
                self.print("%d\n" % i)
                time.sleep(1)
            coll.bulk_write(bulk)
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
                 WHERE mo.object_profile_id = mop.id and mop.enable_%s_discovery = true
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
        job_map = {
            "noc.services.discovery.jobs.periodic.job.PeriodicDiscoveryJob": "periodic",
            "noc.services.discovery.jobs.box.job.BoxDiscoveryJob": "box",
        }
        r = {}
        match = {"ldur": {"$gte": 0.05}}  # If Ping fail and skipping discovery

        for pool in Pool.objects.filter():
            coll = Scheduler("discovery", pool=pool.name).get_collection()
            r[pool] = {
                job_map[c["_id"]]: c["avg_dur"]
                for c in coll.aggregate(
                    [{"$match": match}, {"$group": {"_id": "$jcls", "avg_dur": {"$avg": "$ldur"}}}]
                )
                if c["_id"]
            }
        return r

    def handle_estimate(
        self, device_count=None, box_interval=65400, periodic_interval=300, *args, **options
    ):
        """
        Calculate Resource needed job
        :param device_count: Count active device
        :param box_interval: Box discovery interval
        :param periodic_interval: Periodic discovery interval
        :param
        :return:
        """

        if device_count:
            task_count = {
                Pool.get_by_name("default"): {
                    "box_task_per_seconds": float(device_count) / float(box_interval),
                    "periodic_task_per_seconds": float(device_count) / float(periodic_interval),
                }
            }
            job_avg = {
                Pool.get_by_name("default"): {
                    "box": 120.0,  # Time execute box discovery (average in seconds)
                    "periodic": 10,  # Time execute periodic discovery (average in seconds)
                }
            }
        else:
            task_count = self.get_task_count()
            job_avg = self.get_job_avg()

        for pool in task_count:
            if pool == "all" or not task_count[pool]:
                continue
            job_count = task_count[pool]["box_task_per_seconds"] * job_avg[pool].get(
                "box", 0
            ) + task_count[pool]["periodic_task_per_seconds"] * job_avg[pool].get("periodic", 0)
            self.print("%20s %s" % ("Pool", "Threads est."))
            self.print("%40s %d" % (pool.name, math.ceil(job_count)))

    @classmethod
    def get_max_slots(cls, scheduler: Scheduler) -> int:
        slots = 0
        if scheduler.pool:
            slots = run_sync(partial(cls.get_slot_limits, f"{scheduler.name}-{scheduler.pool}"))
        return slots

    def handle_stats(
        self,
        scheduler: Scheduler,
        mos: Optional[List[int]] = None,
        slots: Optional[List[int]] = None,
        **options,
    ):
        from noc.sa.models.profile import Profile

        if isinstance(slots, str):
            slots = [int(s) for s in slots.split(",")]
        max_slots = self.get_max_slots(scheduler)
        if not max_slots:
            self.print("Unknown scheduler name or it has not slots")
            return
        pool = Pool.get_by_name(scheduler.pool)
        self.print(f"Max Slots is {max_slots}")
        query = f"""
        SELECT mod(mo.id, {max_slots}) as slot, profile, count(*) as number
        FROM sa_managedobject mo JOIN sa_managedobjectprofile mop ON (mo.object_profile_id = mop.id)
        WHERE mop.enable_periodic_discovery = true AND pool = %s {"AND mo.id=ANY(%s)" if mos else ""}
        GROUP BY profile, slot
        {"HAVING mod(mo.id, %d)=ANY(%%s)" % max_slots if slots else ""}
        ORDER BY slot, number desc
        """
        params = [str(pool.id)]
        if mos:
            params += [mos]
        if slots:
            params += [slots]
        cursor = pg_conn.cursor()
        cursor.execute(query, params)
        c_slot = None
        total = 0
        for slot, profile, count in cursor.fetchall():
            if c_slot and c_slot != slot:
                self.print(f"{'=' * 10} Slot {slot} {'=' * 10}")
            p = Profile.get_by_id(profile)
            self.print(f"Profile: {p} - Count {count}")
            c_slot = slot
            total += count
        self.print(f"Total: {total}")

    def handle_bucket_duration(
        self,
        scheduler: Scheduler,
        min_duration=5,
        buckets=5,
        slots: Optional[List[int]] = None,
        detail: bool = False,
        *args,
        **options,
    ):
        if isinstance(slots, str):
            slots = [int(s) for s in slots.split(",")]
        max_slots = self.get_max_slots(scheduler)
        self.print(f"Max Slots is {max_slots}")
        r = self.get_bucket_ldur(
            scheduler.get_collection(),
            slots=slots,
            max_slots=max_slots,
            buckets=buckets,
            min_duration=min_duration,
        )
        for num, bucket in enumerate(r):
            self.print("\n", "=" * 80)
            self.print(
                f"Bucket {num}:    Count: %d; Duration %d s - %d s"
                % (bucket["count"], bucket["_id"]["min"], bucket["_id"]["max"])
            )
            if detail:
                for o in bucket["objects"]:
                    from noc.sa.models.managedobject import ManagedObject

                    o = ManagedObject.objects.get(id=o)
                    self.print(f"Object:  {o.profile}:{o}")
            else:
                # self.print("Ids: ", ",".join(str(x) for x in bucket["objects"]))
                self.handle_stats(scheduler, mos=bucket["objects"])

    def handle_bucket_late(
        self,
        scheduler: Scheduler,
        min_duration=5,
        buckets=5,
        slots: Optional[List[int]] = None,
        detail: bool = False,
        *args,
        **options,
    ):
        if isinstance(slots, str):
            slots = [int(s) for s in slots.split(",")]
        max_slots = self.get_max_slots(scheduler)
        self.print(f"Max Slots is {max_slots}")
        r = self.get_bucket_late(
            scheduler.get_collection(),
            slots=slots,
            max_slots=max_slots,
            buckets=buckets,
            min_duration=min_duration,
        )
        print(max_slots)
        for num, bucket in enumerate(r):
            self.print("\n", "=" * 80)
            self.print(
                f"Bucket {num}:    Count: %d; Duration %d s - %d s"
                % (bucket["count"], bucket["_id"]["min"], bucket["_id"]["max"])
            )
            if detail:
                for o in bucket["objects"]:
                    from noc.sa.models.managedobject import ManagedObject

                    o = ManagedObject.objects.get(id=o)
                    self.print(f"Object:  {o.profile}:{o}")
            else:
                # self.print("Ids: ", ",".join(str(x) for x in bucket["objects"]))
                self.handle_stats(scheduler, mos=bucket["objects"])

    @staticmethod
    async def get_slot_limits(slot_name):
        dcs = get_dcs()
        return await dcs.get_slot_limit(slot_name)

    @staticmethod
    def get_bucket_ldur(
        scheduler, slots=None, max_slots=None, min_duration: int = 5, buckets: int = 5
    ):
        pipeline = [
            {"$project": {"slot": {"$mod": ["$key", max_slots]}, "key": 1, "jcls": 1, "ldur": 1}},
            {
                "$match": {
                    "slot": {"$in": slots},
                    "jcls": "noc.services.discovery.jobs.interval.job.IntervalDiscoveryJob",
                    # "jcls": "noc.services.discovery.jobs.periodic.job.PeriodicDiscoveryJob",
                    # "jcls": "noc.services.discovery.jobs.box.job.BoxDiscoveryJob",
                    "ldur": {"$gte": min_duration},
                }
            },
            {
                "$bucketAuto": {
                    "groupBy": "$ldur",
                    "buckets": buckets,
                    "output": {"count": {"$sum": 1}, "objects": {"$push": "$key"}},
                }
            },
        ]
        return scheduler.aggregate(pipeline)

    @staticmethod
    def get_bucket_late(
        scheduler, slots=None, max_slots=None, min_duration: int = 5, buckets: int = 5
    ):
        now = datetime.now()
        pipeline = [
            {
                "$match": {
                    "jcls": "noc.services.discovery.jobs.interval.job.IntervalDiscoveryJob",
                    # "jcls": "noc.services.discovery.jobs.periodic.job.PeriodicDiscoveryJob",
                    # "jcls": "noc.services.discovery.jobs.box.job.BoxDiscoveryJob",
                    "s": "R",
                }
            },
            {
                "$project": {
                    "slot": {"$mod": ["$key", max_slots]},
                    "key": 1,
                    "jcls": 1,
                    "ldur": 1,
                    "ts": 1,
                    "duration": {"$subtract": [now, "$ts"]},
                }
            },
            {
                "$match": {
                    "slot": {"$in": slots},
                    "duration": {"$gte": min_duration},
                }
            },
            {
                "$bucketAuto": {
                    "groupBy": "$ldur",
                    "buckets": buckets,
                    "output": {"count": {"$sum": 1}, "objects": {"$push": "$key"}},
                }
            },
        ]
        return scheduler.aggregate(pipeline)


if __name__ == "__main__":
    Command().run()
