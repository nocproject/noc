# -*- coding: utf-8 -*-
##----------------------------------------------------------------------
## display PYTHONPATH
##----------------------------------------------------------------------
## Copyright (C) 2007-2010 The NOC Project
## See LICENSE for details
##----------------------------------------------------------------------
"""
"""
from django.core.management.base import BaseCommand
from optparse import make_option
import sys
##
## build-manifest command handler
##
class Command(BaseCommand):
    help="Display PYTHONPATH"
    option_list = BaseCommand.option_list + (
        make_option("-1",action="store_true",dest="one_column",default=False,
            help="Display one path per line"),
    )
    
    def handle(self, *args, **options):
        if options.get("one_column",False):
            print "\n".join(sys.path)
        else:
            print ":".join(sys.path)
