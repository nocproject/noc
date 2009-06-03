# -*- coding: utf-8 -*-
##----------------------------------------------------------------------
## Load and syncronized built-in FM classes, rules and MIBs
##----------------------------------------------------------------------
## Copyright (C) 2007-2009 The NOC Project
## See LICENSE for details
##----------------------------------------------------------------------
"""
"""
from __future__ import with_statement
from django.core.management.base import BaseCommand
from django.db import transaction
from noc.fm.rules.classes import EventClass
from noc.fm.rules.classification import ClassificationRule
from noc.fm.rules.correlation import CorrelationRule
from noc.fm.models import MIB,MIBRequiredException,EventClassificationRule,EventCorrelationRule
import os
##
## Command handler
##
class Command(BaseCommand):
    help="Syncronize built-in FM classes and rules"
    def handle(self, *args, **options):
        transaction.enter_transaction_management()
        self.sync_mibs()
        self.sync_classes()
        self.sync_classification_rules()
        self.sync_correlation_rules()
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
        # Make built-in rules list
        loaded_rules={}
        for r in EventClassificationRule.objects.filter(is_builtin=True):
            loaded_rules[r.name]=None
        # Sync new rules
        for c in self.search(ClassificationRule,"fm/rules/classification"):
            c.sync()
            if c.name in loaded_rules:
                del loaded_rules[c.name]
        # Delete stale rules
        for r in loaded_rules:
            rule=EventClassificationRule.objects.get(name=r)
            rule.delete()
            print "DELETE CLASSIFICATION RULE %s"%r
    ##
    ## Syncronize event correlation rules
    ##
    def sync_correlation_rules(self):
        # Make built-in rules list
        loaded_rules={}
        for r in EventCorrelationRule.objects.filter(is_builtin=True):
            loaded_rules[r.name]=None
        # Sync new rules
        for c in self.search(CorrelationRule,"fm/rules/correlation"):
            c.sync()
            if c.name in loaded_rules:
                del loaded_rules[c.name]
        # Delete stale rules
        for r in loaded_rules:
            rule=EventCorrelationRule.objects.get(name=r)
            rule.delete()
            print "DELETE CORRELATION RULE %s"%r
    ##
    ## Syncronize built-in MIBs
    ##
    def sync_mibs(self):
        # Loaded MIBs cache
        loaded_mibs={}
        for m in MIB.objects.all():
            loaded_mibs[m.name]=None
        # Enumerate local stored MIBs
        prefix=os.path.join("share","mibs")
        new_mibs={}
        for m in os.listdir(prefix):
            mib_name,ext=os.path.splitext(m)
            if mib_name not in loaded_mibs:
                # Try to upload new MIB
                try:
                    MIB.load(os.path.join(prefix,m))
                    loaded_mibs[mib_name]=None
                    print "CREATE MIB %s"%mib_name
                except MIBRequiredException,x:
                    new_mibs[mib_name]=x.requires_mib
        # Try to load new MIBs
        while new_mibs:
            l_new_mibs=len(new_mibs)
            for mib_name,requires_mib in new_mibs.items():
                if requires_mib in loaded_mibs:
                    try:
                        MIB.load(os.path.join(prefix,mib_name+".mib"))
                        loaded_mibs[mib_name]=None
                        print "CREATE MIB %s"%mib_name
                        del new_mibs[mib_name]
                    except MIBRequiredException,x:
                        new_mibs[mib_name]=x.requires_mib
            if len(new_mibs)==l_new_mibs: # No new MIBs loaded
                raise Exception("Following builtin MIBs cannot be loaded: %s"%" ".join(new_mibs.keys()))
