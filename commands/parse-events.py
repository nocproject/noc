# -*- coding: utf-8 -*-
# ----------------------------------------------------------------------
# parse-events command
# ----------------------------------------------------------------------
# Copyright (C) 2007-2017 The NOC Project
# See LICENSE for details
# ----------------------------------------------------------------------

# Python modules
from __future__ import print_function
import argparse
import time
import os
from collections import defaultdict
import datetime
import operator
# NOC modules
from noc.core.management.base import BaseCommand
from noc.services.classifier.ruleset import RuleSet
from noc.core.profile.loader import loader as profile_loader
from noc.fm.models.mib import MIB
from noc.sa.models.managedobject import ManagedObject
from noc.fm.models.activeevent import ActiveEvent


class Command(BaseCommand):
    def add_arguments(self, parser):
        parser.add_argument(
            "--profile",
            default="Generic.Host",
            help="Object profile"
        )
        parser.add_argument(
            "--format",
            default="syslog",
            help="Input format"
        )
        parser.add_argument(
            "paths",
            nargs=argparse.REMAINDER,
            help="List of input file paths"
        )

    def handle(self, paths, profile, format, *args, **options):
        assert profile_loader.get_profile(profile), "Invalid profile: %s" % profile
        t0 = time.time()
        ruleset = RuleSet()
        ruleset.load()
        self.print("Ruleset load in %.2fms" % ((time.time() - t0) * 1000))
        reader = getattr(self, "read_%s" % format, None)
        assert reader, "Invalid format %s" % format
        self.managed_object = ManagedObject(
            id=1,
            name="test",
            address="127.0.0.1",
            profile_name=profile
        )
        t0 = time.time()
        stats = defaultdict(int)
        total = 0
        for p in paths:
            if not os.path.isfile(p):
                continue
            with open(p) as f:
                for event in reader(f):
                    e_vars = event.raw_vars.copy()
                    if event.source == "SNMP Trap":
                        e_vars.update(MIB.resolve_vars(event.raw_vars))
                    rule, r_vars = ruleset.find_rule(event, e_vars)
                    stats[rule.event_class.name] += 1
                    total += 1
        dt = time.time() - t0
        self.print("%d events processed in %.2fms (%.fevents/sec)" % (
            total, dt * 1000, float(total) / dt
        ))
        summary = sorted(
            [(k, stats[k]) for k in stats],
            key=operator.itemgetter(0),
            reverse=True
        )
        self.print("Event classes summary:")
        for ecls, n in summary:
            self.print("%8d\t%3.2f%%\t%s" % (n, float(n * 100) / float(total), ecls))

    def read_syslog(self, f):
        now = datetime.datetime.now()
        for line in f:
            yield ActiveEvent(
                timestamp=now,
                start_timestamp=now,
                managed_object=self.managed_object,
                raw_vars={
                    "source": "syslog",
                    "collector": "default",
                    "message": line[-1]
                },
                repeats=1
            )

if __name__ == "__main__":
    Command().run()
