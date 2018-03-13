# -*- coding: utf-8 -*-
# ---------------------------------------------------------------------
# Export model to CSV
# ---------------------------------------------------------------------
# Copyright (C) 2007-2011 The NOC Project
# See LICENSE for details
# ---------------------------------------------------------------------

# Python modules
from __future__ import print_function
import sys
import argparse
# Django modules
from django.db import models
# NOC modules
from noc.sa.models.managedobject import ManagedObject  # noqa
from noc.core.management.base import BaseCommand
from noc.core.csvutils import csv_export


class Command(BaseCommand):
    help = "Export model to CSV"

    def add_arguments(self, parser):
        parser.add_argument("-t", "--template",
                            dest="template",
                            action="store_true",
                            default=False,
                            help="dump only header row"
                            ),
        parser.add_argument(
            "args",
            nargs=argparse.REMAINDER,
            help="List of extractor names"
        )

    def _usage(self):
        print("Usage:")
        print("%s csv-export [-t] <model>" % (sys.argv[0]))
        print("Where <model> is one of:")
        for m in models.get_models():
            t = m._meta.db_table
            app, model = t.split("_", 1)
            print("%s.%s" % (app, model))
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
        print(csv_export(m,
                         queryset=self.get_queryset(m, args[1:]),
                         first_row_only=options.get("template")),)


if __name__ == "__main__":
    Command().run()
