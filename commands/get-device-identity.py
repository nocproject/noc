# -*- coding: utf-8 -*-
##----------------------------------------------------------------------
## Service command
##----------------------------------------------------------------------
## Copyright (C) 2007-2015 The NOC Project
## See LICENSE for details
##----------------------------------------------------------------------

## Python modules
import argparse
## Third-party modules
## NOC modules
from noc.core.management.base import BaseCommand
from noc.sa.models.managedobjectselector import ManagedObjectSelector
from noc.lib.mib import mib


class Command(BaseCommand):
    def add_arguments(self, parser):
        parser.add_argument(
            "devices",
            nargs=argparse.REMAINDER,
            help="Device or selector list. Selectors starts with @"
        )

    def handle(self, devices, *args, **options):
        devs = set()
        for d in devices:
            try:
                devs |= set(ManagedObjectSelector.resolve_expression(d))
            except ManagedObjectSelector.DoesNotExist:
                self.die("Invalid object '%s'" % d)
        self.stdout.write("profile,platform,oid,value\n")
        for o in sorted(devs, key=lambda x: x.name):
            try:
                v = o.scripts.get_version()
            except AttributeError:
                v = {
                    "platform": "Unknown"
                }
            platform = v["platform"]
            # sysObjectID
            v = o.scripts.get_snmp_get(oid=mib["SNMPv2-MIB::sysObjectID.0"])
            self.stdout.write(
                "%s,%s,%s,%s\n" % (
                    o.profile_name,
                    platform,
                    "SNMPv2-MIB::sysObjectID.0",
                    v
                )
            )


if __name__ == "__main__":
    Command().run()
