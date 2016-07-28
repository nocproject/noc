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


class Command(BaseCommand):
    jcls = {
        "box": "noc.services.discovery.jobs.box.job.BoxDiscoveryJob",
        "periodic": "noc.services.discovery.jobs.periodic.job.PeriodicDiscoveryJob"
    }

    checks = {
        "box": [
            "profile", "version", "caps", "interface",
            "id", "config", "asset", "vlan", "nri",
            "oam", "lldp", "cdp", "stp"
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
        job_args = {
            Job.ATTR_KEY: mo.id,
            "_checks": checks
        }
        if self.requires_context(job, checks):
            d = scheduler.get_collection().find_one({
                Job.ATTR_CLASS: self.jcls[job],
                Job.ATTR_KEY: mo.id

            }, {
                Job.ATTR_CONTEXT: 1
            })
            if d and d[Job.ATTR_CONTEXT]:
                job_args[Job.ATTR_CONTEXT] = d[Job.ATTR_CONTEXT]
        job = get_handler(self.jcls[job])(scheduler, job_args)
        job.dereference()
        job.handler()
        if scheduler.service.metrics:
            for m in scheduler.service.metrics:
                self.stdout.write("Collected metric: %s\n" % m)

    def requires_context(self, job, checks):
        """
        Returns True if job uses context
        """
        return job == "periodic" and (not checks or "metrics" in checks)


class ServiceStub(object):
    def __init__(self):
        self.metrics = []

    def register_metrics(self, batch):
        self.metrics += batch

if __name__ == "__main__":
    Command().run()
