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
from django.contrib.contenttypes.models import ContentType
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
        for t in ContentType.objects.all():
            print "%s.%s" % (t.app_label, t.model)
        sys.exit(1)

    def handle(self, *args, **options):
        if len(args) != 1:
            self._usage()
        r = args[0].split(".")
        if len(r) != 2:
            self._usage()
        app, model = r
        try:
            m = ContentType.objects.get(app_label=app,
                                        model=model).model_class()
        except ContentType.DoesNotExist:
            return self._usage()
        print csv_export(m, first_row_only=options.get("template")),
