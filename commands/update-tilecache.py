# -*- coding: utf-8 -*-
# ---------------------------------------------------------------------
# ./noc update-tilecache command
# @todo: logging
# ---------------------------------------------------------------------
# Copyright (C) 2007-2012 The NOC Project
# See LICENSE for details
# ---------------------------------------------------------------------

# Python modules
import argparse
import logging
# NOC modules
from noc.core.management.base import BaseCommand, CommandError
from noc.gis.models import Map
from noc.gis.tile import TileTask
from noc.lib.sysutils import get_cpu_cores


class Command(BaseCommand):
    help = "Update tilecache"

    def add_arguments(self, parser):
        parser.add_argument("-a", "--all",
                            dest="all",
                            action="store_true",
                            default=False),
        parser.add_argument("-w", "--workers",
                            dest="workers",
                            action="store",
                            default=get_cpu_cores() * 2),
        parser.add_argument("-l", "--log",
                            dest="log",
                            action="store"),
        parser.add_argument("-f", "--force",
                            dest="force",
                            action="store_true",
                            default=False),
        parser.add_argument(
            "maps",
            nargs=argparse.REMAINDER,
            help="List of maps"
        )

    def handle(self, *args, **options):
        maps = []
        # Set up logging
        logging.root.setLevel(logging.DEBUG)
        # logging.root.setFormatter(logging.Formatter("%(asctime)s %(message)s"))
        # if options["log"]:
        #    logging.basicConfig(filename=options["log"], level=logging.DEBUG,
        #                        format="%(asctime)s %(message)s")
        # else:
        #    logging.basicConfig(level=logging.DEBUG,
        #                        format="%(asctime)s %(message)s")
        # Process -a option
        if "all" in options:
            for m in Map.objects.filter(is_active=True):
                if m.name not in options.get("maps", []):
                    maps += [m]
        # Process -m options
        for name in options.get("maps", []):
            m = Map.objects.filter(name=name).first()
            if not m:
                raise CommandError("Invalid map: '%s'" % name)
            if m.is_active:
                maps += [m]
        if not maps:
            raise CommandError("No active maps selected. Use -a or -m options")
        # Process tilecaches
        for m in maps:
            tt = TileTask(m, int(options["workers"]))
            tt.run()


if __name__ == "__main__":
    Command().run()
