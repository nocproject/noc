# -*- coding: utf-8 -*-
##----------------------------------------------------------------------
## Load and syncronize built-in pyRules
##----------------------------------------------------------------------
## Copyright (C) 2007-2009 The NOC Project
## See LICENSE for details
##----------------------------------------------------------------------
"""
"""
from __future__ import with_statement
from django.core.management.base import BaseCommand
from django.db import transaction
from noc.main.models import PyRule
import os,re
##
rx_description=re.compile(r"\n##-----+\n##\s+DESCRIPTION:\s*\n(?P<description>.+?)\n##-----+",re.MULTILINE|re.DOTALL|re.UNICODE)
rx_interface=re.compile(r"\n##\s+INTERFACE:\s*(?P<interface>\S+)",re.MULTILINE|re.DOTALL|re.UNICODE)
##
## Command handler
##
class Command(BaseCommand):
    help="Synchronize built-in pyRules"
    def handle(self, *args, **options):
        transaction.enter_transaction_management()
        self.sync_pyrules()
        transaction.leave_transaction_management()
    
    def sync_pyrules(self):
        print "Synchronizing pyRules"
        left=set(PyRule.objects.filter(is_builtin=True).values_list("name",flat=True))
        p=os.path.join("main","pyrules")
        for fn in os.listdir(p):
            if not fn.endswith(".py") or fn=="__init__.py" or fn.startswith("."):
                continue
            with open(os.path.join(p,fn)) as f:
                data=f.read()
            match=rx_interface.search(data)
            if not match:
                raise Exception("No interface found in %s"%fn)
            interface=match.group("interface")
            match=rx_description.search(data)
            if not match:
                raise Exception("No description found in %s"%fn)
            description=match.group("description")
            description="\n".join([x[3:].strip() for x in description.splitlines()])
            name,x=os.path.splitext(fn)
            try:
                r=PyRule.objects.get(name=name)
                print "Updating pyRule %s"%name
                r.is_builtin=True
                r.description=description
                r.text=data
                r.interface=interface
                r.save()
            except PyRule.DoesNotExist:
                print "Creating pyRule %s"%name
                PyRule(name=name,description=description,text=data,is_builtin=True,interface=interface).save()
            try:
                left.remove(name)
            except:
                pass
        # Delete outdated rules
        for name in left:
            print "Deleting pyRule %s"%name
            PyRule.objects.get(name=name).delete()


