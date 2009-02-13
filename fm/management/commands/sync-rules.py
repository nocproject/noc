# -*- coding: utf-8 -*-
##----------------------------------------------------------------------
## Load and syncronized built-in FM classes and rules
##----------------------------------------------------------------------
## Copyright (C) 2007-2009 The NOC Project
## See LICENSE for details
##----------------------------------------------------------------------
"""
"""
from django.core.management.base import BaseCommand
from django.db import transaction
from noc.fm.rules.classes import EventClass
from noc.fm.rules.classification import ClassificationRule
import os

class Command(BaseCommand):
    help="Syncronize built-in FM classes and rules"
    def handle(self, *args, **options):
        transaction.enter_transaction_management()
        self.sync_classes()
        self.sync_classification_rules()
        transaction.leave_transaction_management()
    ##
    ## Search for subclasses of givent class inside given directory
    ##
    def search(self,cls,d):
        classes={}
        for dirpath,dirnames,filenames in os.walk(d):
            mb="noc.fm."+".".join(dirpath.split(os.sep)[1:])+"."
            for f in [f for f in filenames if f.endswith(".py") and f!="__init__.py"]:
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
    ## Syncronize event classes
    ##
    def sync_classes(self):
        for c in self.search(EventClass,"fm/rules/classes"):
            c.sync()
    ##
    ## Syncronize event classification rules
    ##
    def sync_classification_rules(self):
        for c in self.search(ClassificationRule,"fm/rules/classification"):
            c.sync()
