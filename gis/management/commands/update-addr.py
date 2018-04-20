# -*- coding: utf-8 -*-
##----------------------------------------------------------------------
## Update address database
##----------------------------------------------------------------------
## Copyright (C) 2007-2014 The NOC Project
## See LICENSE for details
##----------------------------------------------------------------------

## Python modules
from ConfigParser import SafeConfigParser
import os
import inspect
from optparse import make_option
## Django modules
from django.core.management.base import BaseCommand, CommandError
## NOC modules
from noc.gis.parsers.address.base import AddressParser
from noc.lib.debug import error_report


class Command(BaseCommand):
    help = "Update address database"

    option_list = BaseCommand.option_list + (
        make_option("--no-download", action="store_false",
                    dest="download"),
        make_option("--download", action="store_true",
                    dest="download", default=True),
        make_option("--no-reset-cache", action="store_false",
                    dest="reset_cache"),
        make_option("--reset-cache", action="store_true",
                    dest="reset_cache", default=True),
    )

    def get_parsers(self):
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
        # Initialize parsers
        parsers = [p(config, options) for p in parsers]
        # Download
        if options["download"]:
            for p in parsers:
                print "Downloading", p.name
                if not p.download():
                    raise CommandError("Failed to download %s" % p.name)
        else:
            print "Skipping downloads"
        # Sync
        try:
            for p in parsers:
                print "Syncing", p.name
                p.sync()
        except:
            error_report()