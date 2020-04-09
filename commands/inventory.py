# -*- coding: utf-8 -*-
# ----------------------------------------------------------------------
# ./noc inventory command
# ----------------------------------------------------------------------
# Copyright (C) 2007-2020 The NOC Project
# See LICENSE for details
# ----------------------------------------------------------------------

# Python modules
import argparse

# NOC modules
from noc.core.management.base import BaseCommand
from noc.core.mongo.connection import connect
from noc.inv.models.object import Object


class Command(BaseCommand):
    help = "Query inventory"

    def add_arguments(self, parser):
        subparsers = parser.add_subparsers(dest="cmd")
        #
        rebuild_parser = subparsers.add_parser("find-serial")
        rebuild_parser.add_argument("serials", nargs=argparse.REMAINDER, help="Serials to search")

    def handle(self, cmd, *args, **options):
        getattr(self, "handle_%s" % cmd.replace("-", "_"))(*args, **options)

    def handle_find_serial(self, serials):
        connect()
        for serial in serials:
            for obj in Object.objects.filter(data__asset__serial=serial):
                self.print("@@@ Serial %s" % serial)
                self.dump_object(obj)

    def dump_object(self, obj):
        def obj_str(o, conn_name=None):
            r = []
            if conn_name:
                r += ["%s:" % conn_name]
            if o.name:
                r += [str(o.name)]
            r += ["(%s)" % o.model.name]
            sn = o.get_data("asset", "serial")
            if sn:
                r += ["Serial=%s" % sn]
            return " ".join(r)

        def iter_obj(o):
            outer_conns = list(o.iter_outer_connections())
            if len(outer_conns) == 1:
                # Allow follow up
                _, ro, rn = outer_conns[0]
                yield obj_str(o, rn)
                # Follow up
                for rr in iter_obj(ro):
                    yield rr
            else:
                # Try up to container
                yield obj_str(o)
                if o.container:
                    for rr in iter_obj(o.container):
                        yield rr

        for n, sr in enumerate(reversed(list(iter_obj(obj)))):
            self.print("%s * %s" % ("  " * n, sr))


if __name__ == "__main__":
    Command().run()
