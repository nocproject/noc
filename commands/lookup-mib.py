# -*- coding: utf-8 -*-
# ---------------------------------------------------------------------
# Lookup MIB
# ---------------------------------------------------------------------
# Copyright (C) 2007-2011 The NOC Project
# See LICENSE for details
# ---------------------------------------------------------------------

# Python modules
import re
import argparse
# NOC modules
from noc.core.management.base import BaseCommand
from noc.fm.models.mib import MIB


class Command(BaseCommand):
    help = "Lookup MIBs"

    def add_arguments(self, parser):
        parser.add_argument(
            "args",
            nargs=argparse.REMAINDER,
            help="SNMP OIDs"
        )

    rx_oid = re.compile("^\d+(\.\d+)+")

    def handle(self, *args, **options):
        for a in args:
            self.lookup_mib(a)

    def lookup_mib(self, v):
        if self.rx_oid.match(v):
            # oid -> name
            r = MIB.get_name(v)
        else:
            r = MIB.get_oid(v)
        if r:
            print r
        else:
            self.die("Not found: %s" % v)

if __name__ == "__main__":
    Command().run()
