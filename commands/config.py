# -*- coding: utf-8 -*-
# ----------------------------------------------------------------------
# Collections manipulation
# ----------------------------------------------------------------------
# Copyright (C) 2007-2017 The NOC Project
# See LICENSE for details
# ----------------------------------------------------------------------

# Python modules
from noc.config import config
# NOC modules
from noc.core.management.base import BaseCommand


class Command(BaseCommand):
    def add_arguments(self, parser):
        subparsers = parser.add_subparsers(dest="cmd")
        subparsers.add_parser("dump")

    def handle(self, cmd, *args, **options):
        getattr(self, "handle_%s" % cmd)(*args, **options)

    def handle_dump(self):
        config.dump(url="yaml://")


if __name__ == "__main__":
    Command().run()
