# -*- coding: utf-8 -*-
# ---------------------------------------------------------------------
# ./noc dump-crashinfo
# ---------------------------------------------------------------------
# Copyright (C) 2007-2017 The NOC Project
# See LICENSE for details
# ---------------------------------------------------------------------

# Python modules
from __future__ import print_function
import argparse
import cPickle
import time
# NOC modules
from noc.core.management.base import BaseCommand


class Command(BaseCommand):
    help = "Dump crashinfo file"

    def add_arguments(self, parser):
        parser.add_argument(
            "args",
            nargs=argparse.REMAINDER,
            help="List traceback files"
        )

    def handle(self, *args, **options):
        for path in args:
            with open(path) as f:
                self.dump_crashinfo(path, cPickle.load(f))

    def dump_crashinfo(self, path, data):
        ts = time.localtime(data.get("ts", 0))
        print("=" * 72)
        print("PATH      :", path)
        print("COMPONENT :", data.get("component"))
        print("TIME      : %04d-%02d-%02d %02d:%02d:%02d" % ts[:6])
        print("-" * 72)
        print(data.get("traceback"))


if __name__ == "__main__":
    Command().run()
