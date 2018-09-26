# -*- coding: utf-8 -*-
# ----------------------------------------------------------------------
# noc datastream command
# ----------------------------------------------------------------------
# Copyright (C) 2007-2018 The NOC Project
# See LICENSE for details
# ----------------------------------------------------------------------


# Python modules
from __future__ import print_function
import argparse
# Third-party modules
import ujson
# NOC modules
from noc.core.management.base import BaseCommand
from noc.core.datastream.loader import loader
from noc.sa.models.managedobject import ManagedObject
from noc.sa.models.administrativedomain import AdministrativeDomain
from noc.dns.models.dnszone import DNSZone
from noc.inv.models.resourcegroup import ResourceGroup
from noc.fm.models.activealarm import ActiveAlarm
from noc.fm.models.archivedalarm import ArchivedAlarm
from noc.models import is_document


class Command(BaseCommand):
    MODELS = {
        "managedobject": ManagedObject,
        "administrativedomain": AdministrativeDomain,
        "cfgping": ManagedObject,
        "cfgsyslog": ManagedObject,
        "cfgtrap": ManagedObject,
        "dnszone": DNSZone,
        "resourcegroup": ResourceGroup,
        "alarm": (ActiveAlarm, ArchivedAlarm)
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
        # get
        get_parser = subparsers.add_parser("get")
        get_parser.add_argument(
            "--datastream",
            help="Datastream name"
        )
        get_parser.add_argument(
            "--filter",
            action="append",
            help="Datastream filter"
        )
        get_parser.add_argument(
            "objects",
            nargs=argparse.REMAINDER,
            help="Object ids"
        )

    def handle(self, cmd, *args, **options):
        getattr(self, "handle_%s" % cmd)(*args, **options)

    def handle_list(self):
        for ds_name in sorted(loader.iter_datastreams()):
            self.print(ds_name)

    def iter_id(self, model):
        if not isinstance(model, tuple):
            model = (model,)
        for m in model:
            if is_document(m):
                for d in m._get_collection().find({}, {"_id": 1}, no_cursor_timeout=True).sort("_id"):
                    yield d["_id"]
            else:
                for id in m.objects.values_list("id", flat=True):
                    yield id

    def get_total(self, model):
        if isinstance(model, tuple):
            c = 0
            for m in model:
                c += m.objects.count()
            return c
        return model.objects.count()

    def handle_rebuild(self, datastream, *args, **kwargs):
        if not datastream:
            self.die("--datastream is not set. Set one from list: %s" % self.MODELS.keys())
        model = self.MODELS.get(datastream)
        if not model:
            self.die("Unsupported datastream")
        ds = loader.get_datastream(datastream)
        if not ds:
            self.die("Cannot initialize datastream")
        total = self.get_total(model)
        STEP = 100
        report_interval = max(total // STEP, 1)
        next_report = report_interval
        for n, obj_id in enumerate(self.iter_id(model)):
            ds.update_object(obj_id)
            if n == next_report:
                self.print("[%02d%%]" % ((n * 100) // total))
                next_report += report_interval
        self.print("Done")

    def handle_get(self, datastream, objects, filter, *args, **kwargs):
        if not datastream:
            self.die("--datastream is not set. Set one from list: %s" % self.MODELS.keys())
        ds = loader.get_datastream(datastream)
        if not ds:
            self.die("Cannot initialize datastream")
        filter = filter or []
        filters = filter[:]
        if objects:
            filters += ["id(%s)" % ",".join(objects)]
        for obj_id, change_id, data in ds.iter_data(filters=filters):
            gt = change_id.generation_time.strftime("%Y-%m-%d %H:%M:%S")
            self.print("===[id: %s, change id: %s, time: %s]================" % (obj_id, change_id, gt))
            d = ujson.loads(data)
            self.print(ujson.dumps(d, indent=2))


if __name__ == "__main__":
    Command().run()
