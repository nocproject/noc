# -*- coding: utf-8 -*-
##----------------------------------------------------------------------
## ./noc crashinfo
##----------------------------------------------------------------------
## Copyright (C) 2007-2016 The NOC Project
## See LICENSE for details
##----------------------------------------------------------------------

## Python modules
import operator
import os
import stat
import datetime
import argparse
import stat
import re
## Third-party modules
import ujson
## NOC modules
from noc.core.management.base import BaseCommand
from noc.config import config


class Command(BaseCommand):
    PREFIX = config.path.cp_new

    rx_xtype = re.compile(r"^<(?:type|class) '(?P<xtype>[^']+)'>\s+")

    def add_arguments(self, parser):
        subparsers = parser.add_subparsers(dest="cmd")
        # list command
        list_parser = subparsers.add_parser("list")
        # view command
        view_parser = subparsers.add_parser("view")
        view_parser.add_argument(
            "view_uuids",
            nargs=argparse.REMAINDER,
            help="Crashinfo UUIDs"
        )
        # clear command
        clear_parser = subparsers.add_parser("clear")
        clear_parser.add_argument(
            "clear_uuids",
            nargs=argparse.REMAINDER,
            help="Crashinfo UUIDs"
        )

    def handle(self, cmd, *args, **options):
        return getattr(self, "handle_%s" % cmd)(*args, **options)

    def handle_list(self):
        # Get last update timestamp
        if os.path.exists(".hg/dirstate"):
            uts = os.stat(".hg/dirstate")[stat.ST_MTIME]
        else:
            uts = 0
        # Build list
        fl = []
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
            x = str(data["traceback"].splitlines()[5])
            if x.startswith("EXCEPTION: "):
                x = x[11:]
            x = self.rx_xtype.sub(lambda match: "%s: " % match.group("xtype"), x)
            x = unicode(x)[:100].encode("utf-8")
            fl += [{
                "uuid": fn[:-5],
                "time": t,
                "status": "*" if uts and ts > uts else " ",
                "service": service,
                "exception": x
            }]
        fs = "%s %36s  %19s  %-29s %-s\n"
        self.stdout.write(fs % ("N", "UUID", "Time", "Service", "Exception"))
        for l in sorted(fl, key=operator.itemgetter("time"), reverse=True):
            self.stdout.write(fs % (l["status"], l["uuid"], l["time"].isoformat(), l["service"], l["exception"]))

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
        if clear_uuids == "all":
            clear_uuids = [
                fn[:-5]
                for fn in os.listdir(self.PREFIX)
                if fn.endswith(".json")
            ]
        for u in clear_uuids:
            path = os.path.join(self.PREFIX, "%s.json" % u)
            if not os.path.exists(path):
                self.stderr.write("Crashinfo not found: %s\n" % u)
            else:
                self.stdout.write("Removing %s\n" % u)
                os.unlink(path)

if __name__ == "__main__":
    Command().run()
