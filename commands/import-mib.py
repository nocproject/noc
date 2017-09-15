# -*- coding: utf-8 -*-
# ---------------------------------------------------------------------
# Load MIBs
# ---------------------------------------------------------------------
# Copyright (C) 2007-2011 The NOC Project
# See LICENSE for details
# ---------------------------------------------------------------------

# Python modules
import argparse
# NOC modules
from noc.core.management.base import BaseCommand
from noc.fm.models.mib import MIB
from noc.fm.models.error import MIBRequiredException, OIDCollision


class Command(BaseCommand):
    help = "Import MIBs into database"

    def add_arguments(self, parser):
        parser.add_argument("-f", "--force", dest="force", action="store_true",
                            default=False),
        parser.add_argument(
            "args",
            nargs=argparse.REMAINDER,
            help="List of extractor names"
        )

    def handle(self, *args, **options):
        for a in args:
            try:
                MIB.load(a, force=options.get("force"))
            except MIBRequiredException as e:
                self.die(str(e))
            except ValueError as e:
                self.die(str(e))
            except OIDCollision as e:
                self.die(str(e))
        self.stdout.write("Import successful\n")

if __name__ == "__main__":
    Command().run()
