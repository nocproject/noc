# -*- coding: utf-8 -*-
# ----------------------------------------------------------------------
# Service command
# ----------------------------------------------------------------------
# Copyright (C) 2007-2017 The NOC Project
# See LICENSE for details
# ----------------------------------------------------------------------

# Python modules
import argparse
# Third-party modules
# NOC modules
from noc.core.management.base import BaseCommand
from noc.sa.models.managedobjectselector import ManagedObjectSelector
from noc.core.mib import mib
from noc.core.error import NOCError


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
            if "get_snmp_get" not in o.scripts:
                continue
            if o.platform:
                platform = o.platform.full_name
            else:
                try:
                    v = o.scripts.get_version()
                except AttributeError:
                    v = {
                        "platform": "Unknown"
                    }
                platform = v["platform"]
            # sysObjectID
            try:
                v = o.scripts.get_snmp_get(oid=mib["SNMPv2-MIB::sysObjectID.0"])
            except NOCError:
                continue
            self.stdout.write(
                "%s,%s,%s,%s\n" % (
                    o.profile.name,
                    platform,
                    "SNMPv2-MIB::sysObjectID.0",
                    v
                )
            )


if __name__ == "__main__":
    Command().run()
