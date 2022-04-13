# ----------------------------------------------------------------------
# Collections manipulation
# ----------------------------------------------------------------------
# Copyright (C) 2007-2017 The NOC Project
# See LICENSE for details
# ----------------------------------------------------------------------

# Python modules
import argparse
from noc.config import config

# NOC modules
from noc.core.management.base import BaseCommand


class Command(BaseCommand):
    def add_arguments(self, parser):
        subparsers = parser.add_subparsers(dest="cmd", required=True)
        dump_parser = subparsers.add_parser("dump")
        dump_parser.add_argument(
            "section",
            help="Print only config section with Name",
            nargs=argparse.REMAINDER,
            default=None,
        )

    def handle(self, cmd, *args, **options):
        getattr(self, "handle_%s" % cmd)(*args, **options)

    def handle_dump(self, section=None, *args, **options):
        config.dump(url="yaml://", section=section)


if __name__ == "__main__":
    Command().run()
