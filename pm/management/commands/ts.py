# -*- coding: utf-8 -*-
##----------------------------------------------------------------------
## Time series operations
##----------------------------------------------------------------------
## Copyright (C) 2007-2014 The NOC Project
## See LICENSE for details
##----------------------------------------------------------------------

## Python modules
import logging
from optparse import make_option
## Django modules
from django.core.management.base import BaseCommand, CommandError
## NOC modules
from noc.pm.models.metric import Metric
from noc.pm.db.base import tsdb

logger = logging.getLogger(__name__)


class Command(BaseCommand):
    """
    Manage Jobs
    """
    help = "Update Probe Form"
    option_list=BaseCommand.option_list + (
        make_option(
            "--list",
            action="store_const",
            dest="cmd",
            const="list",
            help="List time series"
        ),
        make_option(
            "--export",
            action="store_const",
            dest="cmd",
            const="export",
            help="Export time series"
        ),
        # @todo: --remove option
    )

    def handle(self, *args, **options):
        if options["cmd"]:
            getattr(self, "handle_%s" % options["cmd"])(*args, **options)

    def iter_metrics(self, path=None):
        if path:
            for m in tsdb.find(path):
                yield m
        else:
            for m in Metric.objects.order_by("name"):
                yield m

    def handle_list(self, *args, **options):
        if not args:
            args = (None,)
        for p in args:
            for m in self.iter_metrics(p):
                print m

    def handle_export(self, *args, **options):
        pass