# -*- coding: utf-8 -*-
##----------------------------------------------------------------------
## Import data from CSV
##----------------------------------------------------------------------
## Copyright (C) 2007-2010 The NOC Project
## See LICENSE for details
##----------------------------------------------------------------------
"""
"""
from __future__ import with_statement
from django.core.management.base import BaseCommand
from django.db import transaction
from optparse import make_option
from noc.lib.csvutils import csv_import
from django.contrib.contenttypes.models import ContentType
import sys
##
## build-manifest command handler
##
class Command(BaseCommand):
    help="Import data from csv file"
    def _usage(self):
        print "Usage:"
        print "%s csv-import <model> <file1> .. <fileN>"%(sys.argv[0])
        print "Where <model> is one of:"
        for t in ContentType.objects.all():
            print "%s.%s"%(t.app_label,t.model)
        sys.exit(1)
            
    def handle(self, *args, **options):
        if len(args)<1:
            self._usage()
        r=args[0].split(".")
        if len(r)!=2:
            self._usage()
        app,model=r
        try:
            m=ContentType.objects.get(app_label=app,model=model).model_class()
        except ContentType.DoesNotExist:
            self._usage()
        # Begin import
        transaction.enter_transaction_management()
        for f in args[1:]:
            print "Importing %s"%f
            with open(f) as f:
                count,error=csv_import(m,f)
                if count is None:
                    print "... Error: %s"%error
                    sys.exit(1)
                else:
                    print "... %d rows imported/updated"%count
        transaction.commit()
        transaction.leave_transaction_management()
        sys.exit(0)
