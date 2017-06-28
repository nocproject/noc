# -*- coding: utf-8 -*-
# ---------------------------------------------------------------------
# job management
# ---------------------------------------------------------------------
# Copyright (C) 2007-2012 The NOC Project
# See LICENSE for details
# ---------------------------------------------------------------------

# Python modules
from optparse import make_option
import csv
import sys
# Django modules
from django.core.management.base import BaseCommand, CommandError
# NOC modules
from noc.lib.scheduler.scheduler import Scheduler


class Command(BaseCommand):
    """
    Manage Jobs
    """
    help = "Manage Jobs"
    option_list=BaseCommand.option_list+(
        make_option("--scheduler", "-s",
            dest="scheduler",
            default="main.jobs",
            choices=[
                "main.jobs",
                "inv.discovery"
                ],
            help="Select scheduler"),
        make_option("--list", "-l",
            action="store_const",
            const="list",
            dest="action",
            help="List active jobs"
        ),
        make_option("--format", "-f",
            action="store",
            dest="format",
            choices=["json", "csv"],
            help="Set output format"
        ),
    )

    def get_scheduler(self, **options):
        return Scheduler(options["scheduler"])

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
        print job

    def format_csv(self, job):
        s = job["schedule"] or {}
        self.writer.writerow([
            job["ts"], job["_id"], job["jcls"], job["key"],
            job["s"], job.get("ls", ""), job.get("runs", 0),
            job.get("last", ""), job.get("ldur", ""),
            s.get("interval", ""), s.get("failed_interval", ""),
            s.get("offset", "")
            ])

    def handle(self, *args, **options):
        action = options["action"] or "list"
        return getattr(self, "handle_%s" % action)(*args, **options)

    def handle_list(self, *args, **options):
        scheduler = self.get_scheduler(**options)
        fname = options["format"] or "csv"
        format = getattr(self, "format_%s" % fname)
        # Print header
        getattr(self, "init_%s" % fname)()
        # Print jobs
        for j in scheduler.collection.find().sort("ts"):
            format(j)
