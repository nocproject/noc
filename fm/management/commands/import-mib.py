# -*- coding: utf-8 -*-
##----------------------------------------------------------------------
## Copyright (C) 2007-2009 The NOC Project
## See LICENSE for details
##----------------------------------------------------------------------
"""
"""
from django.core.management.base import BaseCommand,CommandError
from django.db import transaction
from noc.fm.models import MIB,MIBRequiredException

class Command(BaseCommand):
    help="Import MIB into database"
    def handle(self, *args, **options):
        transaction.enter_transaction_management()
        for a in args:
            try:
                MIB.load(a)
            except MIBRequiredException, why:
                raise CommandError(why)
        transaction.commit()
        transaction.leave_transaction_management()
