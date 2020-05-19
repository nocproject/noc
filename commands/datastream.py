# ----------------------------------------------------------------------
# noc datastream command
# ----------------------------------------------------------------------
# Copyright (C) 2007-2020 The NOC Project
# See LICENSE for details
# ----------------------------------------------------------------------


# Python modules
import argparse
import itertools
import logging

# Third-party modules
import ujson

# NOC modules
from noc.core.management.base import BaseCommand
from noc.core.datastream.loader import loader
from noc.core.mongo.connection import connect
from noc.models import get_model
from noc.models import is_document

BATCH_SIZE = 20000


class Command(BaseCommand):
    MODELS = {
        "managedobject": "sa.ManagedObject",
        "administrativedomain": "sa.AdministrativeDomain",
        "cfgping": "sa.ManagedObject",
        "cfgsyslog": "sa.ManagedObject",
        "cfgtrap": "sa.ManagedObject",
        "dnszone": "dns.DNSZone",
        "resourcegroup": "inv.ResourceGroup",
        "alarm": ("fm.ActiveAlarm", "fm.ArchivedAlarm"),
        "vrf": "ip.VRF",
        "prefix": "ip.Prefix",
        "address": "ip.Address",
    }

    def add_arguments(self, parser):
        subparsers = parser.add_subparsers(dest="cmd")
        #
        subparsers.add_parser("list")
        # rebuild
        rebuild_parser = subparsers.add_parser("rebuild")
        rebuild_parser.add_argument("--datastream", help="Datastream name")
        rebuild_parser.add_argument("--jobs", type=int, default=0, help="Number of concurrent jobs")
        # get
        get_parser = subparsers.add_parser("get")
        get_parser.add_argument("--datastream", help="Datastream name")
        get_parser.add_argument("--filter", action="append", help="Datastream filter")
        get_parser.add_argument("objects", nargs=argparse.REMAINDER, help="Object ids")

    def handle(self, cmd, *args, **options):
        getattr(self, "handle_%s" % cmd)(*args, **options)

    def handle_list(self):
        for ds_name in sorted(loader.iter_classes()):
            self.print(ds_name)

    def iter_id(self, model):
        if not isinstance(model, tuple):
            model = (model,)
        for m in model:
            if is_document(m):
                match = {}
                while True:
                    print(match)
                    cursor = (
                        m._get_collection()
                        .find(match, {"_id": 1}, no_cursor_timeout=True)
                        .sort("_id")
                        .limit(BATCH_SIZE)
                    )
                    for d in cursor:
                        yield d["_id"]
                    if match and match["_id"]["$gt"] == d["_id"]:
                        break
                    match = {"_id": {"$gt": d["_id"]}}
            else:
                for id in m.objects.values_list("id", flat=True).order_by("id"):
                    yield id

    def get_total(self, model):
        if isinstance(model, tuple):
            c = 0
            for m in model:
                c += m.objects.count()
            return c
        return model.objects.count()

    def get_model(self, datastream):
        if isinstance(datastream, tuple):
            return tuple(self.get_model(ds) for ds in datastream)
        model_id = self.MODELS.get(datastream)
        if not model_id:
            self.die("Unsupported datastream")
        model = get_model(model_id)
        if not model:
            self.die("Invalid model")
        return model

    def handle_rebuild(self, datastream, jobs=0, *args, **kwargs):
        def update_object(obj_id):
            ds.update_object(obj_id)
            return obj_id

        def grouper(iterable, n):
            args = [iter(iterable)] * n
            return itertools.zip_longest(*args)

        def do_update(bulk):
            ds.bulk_update(bulk)
            yield from range(len(bulk))

        if not datastream:
            self.die("--datastream is not set. Set one from list: %s" % ", ".join(self.MODELS))
        model = self.get_model(datastream)
        connect()
        ds = loader[datastream]
        if not ds:
            self.die("Cannot initialize datastream")
        total = self.get_total(model)
        STEP = 100
        BATCH = 100
        n = 1
        report_interval = max(total // STEP, 1)
        next_report = report_interval
        if jobs:
            from multiprocessing.pool import ThreadPool

            pool = ThreadPool(jobs)
            iterable = pool.imap_unordered(update_object, self.iter_id(model))
        else:
            iterable = (ds.bulk_update(bulk) for bulk in grouper(self.iter_id(model), BATCH))

        if not self.no_progressbar:
            # Disable logging
            from noc.core.datastream.base import logger

            logger.setLevel(logging.CRITICAL)

        for _ in self.progress(iterable, max_value=total / BATCH):
            if self.no_progressbar and n == next_report:
                self.print("[%02d%%]" % ((n * 100) // total))
                next_report += report_interval
            n += 1
        self.print("Done")

    def handle_get(self, datastream, objects, filter, *args, **kwargs):
        if not datastream:
            self.die("--datastream is not set. Set one from list: %s" % ", ".join(self.MODELS))
        connect()
        ds = loader[datastream]
        if not ds:
            self.die("Cannot initialize datastream")
        filter = filter or []
        filters = filter[:]
        if objects:
            filters += ["id(%s)" % ",".join(objects)]
        for obj_id, change_id, data in ds.iter_data(filters=filters):
            gt = change_id.generation_time.strftime("%Y-%m-%d %H:%M:%S")
            self.print(
                "===[id: %s, change id: %s, time: %s]================" % (obj_id, change_id, gt)
            )
            d = ujson.loads(data)
            self.print(ujson.dumps(d, indent=2))


if __name__ == "__main__":
    Command().run()
