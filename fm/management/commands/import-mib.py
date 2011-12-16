# -*- coding: utf-8 -*-
##----------------------------------------------------------------------
## Load MIBs
##----------------------------------------------------------------------
## Copyright (C) 2007-2011 The NOC Project
## See LICENSE for details
##----------------------------------------------------------------------

## Python modules
from optparse import make_option
## Django modules
from django.core.management.base import BaseCommand, CommandError
## NOC modules
from noc.fm.models import MIB, MIBRequiredException, OIDCollision


class Command(BaseCommand):
    help = "Import MIBs into database"
    option_list = BaseCommand.option_list + (
        make_option("-f", "--force", dest="force", action="store_true",
                    default=False),
        )

    def handle(self, *args, **options):
        for a in args:
            try:
                MIB.load(a, force=options.get("force"))
            except MIBRequiredException, why:
                raise CommandError(why)
            except ValueError, why:
                raise CommandError(why)
            except OIDCollision, why:
                raise CommandError(why)
