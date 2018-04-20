# -*- coding: utf-8 -*-
##----------------------------------------------------------------------
## ./noc update-tilecache command
## @todo: logging
##----------------------------------------------------------------------
## Copyright (C) 2007-2012 The NOC Project
## See LICENSE for details
##----------------------------------------------------------------------

## Python modules
import logging
from optparse import make_option
## Django modules
from django.core.management.base import BaseCommand, CommandError
## NOC modules
from noc.gis.models import Map
from noc.gis.tile import TileTask
from noc.lib.sysutils import get_cpu_cores


class Command(BaseCommand):
    help = "Update tilecache"

    option_list = BaseCommand.option_list + (
        make_option("-a", "--all", dest="all", action="store_true",
                   default=False),
        make_option("-m", "--map", dest="maps", action="append", default=[]),
        make_option("-w", "--workers", dest="workers", action="store",
                    default=get_cpu_cores() * 2),
        make_option("-l", "--log", dest="log", action="store"),
        make_option("-f", "--force", dest="force", action="store_true",
                    default=False)
    )

    def handle(self, *args, **options):
        maps = []
        # Set up logging
        logging.root.setLevel(logging.DEBUG)
        #logging.root.setFormatter(logging.Formatter("%(asctime)s %(message)s"))
        #if options["log"]:
        #    logging.basicConfig(filename=options["log"], level=logging.DEBUG,
        #                        format="%(asctime)s %(message)s")
        #else:
        #    logging.basicConfig(level=logging.DEBUG,
        #                        format="%(asctime)s %(message)s")
        # Process -a option
        if options["all"]:
            for m in Map.objects.filter(is_active=True):
                if m.name not in options["maps"]:
                    maps += [m]
        # Process -m options
        for name in options["maps"]:
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
