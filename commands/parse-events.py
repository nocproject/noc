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
from noc.core.fileutils import iter_open
from noc.lib.text import format_table


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
            "--progress",
            action="store_true",
            help="Display progress"
        )
        parser.add_argument(
            "paths",
            nargs=argparse.REMAINDER,
            help="List of input file paths"
        )

    def handle(self, paths, profile, format, progress=False,
               *args, **options):
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
            for f in iter_open(p):
                for event in reader(f):
                    e_vars = event.raw_vars.copy()
                    if event.source == "SNMP Trap":
                        e_vars.update(MIB.resolve_vars(event.raw_vars))
                    rule, r_vars = ruleset.find_rule(event, e_vars)
                    stats[rule.event_class.name] += 1
                    total += 1
                    if progress and total % 1000 == 0:
                        self.print("%d records processed" % total)
        dt = time.time() - t0
        self.print("%d events processed in %.2fms (%.fevents/sec)" % (
            total, dt * 1000, float(total) / dt
        ))
        if stats:
            s_data = sorted(
                [(k, stats[k]) for k in stats],
                key=operator.itemgetter(1),
                reverse=True
            )
            s_total = sum(stats[k] for k in stats if not self.is_ignored(k))
            data = [["Events", "%", "Event class"]]
            for ecls, qty in s_data:
                data += [[str(qty), "%3.2f%%" % (float(stats[ecls] * 100) / float(total)), ecls]]
            data += [["", "%3.2f%%" % (float(s_total * 100) / total), "Classification Quality"]]
            self.print("Event classes summary:")
            self.print(format_table([4, 6, 10], data))

    @staticmethod
    def is_ignored(ecls):
        return ecls.startswith("Unknown | ") and ecls != "Unknown | Ignore"

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
                    "message": line[:-1]
                },
                repeats=1
            )

if __name__ == "__main__":
    Command().run()
