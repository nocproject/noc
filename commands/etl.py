# -*- coding: utf-8 -*-
##----------------------------------------------------------------------
## Extract/Transfer/Load commands
##----------------------------------------------------------------------
## Copyright (C) 2007-2015 The NOC Project
## See LICENSE for details
##----------------------------------------------------------------------

## NOC modules
from noc.core.management.base import BaseCommand


class Command(BaseCommand):
    def add_arguments(self, parser):
        subparsers = parser.add_subparsers(dest="cmd")
        # load command
        load_parser = subparsers.add_parser("load")

    def handle(self, cmd, *args, **options):
        return getattr(self, "handle_%s" % cmd)(*args, **options)

    def handle_load(self, *args, **options):
        from noc.core.etl.loader.base import BaseLoader
        BaseLoader.load_all("test")


if __name__ == "__main__":
    Command().run()
