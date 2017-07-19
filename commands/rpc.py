# -*- coding: utf-8 -*-
##----------------------------------------------------------------------
## RPC cli
##----------------------------------------------------------------------
## Copyright (C) 2007-2015 The NOC Project
## See LICENSE for details
##----------------------------------------------------------------------

## Python modules
import os
import argparse
import pprint
## NOC modules
from noc.core.management.base import BaseCommand
from noc.core.service.client import open_sync_rpc, RPCError


class Command(BaseCommand):
    def add_arguments(self, parser):
        parser.add_argument(
            "--pretty",
            action="store_true",
            dest="pretty",
            default=False,
            help="Pretty-print output"
        )
        parser.add_argument(
            "--hint",
            action="append",
            dest="hints",
            help="<ip>:<port> of RPC service"
        )
        parser.add_argument(
            "rpc",
            nargs=1,
            help="RPC name in form <api>[-<pool>].<method>"
        )
        parser.add_argument(
            "arguments",
            nargs=argparse.REMAINDER,
            help="Arguments passed to RPC calls"
        )

    def handle(self, rpc, arguments, pretty, hints,
               *args, **options):
        service, method = rpc[0].split(".", 1)
        try:
            client = open_sync_rpc(
                service,
                calling_service="cli",
                hints=hints
            )
            method = getattr(client, method)
            result = method(*arguments)
        except RPCError as e:
            self.die("RPC Error: %s" % e)
        if pretty:
            self.stdout.write(
                pprint.pformat(result) + "\n"
            )
        else:
            self.stdout.write(str(result) + "\n")

if __name__ == "__main__":
    Command().run()
