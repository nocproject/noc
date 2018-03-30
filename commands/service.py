# -*- coding: utf-8 -*-
# ----------------------------------------------------------------------
# Service command
# ----------------------------------------------------------------------
# Copyright (C) 2007-2015 The NOC Project
# See LICENSE for details
# ----------------------------------------------------------------------

# Python modules
import argparse
# NOC modules
from noc.core.management.base import BaseCommand
from noc.core.service.loader import get_service
from noc.lib.text import format_table


class Command(BaseCommand):
    def add_arguments(self, parser):
        parser.add_argument(
            "services",
            nargs=argparse.REMAINDER,
            help="Service names"
        )

    def handle(self, services=None, *args, **options):
        service = get_service()

        out = [["Service", "ID", "Address"]]
        for sn in services:
            service.dcs.resolve_sync(sn)
            if sn in service.dcs.resolvers:
                for svc_id, address in service.dcs.resolvers[sn].services.items():
                    out += [[sn, svc_id, address]]
        self.stdout.write(
            format_table(
                [0, 0, 0, 0, 0],
                out
            ) + "\n"
        )


if __name__ == "__main__":
    Command().run()
