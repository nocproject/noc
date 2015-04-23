# -*- coding: utf-8 -*-
##----------------------------------------------------------------------
## Export model to CSV
##----------------------------------------------------------------------
## Copyright (C) 2007-2011 The NOC Project
## See LICENSE for details
##----------------------------------------------------------------------

## Python modules
import sys
from optparse import make_option
## Django modules
from django.core.management.base import BaseCommand
from django.db import models
## Python modules
from noc.lib.csvutils import csv_export


class Command(BaseCommand):
    help = "Export model to CSV"
    option_list = BaseCommand.option_list + (
        make_option("-t", "--template", dest="template", default=False,
                    action="store_true",
                    help="dump only header row"),
    )

    def _usage(self):
        print "Usage:"
        print "%s csv-export [-t] <model>" % (sys.argv[0])
        print "Where <model> is one of:"
        for m in models.get_models():
            t = m._meta.db_table
            app, model = t.split("_", 1)
            print "%s.%s" % (app, model)
        sys.exit(1)

    def get_queryset(self, model, args):
        if not args:
            return model.objects.all()
        q = {}
        for a in args:
            if "=" in a:
                k, v = a.split("=", 1)
                q[k] = v
        return model.objects.filter(**q)

    def handle(self, *args, **options):
        if len(args) < 1:
            self._usage()
        r = args[0].split(".")
        if len(r) != 2:
            self._usage()
        app, model = r
        m = models.get_model(app, model)
        if not m:
            return self._usage()
        print csv_export(m,
            queryset=self.get_queryset(m, args[1:]),
            first_row_only=options.get("template")),
