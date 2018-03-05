# -*- coding: utf-8 -*-
# ---------------------------------------------------------------------
# display PYTHONPATH
# ---------------------------------------------------------------------
# Copyright (C) 2007-2010 The NOC Project
# See LICENSE for details
# ---------------------------------------------------------------------

# Python modules
import sys
# NOC modules
from noc.core.management.base import BaseCommand


class Command(BaseCommand):
    help = "Display PYTHONPATH"

    def add_arguments(self, parser):
        parser.add_argument("--list", "-l",
                            dest="one_column",
                            action="store_true",
                            const="list",
                            help="Display one path per line",
                            default=False,
                            ),

    def handle(self, *args, **options):
        if options.get("one_column", False):
            print "\n".join(sys.path)
        else:
            print ":".join(sys.path)


if __name__ == "__main__":
    Command().run()
