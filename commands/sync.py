# -*- coding: utf-8 -*-
# ---------------------------------------------------------------------
# ./noc sync
# ---------------------------------------------------------------------
# Copyright (C) 2007-2014 The NOC Project
# See LICENSE for details
# ---------------------------------------------------------------------

# Python modules
from __future__ import print_function
import csv
import sys
# NOC modules
from noc.core.management.base import BaseCommand, CommandError
from noc.main.models.synccache import SyncCache
from noc.core.debug import error_report


class Command(BaseCommand):

    def add_arguments(self, parser):
        parser.add_argument("--list", "-l",
                            dest="cmd",
                            action="store_const",
                            const="list",
                            help="List configs"
                            ),
        parser.add_argument("--refresh", "-r",
                            dest="cmd",
                            action="store_const",
                            const="refresh",
                            help="Soft rebuild"
                            ),
        parser.add_argument("--uuid", "-U",
                            dest="uuid",
                            action="store",
                            help="Filter by UUID"
                            ),
        parser.add_argument("--model", "-m",
                            dest="model",
                            action="store",
                            help="Filter by model"
                            ),

    def handle(self, *args, **kwargs):
        try:
            self._handle(*args, **kwargs)
        except CommandError:
            raise
        except Exception:
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


if __name__ == "__main__":
    Command().run()
