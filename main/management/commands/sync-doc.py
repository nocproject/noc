# -*- coding: utf-8 -*-
##----------------------------------------------------------------------
## Rebuild online documentation
##----------------------------------------------------------------------
## Copyright (C) 2007-2009 The NOC Project
## See LICENSE for details
##----------------------------------------------------------------------
"""
"""
from django.core.management.base import BaseCommand
import os,glob,subprocess

##
## Command handler
##
class Command(BaseCommand):
    help="Syncronize online documentation"
    def handle(self, *args, **options):
        # Find and build all makefiles
        for makefile in glob.glob("share/doc/*/*/Makefile"):
            d,f=os.path.split(makefile)
            subprocess.call(["make","html"],cwd=d)
