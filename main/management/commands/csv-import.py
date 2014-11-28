# -*- coding: utf-8 -*-
##----------------------------------------------------------------------
## Import data from CSV
##----------------------------------------------------------------------
## Copyright (C) 2007-2011 The NOC Project
## See LICENSE for details
##----------------------------------------------------------------------

## Python modules
from __future__ import with_statement
import sys
from optparse import make_option
## Django modules
from django.core.management.base import BaseCommand, CommandError
from django.db import transaction
from django.contrib.contenttypes.models import ContentType
## NOC modules
from noc.lib.csvutils import csv_import, IR_FAIL, IR_SKIP, IR_UPDATE
from noc.lib.debug import error_report


class Command(BaseCommand):
    help = "Import data from csv file"

    option_list = BaseCommand.option_list + (
        make_option("-r", "--resolve", action="store", dest="resolve",
                    default="fail"),
        make_option("-d", "--delimiter", action="store",
                    dest="delimiter", default=",")
    )

    def _usage(self):
        print "Usage:"
        print "%s csv-import [--resolve=action] [--delimiter=<char>] <model> <file1> .. <fileN>" % (sys.argv[0])
        print "<action> is one of:"
        print "        fail - fail when record is already exists"
        print "        skip - skip duplicated records"
        print "        update - update duplicated records"
        print "<model> is one of:"
        for t in ContentType.objects.all():
            print "%s.%s" % (t.app_label, t.model)
        sys.exit(1)

    def handle(self, *args, **options):
        try:
            self._handle(*args, **options)
        except CommandError, why:
            raise CommandError(why)
        except SystemExit:
            pass
        except:
            error_report()

    def _handle(self, *args, **options):
        if len(args) < 1:
            self._usage()
        r = args[0].split(".")
        if len(r) != 2:
            self._usage()
        app, model = r
        try:
            m = ContentType.objects.get(app_label=app,
                                        model=model).model_class()
        except ContentType.DoesNotExist:
            self._usage()
        #
        try:
            resolve = {
                "fail": IR_FAIL,
                "skip": IR_SKIP,
                "update": IR_UPDATE
            }[options["resolve"]]
        except KeyError:
            raise CommandError("Invalid resolve option: %s" % options["resolve"])
        # Begin import
        transaction.enter_transaction_management()
        for f in args[1:]:
            print "Importing %s" % f
            with open(f) as f:
                count, error = csv_import(m, f, resolution=resolve,
                                          delimiter=options["delimiter"])
                if count is None:
                    raise CommandError(error)
                else:
                    print "... %d rows imported/updated" % count
        transaction.commit()
        transaction.leave_transaction_management()
