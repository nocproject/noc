# -*- coding: utf-8 -*-
##----------------------------------------------------------------------
## List available Time Series
##----------------------------------------------------------------------
## Copyright (C) 2007-2009 The NOC Project
## See LICENSE for details
##----------------------------------------------------------------------
"""
"""
from django.core.management.base import BaseCommand
from noc.pm.models import TimeSeries
import re
##
## build-manifest command handler
##
class Command(BaseCommand):
    help="List Available Time Series"
    def handle(self, *args, **options):
        rx=[re.compile(o) for o in args]
        for ts in TimeSeries.objects.order_by("name"):
            ts_name=ts.name
            if rx:
                for r in rx:
                    if r.search(ts_name):
                        print ts_name
                        break
            else:
                print ts_name
