# -*- coding: utf-8 -*-
##----------------------------------------------------------------------
## Export model to CSV
##----------------------------------------------------------------------
## Copyright (C) 2007-2010 The NOC Project
## See LICENSE for details
##----------------------------------------------------------------------
"""
"""
from django.core.management.base import BaseCommand
from optparse import make_option
from noc.lib.csvutils import csv_export
from django.contrib.contenttypes.models import ContentType
import sys
##
## build-manifest command handler
##
class Command(BaseCommand):
    help="Export model to CSV"
    def _usage(self):
        print "Usage:"
        print "%s csv-export <model>"%(sys.argv[0])
        print "Where <model> is one of:"
        for t in ContentType.objects.all():
            print "%s.%s"%(t.app_label,t.model)
        sys.exit(1)
            
    def handle(self, *args, **options):
        if len(args)!=1:
            self._usage()
        r=args[0].split(".")
        if len(r)!=2:
            self._usage()
        app,model=r
        try:
            m=ContentType.objects.get(app_label=app,model=model).model_class()
        except ContentType.DoesNotExist:
            self._usage()
        print csv_export(m)
