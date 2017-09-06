# -*- coding: utf-8 -*-
# ----------------------------------------------------------------------
# BI extract/load commands
# ----------------------------------------------------------------------
# Copyright (C) 2007-2017 The NOC Project
# See LICENSE for details
# ----------------------------------------------------------------------

# Python modules
from __future__ import print_function
import os
import datetime
import gzip
import time
# NOC modules
from noc.core.management.base import BaseCommand
from noc.lib.nosql import get_db
from noc.core.etl.bi.extractor.reboots import RebootsExtractor
from noc.core.etl.bi.extractor.alarms import AlarmsExtractor
from noc.core.clickhouse.dictionary import Dictionary
from noc.config import config
from noc.core.service.shard import Sharder


class Command(BaseCommand):
    DATA_PREFIX = config.path.bi_data_prefix
    DICT_XML_PREFIX = config.path.bi_dict_xml_prefix
    DICT_DATA_PREFIX = config.path.bi_dict_data_prefix

    TOPIC = "chwriter"
    NSQ_CONNECT_TIMEOUT = config.nsqd.connect_timeout
    NSQ_PUB_RETRY_DELAY = config.nsqd.pub_retry_delay

    EXTRACTORS = [
        RebootsExtractor,
        AlarmsExtractor
    ]

    # Extract by 1-day chunks
    EXTRACT_WINDOW = config.bi.extract_window

    def add_arguments(self, parser):
        subparsers = parser.add_subparsers(dest="cmd")
        # Args
        parser.add_argument(
            "--data-prefix",
            default=self.DATA_PREFIX,
            help="Show only summary"
        )
        parser.add_argument(
            "--dict-xml-prefix",
            default=self.DICT_XML_PREFIX,
            help="Show only summary"
        )
        parser.add_argument(
            "--dict-data-prefix",
            default=self.DICT_DATA_PREFIX,
            help="Show only summary"
        )
        # extract command
        extract_parser = subparsers.add_parser("extract")
        # clean command
        clean_parser = subparsers.add_parser("clean")
        # load command
        load_parser = subparsers.add_parser("load")
        # extract dicts
        extract_dict = subparsers.add_parser("dictionaries")

    def handle(self, cmd, data_prefix, dict_xml_prefix, dict_data_prefix, *args, **options):
        self.DATA_PREFIX = data_prefix
        self.DICT_XML_PREFIX = dict_xml_prefix
        self.DICT_DATA_PREFIX = dict_data_prefix
        return getattr(self, "handle_%s" % cmd)(*args, **options)

    def get_last_extract(self, name):
        coll = get_db()["noc.bi_timestamps"]
        d = coll.find_one({
            "_id": name
        })
        if d:
            return d["last_extract"]
        else:
            return None

    def set_last_extract(self, name, ts):
        coll = get_db()["noc.bi_timestamps"]
        coll.update({
            "_id": name,
        }, {
            "$set": {
                "last_extract": ts
            }
        }, upsert=True)

    def handle_extract(self, *args, **options):
        now = datetime.datetime.now()
        window = datetime.timedelta(seconds=self.EXTRACT_WINDOW)
        for ecls in self.EXTRACTORS:
            start = self.get_last_extract(ecls.name)
            if not start:
                start = ecls.get_start()
                if not start:
                    self.print("[%s] No data, skipping" % e.name)
                    continue
            stop = now - datetime.timedelta(seconds=ecls.extract_delay)
            while start < stop:
                end = min(start + window, stop)
                e = ecls(start=start, stop=end, prefix=self.DATA_PREFIX)
                self.print("[%s] Extracting %s - %s ... " % (e.name, start, end), end="", flush=True)
                t0 = time.time()
                nr = e.extract()
                dt = time.time() - t0
                if dt > 0.0:
                    self.print("%d records in %.3fs (%.2frec/s)" % (
                        nr, dt, float(nr) / dt
                    ))
                else:
                    self.print("no records")
                self.set_last_extract(ecls.name, e.last_ts or end)
                start += window

    def handle_dictionaries(self, *args, **options):
        # Extract dictionaries
        for dcls in Dictionary.iter_cls():
            # Temporary data
            dpath = os.path.join(self.DICT_DATA_PREFIX, "%s.tsv.tmp" % dcls._meta.name)
            self.stdout.write("Extracting dictionary data to %s\n" % dpath)
            with open(dpath, "w") as f:
                dcls.dump(f)
            # Temporary XML
            xpath = os.path.join(self.DICT_XML_PREFIX, "%s.xml.tml" % dcls._meta.name)
            self.stdout.write("Extracting dictionary XML to %s\n" % xpath)
            with open(xpath, "w") as f:
                f.write(dcls.get_config())
            # Move temporary data
            df = dpath[:-4]
            self.stdout.write("Renaming dictionary data to %s\n" % df)
            os.rename(dpath, df)
            # Move temporary XML
            xf = xpath[:-4]
            self.stdout.write("Rename dictionary XML to %s\n" % xf)
            os.rename(xpath, xf)

    def handle_clean(self, *args, **options):
        for ecls in self.EXTRACTORS:
            stop = self.get_last_extract(ecls.name)
            if not stop:
                continue
            e = ecls(start=stop, stop=stop, prefix=self.DATA_PREFIX)
            e.clean()

    def handle_load(self):
        for fn in sorted(os.listdir(self.DATA_PREFIX)):
            if not fn.endswith(".tsv.gz"):
                continue
            path = os.path.join(self.DATA_PREFIX, fn)
            meta_path = path[:-7] + ".meta"
            # Read fields
            with open(meta_path) as f:
                fields = f.read()
            # Read data
            with gzip.open(path, "rb") as f:
                data = f.read().splitlines()
            sharder = Sharder(fields)
            sharder.feed(data)
            sharder.pub()
            os.unlink(path)
            os.unlink(meta_path)


if __name__ == "__main__":
    Command().run()
