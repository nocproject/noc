# -*- coding: utf-8 -*-
# ----------------------------------------------------------------------
# forensic
# ----------------------------------------------------------------------
# Copyright (C) 2007-2018 The NOC Project
# See LICENSE for details
# ----------------------------------------------------------------------

# Python modules
from __future__ import print_function
import sys
import re
from collections import namedtuple
import operator
import time
# NOC modules
from noc.core.management.base import BaseCommand

SpanData = namedtuple("SpanData", ["ts", "id", "server", "service", "label"])


class Command(BaseCommand):
    rx_open = re.compile(
        r"(\d{4}-\d{2}-\d{2} \d{2}:\d{2}:\d{2},\d+) \[noc\.core\.forensic\] "
        r"\[>([^\|]+)\|([^\|]+)\|([^\]]+)\]\s*(.*)"
    )
    rx_close = re.compile(
        r"(\d{4}-\d{2}-\d{2} \d{2}:\d{2}:\d{2},\d+) \[noc\.core\.forensic\] "
        r"\[<([^\]]+)\]"
    )
    show_mask = "%-23s %-25s %-15s %-30s %s"
    show_watch_mask = "%-23s %6s %-25s %-15s %-30s %s"
    time_format = "%Y-%m-%d %H:%M:%S"

    REFRESH_INTERVAL = 1

    def add_arguments(self, parser):
        subparsers = parser.add_subparsers(
            dest="cmd",
            help="sub-commands help"
        )
        # sync
        incomplete_parser = subparsers.add_parser(
            "incomplete",
            help="Show incomplete operations"
        )
        incomplete_parser.add_argument(
            "--watch",
            action="store_true",
            help="Watch mode"
        )

    def handle(self, cmd, *args, **options):
        getattr(self, "handle_%s" % cmd)(*args, **options)

    def handle_incomplete(self, watch=False, *args, **kwargs):
        def show():
            self.print("\x1b[2J\x1b[1;1H%s Spans: %d/%d" % (time.strftime("%H:%M:%S"), n_closed, n_open))
            self.print(self.show_mask % ("Timestamp", "ID", "Server", "Service", "Label"))
            for s in sorted(spans.values(), key=operator.attrgetter("ts")):
                self.print(self.show_mask % (s.ts, s.id, s.server, s.service, s.label))
            if not spans:
                self.print("  No spans")

        def show_watch():
            now = time.time()
            self.print("\x1b[2J\x1b[1;1H%s Spans: %d/%d" % (time.strftime("%H:%M:%S"), n_closed, n_open))
            self.print(self.show_watch_mask % ("Timestamp", "Dur", "ID", "Server", "Service", "Label"))
            for s in sorted(spans.values(), key=operator.attrgetter("ts")):
                ts = time.mktime(time.strptime(s.ts.split(",", 1)[0], self.time_format))
                duration = str(int(now - ts))
                self.print(self.show_watch_mask % (s.ts, duration, s.id, s.server, s.service, s.label))
            if not spans:
                self.print("  No spans")

        spans = {}
        next_show = 0
        n_open = 0
        n_closed = 0
        for line in sys.stdin:
            line = line.strip()
            if "[noc.core.forensic] [>" in line:
                # Open span
                match = self.rx_open.search(line)
                if match:
                    s = SpanData(
                        ts=match.group(1),
                        id=match.group(2),
                        server=match.group(3),
                        service=match.group(4),
                        label=match.group(5)
                    )
                    spans[s.id] = s
                    n_open += 1
            elif "[noc.core.forensic] [<" in line:
                # Close span
                match = self.rx_close.search(line)
                if match:
                    sid = match.group(2)
                    if sid in spans:
                        del spans[sid]
                        n_closed += 1
            elif "[noc.core.forensic] [=Process restarted]" in line:
                # Process restarted, clear spans
                if not watch:
                    show()
                    self.print("===[ Process Restarted ]==============")
                # Reset spans
                spans = {}
                next_show = 0
                n_open = 0
                n_closed = 0
            if watch:
                t = time.time()
                if t > next_show:
                    next_show = t + self.REFRESH_INTERVAL
                    show_watch()
        if watch:
            show_watch()
        else:
            show()


if __name__ == "__main__":
    Command().run()
