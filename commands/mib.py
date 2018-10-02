# -*- coding: utf-8 -*-
# ----------------------------------------------------------------------
# MIB command
# ----------------------------------------------------------------------
# Copyright (C) 2007-2018 The NOC Project
# See LICENSE for details
# ----------------------------------------------------------------------

# Python modules
from __future__ import print_function
import logging
import argparse
import re
import os
import datetime
# NOC modules
from noc.core.management.base import BaseCommand
from noc.core.service.client import open_sync_rpc, RPCError
from noc.fm.models.mib import MIB, MIBData
from noc.services.mib.api.mib import MIBAPI
from noc.core.error import ERR_MIB_MISSED


class Command(BaseCommand):
    help = "MIB manipulation tool"

    rx_oid = re.compile("^\d+(\.\d+)+")

    svc = open_sync_rpc("mib")

    def add_arguments(self, parser):
        parser.add_argument(
            "--local",
            action="store_false",
            help="Not use mib service for import"
        )
        subparsers = parser.add_subparsers(dest="cmd")
        # get
        get_parser = subparsers.add_parser("get")
        get_parser.add_argument(
            "oids",
            nargs=argparse.REMAINDER,
            help="SNMP OIDs"
        )
        # lookup
        lookup_parser = subparsers.add_parser("lookup")
        lookup_parser.add_argument(
            "oids",
            nargs=argparse.REMAINDER,
            help="SNMP OIDs"
        )
        # Make cmib "Make compiled MIB for SA and PM scripts"
        make_cmib_parser = subparsers.add_parser("make_cmib")
        make_cmib_parser.add_argument("-o", "--output",
                                      dest="output", default="")
        make_cmib_parser.add_argument(
            "oids",
            nargs=argparse.REMAINDER,
            help="SNMP OIDs"
        )
        # import
        import_parser = subparsers.add_parser("import")
        import_parser.add_argument(
            "paths",
            nargs=argparse.REMAINDER,
            help="Path to MIB files"
        )

    def handle(self, cmd, *args, **options):
        if options.get("local"):
            self.svc = MIBAPI(ServiceStub(), None, None)
        return getattr(self, "handle_%s" % cmd)(*args, **options)

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

    def handle_make_cmib(self, oids, *args, **kwargs):
        if len(oids) != 1:
            self.stdout.write("Specify one MIB\n")
            self.die("")
        if kwargs["output"]:
            self.prepare_dirs(kwargs["output"])
            self.print("Opening file %s", kwargs["output"])
            f = open(kwargs["output"], "w")
            f = f.write
        else:
            self.print("Dumping to stdout")
            f = self.print
        mib = oids[0]
        try:
            m = MIB.objects.get(name=mib)
        except MIB.DoesNotExist:
            self.stdout.write("MIB not found: %s\n" % mib)
            self.die("")
        year = datetime.date.today().year
        r = [
            "# -*- coding: utf-8 -*-",
            "# ----------------------------------------------------------------------",
            "# %s" % mib,
            "#     Compiled MIB",
            "#     Do not modify this file directly",
            "#     Run ./noc make-cmib instead",
            "# ----------------------------------------------------------------------",
            "# Copyright (C) 2007-%s The NOC Project" % year,
            "# See LICENSE for details",
            "# ----------------------------------------------------------------------",
            "",
            "# MIB Name",
            "NAME = \"%s\"" % mib,
            "# Metadata",
            "LAST_UPDATED = \"%s\"" %
            m.last_updated.isoformat().split("T")[0],
            "COMPILED = \"%s\"" % datetime.date.today().isoformat(),
            "# MIB Data: name -> oid",
            "MIB = {"
        ]
        rr = []
        for md in sorted(
                MIBData.objects.filter(mib=m.id),
                key=lambda x: [int(y) for y in x.oid.split(".")]
        ):
            rr += ["    \"%s\": \"%s\"" % (md.name, md.oid)]
        r += [",\n".join(rr)]
        r += ["}", ""]
        data = "\n".join(r)
        f(data)

    def prepare_dirs(self, path):
        d = os.path.dirname(path)
        if not os.path.isdir(d):
            self.print("Creating directory %s", d)
            os.makedirs(d)

    def handle_import(self, paths, *args, **kwargs):
        left_paths = paths
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
        with open(path) as f:
            data = f.read()
        try:
            r = self.svc.compile(data)
            if r.get("status"):
                return True
            if r.get("code") == ERR_MIB_MISSED:
                return False
            self.die("Cannot upload %s: %s" % (path, r.get("msg")))
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
