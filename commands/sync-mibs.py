# -*- coding: utf-8 -*-
# ---------------------------------------------------------------------
# Upload bundled MIBs
# ---------------------------------------------------------------------
# Copyright (C) 2007-2017 The NOC Project
# See LICENSE for details
# ---------------------------------------------------------------------

# Python modules
import os
import gzip
import re
import datetime
import time
import argparse
# Third-party modules
import ujson
# NOC modules
from noc.core.management.base import BaseCommand
from noc.fm.models.mib import MIB


class Command(BaseCommand):
    help = "Upload bundled MIBs"

    def add_arguments(self, parser):
        parser.add_argument("-f", "--force", dest="force", action="store_true",
                            default=False, help="Force reload"),
        parser.add_argument(
            "args",
            nargs=argparse.REMAINDER,
            help="List of extractor names"
        )
    rx_last_updated = re.compile(r"\"last_updated\": \"([^\"]+)\"",
                                 re.MULTILINE)
    rx_version = re.compile(r"\"version\":\s*(\d+)", re.MULTILINE)
    PREFIX = "collections/fm.mibs/"

    def handle(self, *args, **options):
        print "Synchronizing MIBs"
        self.sync_mibs(force=options["force"])

    def get_bundled_mibs(self):
        """
        Generator returning bundled MIBs list
        :returns: Yields (MIB Name, path)
        """
        for root, dirs, files in os.walk(self.PREFIX):
            for f in files:
                if (not f.startswith(".") and
                        (f.endswith(".json.gz") or f.endswith(".json"))):
                    mib_name = f.split(".", 1)[0]
                    yield mib_name, os.path.join(root, f)

    def sync_mibs(self, force=False):
        """
        Upload bundled MIBs
        """
        for mib_name, path in self.get_bundled_mibs():
            mib = MIB.objects.filter(name=mib_name).first()
            if path.endswith(".gz"):
                f = gzip.GzipFile(path, "r")
            else:
                f = open(path, "r")
            if mib:
                data = f.read(4096)
                match = self.rx_last_updated.search(data)
                if not match:
                    # Not in first chunk. Read rest
                    data += f.read()
                    match = self.rx_last_updated.search(data)
                last_updated = self.decode_date(match.group(1))
                if (last_updated > mib.last_updated) or force:
                    print "    updating %s" % mib_name
                    self.update_mib(mib, data + f.read(), version=0)
                elif last_updated == mib.last_updated:
                    # Check internal version
                    match = self.rx_version.search(data)
                    if match:
                        version = int(match.group(1))
                    else:
                        # Read rest
                        data += f.read()
                        match = self.rx_version.search(data)
                        if match:
                            version = int(match.group(1))
                        else:
                            version = 0
                    if version > mib.version:
                        print "    updating %s" % mib_name
                        self.update_mib(mib, data + f.read(), version=version)
            else:
                print "    creating %s" % mib_name
                self.create_mib(f.read())
            f.close()

    def decode_date(self, s):
        """
        Convert YYYY-MM-DD date to DateTime
        """
        ts = time.strptime(s, "%Y-%m-%d")
        return datetime.datetime(year=ts.tm_year, month=ts.tm_mon,
                                 day=ts.tm_mday)

    def update_mib(self, mib, data, version=None):
        # Deserealize
        d = ujson.loads(data)
        # Update timestamp
        mib.last_updated = self.decode_date(d["last_updated"])
        # Update version
        if version is not None:
            mib.version = version
        mib.save()
        # Upload
        mib.clean()
        if d["data"]:
            mib.load_data(d["data"])

    def create_mib(self, data):
        # Deserialze
        d = ujson.loads(data)
        # Create MIB
        mib = MIB(name=d["name"], description=d["description"],
                  last_updated=self.decode_date(d["last_updated"]),
                  version=d.get("version", 0),
                  depends_on=d["depends_on"])
        mib.save()
        # Upload
        if d["data"]:
            mib.load_data(d["data"])

if __name__ == "__main__":
    Command().run()
