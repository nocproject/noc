# -*- coding: utf-8 -*-
##----------------------------------------------------------------------
## BI extract/load commands
##----------------------------------------------------------------------
## Copyright (C) 2007-2016 The NOC Project
## See LICENSE for details
##----------------------------------------------------------------------

## Python modules
import datetime
## NOC modules
from noc.core.management.base import BaseCommand


class Command(BaseCommand):
    PREFIX = "var/bi"

    def add_arguments(self, parser):
        subparsers = parser.add_subparsers(dest="cmd")
        # extract command
        extract_parser = subparsers.add_parser("extract")

    def handle(self, cmd, *args, **options):
        return getattr(self, "handle_%s" % cmd)(*args, **options)

    def handle_extract(self, *args, **options):
        from noc.core.etl.bi.extractor.reboot import RebootExtractor

        extractors = [
            RebootExtractor
        ]
        start = datetime.datetime.fromtimestamp(0)
        stop = datetime.datetime.now()
        for ecls in extractors:
            e = ecls(start=start, stop=stop, prefix=self.PREFIX)
            e.extract()


if __name__ == "__main__":
    Command().run()
