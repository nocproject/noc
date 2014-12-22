# -*- coding: utf-8 -*-
##----------------------------------------------------------------------
## ./noc sync
##----------------------------------------------------------------------
## Copyright (C) 2007-2014 The NOC Project
## See LICENSE for details
##----------------------------------------------------------------------

## Python modules
import csv
import sys
from optparse import make_option
## Django modules
from django.core.management.base import BaseCommand, CommandError
## NOC modules
from noc.main.models.synccache import SyncCache
from noc.lib.debug import error_report


class Command(BaseCommand):
    option_list=BaseCommand.option_list+(
        make_option(
            "--list", "-l",
            action="store_const",
            dest="cmd",
            const="list",
            help="List configs"
        ),
        make_option(
            "--refresh", "-r",
            action="store_const",
            dest="cmd",
            const="refresh",
            help="Soft rebuild"
        ),
        make_option(
            "--uuid", "-U",
            action="store",
            dest="uuid",
            help="Filter by UUID"
        ),
        make_option(
            "--model", "-m",
            action="store",
            dest="model",
            help="Filter by model"
        ),
    )

    def handle(self, *args, **kwargs):
        try:
            self._handle(*args, **kwargs)
        except CommandError:
            raise
        except:
            error_report()

    def get_qs(self, **options):
        qs = SyncCache.objects
        if options["uuid"]:
            qs = qs.filter(uuid=options["uuid"])
        elif options["model"]:
            qs = qs.filter(model_id=options["model"])
        return qs

    def _handle(self, *args, **options):
        self.verbose = bool(options.get("verbosity"))
        self.query = {}
        if options["uuid"]:
            self.query["uuid"] = options["uuid"]
        if options["cmd"] == "list":
            return self.handle_list(self.get_qs(**options))
        elif options["cmd"] == "refresh":
            return self.handle_refresh(self.get_qs(**options))

    def handle_list(self, qs):
        writer = csv.writer(sys.stdout)
        h = ["UUID", "Model", "Object ID", "Object", "Sync",
             "instance", "Changed", "Expire"]
        writer.writerow(h)
        for sc in qs:
            writer.writerow([
                sc.uuid, sc.model_id, sc.object_id, unicode(sc.get_object()),
                sc.sync_id, sc.instance_id, sc.changed.isoformat(),
                sc.expire.isoformat()
            ])

    def handle_refresh(self, qs):
        for sc in qs:
            sc.refresh()
