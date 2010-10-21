# -*- coding: utf-8 -*-
##----------------------------------------------------------------------
## manage.py todos
##----------------------------------------------------------------------
## Copyright (C) 2007-2010 The NOC Project
## See LICENSE for details
##----------------------------------------------------------------------
"""
"""
from __future__ import with_statement
from django.core.management.base import BaseCommand,CommandError
from noc.settings import INSTALLED_APPS
from noc.lib.fileutils import read_file
import os,re

class Command(BaseCommand):
    help="Display todo's left in code"
    exclude=set(["main/management/commands/todos.py"])
    def handle(self, *args, **options):
        dirs=["lib"]+[a[4:] for a in INSTALLED_APPS if a.startswith("noc.")]
        n=0
        for d in dirs:
            for dirpath,dirs,files in os.walk(d):
                for f in files:
                    if f.startswith(".") or not f.endswith(".py"):
                        continue
                    path=os.path.join(dirpath,f)
                    if path not in self.exclude:
                        n+=self.show_todos(path)
        if n:
            print "-"*72
            print "%d todos found"%n
        else:
            print "No todos found"
    
    ##
    ## Display todos
    ##
    def show_todos(self,path):
        data=read_file(path)
        if not data:
            return 0
        n=0
        for nl,l in enumerate(data.splitlines()):
            if "@todo:" in l:
                idx=l.index("@todo:")
                todo=l[idx+6:].strip()
                print "%50s:%5d: %s"%(path,nl,todo)
                n+=1
        return n
        