# -*- coding: utf-8 -*-
##----------------------------------------------------------------------
## Check required_mibs=[] declaration in classification rules
##----------------------------------------------------------------------
## Copyright (C) 2007-2009 The NOC Project
## See LICENSE for details
##----------------------------------------------------------------------
"""
"""
from __future__ import with_statement
from django.core.management.base import BaseCommand
from django.db import transaction
from noc.fm.rules.classification import ClassificationRule
from noc.fm.models import MIB
import types,os
##
## Command handler
##
class Command(BaseCommand):
    help="Check required_mibs=[...] declaration in event classification rules"
    def handle(self, *args, **options):
        self.mib_cache={}
        transaction.enter_transaction_management()
        self.check_classification_rules()
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
    ## Check classification rules
    ##
    def check_classification_rules(self):
        for c in self.search(ClassificationRule,"fm/rules/classification"):
            self.check_rule(c)
    ##
    ##
    ##
    def check_rule(self,rule):
        def to_oid(s):
            return s.replace("^","").replace("$","").replace("\\","")
        for p in rule.patterns:
            if type(p) not in [types.TupleType,types.ListType]:
                continue
            l,r=p
            if l=="source" and "SNMP Trap" not in r:
                return
            if to_oid(l)=="1.3.6.1.6.3.1.1.4.1.0":
                oid=to_oid(r)
                if oid.startswith("1.3.6") and not rule.required_mibs:
                    mib=self.resolve_mib(oid)
                    print rule.name+": required_mibs=[\""+mib+"\"]"
                return
    ##
    ## Try to resolve MIB
    ##
    def resolve_mib(self,oid):
        if oid in self.mib_cache:
            return self.mib_cache[oid]
        mib=MIB.get_name(oid)
        if "." in mib:
            mib=oid
        else:
            mib=mib.split("::",1)[0]
        self.mib_cache[oid]=mib
        return self.mib_cache[oid]
