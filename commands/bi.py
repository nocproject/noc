# -*- coding: utf-8 -*-
##----------------------------------------------------------------------
## BI extract/load commands
##----------------------------------------------------------------------
## Copyright (C) 2007-2016 The NOC Project
## See LICENSE for details
##----------------------------------------------------------------------

## Python modules
import os
import datetime
from collections import defaultdict
import gzip
## NOC modules
from noc.core.management.base import BaseCommand
from noc.lib.nosql import get_db
from noc.core.etl.bi.extractor.reboots import RebootsExtractor
from noc.core.clickhouse.connect import connection
from noc.core.clickhouse.model import Model


class Command(BaseCommand):
    PREFIX = "var/bi"

    EXTRACTORS = [
        RebootsExtractor
    ]

    def add_arguments(self, parser):
        subparsers = parser.add_subparsers(dest="cmd")
        # extract command
        extract_parser = subparsers.add_parser("extract")
        # clean command
        clean_parser = subparsers.add_parser("clean")
        # load command
        load_parser = subparsers.add_parser("load")

    def handle(self, cmd, *args, **options):
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
        t0 = datetime.datetime.fromtimestamp(0)
        now = datetime.datetime.now()
        for ecls in self.EXTRACTORS:
            start = self.get_last_extract(ecls.name) or t0
            stop = now - datetime.timedelta(seconds=ecls.extract_delay)
            e = ecls(start=start, stop=stop, prefix=self.PREFIX)
            self.stdout.write("Extracting %s (%s - %s)\n" % (
                e.name, start, stop
            ))
            e.extract()
            self.set_last_extract(ecls.name, e.last_ts or stop)

    def handle_clean(self, *args, **options):
        for ecls in self.EXTRACTORS:
            stop = self.get_last_extract(ecls.name)
            if not stop:
                continue
            e = ecls(start=stop, stop=stop, prefix=self.PREFIX)
            e.clean()

    def handle_load(self):
        ch = connection()
        ch.ensure_db()
        files = defaultdict(list)
        for f in sorted(os.listdir(self.PREFIX)):
            if not f.endswith(".tsv.gz"):
                continue
            x = f.split("-", 1)[0]
            files[x] += [os.path.join(self.PREFIX, f)]
        for mn in files:
            self.stdout.write("Loading %s\n" % mn)
            model = Model.get_model_class(mn)
            if not model:
                self.die("Cannot get model")
            model.ensure_table()
            for fn in files[mn]:
                self.stdout.write("    %s\n" % fn)
                with gzip.open(fn, "rb") as f:
                    data = f.read()
                ch.execute("INSERT INTO %s FORMAT TabSeparated" % mn, post=data)
                os.unlink(fn)

if __name__ == "__main__":
    Command().run()
