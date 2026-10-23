# ---------------------------------------------------------------------
# ./noc dump-crashinfo
# ---------------------------------------------------------------------
# Copyright (C) 2007-2020 The NOC Project
# See LICENSE for details
# ---------------------------------------------------------------------

# Python modules
import argparse
import time
from pickle import load

# NOC modules
from noc.core.management.base import BaseCommand


class Command(BaseCommand):
    help = "Dump crashinfo file"

    def add_arguments(self, parser: argparse.ArgumentParser) -> None:
        parser.add_argument("args", nargs=argparse.REMAINDER, help="List traceback files")

    def handle(self, *args, **options):
        for path in args:
            with open(path) as f:
                self.dump_crashinfo(path, load(f))

    def dump_crashinfo(self, path, data):
        ts = time.localtime(data.get("ts", 0))
        print("=" * 72)
        print("PATH      :", path)
        print("COMPONENT :", data.get("component"))
        print(
            f"TIME      : {ts[0]:04d}-{ts[1]:02d}-{ts[2]:02d} {ts[3]:02d}:{ts[4]:02d}:{ts[5]:02d}"
        )
        print("-" * 72)
        print(data.get("traceback"))
