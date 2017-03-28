# -*- coding: utf-8 -*-
##----------------------------------------------------------------------
## fix command
##----------------------------------------------------------------------
## Copyright (C) 2007-2016 The NOC Project
## See LICENSE for details
##----------------------------------------------------------------------

## Python modules
import argparse
import os
## Third-party modules
import yaml
## NOC modules
from noc.core.management.base import BaseCommand
from noc.core.handler import get_handler


class Command(BaseCommand):
    FIX_DIRS = ["custom/fixes", "fixes"]

    def add_arguments(self, parser):
        subparsers = parser.add_subparsers(dest="cmd")
        #
        subparsers.add_parser("list")
        #
        apply_parser = subparsers.add_parser("apply")
        apply_parser.add_argument(
            "fixes",
            nargs=argparse.REMAINDER,
            help="Apply named fixes"
        )

    def handle(self, cmd, *args, **options):
        return getattr(self, "handle_%s" % cmd)(*args, **options)

    def handle_list(self, *args, **options):
        fixes = set()
        for d in self.FIX_DIRS:
            if not os.path.isdir(d):
                continue
            files = os.listdir(d)
            if "__init__.py" not in files:
                print "WARNING: %s is missed. Create empty file or all fixes from %s will be ignored" % (
                    os.path.join(d, "__init__.py"),
                    d
                )
                continue
            for f in files:
                if not f.startswith("_") and f.endswith(".py"):
                    fixes.add(f[:-3])
        for f in sorted(fixes):
            self.stdout.write("%s\n" % f)

    def get_fix(self, name):
        for d in self.FIX_DIRS:
            if os.path.isfile(os.path.join(d, "%s.py" % name)):
                return get_handler(
                    "noc.%s.%s.fix" % (d.replace(os.sep, "."), name)
                )
        return None

    def handle_apply(self, fixes=None, *args, **options):
        if not fixes:
            return
        import noc.lib.nosql  # Connect to mongo
        for f in fixes:
            fix = self.get_fix(f)
            if not fix:
                self.die("Invalid fix '%s'" % f)
            self.stdout.write("Apply %s ...\n" % f)
            fix()
            self.stdout.write("... done\n")


if __name__ == "__main__":
    Command().run()
