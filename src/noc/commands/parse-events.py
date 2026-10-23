# ----------------------------------------------------------------------
# parse-events command
# ----------------------------------------------------------------------
# Copyright (C) 2007-2021 The NOC Project
# See LICENSE for details
# ----------------------------------------------------------------------

# Python modules
import argparse
import time
import os
from collections import defaultdict
import datetime
import operator
import csv

# NOC modules
from noc.core.management.base import BaseCommand
from noc.core.mongo.connection import connect
from noc.services.classifier.ruleset import RuleSet
from noc.core.profile.loader import loader as profile_loader
from noc.fm.models.mib import MIB
from noc.sa.models.managedobject import ManagedObject
from noc.fm.models.activeevent import ActiveEvent
from noc.core.fileutils import iter_open
from noc.core.text import format_table
from noc.core.perf import metrics
from noc.sa.models.profile import Profile


class Command(BaseCommand):
    def add_arguments(self, parser: argparse.ArgumentParser) -> None:
        parser.add_argument("paths", nargs="+", help="List of input file paths")
        parser.add_argument("--profile", default="Generic.Host", help="Object profile")
        parser.add_argument("--format", default="syslog", help="Input format")
        parser.add_argument(
            "--report",
            type=argparse.FileType("w", encoding="UTF-8"),
            required=False,
            metavar="FILE",
            help="Path output file identified data",
        )
        parser.add_argument(
            "--reject",
            type=argparse.FileType("w", encoding="UTF-8"),
            required=False,
            metavar="FILE",
            help="Path output file unknown data",
        )
        parser.add_argument("--progress", action="store_true", help="Display progress")

    def handle(
        self, paths, profile, format, report=None, reject=None, progress=False, *args, **options
    ):
        connect()
        assert profile_loader.has_profile(profile), f"Invalid profile: {profile}"
        if report:
            report_writer = csv.writer(
                report, delimiter=",", quotechar='"', quoting=csv.QUOTE_MINIMAL
            )
            report_writer.writerow(["message", "event class", "rule name", "vars"])
        t0 = time.time()
        ruleset = RuleSet()
        ruleset.load()
        self.print(f"Ruleset load in {(time.time() - t0) * 1000:.2f}ms")
        reader = getattr(self, f"read_{format}", None)
        assert reader, f"Invalid format {format}"
        self.managed_object = ManagedObject(
            id=1, name="test", address="127.0.0.1", profile=Profile.get_by_name(profile)
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
                    if report:
                        report_writer.writerow(
                            [event.raw_vars["message"], rule.event_class.name, rule.name, r_vars]
                        )
                    if reject and rule.is_unknown:
                        reject.write(f"{event.raw_vars['message']}\n")
                    stats[rule.event_class.name] += 1
                    total += 1
                    if progress and total % 1000 == 0:
                        self.print(f"{int(total)} records processed")
        dt = time.time() - t0
        self.print(
            f"{int(total)} events processed in {dt * 1000:.2f}ms ({float(total) / dt:.f}events/sec)"
        )
        if stats:
            # Prepare statistics
            s_data = sorted(
                [(k, stats[k]) for k in stats], key=operator.itemgetter(1), reverse=True
            )
            s_total = sum(stats[k] for k in stats if not self.is_ignored(k))
            data = [["Events", "%", "Event class"]]
            for ecls, qty in s_data:
                data.append([str(qty), f"{float(stats[ecls] * 100) / float(total):3.2f}%", ecls])
            # Calculate classification quality
            data.append(["", f"{float(s_total * 100) / total:3.2f}%", "Classification Quality"])
            # Ruleset hit rate
            rs_rate = float(metrics["rules_checked"].value) / float(total)
            data.append(["", f"{rs_rate:.2f}", "Rule checks per event"])
            # Dump table
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
                source="syslog",
                raw_vars={"collector": "default", "message": line[:-1]},
                repeats=1,
            )
