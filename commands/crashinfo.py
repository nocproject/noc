# -*- coding: utf-8 -*-
# ----------------------------------------------------------------------
# ./noc crashinfo
# ----------------------------------------------------------------------
# Copyright (C) 2007-2019 The NOC Project
# See LICENSE for details
# ----------------------------------------------------------------------

# Python modules
import operator
import os
import datetime
import argparse
import stat
import re

# Third-party modules
import ujson

# NOC modules
from noc.core.management.base import BaseCommand
from noc.config import config
from noc.core.comp import smart_text


class Command(BaseCommand):
    PREFIX = config.path.cp_new

    rx_xtype = re.compile(r"^<(?:type|class) '(?P<xtype>[^']+)'>\s+")

    def add_arguments(self, parser):
        subparsers = parser.add_subparsers(dest="cmd")
        # list command
        subparsers.add_parser("list")
        # view command
        view_parser = subparsers.add_parser("view")
        view_parser.add_argument("view_uuids", nargs=argparse.REMAINDER, help="Crashinfo UUIDs")
        # clear command
        clear_parser = subparsers.add_parser("clear")
        clear_parser.add_argument("clear_uuids", nargs=argparse.REMAINDER, help="Crashinfo UUIDs")

    def handle(self, cmd, *args, **options):
        return getattr(self, "handle_%s" % cmd)(*args, **options)

    def handle_list(self):
        # Get last update timestamp
        if os.path.exists(".git/index"):
            uts = os.stat(".git/index")[stat.ST_MTIME]
        else:
            uts = 0
        # Build list
        fl = []
        if os.path.exists(self.PREFIX):
            for fn in os.listdir(self.PREFIX):
                if not fn.endswith(".json"):
                    continue
                path = os.path.join(self.PREFIX, fn)
                ts = os.stat(path)[stat.ST_MTIME]
                t = datetime.datetime.fromtimestamp(ts)
                with open(path) as f:
                    data = ujson.load(f)
                service = data["process"]
                if service.startswith("services/") and service.endswith("/service.py"):
                    service = service[9:-11]
                elif service.startswith("commands/"):
                    service = "noc %s" % service[9:-3]
                x = "Unknown exception"
                for xline in data["traceback"].splitlines()[:7]:
                    sl = str(xline)
                    if sl.startswith("EXCEPTION: "):
                        x = sl[11:]
                        break
                x = self.rx_xtype.sub(lambda match: "%s: " % match.group("xtype"), x)
                x = smart_text(x)[:100].encode("utf-8")
                fl += [
                    {
                        "uuid": fn[:-5],
                        "time": t,
                        "status": "*" if uts and ts > uts else " ",
                        "service": service,
                        "exception": x,
                    }
                ]
        fs = "%s %36s  %19s  %-29s %-s\n"
        self.stdout.write(fs % ("N", "UUID", "Time", "Service", "Exception"))
        for l in sorted(fl, key=operator.itemgetter("time"), reverse=True):
            self.stdout.write(
                fs % (l["status"], l["uuid"], l["time"].isoformat(), l["service"], l["exception"])
            )

    def handle_view(self, view_uuids, *args, **options):
        for u in view_uuids:
            path = os.path.join(self.PREFIX, "%s.json" % u)
            if not os.path.exists(path):
                self.stderr.write("Crashinfo not found: %s\n" % u)
                if os.path.exists(u):
                    path = u
                else:
                    continue
            with open(path) as f:
                data = ujson.load(f)
            self.stdout.write(data["traceback"])
            self.stdout.write("\n\n")

    def handle_clear(self, clear_uuids, *args, **options):
        if not clear_uuids:
            self.stdout.write(
                "Use './noc crashninfo clear all' for clear all crashinfo or"
                " './noc crashinfo clear UUID1 UUID2 ...'\n"
            )
        if clear_uuids and clear_uuids[0] == "all":
            clear_uuids = [fn[:-5] for fn in os.listdir(self.PREFIX) if fn.endswith(".json")]
        for u in clear_uuids:
            path = os.path.join(self.PREFIX, "%s.json" % u)
            if not os.path.exists(path):
                self.stderr.write("Crashinfo not found: %s\n" % u)
            else:
                self.stdout.write("Removing %s\n" % u)
                os.unlink(path)


if __name__ == "__main__":
    Command().run()
