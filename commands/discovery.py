# ----------------------------------------------------------------------
# discovery commands
# ----------------------------------------------------------------------
# Copyright (C) 2007-2020 The NOC Project
# See LICENSE for details
# ----------------------------------------------------------------------

# Python modules
import argparse
import time
from collections import defaultdict
from functools import partial

# NOC modules
from noc.core.management.base import BaseCommand
from noc.core.mongo.connection import connect
from noc.core.handler import get_handler
from noc.inv.models.resourcegroup import ResourceGroup
from noc.inv.models.networksegment import NetworkSegment
from noc.core.scheduler.scheduler import Scheduler
from noc.core.scheduler.job import Job
from noc.core.cache.base import cache
from noc.core.span import Span, get_spans
from noc.core.service.pub import publish
from noc.core.comp import smart_bytes


class Command(BaseCommand):
    jcls = {
        "box": "noc.services.discovery.jobs.box.job.BoxDiscoveryJob",
        "periodic": "noc.services.discovery.jobs.periodic.job.PeriodicDiscoveryJob",
        "segment": "noc.services.discovery.jobs.segment.job.SegmentDiscoveryJob",
        "interval": "noc.services.discovery.jobs.interval.job.IntervalDiscoveryJob",
    }

    checks = {
        "box": [
            "profile",
            "version",
            "caps",
            "interface",
            "id",
            "config",
            "asset",
            "configvalidation",
            "vlan",
            "nri",
            "udld",
            "oam",
            "lldp",
            "cdp",
            "huawei_ndp",
            "stp",
            "sla",
            "cpe",
            "lacp",
            "hk",
            "mac",
            "xmac",
            "ifdesc",
            "bfd",
            "fdp",
            "vpn",
            "prefix",
            "address",
            "nri_portmap",
            "nri_service",
            "alarms",
            "diagnostic",
            "configparam",
        ],
        "periodic": [
            "uptime",
            "interfacestatus",
            "mac",
            "cpestatus",
            "alarms",
            "diagnostic",
        ],
        "interval": ["metrics"],
        "segment": ["mac"],
    }

    def add_arguments(self, parser):
        subparsers = parser.add_subparsers(dest="cmd", required=True)
        #
        run_parser = subparsers.add_parser("run")
        run_parser.add_argument(
            "-c", "--check", action="append", default=[], help="Execute selected checks only"
        )
        run_parser.add_argument("--trace", action="store_true", default=False, help="Trace process")
        run_parser.add_argument(
            "--dump-buffer", action="store_true", default=False, help="Trace process"
        )
        run_parser.add_argument("job", nargs=1, choices=list(self.jcls), help="Job name")
        run_parser.add_argument("managed_objects", nargs=argparse.REMAINDER, help="Managed objects")

    def handle(self, cmd, *args, **options):
        connect()
        return getattr(self, "handle_%s" % cmd)(*args, **options)

    def handle_run(
        self, job, managed_objects, check=None, trace=False, dump_buffer=False, *args, **options
    ):
        self.trace = trace
        job = job[0]
        mos = []
        for x in managed_objects:
            if job == "segment":
                mos += [NetworkSegment.objects.get(name=x)]
            else:
                for mo in ResourceGroup.get_objects_from_expression(x, model_id="sa.ManagedObject"):
                    if mo not in mos:
                        mos += [mo]
        checks = set()
        for c in check:
            checks.update(c.split(","))
        for c in checks:
            if c not in self.checks[job]:
                self.die(
                    "Unknown check '%s' for job '%s'. Available checks are: %s\n"
                    % (c, job, ", ".join(self.checks[job]))
                )
        for mo in mos:
            self.run_job(job, mo, checks, dump_buffer=dump_buffer)

    def run_job(self, job, mo, checks, dump_buffer=False):
        if job == "segment":
            scheduler = Scheduler("scheduler", pool=None, service=ServiceStub())
        else:
            scheduler = Scheduler("discovery", pool=mo.pool.name, service=ServiceStub())
        jcls = self.jcls[job]
        # Try to dereference job
        job_args = scheduler.get_collection().find_one({Job.ATTR_CLASS: jcls, Job.ATTR_KEY: mo.id})
        if job_args:
            self.print("Job ID: %s" % job_args["_id"])
        else:
            job_args = {Job.ATTR_ID: "fakeid", Job.ATTR_KEY: mo.id}
        job_args["_checks"] = checks
        job = get_handler(jcls)(scheduler, job_args)
        if job.context_version:
            ctx_key = job.get_context_cache_key()
            self.print("Loading job context from %s" % ctx_key)
            ctx = cache.get(ctx_key, version=job.context_version)
            if not ctx:
                self.print("Job context is empty")
            job.load_context(ctx)
        sample = 1 if self.trace else 0
        with Span(sample=sample):
            job.dereference()
            job.handler()
        if sample:
            spans = get_spans()
            self.print("Spans:")
            self.print("\n".join(str(s) for s in spans))
        if scheduler.service.metrics:
            self.print("Collected CH data:")
            for t in scheduler.service.metrics:
                self.print("Table: %s" % t)
                self.print("\n".join(str(x) for x in scheduler.service.metrics[t]))
        # job.update_alarms()
        if job.context_version and job.context:
            self.print("Saving job context to %s" % ctx_key)
            scheduler.cache_set(key=ctx_key, value=job.context, version=job.context_version)
            scheduler.apply_cache_ops()
            time.sleep(3)
        if dump_buffer and job.out_buffer:
            print("OUT Buffer")
            print(smart_bytes(job.out_buffer.getvalue()))


class ServiceStub(object):
    def __init__(self):
        self.metrics = defaultdict(list)
        self.service_id = "stub"
        self.address = "127.0.0.1"
        self.port = 0
        self.publish = publish

    def register_metrics(self, table, data, key=None):
        self.metrics[table] += data

    @staticmethod
    def get_slot_limits(slot_name):
        """
        Get slot count
        :param slot_name:
        :return:
        """
        from noc.core.dcs.loader import get_dcs, DEFAULT_DCS
        from noc.core.ioloop.util import run_sync

        dcs = get_dcs(DEFAULT_DCS)
        return run_sync(partial(dcs.get_slot_limit, slot_name))


if __name__ == "__main__":
    Command().run()
