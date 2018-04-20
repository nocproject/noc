# -*- coding: utf-8 -*-
##----------------------------------------------------------------------
## manage.py unpickle
##----------------------------------------------------------------------
## Copyright (C) 2007-2010 The NOC Project
## See LICENSE for details
##----------------------------------------------------------------------
"""
"""
from __future__ import with_statement
from django.core.management.base import BaseCommand,CommandError
import cPickle,pprint

class Command(BaseCommand):
    help="Unpickle and display raw data"
    def handle(self, *args, **options):
        for path in args:
            with open(path) as f:
                pprint.pprint(cPickle.load(f))
