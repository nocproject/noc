# -*- coding: utf-8 -*-
#----------------------------------------------------------------------
# forensic
#----------------------------------------------------------------------
# Copyright (C) 2007-2017 The NOC Project
# See LICENSE for details
#----------------------------------------------------------------------

# Python modules
from __future__ import print_function
import sys
import re
from collections import namedtuple
import operator
# NOC modules
from noc.core.management.base import BaseCommand

SpanData = namedtuple("SpanData", ["ts", "id", "server", "service", "label"])


class Command(BaseCommand):
    rx_open = re.compile(
        r"(\d{4}-\d{2}-\d{2} \d{2}:\d{2}:\d{2},\d+) \[forensic\] "
        r"\[>([^\|]+)\|([^\|]+)\|([^\]]+)\]\s*(.*)"
    )
    rx_close = re.compile(
        r"(\d{4}-\d{2}-\d{2} \d{2}:\d{2}:\d{2},\d+) \[forensic\] "
        r"\[<([^\]]+)\]"
    )

    def add_arguments(self, parser):
        subparsers = parser.add_subparsers(
            dest="cmd",
            help="sub-commands help"
        )
        # sync
        subparsers.add_parser(
            "incomplete",
            help="Show incomplete operations"
        )

    def handle(self, cmd, *args, **options):
        getattr(self, "handle_%s" % cmd)(*args, **options)

    def handle_incomplete(self):
        spans = {}
        for line in sys.stdin:
            line = line.strip()
            if "[forensic] [>" in line:
                # Open span
                match = self.rx_open.search(line)
                if not match:
                    continue
                s = SpanData(
                    ts=match.group(1),
                    id=match.group(2),
                    server=match.group(3),
                    service=match.group(4),
                    label=match.group(5)
                )
                spans[s.id] = s
            elif "[forensic] [<" in line:
                # Close span
                match = self.rx_close.search(line)
                if not match:
                    continue
                sid = match.group(2)
                if sid in spans:
                    del spans[sid]
        if spans:
            self.print("Timestamp\t\tID\t\t\t\t\tServer\t\tService\t\tLabel")
        for s in sorted(spans.values(), key=operator.attrgetter("ts")):
            self.print("%s\t%s\t%s\t%s\t%s" % (s.ts, s.id, s.server, s.service, s.label))

if __name__ == "__main__":
    Command().run()
