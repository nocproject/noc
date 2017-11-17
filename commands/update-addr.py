# -*- coding: utf-8 -*-
# ---------------------------------------------------------------------
# Update address database
# ---------------------------------------------------------------------
# Copyright (C) 2007-2014 The NOC Project
# See LICENSE for details
# ---------------------------------------------------------------------

# Python modules
from __future__ import print_function
from ConfigParser import SafeConfigParser
import os
import inspect
# NOC modules
from noc.core.management.base import BaseCommand, CommandError
from noc.gis.parsers.address.base import AddressParser
from noc.core.debug import error_report


class Command(BaseCommand):
    help = "Update address database"

    def add_arguments(self, parser):
        parser.add_argument("--no-download",
                            dest="download",
                            action="store_false"),
        parser.add_argument("--download",
                            dest="download",
                            action="store_true",
                            default=True),
        parser.add_argument("--no-reset-cache",
                            dest="reset_cache",
                            action="store_false",
                            default=False),
        parser.add_argument("--reset-cache",
                            dest="reset_cache",
                            action="store_true",
                            default=True)

    @staticmethod
    def get_parsers():
        parsers = []
        root = "gis/parsers/address"
        for m in os.listdir(root):
            if m in ("__init__.py", "base.py"):
                continue
            p = os.path.join(root, m)
            if os.path.isfile(p) and p.endswith(".py"):
                parsers += [m[:-3]]
            elif os.path.isdir(p) and os.path.isfile(os.path.join(p, "__init__.py")):
                parsers += [m]
        return parsers

    def handle(self, *args, **options):
        #
        parsers = []
        # Read config
        config = SafeConfigParser()
        for p in self.get_parsers():
            config.read(os.path.join("etc", "address", "%s.defaults" % p))
            config.read(os.path.join("etc", "address", "%s.conf" % p))
            if config.getboolean(p, "enabled"):
                m = __import__("noc.gis.parsers.address.%s" % p, {}, {}, "*")
                for l in dir(m):
                    a = getattr(m, l)
                    if inspect.isclass(a) and issubclass(a, AddressParser) and a != AddressParser:
                        parsers += [a]
            else:
                print("Parser '%s' is not enabled. Skipping.." % p)
        # Initialize parsers
        parsers = [p(config, options) for p in parsers]
        # Download
        if options["download"]:
            for p in parsers:
                print("Downloading", p.name)
                if not p.download():
                    raise CommandError("Failed to download %s" % p.name)
        else:
            print("Skipping downloads")
        # Sync
        try:
            for p in parsers:
                print("Syncing", p.name)
                p.sync()
        except:
            error_report()


if __name__ == "__main__":
    Command().run()
