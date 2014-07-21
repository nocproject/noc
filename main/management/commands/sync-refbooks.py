# -*- coding: utf-8 -*-
##----------------------------------------------------------------------
## Load and syncronize built-in refbooks
##----------------------------------------------------------------------
## Copyright (C) 2007-2009 The NOC Project
## See LICENSE for details
##----------------------------------------------------------------------
"""
"""
from __future__ import with_statement
from django.core.management.base import BaseCommand
from django.db import transaction
from noc.main.refbooks.refbooks import RefBook
from noc.main.models import RefBook as RB
import os
##
## Command handler
##
class Command(BaseCommand):
    help="Synchronize built-in Reference Books"
    def handle(self, *args, **options):
        transaction.enter_transaction_management()
        self.sync_refbooks()
        transaction.leave_transaction_management()
    
    ##
    ## Search for subclasses of givent class inside given directory
    ##
    def search(self,cls,d):
        classes={}
        for dirpath,dirnames,filenames in os.walk(d):
            mb="noc.main."+".".join(dirpath.split(os.sep)[1:])+"."
            for f in [f for f in filenames if f.endswith(".py") and f!="__init__.py" and not f.startswith(".")]:
                m=__import__(mb+f[:-3],{},{},"*")
                for ec_name in dir(m):
                    ec=getattr(m,ec_name)
                    try:
                        if not issubclass(ec,cls) or ec==cls:
                            continue
                    except:
                        continue
                    classes[ec]=None
        return classes.keys()
    ##
    def sync_refbooks(self):
        # Make built-in refbooks inventory
        loaded_refbooks={}
        for rb in RB.objects.filter(is_builtin=True):
            loaded_refbooks[rb.name]=rb
        for r in self.search(RefBook,"main/refbooks/refbooks"):
            name=unicode(r.name,"utf-8")
            r.sync()
            if name in loaded_refbooks:
                del loaded_refbooks[name]
        # Delete stale refbooks
        for rb in loaded_refbooks.values():
            print "DELETE REFBOOK ",rb.name
            rb.delete()
