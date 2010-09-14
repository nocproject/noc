# -*- coding: utf-8 -*-
##----------------------------------------------------------------------
## manage.py check-conf
##----------------------------------------------------------------------
## Copyright (C) 2007-2009 The NOC Project
## See LICENSE for details
##----------------------------------------------------------------------
"""
"""
from django.core.management.base import BaseCommand,CommandError
from noc.settings import config
import os,stat

class Command(BaseCommand):
    help="Check configuration files"
    def handle(self, *args, **options):
        # Check executables
        failed=[]
        for f in ["telnet","ssh","pg_dump","tar","gzip","smidump","smilint"]:
            path=config.get("path",f)
            if not os.path.isfile(path):
                failed+=["%s: %s is not found"%(f,path)]
            elif os.stat(path)[stat.ST_MODE]&stat.S_IXUSR==0:
                failed+=["%s: %s is not executeble"%(f,path)]
        if failed:
            raise CommandError("\n".join(failed))
