# -*- coding: utf-8 -*-
##----------------------------------------------------------------------
## job management
##----------------------------------------------------------------------
## Copyright (C) 2007-2012 The NOC Project
## See LICENSE for details
##----------------------------------------------------------------------

## Python modules
import uuid
## Django modules
from django.core.management.base import BaseCommand, CommandError


class Command(BaseCommand):
    """
    Generate UUID
    """
    help = "Generate UUID"

    def handle(self, *args, **options):
        print uuid.uuid4()
