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

    def add_arguments(self, parser):
        subparsers = parser.add_subparsers(dest="cmd", required=True)
        subparsers.add_parser("list")
        apply_parser = subparsers.add_parser("apply")
        apply_parser.add_argument("fixes", nargs=argparse.REMAINDER, help="Apply named fixes")

    def handle(self, cmd, *args, **options):
        return getattr(self, "handle_%s" % cmd)(*args, **options)

    def handle_list(self, *args, **options):
        fixes = set()
        for d in self.FIX_DIRS:
            if not os.path.isdir(d):
                continue
            files = os.listdir(d)
            if "__init__.py" not in files:
                print(
                    "WARNING: %s is missed. "
                    "Create empty file "
                    "or all fixes from %s will be ignored" % (os.path.join(d, "__init__.py"), d),
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
            if os.path.isfile(os.path.join(d, "%s.py" % name)):
                return get_handler("noc.%s.%s.fix" % (d.replace(os.sep, "."), name))
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
                self.die("Invalid fix '%s'" % f)
            print("Apply %s ..." % f, file=self.stdout)
            fix()
            print("... done", file=self.stdout)


if __name__ == "__main__":
    Command().run()
