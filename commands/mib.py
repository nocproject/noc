# ----------------------------------------------------------------------
# MIB command
# ----------------------------------------------------------------------
# Copyright (C) 2007-2020 The NOC Project
# See LICENSE for details
# ----------------------------------------------------------------------

# Python modules
import logging
import argparse
import re
import os
import datetime
import contextlib
import gzip

# Third-party modules
from fastapi import APIRouter
import orjson

# NOC modules
from noc.core.management.base import BaseCommand
from noc.core.mongo.connection import connect
from noc.fm.models.mib import OIDCollision
from noc.core.service.client import open_sync_rpc
from noc.core.service.error import RPCError
from noc.fm.models.mib import MIB, MIBData
from noc.services.mib.paths.mib import MIBAPI
from noc.core.error import ERR_MIB_MISSED
from noc.core.comp import smart_bytes


class Command(BaseCommand):
    help = "MIB manipulation tool"

    rx_oid = re.compile(r"^\d+(\.\d+)+")

    svc = open_sync_rpc("mib")

    def add_arguments(self, parser):
        parser.add_argument("--local", action="store_true", help="Not use mib service for import")
        subparsers = parser.add_subparsers(dest="cmd", required=True)
        # get
        get_parser = subparsers.add_parser("get")
        get_parser.add_argument("oids", nargs=argparse.REMAINDER, help="SNMP OIDs")
        # lookup
        lookup_parser = subparsers.add_parser("lookup")
        lookup_parser.add_argument("oids", nargs=argparse.REMAINDER, help="SNMP OIDs")
        # Make collection-ready MIB
        make_collection_parser = subparsers.add_parser("make-collection")
        make_collection_parser.add_argument("-o", "--output", dest="output", default="")
        make_collection_parser.add_argument(
            "-b", "--bump", dest="bump", action="store_true", default=False
        )
        make_collection_parser.add_argument(
            dest="mib_name", nargs=argparse.REMAINDER, help="MIB Name"
        )
        # Make cmib "Make compiled MIB for SA and PM scripts"
        make_cmib_parser = subparsers.add_parser("make-cmib")
        make_cmib_parser.add_argument("-o", "--output", dest="output", default="")
        make_cmib_parser.add_argument(dest="mib_name", nargs=1, help="MIB Name")
        # import
        import_parser = subparsers.add_parser("import")
        import_parser.add_argument("paths", nargs=argparse.REMAINDER, help="Path to MIB files")

    def handle(self, cmd, *args, **options):
        if options.get("local"):
            self.svc = MIBAPI(APIRouter())
        connect()
        return getattr(self, "handle_%s" % cmd.replace("-", "_"))(*args, **options)

    def handle_lookup(self, oids, *args, **kwargs):
        for oid in oids:
            self.lookup_mib(oid)

    def lookup_mib(self, v):
        try:
            r = self.svc.lookup(v)
            if r.get("status"):
                self.print("%s = %s" % (r["name"], r["oid"]))
            else:
                self.print("%s: Not found" % v)
        except RPCError as e:
            self.die("RPC Error: %s" % e)

    def handle_get(self, oids, *args, **kwargs):
        for oid in oids:
            self.get_mib(oid)

    def get_mib(self, v):
        try:
            r = self.svc.get_text(v)
            if r.get("status"):
                self.print(r["data"])
            else:
                self.print("%s: Not found" % v)
        except RPCError as e:
            self.die("RPC Error: %s" % e)

    @contextlib.contextmanager
    def open_output(self, path=None):
        """
        Context manager for output writer
        :param path:
        :return:
        """
        if path:
            self.prepare_dirs(path)
            self.print("Writing to file %s" % path)
            if os.path.splitext(path)[-1] == ".gz":
                with gzip.GzipFile(path, "w") as f:
                    yield lambda x: f.write(smart_bytes(x))
            else:
                with open(path, "w") as f:
                    yield lambda x: f.write(x)
        else:
            self.print("Dumping to stdout")
            yield self.print

    def handle_make_collection(self, mib_name, bump=False, *args, **kwargs):
        if not mib_name:
            mibs = MIB.objects.filter()
        else:
            mibs = MIB.objects.filter(name__in=mib_name)
        for mib in mibs:
            # Get MIB
            mib_data = sorted(
                [
                    {
                        "oid": dd.oid,
                        "name": dd.name,
                        "description": dd.description,
                        "syntax": dd.syntax,
                    }
                    for dd in MIBData.objects.filter(mib=mib.id)
                ]
                + [
                    {
                        "oid": dd.oid,
                        "name": next((a for a in dd.aliases if a.startswith(mib.name + "::"))),
                        "description": dd.description,
                        "syntax": dd.syntax,
                    }
                    for dd in MIBData.objects.filter(aliases__startswith="%s::" % mib.name)
                ],
                key=lambda x: x["oid"],
            )
            # Prepare MIB
            if mib.last_updated:
                last_updated = mib.last_updated.strftime("%Y-%m-%d")
            else:
                last_updated = "1970-01-01"
            version = mib.version
            if bump:  # Bump to next version
                version += 1
            data = {
                "name": mib.name,
                "description": mib.description,
                "last_updated": last_updated,
                "version": version,
                "depends_on": mib.depends_on,
                "typedefs": mib.typedefs,
                "data": mib_data,
            }
            # Serialize and write
            path = kwargs.get("output") + mib.name + ".json.gz"
            with self.open_output(path) as f:
                f(orjson.dumps(data))

    def handle_make_cmib(self, mib_name, *args, **kwargs):
        def has_worth_hint(syntax):
            if not syntax:
                return False
            hint = syntax.get("display_hint")
            if not hint:
                return False
            base_type = syntax["base_type"]
            if base_type == "Integer32" and hint == "d":
                return False
            return not (base_type == "OctetString" and hint == "255a")

        if len(mib_name) != 1:
            self.print("Specify one MIB")
            self.die("")
        # Get MIB
        mib = MIB.get_by_name(mib_name[0])
        if not mib:
            self.print("MIB not found: %s" % mib_name[0])
            self.die("")
        # Build cmib
        year = datetime.date.today().year
        r = [
            "# ----------------------------------------------------------------------",
            "# %s" % mib,
            "# Compiled MIB",
            "# Do not modify this file directly",
            "# Run ./noc mib make-cmib instead",
            "# ----------------------------------------------------------------------",
            "# Copyright (C) 2007-%s The NOC Project" % year,
            "# See LICENSE for details",
            "# ----------------------------------------------------------------------",
            "",
            "# MIB Name",
            'NAME = "%s"' % mib,
            "",
            "# Metadata",
            'LAST_UPDATED = "%s"' % mib.last_updated.isoformat().split("T")[0],
            'COMPILED = "%s"' % datetime.date.today().isoformat(),
            "",
            "# MIB Data: name -> oid",
            "MIB = {",
        ]
        mib_data = sorted(
            MIBData.objects.filter(mib=mib.id),
            key=lambda x: [int(y) for y in x.oid.split(".")],
        )
        r += ["\n".join('    "%s": "%s",' % (md.name, md.oid) for md in mib_data)]
        r += ["}", "", "DISPLAY_HINTS = {"]
        r += [
            "\n".join(
                '    "%s": ("%s", "%s"),  # %s'
                % (md.oid, md.syntax["base_type"], md.syntax["display_hint"], md.name)
                for md in mib_data
                if has_worth_hint(md.syntax)
            )
        ]
        r += ["}", ""]
        data = "\n".join(r)
        with self.open_output(kwargs.get("output")) as f:
            f(data)

    def prepare_dirs(self, path):
        d = os.path.dirname(path)
        if not os.path.isdir(d):
            self.print("Creating directory %s", d)
            os.makedirs(d)

    def handle_import(self, paths, *args, **kwargs):
        left_paths = []
        for p in paths:
            if os.path.isdir(p):
                for file in os.listdir(p):
                    left_paths += [os.path.join(p, file)]
                continue
            left_paths += [p]
        while left_paths:
            done = set()
            for p in left_paths:
                if self.upload_mib(p, **kwargs):
                    done.add(p)
            if not done:
                # Cannot load additional mibs
                self.die("Cannot load MIBs: %s" % ", ".join(left_paths))
            left_paths = [x for x in left_paths if x not in done]

    def upload_mib(self, path, local=False):
        """
        Upload mib from file
        :param path:
        :param local:
        :return:
        """
        with open(path, "rb") as f:
            data = f.read()
        try:
            r = self.svc.compile(MIB.guess_encoding(data))
            if r.get("status"):
                return True
            if r.get("code") == ERR_MIB_MISSED:
                self.print("Cannot upload %s: MIB Missed - %s" % (path, r.get("msg")))
                return False
            self.die("Cannot upload %s: %s" % (path, r.get("msg")))
        except OIDCollision as e:
            self.print("Cannot upload %s: MIB OID Collision: %s" % (path, e))
            return False
        except RPCError as e:
            self.die("RPC Error: %s" % e)


class ServiceStub(object):
    def __init__(self):
        self.service_id = "stub"
        self.logger = logging.getLogger(__name__)
        self.address = "127.0.0.1"
        self.port = 0


if __name__ == "__main__":
    Command().run()
