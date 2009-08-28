# -*- coding: utf-8 -*-
##----------------------------------------------------------------------
## Remove Time Series
##----------------------------------------------------------------------
## Copyright (C) 2007-2009 The NOC Project
## See LICENSE for details
##----------------------------------------------------------------------
"""
"""
from django.core.management.base import BaseCommand
from noc.pm.models import TimeSeries
##
## build-manifest command handler
##
class Command(BaseCommand):
    help="Remove Time Series"
    def handle(self, *args, **options):
        for a in args:
            for ts in TimeSeries.objects.filter(name__regex=a):
                print "Removing '%s'"%ts.name
                ts.timeseriesdata_set.all().delete()
                ts.delete()
