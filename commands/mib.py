# -*- coding: utf-8 -*-
# ----------------------------------------------------------------------
# MIB command
# ----------------------------------------------------------------------
# Copyright (C) 2007-2018 The NOC Project
# See LICENSE for details
# ----------------------------------------------------------------------

# Python modules
from __future__ import print_function
import argparse
import re
# NOC modules
from noc.core.management.base import BaseCommand
from noc.core.service.client import open_sync_rpc, RPCError
from noc.core.error import ERR_MIB_MISSED


class Command(BaseCommand):
    help = "MIB manipulation tool"

    rx_oid = re.compile("^\d+(\.\d+)+")

    def add_arguments(self, parser):
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
        # import
        import_parser = subparsers.add_parser("import")
        import_parser.add_argument(
            "paths",
            nargs=argparse.REMAINDER,
            help="Path to MIB files"
        )

    def handle(self, cmd, *args, **options):
        return getattr(self, "handle_%s" % cmd)(*args, **options)

    def handle_lookup(self, oids, *args, **kwargs):
        for oid in oids:
            self.lookup_mib(oid)

    def lookup_mib(self, v):
        try:
            svc = open_sync_rpc("mib")
            r = svc.lookup(v)
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
            svc = open_sync_rpc("mib")
            r = svc.get_text(v)
            if r.get("status"):
                self.print(r["data"])
            else:
                self.print("%s: Not found" % v)
        except RPCError as e:
            self.die("RPC Error: %s" % e)

    def handle_import(self, paths, *args, **kwargs):
        left_paths = paths
        while left_paths:
            done = set()
            for p in left_paths:
                if self.upload_mib(p):
                    done.add(p)
            if not done:
                # Cannot load additional mibs
                self.die("Cannot load MIBs: %s" % ", ".join(left_paths))

    def upload_mib(self, path):
        """
        Upload mib from file
        :param path:
        :return:
        """
        with open(path) as f:
            data = f.read()
        try:
            svc = open_sync_rpc("mib")
            r = svc.compile(data)
            if r.get("status"):
                return True
            if r.get("code") == ERR_MIB_MISSED:
                return False
            self.die("Cannot upload %s: %s" % (path, r.get("msg")))
        except RPCError as e:
            self.die("RPC Error: %s" % e)


if __name__ == "__main__":
    Command().run()
