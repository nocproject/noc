# -*- coding: utf-8 -*-
##----------------------------------------------------------------------
## ./noc sync
##----------------------------------------------------------------------
## Copyright (C) 2007-2012 The NOC Project
## See LICENSE for details
##----------------------------------------------------------------------

## NOC modules
import sys
## Django modules
from django.core.management.base import BaseCommand, CommandError
## NOC modules
from noc.lib.scheduler.utils import sync_request


class Command(BaseCommand):
    args = "<channel> <request> [<object1> .. <objectN>]"
    help = "Issue synchronization request"

    def handle(self, *args, **options):
        if len(args) < 2:
            raise CommandError("USAGE: %s <channel> <request> [<object1>.. <objectN>]" % sys.argv[0])

        channel = sys.argv[2]
        request = sys.argv[3].lower()
        if request not in ("list", "verify"):
            raise CommandError("Request must be one of: list, verify")
        if request == "list":
            sync_request([channel], "list")
        elif request == "verify":
            for obj in sys.argv[4:]:
                sync_request([channel], request, obj)
