# -*- coding: utf-8 -*-
##----------------------------------------------------------------------
## discovery commands
##----------------------------------------------------------------------
## Copyright (C) 2007-2016 The NOC Project
## See LICENSE for details
##----------------------------------------------------------------------

## Python modules
import argparse
## NOC modules
from noc.core.management.base import BaseCommand
from noc.core.handler import get_handler
from noc.sa.models.managedobjectselector import ManagedObjectSelector
from noc.core.scheduler.scheduler import Scheduler
from noc.core.scheduler.job import Job
from noc.core.cache.base import cache


class Command(BaseCommand):
    jcls = {
        "box": "noc.services.discovery.jobs.box.job.BoxDiscoveryJob",
        "periodic": "noc.services.discovery.jobs.periodic.job.PeriodicDiscoveryJob"
    }

    checks = {
        "box": [
            "profile", "version", "caps", "interface",
            "id", "config", "asset", "vlan", "nri",
            "oam", "lldp", "cdp", "stp", "sla"
        ],
        "periodic": [
            "uptime", "interfacestatus",
            "mac", "metrics"
        ]
    }

    def add_arguments(self, parser):
        subparsers = parser.add_subparsers(dest="cmd")
        #
        run_parser = subparsers.add_parser("run")
        run_parser.add_argument(
            "-c", "--check",
            action="append",
            default=[],
            help="Execute selected checks only"
        )
        run_parser.add_argument(
            "job",
            nargs=1,
            choices=list(self.jcls),
            help="Job name"
        )
        run_parser.add_argument(
            "managed_objects",
            nargs=argparse.REMAINDER,
            help="Managed objects"
        )

    def handle(self, cmd, *args, **options):
        return getattr(self, "handle_%s" % cmd)(*args, **options)

    def handle_run(self, job, managed_objects, check=None, *args, **options):
        job = job[0]
        mos = []
        for x in managed_objects:
            for mo in ManagedObjectSelector.resolve_expression(x):
                if mo not in mos:
                    mos += [mo]
        checks = set()
        for c in check:
            checks.update(c.split(","))
        for c in checks:
            if c not in self.checks[job]:
                self.die(
                    "Unknown check '%s' for job '%s'. Available checks are: %s\n" % (
                        c, job, ", ".join(self.checks[job])
                    )
                )
        for mo in mos:
            self.run_job(job, mo, checks)

    def run_job(self, job, mo, checks):
        scheduler = Scheduler("discovery", pool=mo.pool.name)
        scheduler.service = ServiceStub()
        jcls = self.jcls[job]
        # Try to dereference job
        job_args = scheduler.get_collection().find_one({
            Job.ATTR_CLASS: jcls,
            Job.ATTR_KEY: mo.id
        })
        if job_args:
            self.stdout.write("Job ID: %s\n" % job_args["_id"])
        else:
            job_args = {
                Job.ATTR_ID: "fakeid",
                Job.ATTR_KEY: mo.id
            }
        job_args["_checks"] = checks
        job = get_handler(jcls)(scheduler, job_args)
        if job.context_version:
            ckey = job.get_context_cache_key()
            self.stdout.write("Getting job context from %s\n" % ckey)
            ctx = cache.get(ckey)
            if not ctx:
                self.stdout.write("Job context is empty\n")
            job.load_context(ctx)
        job.dereference()
        job.handler()
        if scheduler.service.metrics:
            for m in scheduler.service.metrics:
                self.stdout.write("Collected metric: %s\n" % m)


class ServiceStub(object):
    def __init__(self):
        self.metrics = []

    def register_metrics(self, batch):
        self.metrics += batch

if __name__ == "__main__":
    Command().run()
