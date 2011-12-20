# -*- coding: utf-8 -*-
##----------------------------------------------------------------------
## Lookup MIB
##----------------------------------------------------------------------
## Copyright (C) 2007-2011 The NOC Project
## See LICENSE for details
##----------------------------------------------------------------------

## Python modules
import re
## Django modules
from django.core.management.base import BaseCommand, CommandError
## NOC modules
from noc.fm.models import MIB


class Command(BaseCommand):
    help = "Lookup MIBs"

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
            raise CommandError("Not found: %s" % v)
