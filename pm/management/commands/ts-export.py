# -*- coding: utf-8 -*-
##----------------------------------------------------------------------
## Dump time series as CSV
##----------------------------------------------------------------------
## Copyright (C) 2007-2009 The NOC Project
## See LICENSE for details
##----------------------------------------------------------------------
"""
"""
from django.core.management.base import BaseCommand
from noc.pm.models import TimeSeries
import sys
##
## build-manifest command handler
##
class Command(BaseCommand):
    help="Export Time Series as CSV file (timestamp,value)"
    def handle(self, *args, **options):
        for ts_name in args:
            try:
                ts=TimeSeries.objects.get(name=ts_name)
            except TimeSeries.DoesNotExist:
                sys.stderr.write("Time Series not found: '%s'"%ts_name)
                sys.stderr.flush()
                continue
            for tsd in ts.timeseriesdata_set.all().order_by("timestamp"):
                print "%d,%s"%(tsd.timestamp,"%f"%tsd.value if tsd.value is not None else "-")
