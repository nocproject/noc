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
##
## build-manifest command handler
##
class Command(BaseCommand):
    help="List Available Time Series"
    def handle(self, *args, **options):
        for ts in TimeSeries.objects.order_by("name"):
            print ts.name
