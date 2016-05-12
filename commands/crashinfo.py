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
## Third-party modules
import ujson
## NOC modules
from noc.core.management.base import BaseCommand


class Command(BaseCommand):
    PREFIX = "var/cp/crashinfo/new"

    def add_arguments(self, parser):
        subparsers = parser.add_subparsers(dest="cmd")
        # list command
        list_parser = subparsers.add_parser("list")
        # view command
        view_parser = subparsers.add_parser("view")
        view_parser.add_argument(
            "uuids",
            nargs=argparse.REMAINDER,
            help="Crashinfo UUIDs"
        )
        # clear command
        clear_command = subparsers.add_parser("clear")
        view_parser.add_argument(
            "uuids",
            nargs=argparse.REMAINDER,
            help="Crashinfo UUIDs"
        )

    def handle(self, cmd, *args, **options):
        return getattr(self, "handle_%s" % cmd)(*args, **options)

    def handle_list(self):
        fl = []
        for fn in os.listdir(self.PREFIX):
            if not fn.endswith(".json"):
                continue
            path = os.path.join(self.PREFIX, fn)
            t = datetime.datetime.fromtimestamp(
                os.stat(path)[stat.ST_MTIME]
            )
            with open(path) as f:
                data = ujson.load(f)
            service = data["process"]
            if service.startswith("services/") and service.endswith("/service.py"):
                service = service[9:-11]
            fl += [{
                "uuid": fn[:-5],
                "time": t,
                "service": service
            }]
        fs = "%36s  %19s  %s\n"
        self.stdout.write(fs % ("UUID", "Time", "Service"))
        for l in sorted(fl, key=operator.itemgetter("time"), reverse=True):
            self.stdout.write(fs % (l["uuid"], l["time"].isoformat(), l["service"]))

    def handle_view(self, uuids, *args, **options):
        for u in uuids:
            path = os.path.join(self.PREFIX, "%s.json" % u)
            if not os.path.exists(path):
                self.stderr.write("Crashinfo not found: %s\n" % u)
                continue
            with open(path) as f:
                data = ujson.load(f)
            self.stdout.write(data["traceback"])
            self.stdout.write("\n\n")

    def handle_clear(self, uuids, *args, **options):
        for u in uuids:
            path = os.path.join(self.PREFIX, "%s.json" % u)
            if not os.path.exists(path):
                self.stderr.write("Crashinfo not found: %s\n" % u)
            else:
                self.stdout.write("Removing %s\n" % u)
                os.unlink(path)

if __name__ == "__main__":
    Command().run()
