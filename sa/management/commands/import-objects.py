# -*- coding: utf-8 -*-
##----------------------------------------------------------------------
## Import managed objects from CSV file
## USAGE:
## import-objects <file>
##----------------------------------------------------------------------
## Copyright (C) 2007-2010 The NOC Project
## See LICENSE for details
##----------------------------------------------------------------------
"""
"""
from __future__ import with_statement
from django.core.management.base import BaseCommand
from django.db import transaction
from noc.sa.models import ManagedObject
import sys

USAGE="""manage.py import-objects <csv file>
"""

class Command(BaseCommand):
    help="Import objects from CSV file"
    def print_usage(self):
        sys.stderr.write(USAGE)
        sys.exit(1)
        
    def handle(self, *args, **options):
        if not args:
            self.print_usage()
        transaction.enter_transaction_management()
        for file in args:
            with open(file) as f:
                print "Importing from %s"%file
                count,message=ManagedObject.from_csv(f)
                if count is None: # Error
                    print "... Error: %s"%message
                    print "Terminating"
                    sys.exit(1)
                else:
                    print "... %d records are imported"%count
        transaction.commit()
        transaction.leave_transaction_management()
        sys.exit(0)
