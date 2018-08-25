# -*- coding: utf-8 -*-
# ----------------------------------------------------------------------
# ./noc nri
# ----------------------------------------------------------------------
# Copyright (C) 2007-2016 The NOC Project
# See LICENSE for details
# ----------------------------------------------------------------------

# Python modules
import argparse
# NOC modules
from noc.core.management.base import BaseCommand
from noc.inv.models.interface import Interface
from noc.sa.models.managedobjectselector import ManagedObjectSelector
from noc.core.etl.portmapper.loader import loader
from noc.lib.text import split_alnum, format_table


class Command(BaseCommand):
    PORT_ERROR = "ERROR!"

    def add_arguments(self, parser):
        subparsers = parser.add_subparsers(dest="cmd")
        # portmap command
        portmap_parser = subparsers.add_parser("portmap")
        portmap_parser.add_argument(
            "portmap_objects",
            nargs=argparse.REMAINDER,
            help="List of objects"
        )

    def handle(self, cmd, *args, **options):
        return getattr(self, "handle_%s" % cmd)(*args, **options)

    def handle_portmap(self, portmap_objects=[]):
        for po in portmap_objects:
            for o in ManagedObjectSelector.resolve_expression(po):
                if not o.remote_system:
                    self.stdout.write(
                        "%s (%s, %s) NRI: N/A\n" % (o.name, o.address, o.platform)
                    )
                    continue
                portmapper = loader.get_loader(o.remote_system.name)(o)
                nri = o.remote_system.name
                self.stdout.write("%s (%s, %s) NRI: %s\n" % (
                    o.name, o.address, o.platform, nri))
                r = []
                for i in Interface._get_collection().find({
                    "managed_object": o.id,
                    "type": "physical"
                }, {
                    "_id": 1,
                    "name": 1,
                    "nri_name": 1
                }):
                    rn = portmapper.to_remote(i["name"]) or self.PORT_ERROR
                    if rn == self.PORT_ERROR:
                        ln = self.PORT_ERROR
                    else:
                        ln = portmapper.to_local(rn) or self.PORT_ERROR
                    if i.get("nri_name") == rn and ln != self.PORT_ERROR:
                        status = "OK"
                    elif not i.get("nri_name") and ln != self.PORT_ERROR:
                        status = "Not in database"
                    elif rn == self.PORT_ERROR:
                        status = "Failed to convert to remote name"
                    else:
                        print(ln, rn, i.get("nri_name"))
                        status = "Failed to convert to local name"
                    r += [(i["name"], rn, i.get("nri_name", "--"), status)]
                r = [("Local", "Remote", "Interface NRI", "Status")] + sorted(r, key=lambda x: split_alnum(x[0]))
                self.stdout.write(
                    "%s\n" % format_table([0, 0, 0, 0], r, sep=" | ", hsep="-+-")
                )


if __name__ == "__main__":
    Command().run()
