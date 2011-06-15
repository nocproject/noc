# -*- coding: utf-8 -*-
##----------------------------------------------------------------------
## Load MIBs
##----------------------------------------------------------------------
## Copyright (C) 2007-2009 The NOC Project
## See LICENSE for details
##----------------------------------------------------------------------
"""
"""
## Django modules
from django.core.management.base import BaseCommand, CommandError
## NOC modules
from noc.fm.models import MIB, MIBRequiredException


class Command(BaseCommand):
    help = "Import MIBs into database"

    def handle(self, *args, **options):
        for a in args:
            try:
                MIB.load(a)
            except MIBRequiredException, why:
                raise CommandError(why)
