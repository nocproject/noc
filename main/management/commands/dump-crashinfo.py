# -*- coding: utf-8 -*-
##----------------------------------------------------------------------
## ./noc dump-crashinfo
##----------------------------------------------------------------------
## Copyright (C) 2007-2010 The NOC Project
## See LICENSE for details
##----------------------------------------------------------------------

## Python modules
from __future__ import with_statement
import cPickle
import time
## Django modules
from django.core.management.base import BaseCommand, CommandError


class Command(BaseCommand):
    help = "Dump crashinfo file"

    def handle(self, *args, **options):
        for path in args:
            with open(path) as f:
                self.dump_crashinfo(path, cPickle.load(f))

    def dump_crashinfo(self, path, data):
        ts = time.localtime(data.get("ts", 0))
        print "=" * 72
        print "PATH      :", path
        print "COMPONENT :", data.get("component")
        print "TIME      : %04d-%02d-%02d %02d:%02d:%02d" % ts[:6]
        print "-" * 72
        print data.get("traceback")
