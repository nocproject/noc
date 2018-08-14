# -*- coding: utf-8 -*-
# ----------------------------------------------------------------------
# noc datastream command
# ----------------------------------------------------------------------
# Copyright (C) 2007-2018 The NOC Project
# See LICENSE for details
# ----------------------------------------------------------------------


# Python modules
from __future__ import print_function
# NOC modules
from noc.core.management.base import BaseCommand
from noc.core.datastream.loader import loader
from noc.sa.models.managedobject import ManagedObject
from noc.sa.models.administrativedomain import AdministrativeDomain
from noc.models import is_document


class Command(BaseCommand):
    MODELS = {
        "managedobject": ManagedObject,
        "administrativedomain": AdministrativeDomain,
        "cfgping": ManagedObject,
        "cfgsyslog": ManagedObject,
        "cfgtrap": ManagedObject
    }

    def add_arguments(self, parser):
        subparsers = parser.add_subparsers(dest="cmd")
        #
        subparsers.add_parser("list")
        # rebuild
        rebuild_parser = subparsers.add_parser("rebuild")
        rebuild_parser.add_argument(
            "--datastream",
            help="Datastream name"
        )

    def handle(self, cmd, *args, **options):
        getattr(self, "handle_%s" % cmd)(*args, **options)

    def handle_list(self):
        for ds_name in sorted(loader.iter_datastreams()):
            self.print(ds_name)

    def iter_id(self, model):
        if is_document(model):
            for d in model._get_collection().find({}, {"_id": 1}, no_cursor_timeout=True).sort("_id"):
                yield d["_id"]
        else:
            for id in model.objects.values_list("id", flat=True):
                yield id

    def handle_rebuild(self, datastream, *args, **kwargs):
        model = self.MODELS.get(datastream)
        if not model:
            self.die("Unsupported datastream")
        ds = loader.get_datastream(datastream)
        if not ds:
            self.die("Cannot initialize datastream")
        total = model.objects.count()
        STEP = 100
        report_interval = max(total // STEP, 1)
        next_report = report_interval
        for n, obj_id in enumerate(self.iter_id(model)):
            ds.update_object(obj_id)
            if n == next_report:
                self.print("[%02d%%]" % ((n * 100) // total))
                next_report += report_interval
        self.print("Done")


if __name__ == "__main__":
    Command().run()
