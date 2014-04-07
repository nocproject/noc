# -*- coding: utf-8 -*-
##----------------------------------------------------------------------
## Dump address database
##----------------------------------------------------------------------
## Copyright (C) 2007-2014 The NOC Project
## See LICENSE for details
##----------------------------------------------------------------------

## Python modules
from optparse import make_option
import csv
import sys
## Django modules
from django.core.management.base import BaseCommand, CommandError
## NOC modules
from noc.gis.models.division import Division


class Command(BaseCommand):
    help = "Dump address database"

    option_list = BaseCommand.option_list + (
        make_option("-c", "--country", dest="countries", action="append"),
    )

    HEADERS = {
        "ru": ["RU_OKATO", "RU_OKTMO", "RU_FIAS_HOUSEGUID"]
    }

    DATA = {
        "ru": ["OKATO", "OKTMO", "FIAS_HOUSEGUID"]
    }

    LEVELS = 10

    def dump_division(self, writer, d, ctr, level):
        level = level + [d.name]
        # Dump buildings
        for bld in d.get_buildings():
            row = level + [""] * (self.LEVELS - len(level))
            addr = bld.primary_address
            row += [
                addr.display_ru(),
                addr.street,
                addr.num,
                addr.num2,
                addr.num_letter,
                addr.build,
                addr.build_letter,
                addr.struct,
                addr.struct2,
                addr.struct_letter,
                bld.postal_code
            ]
            for c in ctr:
                for cc in self.DATA[c]:
                    row += [bld.data.get(cc, "") or ""]
            writer.writerow(row)
        # Dump children
        for c in d.get_children().order_by("name"):
            self.dump_division(writer, c, ctr, level)

    def handle(self, *args, **options):
        ctr = options["countries"] or []
        # Check countries
        for c in ctr:
            if c not in self.HEADERS or c not in self.DATA:
                raise CommandError("Unsupported country: %s" % c)
        #
        header = ["LEVEL%d" % d for d in range(self.LEVELS)]
        header += [
            "HOUSE_ADDR", "STREET",
            "NUM", "NUM2", "NUM_LETTER",
            "BUILD", "BUILD_LETTER",
            "STRUCT", "STRUCT2", "STRUCT_LETTER",
            "POSTAL_CODE"
        ]
        for c in ctr:
            header += self.HEADERS[c]
        writer = csv.writer(sys.stdout)
        writer.writerow(header)
        for d in Division.get_top():
            self.dump_division(writer, d, ctr, [])
