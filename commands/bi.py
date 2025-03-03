# ----------------------------------------------------------------------
# BI extract/load commands
# ----------------------------------------------------------------------
# Copyright (C) 2007-2022 The NOC Project
# See LICENSE for details
# ----------------------------------------------------------------------

# Python modules
import os
import datetime
import gzip
import time
import random
import argparse
from typing import List, Optional
from functools import partial
from gc import collect

# Third-party modules
import orjson
from pymongo.errors import OperationFailure

# NOC modules
from noc.core.management.base import BaseCommand
from noc.core.mongo.connection import get_db, connect
from noc.core.etl.bi.extractor.reboots import RebootsExtractor
from noc.core.etl.bi.extractor.alarms import AlarmsExtractor
from noc.core.etl.bi.extractor.alarmlogs import AlarmLogsExtractor
from noc.core.etl.bi.extractor.managedobject import ManagedObjectsExtractor
from noc.core.bi.dictionaries.loader import loader
from noc.core.clickhouse.model import DictionaryModel
from noc.core.msgstream.client import MessageStreamClient
from noc.config import config
from noc.core.ioloop.util import run_sync
from noc.models import get_model, is_document

BATCH_SIZE = 10000


class Command(BaseCommand):
    EXTRACTORS = [RebootsExtractor, AlarmsExtractor, ManagedObjectsExtractor, AlarmLogsExtractor]
    # Extract by 1-day chunks
    EXTRACT_WINDOW = config.bi.extract_window
    MIN_WINDOW = datetime.timedelta(seconds=2)

    def add_arguments(self, parser):
        subparsers = parser.add_subparsers(dest="cmd", required=True)
        # Args
        parser.add_argument(
            "--data-prefix", default=config.path.bi_data_prefix, help="Show only summary"
        )
        # extract command
        extract = subparsers.add_parser("extract")
        extract.add_argument(
            "--use-archive",
            action="store_true",
            default=False,
            help="Use archived collection for extract",
        )
        # clean command
        clean = subparsers.add_parser("clean")
        clean.add_argument("--force", action="store_true", default=False, help="Really remove data")
        # load command
        subparsers.add_parser("load")
        # dictionary command
        rebuild_dict = subparsers.add_parser("rebuild-dictionary")
        rebuild_dict.add_argument(
            "dictionaries",
            help="List rebuilding dictionaries",
            nargs=argparse.REMAINDER,
            default=None,
        )

    def handle(self, cmd, data_prefix, *args, **options):
        self.data_prefix = data_prefix
        connect()
        return getattr(self, "handle_%s" % cmd.replace("-", "_"))(*args, **options)

    def get_last_extract(self, name):
        coll = get_db()["noc.bi_timestamps"]
        d = coll.find_one({"_id": name})
        if d:
            return d["last_extract"]
        else:
            return None

    def set_last_extract(self, name, ts):
        coll = get_db()["noc.bi_timestamps"]
        coll.update_one({"_id": name}, {"$set": {"last_extract": ts}}, upsert=True)

    def handle_extract(self, use_archive=False, *args, **options):
        now = datetime.datetime.now()
        window = datetime.timedelta(seconds=self.EXTRACT_WINDOW)
        for ecls in self.EXTRACTORS:
            if not ecls.is_enabled():
                self.print("[%s] Not enabled, skipping" % ecls.name)
                continue
            start = self.get_last_extract(ecls.name)
            if not start or ecls.is_snapshot:
                start = ecls.get_start()
                if not start:
                    self.print("[%s] No data, skipping" % ecls.name)
                    continue
            stop = now - datetime.timedelta(seconds=ecls.extract_delay)
            extracted_record = 0
            is_exception = False
            while start < stop:
                end = min(start + window, stop)
                if hasattr(ecls, "use_archive"):
                    e = ecls(
                        start=start, stop=end, prefix=self.data_prefix, use_archive=use_archive
                    )
                else:
                    e = ecls(start=start, stop=end, prefix=self.data_prefix)
                t0 = time.time()
                try:
                    nr = e.extract(*args, **options)
                except OperationFailure as ex:
                    window = window // 2
                    if window < self.MIN_WINDOW:
                        self.print(
                            f"[{e.name}] Window less than {self.MIN_WINDOW.total_seconds()} seconds. Too many element in interval. Fix it manually"
                        )
                        self.die("Too many elements per interval")
                    self.print(
                        "[%s] Mongo Exception: %s, switch window to: %s" % (e.name, ex, window)
                    )
                    is_exception = True
                    continue
                self.print(
                    "[%s] Extracting %s - %s ... " % (e.name, start, end), end="", flush=True
                )
                dt = time.time() - t0
                if dt > 0.0:
                    self.print("%d records in %.3fs (%.2frec/s)" % (nr, dt, float(nr) / dt))
                else:
                    self.print("no records")
                self.set_last_extract(ecls.name, e.last_ts or end)
                start += window

                if is_exception:  # Save extracted record after exception
                    extracted_record = nr
                    is_exception = False
                if (
                    window != datetime.timedelta(seconds=self.EXTRACT_WINDOW)
                    and nr < extracted_record * 0.75
                ):
                    self.print("[%s] Restore Window to: %s" % (e.name, window * 2))
                    window = min(window * 2, datetime.timedelta(seconds=self.EXTRACT_WINDOW))

    def handle_dictionaries(self, *args, **options):
        # Extract dictionaries
        for dcls_name in loader:
            dcls: Optional["DictionaryModel"] = loader[dcls_name]
            if not dcls:
                continue
            # Temporary XML
            xpath = os.path.join(self.DICT_XML_PREFIX, "%s.xml.tml" % dcls._meta.name)
            self.stdout.write("Extracting dictionary XML to %s\n" % xpath)
            with open(xpath, "w") as f:
                f.write(dcls.get_config())
            # Move temporary XML
            xf = xpath[:-4]
            self.stdout.write("Rename dictionary XML to %s\n" % xf)
            os.rename(xpath, xf)

    def iter_id(self, model):
        if not isinstance(model, tuple):
            model = (model,)
        for m in model:
            if is_document(m):
                match = {}
                d = {}
                while True:
                    cursor = (
                        m._get_collection()
                        .find(match, {"_id": 1}, no_cursor_timeout=True)
                        .sort("_id")
                        .limit(BATCH_SIZE)
                    )
                    for d in cursor:
                        yield d["_id"]
                    if not d:
                        break
                    if match and match["_id"]["$gt"] == d["_id"]:
                        break
                    match = {"_id": {"$gt": d["_id"]}}
            else:
                for id in m.objects.values_list("id", flat=True).order_by("id"):
                    yield id

    def handle_rebuild_dictionary(self, dictionaries=None, *args, **options):
        async def upload(table: str, data: List[bytes]):
            CHUNK = 500
            n_parts = len(config.clickhouse.cluster_topology.split(","))
            async with MessageStreamClient() as client:
                while data:
                    chunk, data = data[:CHUNK], data[CHUNK:]
                    for part in range(0, n_parts):
                        await client.publish(
                            b"\n".join(chunk),
                            stream=f"ch.{table}",
                            partition=part,
                        )

        t0 = time.time()
        lt = time.localtime(t0)

        # Extract dictionaries
        for dcls_name in loader:
            if dictionaries and dcls_name not in dictionaries:
                continue
            self.print(f"Rebuild Dictionary: {dcls_name}")
            bi_dict_model: Optional["DictionaryModel"] = loader[dcls_name]
            if not bi_dict_model:
                continue
            model = get_model(bi_dict_model._meta.source_model)
            ids = list(self.iter_id(model))
            while ids:
                c_ids, ids = ids[:BATCH_SIZE], ids[BATCH_SIZE:]
                data = []
                collect()  # Collect previous item
                for item in model.objects.filter(id__in=c_ids):
                    try:
                        r = bi_dict_model.extract(item)
                    except (AttributeError, ValueError) as e:
                        self.print(f"[{model}:{item.id}] Error when extract item", e)
                        continue
                    if "bi_id" not in r:
                        r["bi_id"] = item.bi_id
                    r["ts"] = time.strftime("%Y-%m-%d %H:%M:%S", lt)
                    data += [orjson.dumps(r)]
                table = bi_dict_model._meta.db_table
                run_sync(partial(upload, table, data))

    def handle_clean(self, *args, **options):
        for ecls in self.EXTRACTORS:
            if not ecls.is_enabled():
                self.print("[%s] Not enabled, skipping" % ecls.name)
                continue
            stop = self.get_last_extract(ecls.name)
            if not stop:
                continue
            force = options.get("force")
            e = ecls(start=stop, stop=stop, prefix=self.data_prefix)
            self.print(
                "[%s] Cleaned before %s ... \n"
                % (e.name, stop - datetime.timedelta(seconds=ecls.clean_delay)),
                end="",
                flush=True,
            )
            if force:
                self.print(
                    "All data before %s from collection %s will be Remove..\n"
                    % (e.name, stop - datetime.timedelta(seconds=ecls.clean_delay))
                )
                for i in reversed(range(1, 10)):
                    self.print("%d\n" % i)
                    time.sleep(1)
            e.clean(force=force)

    def handle_load(self):
        async def upload(table: str, data: List[bytes]):
            CHUNK = 500
            n_parts = len(config.clickhouse.cluster_topology.split(","))
            async with MessageStreamClient() as client:
                while data:
                    chunk, data = data[:CHUNK], data[CHUNK:]
                    await client.publish(
                        b"\n".join(chunk),
                        stream=f"ch.{table}",
                        partition=random.randint(0, n_parts - 1),
                    )

        for fn in sorted(os.listdir(self.data_prefix)):
            if not fn.endswith(".jsonl.gz"):
                continue
            path = os.path.join(self.data_prefix, fn)
            # Read data
            with gzip.open(path, "rb") as f:
                data = f.read().splitlines()
            table = fn.split("-", 1)[0]
            run_sync(partial(upload, table, data))
            os.unlink(path)


if __name__ == "__main__":
    Command().run()
