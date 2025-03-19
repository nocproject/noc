# ----------------------------------------------------------------------
# noc datastream command
# ----------------------------------------------------------------------
# Copyright (C) 2007-2020 The NOC Project
# See LICENSE for details
# ----------------------------------------------------------------------


# Python modules
import argparse
import datetime
import itertools
import logging

# Third-party modules
import orjson
from bson.objectid import ObjectId

# NOC modules
from noc.config import config
from noc.core.management.base import BaseCommand
from noc.core.datastream.loader import loader
from noc.core.mongo.connection import connect
from noc.models import get_model, get_model_id
from noc.models import is_document
from noc.core.comp import smart_text

BATCH_SIZE = 20000


class Command(BaseCommand):
    MODELS = {
        "managedobject": "sa.ManagedObject",
        "administrativedomain": "sa.AdministrativeDomain",
        "cfgmetrics": "pm.MetricType",
        "cfgmetricsources": ("sa.ManagedObject", "sla.SLAProbe", "inv.Sensor"),
        "cfgping": "sa.ManagedObject",
        "cfgsyslog": "sa.ManagedObject",
        "cfgtrap": "sa.ManagedObject",
        "cfgtarget": "sa.ManagedObject",
        "dnszone": "dns.DNSZone",
        "resourcegroup": "inv.ResourceGroup",
        "alarm": ("fm.ActiveAlarm", "fm.ArchivedAlarm"),
        "vrf": "ip.VRF",
        "prefix": "ip.Prefix",
        "address": "ip.Address",
        "cfgmxroute": "main.MessageRoute",
        "cfgmetricrules": "pm.MetricRule",
        "cfgeventrules": "fm.EventClassificationRule",
        "cfgdispositionrules": "fm.DispositionRule",
    }
    OLD_MAP = {
        "cfgsyslog": "cfgtarget",
        "cfgtrap": "cfgtarget",
        "cfgping": "cfgtarget",
    }
    BI_ID_DATASTREAM = {"cfgmetricsources"}  # DataStream that used bi_id as ID

    def add_arguments(self, parser):
        subparsers = parser.add_subparsers(dest="cmd", required=True)
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
        # clean
        clean_parser = subparsers.add_parser("clean")
        clean_parser.add_argument("--datastream", help="Datastream name")

    def handle(self, cmd, *args, **options):
        getattr(self, "handle_%s" % cmd)(*args, **options)

    def handle_list(self):
        for ds_name in sorted(loader.iter_classes()):
            self.print(ds_name)

    def iter_id(self, model, as_bi_id: bool = False):
        if not isinstance(model, tuple):
            model = (model,)
        for m in model:
            model_id = get_model_id(m)
            if is_document(m):
                match, d = {}, None
                while True:
                    cursor = (
                        m._get_collection()
                        .find(match, {"_id": 1, "bi_id": 1}, no_cursor_timeout=True)
                        .sort("_id")
                        .limit(BATCH_SIZE)
                    )
                    for d in cursor:
                        if as_bi_id:
                            yield f'{model_id}::{d["bi_id"]}'
                        else:
                            yield d["_id"]
                    if not d or (match and match["_id"]["$gt"] == d["_id"]):
                        break
                    match = {"_id": {"$gt": d["_id"]}}
            elif as_bi_id:
                for id, bi_id in m.objects.values_list("id", "bi_id").order_by("id"):
                    yield f"{model_id}::{bi_id}"
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
        if isinstance(model_id, tuple):
            model = tuple(get_model(mid) for mid in model_id)
        else:
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
        if datastream in self.OLD_MAP:
            datastream = self.OLD_MAP[datastream]
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
            iterable = pool.imap_unordered(
                update_object, self.iter_id(model, datastream in self.BI_ID_DATASTREAM)
            )
        else:
            iterable = (
                ds.bulk_update([b for b in bulk if b is not None])
                for bulk in grouper(self.iter_id(model, datastream in self.BI_ID_DATASTREAM), BATCH)
            )

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
        if datastream in self.OLD_MAP:
            datastream = self.OLD_MAP[datastream]
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
            d = orjson.loads(data)
            self.print(smart_text(orjson.dumps(d, option=orjson.OPT_INDENT_2)))

    def handle_clean(self, datastream, *args, **options):
        if datastream not in self.MODELS:
            self.die("--datastream is not set. Set one from list: %s" % ", ".join(self.MODELS))
        connect()
        ttl = getattr(config.datastream, "%s_ttl" % datastream, 0)
        if ttl:
            start_date = datetime.datetime.now() - datetime.timedelta(seconds=ttl)
            ds = loader[datastream]
            collection = ds.get_collection()
            collection.delete_many({"_id": {"$lte": ObjectId.from_datetime(start_date)}})
        self.print("Done")


if __name__ == "__main__":
    Command().run()
