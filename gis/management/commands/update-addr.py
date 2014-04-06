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
## Django modules
from django.core.management.base import BaseCommand, CommandError
## NOC modules
from noc.gis.parsers.address.base import AddressParser


class Command(BaseCommand):
    help = "Update address database"

    def get_parsers(self):
        # @todo: Read directory
        return ["fias"]

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
        parsers = [p(config) for p in parsers]
        # Download
        for p in parsers:
            print "Downloading", p.name
            if not p.download():
                raise CommandError("Failed to download %s" % p.name)
        # Sync
        for p in parsers:
            print "Syncing", p.name
            p.sync()
