# ----------------------------------------------------------------------
# fix command
# ----------------------------------------------------------------------
# Copyright (C) 2007-2019 The NOC Project
# See LICENSE for details
# ----------------------------------------------------------------------

# Python modules
import argparse
import os

# NOC modules
from noc.core.management.base import BaseCommand
from noc.core.handler import get_handler
from noc.config import config


class Command(BaseCommand):
    FIX_DIRS = config.get_customized_paths("fixes")

    def add_arguments(self, parser: argparse.ArgumentParser) -> None:
        subparsers = parser.add_subparsers(dest="cmd", required=True)
        subparsers.add_parser("list")
        apply_parser = subparsers.add_parser("apply")
        apply_parser.add_argument("fixes", nargs=argparse.REMAINDER, help="Apply named fixes")

    def handle(self, cmd, *args, **options):
        return getattr(self, f"handle_{cmd}")(*args, **options)

    def handle_list(self, *args, **options):
        fixes = set()
        for d in self.FIX_DIRS:
            if not os.path.isdir(d):
                continue
            files = os.listdir(d)
            if "__init__.py" not in files:
                print(
                    f"WARNING: {os.path.join(d, '__init__.py')} is missed. Create empty file or all fixes from {d} will be ignored",
                    file=self.stdout,
                )
                continue
            for f in files:
                if not f.startswith("_") and f.endswith(".py"):
                    fixes.add(f[:-3])
        for f in sorted(fixes):
            print(f, file=self.stdout)

    def get_fix(self, name):
        for d in self.FIX_DIRS:
            if os.path.isfile(os.path.join(d, f"{name}.py")):
                return get_handler(f"noc.{d.replace(os.sep, '.')}.{name}.fix")
        return None

    def handle_apply(self, fixes=None, *args, **options):
        if not fixes:
            return
        # Connect to mongo
        from noc.core.mongo.connection import connect

        connect()
        # Apply fixes
        for f in fixes:
            fix = self.get_fix(f)
            if not fix:
                self.die(f"Invalid fix '{f}'")
            print(f"Apply {f} ...", file=self.stdout)
            fix()
            print("... done", file=self.stdout)
